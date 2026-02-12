"""
Job schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class JobBase(BaseModel):
    """Base job schema."""

    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    job_url: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None  # pending | approved | rejected


class JobCreate(JobBase):
    """Job creation schema."""

    external_id: Optional[str] = None


class JobResponse(JobBase):
    """Job response schema."""

    id: int
    external_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobSearchParams(BaseModel):
    """Job search parameters schema."""

    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    source: Optional[str] = None
