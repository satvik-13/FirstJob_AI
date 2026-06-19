"""
Job Scraper Agent
-----------------
Fetches job listings from multiple sources:
- JSearch API (RapidAPI) → real Indeed + LinkedIn + Glassdoor data
- Naukri mock data (no public API)
- Internshala mock data (no public API)

Responsibilities:
- Fetch jobs based on user preferences
- Deduplicate across sources using content hash
- Compute match score against user profile
- Normalize all sources into a unified Job schema
"""

import hashlib
import json
from typing import Optional
import httpx
from openai import AsyncOpenAI
from core.config import settings
from loguru import logger

client = AsyncOpenAI(
    api_key=settings.anthropic_api_key,
    base_url="https://api.aimlapi.com/v1",
)

JSEARCH_BASE = "https://jsearch.p.rapidapi.com"
JSEARCH_HEADERS = {
    "X-RapidAPI-Key": settings.rapidapi_key,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
}


# ---------------------------------------------------------------------------
# Source: JSearch (real data)
# ---------------------------------------------------------------------------

async def fetch_jsearch_jobs(query: str, location: str = "", page: int = 1) -> list[dict]:
    """Fetch real jobs from JSearch API (Indeed + LinkedIn + Glassdoor)."""
    search_query = f"{query} fresher OR entry level OR graduate"
    if location:
        search_query += f" {location}"

    params = {
        "query": search_query,
        "page": str(page),
        "num_pages": "1",
        "date_posted": "month",
        "employment_types": "FULLTIME,INTERN,PARTTIME",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            res = await http.get(f"{JSEARCH_BASE}/search", headers=JSEARCH_HEADERS, params=params)
            res.raise_for_status()
            data = res.json()
            jobs = data.get("data", [])
            logger.info(f"JSearch returned {len(jobs)} jobs for '{query}'")
            return [normalize_jsearch_job(j) for j in jobs]
    except Exception as e:
        logger.error(f"JSearch API error: {e}")
        return []


def normalize_jsearch_job(raw: dict) -> dict:
    """Normalize a JSearch job into our unified schema."""
    salary = raw.get("job_salary_period") or ""
    return {
        "source": raw.get("job_publisher", "indeed").lower().replace(" ", "_"),
        "source_job_id": raw.get("job_id", ""),
        "source_url": raw.get("job_apply_link", raw.get("job_google_link", "")),
        "title": raw.get("job_title", ""),
        "company": raw.get("employer_name", ""),
        "company_logo": raw.get("employer_logo", ""),
        "location": f"{raw.get('job_city', '')} {raw.get('job_country', '')}".strip(),
        "job_type": _map_employment_type(raw.get("job_employment_type", "")),
        "salary_min": raw.get("job_min_salary"),
        "salary_max": raw.get("job_max_salary"),
        "salary_currency": raw.get("job_salary_currency", "USD"),
        "description": raw.get("job_description", ""),
        "requirements": raw.get("job_highlights", {}).get("Qualifications", []),
        "skills_required": raw.get("job_required_skills") or [],
        "experience_required": raw.get("job_required_experience", {}).get("required_experience_in_months"),
        "posted_at": raw.get("job_posted_at_datetime_utc"),
    }


def _map_employment_type(raw_type: str) -> str:
    mapping = {
        "FULLTIME": "full_time",
        "PARTTIME": "part_time",
        "INTERN": "internship",
        "CONTRACTOR": "contract",
    }
    return mapping.get(raw_type.upper(), "full_time")


# ---------------------------------------------------------------------------
# Source: Mock data for Naukri + Internshala
# ---------------------------------------------------------------------------

from agents.mock_jobs import MOCK_JOBS as ALL_MOCK_JOBS
MOCK_NAUKRI_JOBS = [
    {
        "source": "naukri",
        "source_job_id": "naukri_001",
        "source_url": "https://www.naukri.com/job-listings-software-engineer",
        "title": "Software Engineer - Fresher",
        "company": "Infosys",
        "company_logo": "",
        "location": "Bangalore, India",
        "job_type": "full_time",
        "salary_min": 350000,
        "salary_max": 600000,
        "salary_currency": "INR",
        "description": "We are looking for fresh graduates passionate about software development...",
        "requirements": ["B.Tech/BE in CS or related", "Knowledge of Java/Python", "Good problem-solving skills"],
        "skills_required": ["Java", "Python", "SQL", "Data Structures"],
        "experience_required": "0",
        "posted_at": None,
    },
    {
        "source": "naukri",
        "source_job_id": "naukri_002",
        "source_url": "https://www.naukri.com/job-listings-analyst",
        "title": "Graduate Engineer Trainee",
        "company": "Wipro",
        "company_logo": "",
        "location": "Hyderabad, India",
        "job_type": "full_time",
        "salary_min": 330000,
        "salary_max": 550000,
        "salary_currency": "INR",
        "description": "Wipro is hiring Graduate Engineer Trainees for our technology division...",
        "requirements": ["B.Tech/BE in any discipline", "60% aggregate", "No active backlogs"],
        "skills_required": ["C", "C++", "DBMS", "OS Concepts"],
        "experience_required": "0",
        "posted_at": None,
    },
    {
        "source": "naukri",
        "source_job_id": "naukri_003",
        "source_url": "https://www.naukri.com/job-listings-data",
        "title": "Junior Data Analyst",
        "company": "TCS",
        "company_logo": "",
        "location": "Mumbai, India",
        "job_type": "full_time",
        "salary_min": 360000,
        "salary_max": 650000,
        "salary_currency": "INR",
        "description": "TCS is looking for data analysts with passion for numbers and insights...",
        "requirements": ["Degree in Statistics/Math/CS", "SQL knowledge", "Excel proficiency"],
        "skills_required": ["SQL", "Excel", "Python", "Tableau"],
        "experience_required": "0",
        "posted_at": None,
    },
]

MOCK_INTERNSHALA_JOBS = [
    {
        "source": "internshala",
        "source_job_id": "intern_001",
        "source_url": "https://internshala.com/internship/software-development",
        "title": "Software Development Intern",
        "company": "Razorpay",
        "company_logo": "",
        "location": "Bangalore, India",
        "job_type": "internship",
        "salary_min": 25000,
        "salary_max": 40000,
        "salary_currency": "INR",
        "description": "6-month internship with Razorpay's core payments team...",
        "requirements": ["Currently pursuing or recently completed B.Tech", "Strong DSA fundamentals"],
        "skills_required": ["JavaScript", "React", "Node.js", "REST APIs"],
        "experience_required": "0",
        "posted_at": None,
    },
    {
        "source": "internshala",
        "source_job_id": "intern_002",
        "source_url": "https://internshala.com/internship/product-management",
        "title": "Product Management Intern",
        "company": "Meesho",
        "company_logo": "",
        "location": "Bangalore, India",
        "job_type": "internship",
        "salary_min": 20000,
        "salary_max": 35000,
        "salary_currency": "INR",
        "description": "Work directly with PMs on Meesho's seller platform...",
        "requirements": ["Strong analytical skills", "Excellent communication", "Interest in e-commerce"],
        "skills_required": ["Product Thinking", "SQL", "Excel", "Figma"],
        "experience_required": "0",
        "posted_at": None,
    },
]


# ---------------------------------------------------------------------------
# Match scoring
# ---------------------------------------------------------------------------

MATCH_SCORE_SYSTEM_PROMPT = """You are a recruiter scoring job-candidate fit. Given a job description and a candidate profile, output ONLY a JSON object:
{
  "score": <0-100 integer>,
  "reasons": ["reason 1", "reason 2", "reason 3"]
}

Scoring criteria:
- Skills overlap (40%): How many required skills does the candidate have?
- Experience relevance (30%): Does their experience align with the role?
- Education fit (15%): Does their degree match requirements?
- Location/type match (15%): Does their preference match?

Be honest. A score of 60+ means a reasonable chance. Output ONLY the JSON, no preamble."""


async def compute_match_score(job: dict, user_profile: dict) -> tuple[float, list[str]]:
    """Use the LLM to compute a match score between a job and user profile."""
    try:
        prompt = f"""Job Title: {job['title']} at {job['company']}
Location: {job.get('location', 'N/A')}
Required Skills: {', '.join(job.get('skills_required', []))}
Requirements: {chr(10).join(job.get('requirements', [])[:5])}
Description excerpt: {job.get('description', '')[:500]}

Candidate Skills: {', '.join(user_profile.get('skills', []))}
Experience: {len(user_profile.get('experience', []))} roles - {', '.join([e.get('title','') for e in user_profile.get('experience', [])[:2]])}
Education: {', '.join([f"{e.get('degree','')} {e.get('field','')}" for e in user_profile.get('education', [])[:1]])}"""

        response = await client.chat.completions.create(
            model="claude-haiku-4-5",
            max_tokens=256,
            messages=[
                {"role": "system", "content": MATCH_SCORE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return float(result.get("score", 50)), result.get("reasons", [])
    except Exception as e:
        logger.error(f"Match score error: {e}")
        return 50.0, ["Could not compute match score"]


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def compute_content_hash(job: dict) -> str:
    """Hash title + company + location for deduplication."""
    key = f"{job['title'].lower().strip()}|{job['company'].lower().strip()}|{job.get('location','').lower().strip()}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Fetch + dedupe (no scoring) — used for caching match scores
# ---------------------------------------------------------------------------

async def fetch_and_dedupe_jobs(
    user_profile: dict,
    preferences: dict,
    page: int = 1,
) -> list[dict]:
    """Fetch jobs from all sources and deduplicate, without scoring."""
    from agents.mock_jobs import MOCK_JOBS as ALL_MOCK_JOBS

    domain = preferences.get("domain", "software engineering")
    locations = preferences.get("locations", [])
    job_types = preferences.get("job_types", ["full_time"])
    location_str = locations[0] if locations else ""

    jsearch_results = await fetch_jsearch_jobs(domain.replace("_", " "), location_str, page)

    mock_jobs = []
    for job in ALL_MOCK_JOBS:
        if not job_types or job.get("job_type") in job_types or "full_time" in job_types:
            mock_jobs.append(job)

    mock_jobs.extend(MOCK_NAUKRI_JOBS)
    if "internship" in job_types:
        mock_jobs.extend(MOCK_INTERNSHALA_JOBS)

    all_jobs = jsearch_results + mock_jobs

    seen_hashes = set()
    unique_jobs = []
    for job in all_jobs:
        h = compute_content_hash(job)
        if h not in seen_hashes:
            seen_hashes.add(h)
            job["content_hash"] = h
            unique_jobs.append(job)

    logger.info(f"After dedup: {len(unique_jobs)} unique jobs from {len(all_jobs)} total")
    return unique_jobs[:20]


# ---------------------------------------------------------------------------
# Main fetch pipeline (fetch + dedupe + score, all at once)
# ---------------------------------------------------------------------------

async def fetch_jobs_for_user(
    user_profile: dict,
    preferences: dict,
    page: int = 1,
) -> list[dict]:
    """
    Main entry point for the Job Scraper Agent.
    Fetches, deduplicates, scores, and returns jobs.
    """
    unique_jobs = await fetch_and_dedupe_jobs(user_profile, preferences, page)

    scored_jobs = []
    for job in unique_jobs:
        score, reasons = await compute_match_score(job, user_profile)
        job["match_score"] = score
        job["match_reasons"] = reasons
        scored_jobs.append(job)

    scored_jobs.sort(key=lambda j: j.get("match_score", 0), reverse=True)
    return scored_jobs