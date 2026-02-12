"""
User settings schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SettingsDataOut(BaseModel):
    """Settings data returned to frontend (camelCase for frontend compatibility)."""
    display_name: str
    username: Optional[str] = None
    email: str
    email_verified: bool = False
    password_last_changed: Optional[str] = None  # human-readable or ISO date
    two_factor_enabled: bool = False

    class Config:
        from_attributes = False


class UpdateAccountRequest(BaseModel):
    """Update display name and/or username."""
    display_name: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")


class UpdateEmailRequest(BaseModel):
    """Update email address."""
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    """Change password."""
    current_password: str = Field(..., min_length=1, max_length=72)
    new_password: str = Field(..., min_length=8, max_length=72)


class DeleteAccountRequest(BaseModel):
    """Delete account confirmation."""
    confirmation: str = Field(..., min_length=1)
