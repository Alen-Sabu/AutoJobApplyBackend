"""
Company schemas for API.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    """Create company profile (used at signup)."""

    company_name: str = Field(..., min_length=1)
    description: Optional[str] = None
    website: Optional[str] = None


class CompanyUpdate(BaseModel):
    """Update company profile."""

    company_name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyResponse(BaseModel):
    """Company in API responses."""

    id: int
    user_id: int
    company_name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CompanyRegister(BaseModel):
    """Company signup: user + company in one."""

    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8, max_length=72)
    full_name: Optional[str] = None  # contact name
    company_name: str = Field(..., min_length=1)
    description: Optional[str] = None
    website: Optional[str] = None


class ApplicantSummary(BaseModel):
    """Applicant row for company job applicants list."""

    id: int  # user_job id
    user_id: int
    user_email: str
    user_name: str
    status: str
    applied_at: Optional[datetime] = None
    created_at: datetime
    has_resume: bool = False  # True if applicant has a resume available to view


class ApplicationStatusUpdate(BaseModel):
    """Company updates application status (approve/reject/etc)."""

    status: str = Field(..., description="One of: reviewing, interview, accepted, rejected")


class CompanyStats(BaseModel):
    """Company dashboard stats."""

    total_jobs: int
    total_applicants: int
