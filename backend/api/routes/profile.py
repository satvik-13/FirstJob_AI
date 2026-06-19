from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from core.database import get_db
from models.user import User, UserProfile
from agents.profile_agent import process_resume_upload
from api.routes.auth import get_current_user
import tempfile, os, uuid, shutil

router = APIRouter(prefix="/profile", tags=["profile"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE_MB = 5


class PreferencesRequest(BaseModel):
    domain: str
    sub_domains: Optional[List[str]] = []
    locations: Optional[List[str]] = []
    job_types: Optional[List[str]] = ["full_time"]
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    open_to_remote: Optional[bool] = True
    experience_level: Optional[str] = "fresher"


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate file type
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB")

    # Save to temp file for processing
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await process_resume_upload(tmp_path, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    finally:
        os.unlink(tmp_path)

    # Upsert profile
    stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    existing = (await db.execute(stmt)).scalar_one_or_none()

    if existing:
        existing.resume_original_filename = result["original_filename"]
        existing.resume_raw_text = result["raw_text"]
        existing.parsed_profile = result["parsed_profile"]
        profile = existing
    else:
        profile = UserProfile(
            user_id=current_user.id,
            resume_original_filename=result["original_filename"],
            resume_raw_text=result["raw_text"],
            parsed_profile=result["parsed_profile"],
        )
        db.add(profile)

    await db.flush()

    return {
        "message": "Resume parsed successfully",
        "profile_id": str(profile.id),
        "parsed": result["parsed_profile"],
    }


@router.get("/me")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    profile = (await db.execute(stmt)).scalar_one_or_none()

    if not profile:
        return {"profile": None, "message": "No resume uploaded yet"}

    return {
        "profile_id": str(profile.id),
        "parsed_profile": profile.parsed_profile,
        "preferences": profile.preferences,
        "resume_filename": profile.resume_original_filename,
    }


@router.put("/preferences")
async def update_preferences(
    data: PreferencesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(UserProfile).where(UserProfile.user_id == current_user.id)
    profile = (await db.execute(stmt)).scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Please upload your resume first")

    profile.preferences = data.model_dump()
    await db.flush()

    return {"message": "Preferences saved", "preferences": profile.preferences}
