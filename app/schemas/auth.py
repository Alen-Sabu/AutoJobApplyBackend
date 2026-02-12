"""
Authentication schemas.
"""
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)
    full_name: str | None = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    full_name: str | None
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str

