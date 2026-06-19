"""
Resume Tailor Agent
--------------------
The most intelligence-heavy agent in FirstJob.

Philosophy:
- We do NOT keyword-stuff. That's detectable and looks fake.
- We do NOT fabricate experience. That's dishonest and harmful.
- We DO intelligently reframe, reorder, and rephrase the user's
  REAL experience to best speak to what this specific JD is asking for.

The process:
1. Deep JD analysis: understand the role's core needs, not just keywords
2. Profile mapping: for each JD requirement, find the closest real match
3. Intelligent rewriting: rephrase bullets to surface relevance
4. Reordering: lead with what matters most for this role
5. Diff generation: show user exactly what changed and why
"""

import json
import re
import copy
from openai import AsyncOpenAI
from core.config import settings
from loguru import logger

client = AsyncOpenAI(
    api_key=settings.anthropic_api_key,
    base_url="https://api.aimlapi.com/v1",
)


# ---------------------------------------------------------------------------
# System prompts — carefully engineered
# ---------------------------------------------------------------------------

JD_ANALYSIS_PROMPT = """You are a senior recruiter with 15 years of experience. Analyze this job description deeply.

Output ONLY valid JSON:
{
  "core_responsibilities": ["what they'll actually do day-to-day, top 5"],
  "must_have_skills": ["non-negotiable technical skills"],
  "nice_to_have_skills": ["preferred but not required"],
  "implied_soft_skills": ["communication, ownership, etc. implied by the JD"],
  "seniority_signals": "what level of depth/ownership is expected",
  "domain_vocabulary": ["specific terms, frameworks, methodologies they use"],
  "company_culture_signals": ["fast-paced, collaborative, data-driven, etc."],
  "what_they_care_most_about": "1-2 sentences on the single most important thing"
}"""

RESUME_TAILOR_PROMPT = """You are an expert resume writer helping a fresh graduate maximize their chances for a specific job.

STRICT RULES — violating these disqualifies the output:
1. NEVER invent experience, skills, or achievements that aren't in the base profile
2. NEVER add fake metrics or numbers — only use numbers already present
3. NEVER change company names, job titles, dates, or education details
4. DO reorder bullet points to lead with most relevant first
5. DO rephrase bullets to use the vocabulary from the JD (if the meaning is the same)
6. DO surface skills that are buried in bullet points into the skills section
7. DO reorder experience/projects sections to lead with most relevant
8. DO tighten wordy bullets to be more impactful
9. PRESERVE the candidate's authentic voice — don't make it sound AI-generated

For each change you make, provide the reason. The user must be able to trust every word.

Output ONLY valid JSON with this structure:
{
  "tailored_profile": { ...full profile JSON with modifications... },
  "diff": [
    {
      "section": "experience|skills|projects|summary",
      "type": "reorder|rephrase|surface|tighten",
      "original": "original text",
      "modified": "modified text",
      "reason": "why this change helps for this specific role"
    }
  ],
  "summary": "2-sentence explanation of the overall tailoring strategy",
  "match_improvements": ["specific things that now better match the JD"]
}"""


# ---------------------------------------------------------------------------
# Core tailoring pipeline
# ---------------------------------------------------------------------------

async def analyze_job_description(job: dict) -> dict:
    """Step 1: Deeply understand what the JD is really asking for."""
    jd_text = f"""
Title: {job['title']} at {job['company']}
Description: {job['description'][:2000]}
Requirements: {chr(10).join(job.get('requirements', []))}
Skills: {', '.join(job.get('skills_required', []))}
"""
    response = await client.chat.completions.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": JD_ANALYSIS_PROMPT},
            {"role": "user", "content": f"Analyze this JD:\n{jd_text}"}
        ]
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


async def tailor_resume_for_job(base_profile: dict, job: dict) -> dict:
    """
    Main entry point.
    Takes the user's base profile and a job, returns intelligently tailored resume + diff.
    """
    logger.info(f"Tailoring resume for: {job['title']} at {job['company']}")

    # Step 1: Analyze the JD
    jd_analysis = await analyze_job_description(job)
    logger.info(f"JD analyzed. Core focus: {jd_analysis.get('what_they_care_most_about', '')[:80]}")

    # Step 2: Tailor the resume
    tailor_prompt = f"""
JOB ANALYSIS:
{json.dumps(jd_analysis, indent=2)}

BASE RESUME PROFILE (DO NOT MODIFY company names, titles, dates, education):
{json.dumps(base_profile, indent=2)}

JOB BEING APPLIED TO:
Title: {job['title']} at {job['company']}
Full Description: {job['description'][:1500]}

Tailor this resume for the job. Follow all rules strictly.
Remember: The candidate's trust depends on you not fabricating anything.
"""

    response = await client.chat.completions.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[
            {"role": "system", "content": RESUME_TAILOR_PROMPT},
            {"role": "user", "content": tailor_prompt}
        ]
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    result = json.loads(raw)

    # Safety check: ensure critical fields weren't modified
    result = _safety_check(base_profile, result)

    logger.info(f"Tailoring complete. {len(result.get('diff', []))} changes made.")
    return result


def _safety_check(base_profile: dict, result: dict) -> dict:
    """
    Safety guard: ensure the AI didn't modify protected fields
    like company names, job titles, dates, or education.
    If violations found, revert those specific fields.
    """
    tailored = result.get("tailored_profile", {})
    violations = []

    # Check experience: company names, titles, dates must be unchanged
    base_exp = base_profile.get("experience", [])
    tailored_exp = tailored.get("experience", [])

    for i, (base, tail) in enumerate(zip(base_exp, tailored_exp)):
        if base.get("company") != tail.get("company"):
            violations.append(f"Company name changed at index {i}")
            tailored_exp[i]["company"] = base["company"]

        if base.get("title") != tail.get("title"):
            violations.append(f"Job title changed at index {i}")
            tailored_exp[i]["title"] = base["title"]

        if base.get("start_date") != tail.get("start_date"):
            tailored_exp[i]["start_date"] = base.get("start_date")

        if base.get("end_date") != tail.get("end_date"):
            tailored_exp[i]["end_date"] = base.get("end_date")

    # Check education: institution, degree, year must be unchanged
    base_edu = base_profile.get("education", [])
    tailored_edu = tailored.get("education", [])
    for i, (base, tail) in enumerate(zip(base_edu, tailored_edu)):
        if base.get("institution") != tail.get("institution"):
            violations.append(f"Institution changed at index {i}")
            tailored_edu[i]["institution"] = base["institution"]
        if base.get("degree") != tail.get("degree"):
            tailored_edu[i]["degree"] = base["degree"]

    if violations:
        logger.warning(f"Safety check caught {len(violations)} violations: {violations}")
        result["safety_violations"] = violations

    return result