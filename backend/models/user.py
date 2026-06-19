from sqlalchemy import Column, String, DateTime, JSON, Text, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base
import uuid
import enum


class JobType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    internship = "internship"
    contract = "contract"
    remote = "remote"
    hybrid = "hybrid"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Gmail OAuth tokens
    gmail_access_token = Column(Text, nullable=True)
    gmail_refresh_token = Column(Text, nullable=True)
    gmail_token_expiry = Column(DateTime(timezone=True), nullable=True)


class UserProfile(Base):
    """
    Structured profile parsed from the user's resume.
    This is the immutable source of truth — agents read from this, never overwrite it.
    """
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Raw resume storage
    resume_original_filename = Column(String(255), nullable=True)
    resume_raw_text = Column(Text, nullable=True)         # Full text extracted from PDF/DOCX

    # Structured parsed data (JSON)
    parsed_profile = Column(JSON, nullable=True)
    # Shape:
    # {
    #   "full_name": str,
    #   "email": str,
    #   "phone": str,
    #   "location": str,
    #   "summary": str,
    #   "skills": ["Python", "React", ...],
    #   "experience": [
    #     {
    #       "company": str, "title": str, "duration": str,
    #       "bullets": [str, ...], "start_date": str, "end_date": str
    #     }
    #   ],
    #   "education": [
    #     { "institution": str, "degree": str, "field": str, "year": str, "gpa": str }
    #   ],
    #   "projects": [
    #     { "name": str, "description": str, "tech_stack": [str], "bullets": [str] }
    #   ],
    #   "certifications": [str],
    #   "languages": [str],
    #   "links": { "linkedin": str, "github": str, "portfolio": str }
    # }

    # Job search preferences
    preferences = Column(JSON, nullable=True)
    # Shape:
    # {
    #   "domain": str,           e.g. "software_engineering"
    #   "sub_domains": [str],    e.g. ["backend", "fullstack"]
    #   "locations": [str],      e.g. ["Bangalore", "Remote"]
    #   "job_types": [str],      e.g. ["full_time", "internship"]
    #   "salary_min": int,
    #   "salary_max": int,
    #   "open_to_remote": bool,
    #   "experience_level": str  e.g. "fresher", "0-2 years"
    # }

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
