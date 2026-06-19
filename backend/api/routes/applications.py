from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import Optional
from core.database import get_db
from models.application import Application, ApplicationStatus
from models.job import Job
from models.outreach import Outreach
from agents.tracker_agent import generate_tracker_excel
from api.routes.auth import get_current_user
from models.user import User
import uuid

router = APIRouter(prefix="/applications", tags=["applications"])


class UpdateStatusRequest(BaseModel):
    status: ApplicationStatus
    notes: Optional[str] = None


@router.get("")
async def get_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Application).where(Application.user_id == current_user.id).order_by(Application.created_at.desc())
    apps = (await db.execute(stmt)).scalars().all()

    result = []
    for app in apps:
        job = await db.get(Job, app.job_id)
        outreaches = (await db.execute(
            select(Outreach).where(Outreach.application_id == app.id)
        )).scalars().all()

        result.append({
            "id": str(app.id),
            "status": app.status.value,
            "applied_at": app.applied_at.isoformat() if app.applied_at else None,
            "notes": app.notes,
            "resume_diff": app.resume_diff,
            "job": {
                "id": str(job.id) if job else None,
                "title": job.title if job else "Unknown",
                "company": job.company if job else "Unknown",
                "location": job.location if job else "",
                "job_type": job.job_type if job else "",
                "source": job.source if job else "",
                "source_url": job.source_url if job else "",
                "salary_min": job.salary_min if job else None,
                "salary_max": job.salary_max if job else None,
                "salary_currency": job.salary_currency if job else "",
                "match_score": job.match_score if job else None,
            } if job else {},
            "outreach": [
                {
                    "id": str(o.id),
                    "contact_email": o.contact_email,
                    "contact_name": o.contact_name,
                    "contact_role": o.contact_role,
                    "subject": o.subject,
                    "status": o.status.value,
                    "sent_at": o.sent_at.isoformat() if o.sent_at else None,
                    "followup_sent": o.followup_sent,
                }
                for o in outreaches
            ],
        })

    return {"applications": result, "total": len(result)}


@router.patch("/{application_id}/status")
async def update_status(
    application_id: str,
    data: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    app = await db.get(Application, uuid.UUID(application_id))
    if not app or app.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    app.status = data.status
    if data.notes is not None:
        app.notes = data.notes

    return {"message": "Status updated", "status": app.status.value}


@router.get("/export/excel")
async def export_excel(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export all applications as a formatted Excel file."""
    stmt = select(Application).where(Application.user_id == current_user.id).order_by(Application.created_at.desc())
    apps = (await db.execute(stmt)).scalars().all()

    app_data = []
    for app in apps:
        job = await db.get(Job, app.job_id)
        outreaches = (await db.execute(
            select(Outreach).where(Outreach.application_id == app.id)
        )).scalars().all()

        app_data.append({
            "job_title": job.title if job else "Unknown",
            "company": job.company if job else "Unknown",
            "location": job.location if job else "",
            "job_type": job.job_type if job else "",
            "source": job.source if job else "",
            "source_url": job.source_url if job else "",
            "salary_min": job.salary_min if job else None,
            "salary_max": job.salary_max if job else None,
            "salary_currency": job.salary_currency if job else "USD",
            "match_score": job.match_score if job else None,
            "status": app.status.value,
            "applied_at": app.applied_at.isoformat() if app.applied_at else None,
            "notes": app.notes or "",
            "outreach_sent": [{"status": o.status.value} for o in outreaches],
        })

    excel_bytes = generate_tracker_excel(app_data)

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=firstjob_applications.xlsx"}
    )


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get application statistics for the dashboard."""
    stmt = select(Application).where(Application.user_id == current_user.id)
    apps = (await db.execute(stmt)).scalars().all()

    status_counts = {}
    for app in apps:
        s = app.status.value
        status_counts[s] = status_counts.get(s, 0) + 1

    total = len(apps)
    responses = sum(status_counts.get(s, 0) for s in ["shortlisted", "interview", "offer"])
    response_rate = round(responses / total * 100, 1) if total > 0 else 0

    return {
        "total": total,
        "by_status": status_counts,
        "response_rate": response_rate,
        "offers": status_counts.get("offer", 0),
        "interviews": status_counts.get("interview", 0),
        "rejected": status_counts.get("rejected", 0),
    }
