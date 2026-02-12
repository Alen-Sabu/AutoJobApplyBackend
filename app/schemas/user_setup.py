"""
Setup (onboarding) schemas.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class SetupPersonalDetails(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    years_experience: Optional[str] = None
    top_skills: Optional[str] = None

    class Config:
        extra = "ignore"  # allow camelCase from frontend if we add aliases


class SetupResumeOut(BaseModel):
    fileName: str
    uploadedAt: str
    url: Optional[str] = None  # download URL path for frontend


class SetupDataOut(BaseModel):
    personal: SetupPersonalDetails
    resume: Optional[SetupResumeOut] = None


class SetupStatusResponse(BaseModel):
    complete: bool
    data: Optional[SetupDataOut] = None


class SetupCompleteResponse(BaseModel):
    complete: bool
    message: str = "Setup complete."
