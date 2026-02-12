"""
Profile schemas.
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class ProfileBase(BaseModel):
    """Base profile schema."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    resume_path: Optional[str] = None
    cover_letter_path: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    bio: Optional[str] = None
    headline: Optional[str] = None
    primary_location: Optional[str] = None
    years_experience: Optional[str] = None
    compensation_currency: Optional[str] = None
    top_skills: Optional[str] = None
    cover_letter_tone: Optional[str] = None
    matching_preferences: Optional[List[str]] = None


class ProfileCreate(ProfileBase):
    """Profile creation schema."""
    pass


class ProfileUpdate(ProfileBase):
    """Profile update schema. full_name is written as first_name + last_name."""
    full_name: Optional[str] = None


class ProfileResponse(ProfileBase):
    """Profile response schema."""
    id: int
    user_id: int
    full_name: Optional[str] = None
    initials: Optional[str] = None

    class Config:
        from_attributes = True

