from sqlalchemy import Column, String, DateTime, JSON, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base
import uuid
import enum


class ApplicationStatus(str, enum.Enum):
    saved = "saved"               # Swiped right but not yet applied
    applied = "applied"           # Application submitted
    shortlisted = "shortlisted"   # Got a callback
    interview = "interview"       # Interview scheduled
    offer = "offer"               # Received offer
    rejected = "rejected"         # Rejected
    ghosted = "ghosted"           # No response after 2+ weeks
    withdrawn = "withdrawn"       # User withdrew


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    status = Column(SAEnum(ApplicationStatus), default=ApplicationStatus.applied, nullable=False)

    # Tailored resume for this specific application
    tailored_resume = Column(JSON, nullable=True)
    # Shape: same as parsed_profile but with AI-modified bullets/ordering
    tailored_resume_pdf_path = Column(Text, nullable=True)  # Path to generated PDF

    # Diff: what the AI changed
    resume_diff = Column(JSON, nullable=True)
    # Shape: [{ "section": str, "original": str, "modified": str, "reason": str }]

    # Cover letter (optional)
    cover_letter = Column(Text, nullable=True)

    # Application metadata
    applied_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Outreach tracking
    outreach_sent = Column(JSON, nullable=True)
    # Shape: [{ "email": str, "name": str, "role": str, "sent_at": str, "opened": bool, "replied": bool }]

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
