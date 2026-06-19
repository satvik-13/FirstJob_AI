"""
Outreach Agent
--------------
After a user applies to a job, this agent:
1. Finds the HR/recruiter/hiring manager at the company
2. Writes a personalized, human-sounding cold email
3. Sends it via the user's Gmail account
4. Schedules a follow-up after 4 days if no reply

Key principle: Every email must feel personally written.
No templates. No mass-email tone. Short, specific, human.
"""

import json
import re
import base64
import httpx
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from openai import AsyncOpenAI
from core.config import settings
from loguru import logger

client = AsyncOpenAI(
    api_key=settings.anthropic_api_key,
    base_url="https://api.aimlapi.com/v1",
)


# ---------------------------------------------------------------------------
# Contact finding
# ---------------------------------------------------------------------------

async def find_contact_via_hunter(company_name: str, job_title: str) -> list[dict]:
    """Use Hunter.io to find HR/recruiter emails at the company."""
    if not settings.hunter_api_key:
        return []

    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            res = await http.get(
                "https://api.hunter.io/v2/domain-search",
                params={
                    "company": company_name,
                    "api_key": settings.hunter_api_key,
                    "limit": 5,
                    "type": "personal",
                    "seniority": "senior,executive",
                    "department": "human_resources,management",
                }
            )
            data = res.json()
            emails = data.get("data", {}).get("emails", [])

            contacts = []
            for e in emails[:3]:
                contacts.append({
                    "email": e.get("value"),
                    "name": f"{e.get('first_name', '')} {e.get('last_name', '')}".strip(),
                    "role": e.get("position", "HR/Recruiter"),
                    "source": "hunter",
                    "confidence": e.get("confidence", 0),
                })

            logger.info(f"Hunter found {len(contacts)} contacts for {company_name}")
            return contacts
    except Exception as e:
        logger.error(f"Hunter API error: {e}")
        return []


def guess_email_patterns(company_name: str, contact_name: str) -> list[dict]:
    """
    Fallback: generate likely email patterns.
    Works for ~40% of companies where pattern guessing is accurate.
    """
    domain = company_name.lower()
    domain = re.sub(r'\s+(inc|ltd|llc|pvt|technologies|solutions|tech|software|systems)\.?$', '', domain)
    domain = re.sub(r'[^a-z0-9]', '', domain)
    domain = f"{domain}.com"

    if not contact_name:
        return [{"email": f"hr@{domain}", "name": "HR Team", "role": "HR", "source": "pattern_guess", "confidence": 30}]

    parts = contact_name.lower().split()
    if len(parts) < 2:
        return []

    first, last = parts[0], parts[-1]
    patterns = [
        f"{first}.{last}@{domain}",
        f"{first}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{first}{last[0]}@{domain}",
    ]

    return [{"email": p, "name": contact_name, "role": "Unknown", "source": "pattern_guess", "confidence": 25} for p in patterns[:2]]


# ---------------------------------------------------------------------------
# Email writing
# ---------------------------------------------------------------------------

COLD_EMAIL_SYSTEM_PROMPT = """You are helping a fresh graduate write a cold outreach email to a hiring manager or HR professional.

RULES for the email:
1. Maximum 100 words in the body — busy people don't read long emails
2. Write in first person, natural tone — NOT formal/stiff
3. Reference something SPECIFIC about the company (use the company context provided)
4. Mention 1-2 genuinely relevant things from the candidate's background
5. End with a clear, low-pressure ask (a quick call or reply)
6. Subject line: specific and intriguing, not generic ("RE: Software Engineer Role" > "Job Application")
7. NO: "I hope this email finds you well", "I am writing to express my interest", or any cliché openers
8. Sound like a smart, confident person — not a nervous student

Output ONLY valid JSON:
{
  "subject": "email subject line",
  "body": "full email body (greeting through sign-off)",
  "followup_body": "short follow-up to send after 4 days if no reply"
}"""


async def write_cold_email(
    contact: dict,
    job_title: str,
    company_name: str,
    user_profile: dict,
    company_context: str = "",
) -> dict:
    """Use the LLM to write a personalized cold email."""

    skills = user_profile.get("skills", [])[:5]
    experience = user_profile.get("experience", [])
    projects = user_profile.get("projects", [])
    name = user_profile.get("full_name", "the candidate")

    top_experience = ""
    if experience:
        exp = experience[0]
        top_experience = f"worked as {exp.get('title')} at {exp.get('company')}"
    elif projects:
        p = projects[0]
        top_experience = f"built {p.get('name')} using {', '.join(p.get('tech_stack', [])[:2])}"

    prompt = f"""
Write a cold email for this situation:

Sender: {name}
Applying for: {job_title} at {company_name}
Recipient: {contact.get('name', 'Hiring Manager')} ({contact.get('role', 'HR')})
Candidate background: {top_experience}. Skills: {', '.join(skills)}
Company context: {company_context or f'{company_name} is a technology company'}

Make it feel genuinely personal and specific to this company.
"""

    response = await client.chat.completions.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[
            {"role": "system", "content": COLD_EMAIL_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Gmail sending
# ---------------------------------------------------------------------------

async def send_via_gmail(
    user_gmail_token: str,
    to_email: str,
    subject: str,
    body: str,
    sender_name: str,
) -> str:
    """Send email via Gmail API. Returns message ID."""
    message = MIMEText(body)
    message["to"] = to_email
    message["subject"] = subject
    message["from"] = f"{sender_name}"

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            res = await http.post(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                headers={
                    "Authorization": f"Bearer {user_gmail_token}",
                    "Content-Type": "application/json",
                },
                json={"raw": raw_message}
            )
            res.raise_for_status()
            data = res.json()
            logger.info(f"Email sent to {to_email}, message ID: {data.get('id')}")
            return data.get("id", "")
    except Exception as e:
        logger.error(f"Gmail send error: {e}")
        raise


# ---------------------------------------------------------------------------
# Main outreach pipeline
# ---------------------------------------------------------------------------

async def find_and_queue_outreach(
    application_id: str,
    user_id: str,
    company_name: str,
    job_title: str,
    user_profile: dict,
):
    """
    Full outreach pipeline triggered after apply.
    Runs as a background task.
    """
    from core.database import AsyncSessionLocal
    from models.outreach import Outreach, OutreachStatus
    from models.user import User
    from sqlalchemy import select
    import uuid

    logger.info(f"Starting outreach for {job_title} at {company_name}")

    async with AsyncSessionLocal() as db:
        user = await db.get(User, uuid.UUID(user_id))
        if not user or not user.gmail_access_token:
            logger.warning("No Gmail token — skipping outreach")
            return

        contacts = await find_contact_via_hunter(company_name, job_title)
        if not contacts:
            contacts = [{"email": f"hr@{company_name.lower().replace(' ', '')}.com",
                        "name": "HR Team", "role": "HR Manager",
                        "source": "pattern_guess", "confidence": 25}]

        contact = contacts[0]
        logger.info(f"Outreach target: {contact['email']} ({contact['source']})")

        email_content = await write_cold_email(
            contact=contact,
            job_title=job_title,
            company_name=company_name,
            user_profile=user_profile,
        )

        try:
            gmail_id = await send_via_gmail(
                user_gmail_token=user.gmail_access_token,
                to_email=contact["email"],
                subject=email_content["subject"],
                body=email_content["body"],
                sender_name=user_profile.get("full_name", user.full_name),
            )
            status = OutreachStatus.sent
        except Exception:
            gmail_id = None
            status = OutreachStatus.failed

        outreach = Outreach(
            user_id=uuid.UUID(user_id),
            application_id=uuid.UUID(application_id),
            contact_name=contact.get("name"),
            contact_email=contact["email"],
            contact_role=contact.get("role"),
            contact_source=contact.get("source"),
            subject=email_content["subject"],
            body=email_content["body"],
            followup_body=email_content.get("followup_body"),
            status=status,
            sent_at=datetime.utcnow() if status == OutreachStatus.sent else None,
            followup_scheduled_at=datetime.utcnow() + timedelta(days=4),
            gmail_message_id=gmail_id,
        )
        db.add(outreach)
        await db.commit()
        logger.info(f"Outreach saved. Status: {status}")