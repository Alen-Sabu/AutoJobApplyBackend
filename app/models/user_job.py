"""
UserJob – jobs that a user has saved or applied to.
"""
import enum

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserJobStatus(str, enum.Enum):
    """Status of a user's relationship to a job."""

    SAVED = "saved"
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    INTERVIEW = "interview"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class UserJob(Base):
    """User–job association: jobs the user has saved or applied to."""

    __tablename__ = "user_jobs"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_user_job"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(Enum(UserJobStatus), default=UserJobStatus.SAVED, nullable=False)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    resume_path = Column(String, nullable=True)
    cover_letter_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="user_jobs")
    job = relationship("Job", back_populates="user_jobs")
