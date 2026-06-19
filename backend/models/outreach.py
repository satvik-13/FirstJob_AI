from sqlalchemy import Column, String, DateTime, Text, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base
import uuid
import enum


class OutreachStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    opened = "opened"
    replied = "replied"
    bounced = "bounced"
    failed = "failed"


class Outreach(Base):
    __tablename__ = "outreaches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    application_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Contact details
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=False)
    contact_role = Column(String(255), nullable=True)    # "HR Manager", "Engineering Lead" etc.
    contact_source = Column(String(50), nullable=True)   # "hunter", "pattern_guess", "linkedin"

    # Email content
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)

    # Status tracking
    status = Column(SAEnum(OutreachStatus), default=OutreachStatus.pending)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    replied_at = Column(DateTime(timezone=True), nullable=True)

    # Follow-up
    followup_scheduled_at = Column(DateTime(timezone=True), nullable=True)
    followup_sent = Column(Boolean, default=False)
    followup_body = Column(Text, nullable=True)

    # Gmail message ID for tracking
    gmail_message_id = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
