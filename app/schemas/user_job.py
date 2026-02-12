"""
UserJob schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.user_job import UserJobStatus


class UserJobBase(BaseModel):
    """Base user_job schema."""

    job_id: int
    status: Optional[UserJobStatus] = UserJobStatus.SAVED
    notes: Optional[str] = None
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None


class UserJobCreate(UserJobBase):
    """Create a user_job (save a job or start an application)."""

    pass


class UserJobUpdate(BaseModel):
    """Update user_job fields."""

    status: Optional[UserJobStatus] = None
    notes: Optional[str] = None
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None


class UserJobResponse(UserJobBase):
    """UserJob response schema."""

    id: int
    user_id: int
    applied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserJobResponseWithJob(UserJobResponse):
    """UserJob response with nested job details."""

    job: "JobResponse"

    class Config:
        from_attributes = True


from app.schemas.job import JobResponse  # noqa: E402

UserJobResponseWithJob.model_rebuild()
