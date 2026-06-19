from sqlalchemy import Column, String, DateTime, JSON, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base
import uuid


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Source info
    source = Column(String(50), nullable=False)          # "indeed", "linkedin", "naukri", etc.
    source_job_id = Column(String(255), nullable=True)   # ID from the source platform
    source_url = Column(Text, nullable=True)             # Direct link to apply

    # Job details
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    company_logo = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    job_type = Column(String(50), nullable=True)         # full_time, internship, remote, etc.
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)            # Full JD text
    requirements = Column(JSON, nullable=True)           # Extracted requirements list
    skills_required = Column(JSON, nullable=True)        # Extracted skills list
    experience_required = Column(String(100), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    # AI-computed fields
    match_score = Column(Float, nullable=True)           # 0-100, computed per user
    match_reasons = Column(JSON, nullable=True)          # Why it matched

    # Deduplication
    content_hash = Column(String(64), nullable=True, index=True)  # Hash of title+company+location

    created_at = Column(DateTime(timezone=True), server_default=func.now())
