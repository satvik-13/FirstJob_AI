from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from core.database import get_db
from models.user import UserProfile
from models.job import Job
from models.application import Application, ApplicationStatus
from agents.job_scraper_agent import fetch_and_dedupe_jobs, compute_match_score
from api.routes.auth import get_current_user
from models.user import User
import uuid

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
async def get_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=50),
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    remote_only: bool = False,
    sort_by: str = "match_score",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Load user profile
    stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    profile = (await db.execute(stmt)).scalar_one_or_none()

    if not profile or not profile.parsed_profile:
        raise HTTPException(
            status_code=404,
            detail="Please complete onboarding first — upload your resume at /onboarding"
        )

    # Use preferences or sensible defaults
    preferences = profile.preferences or {
        "domain": "software engineering",
        "locations": [],
        "job_types": ["full_time", "internship"],
        "open_to_remote": True,
    }

    # Apply filter overrides from query params
    if job_type:
        preferences = {**preferences, "job_types": [job_type]}
    if location:
        preferences = {**preferences, "locations": [location]}
    if remote_only:
        preferences = {**preferences, "job_types": ["remote"]}

    # Fetch and deduplicate jobs (no scoring yet)
    unique_jobs = await fetch_and_dedupe_jobs(
        user_profile=profile.parsed_profile,
        preferences=preferences,
        page=page,
    )

    # Check which jobs already have cached scores in DB
    hashes = [j["content_hash"] for j in unique_jobs]
    existing_jobs = []
    if hashes:
        existing_jobs_stmt = select(Job).where(Job.content_hash.in_(hashes))
        existing_jobs = (await db.execute(existing_jobs_stmt)).scalars().all()
    existing_by_hash = {j.content_hash: j for j in existing_jobs}

    # Score only new jobs; reuse cached scores for existing ones
    jobs = []
    for job_data in unique_jobs:
        existing = existing_by_hash.get(job_data["content_hash"])
        if existing and existing.match_score is not None:
            job_data["match_score"] = existing.match_score
            job_data["match_reasons"] = existing.match_reasons
        else:
            score, reasons = await compute_match_score(job_data, profile.parsed_profile)
            job_data["match_score"] = score
            job_data["match_reasons"] = reasons
        jobs.append(job_data)

    jobs.sort(key=lambda j: j.get("match_score", 0), reverse=True)

    # Save new jobs to DB (upsert by content_hash)
    saved_jobs = []
    for job_data in jobs:
        existing = existing_by_hash.get(job_data.get("content_hash"))

        if not existing:
            job = Job(**{k: v for k, v in job_data.items() if hasattr(Job, k) and k != 'id'})
            db.add(job)
            await db.flush()
            saved_jobs.append((job, job_data))
        else:
            existing.match_score = job_data.get("match_score")
            existing.match_reasons = job_data.get("match_reasons")
            saved_jobs.append((existing, job_data))

    # Filter out already-applied or swiped jobs
    applied_ids = set()
    if saved_jobs:
        job_ids = [j.id for j, _ in saved_jobs]
        apps = await db.execute(
            select(Application.job_id).where(
                and_(Application.user_id == current_user.id, Application.job_id.in_(job_ids))
            )
        )
        applied_ids = {row[0] for row in apps.fetchall()}

    result = []
    for job, raw in saved_jobs:
        if job.id not in applied_ids:
            result.append({
                "id": str(job.id),
                "title": job.title,
                "company": job.company,
                "company_logo": job.company_logo,
                "location": job.location,
                "job_type": job.job_type,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "salary_currency": job.salary_currency,
                "description": job.description,
                "requirements": job.requirements,
                "skills_required": job.skills_required,
                "source": job.source,
                "source_url": job.source_url,
                "posted_at": job.posted_at.isoformat() if job.posted_at else None,
                "match_score": job.match_score,
                "match_reasons": job.match_reasons,
            })

    return {"jobs": result, "total": len(result), "page": page}


@router.get("/{job_id}")
async def get_job_detail(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = await db.get(Job, uuid.UUID(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": str(job.id),
        "title": job.title,
        "company": job.company,
        "company_logo": job.company_logo,
        "location": job.location,
        "job_type": job.job_type,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "description": job.description,
        "requirements": job.requirements,
        "skills_required": job.skills_required,
        "source": job.source,
        "source_url": job.source_url,
        "match_score": job.match_score,
        "match_reasons": job.match_reasons,
    }


@router.post("/{job_id}/save")
async def save_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = await db.get(Job, uuid.UUID(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    application = Application(
        user_id=current_user.id,
        job_id=job.id,
        status=ApplicationStatus.saved,
    )
    db.add(application)
    return {"message": "Job saved", "application_id": str(application.id)}


@router.post("/{job_id}/apply")
async def apply_to_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import datetime

    job = await db.get(Job, uuid.UUID(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check for existing application
    existing = (await db.execute(
        select(Application).where(
            and_(Application.user_id == current_user.id, Application.job_id == job.id)
        )
    )).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    # Get user profile
    profile_stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    profile = (await db.execute(profile_stmt)).scalar_one_or_none()
    if not profile or not profile.parsed_profile:
        raise HTTPException(status_code=400, detail="Please upload your resume first")

    # Trigger Resume Tailor Agent
    try:
        from agents.resume_tailor_agent import tailor_resume_for_job
        tailoring_result = await tailor_resume_for_job(
            base_profile=profile.parsed_profile,
            job={
                "title": job.title,
                "company": job.company,
                "description": job.description or "",
                "requirements": job.requirements or [],
                "skills_required": job.skills_required or [],
            }
        )
    except Exception as e:
        # Don't fail the application if tailoring fails — apply with original
        tailoring_result = {
            "tailored_profile": profile.parsed_profile,
            "diff": [],
            "summary": "Applied with original resume — tailoring unavailable.",
        }

    # Create application
    application = Application(
        user_id=current_user.id,
        job_id=job.id,
        status=ApplicationStatus.applied,
        tailored_resume=tailoring_result["tailored_profile"],
        resume_diff=tailoring_result["diff"],
        applied_at=datetime.utcnow(),
    )
    db.add(application)
    await db.flush()

    # Trigger Outreach Agent in background (non-blocking)
    try:
        from agents.outreach_agent import find_and_queue_outreach
        import asyncio
        asyncio.create_task(find_and_queue_outreach(
            application_id=str(application.id),
            user_id=str(current_user.id),
            company_name=job.company,
            job_title=job.title,
            user_profile=profile.parsed_profile,
        ))
    except Exception:
        pass  # Outreach failure never blocks the application

    return {
        "message": "Applied successfully",
        "application_id": str(application.id),
        "tailored_resume": tailoring_result["tailored_profile"],
        "diff": tailoring_result["diff"],
        "summary": tailoring_result["summary"],
    }