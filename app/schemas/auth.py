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


class UserInfo(BaseModel):
    """Minimal user info returned with token (for redirect by role)."""
    id: int
    email: str
    full_name: str | None
    role: str  # 'user' | 'company'; admin is is_superuser
    is_superuser: bool


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str
    user: UserInfo | None = None

