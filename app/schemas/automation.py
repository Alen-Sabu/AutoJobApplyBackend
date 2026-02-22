"""
Automation schemas (Pydantic) for API I/O.
"""
from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field


AutomationStatusLiteral = Literal["running", "paused"]


class AutomationBase(BaseModel):
    """Shared fields for automation create/update/response."""

    name: str = Field(..., description="Human friendly name for the automation")
    target_titles: Optional[str] = Field(
        None, description="Raw text of desired titles/keywords, e.g. 'React, Frontend Engineer'"
    )
    locations: Optional[str] = Field(
        None, description="Raw text of preferred locations, e.g. 'Remote, EU, UK'"
    )
    daily_limit: int = Field(
        25,
        ge=1,
        le=500,
        description="Maximum number of applications per day driven by this automation",
    )
    platforms: List[str] = Field(
        default_factory=list,
        description="Job boards / platforms to target, e.g. ['LinkedIn', 'Indeed']",
    )
    cover_letter_template: Optional[str] = Field(
        None, description="Optional basic cover letter template text"
    )


class AutomationCreate(AutomationBase):
    """Payload for creating an automation."""

    pass


class AutomationUpdate(BaseModel):
    """Partial update for automation configuration."""

    name: Optional[str] = None
    target_titles: Optional[str] = None
    locations: Optional[str] = None
    daily_limit: Optional[int] = Field(default=None, ge=1, le=500)
    platforms: Optional[List[str]] = None
    cover_letter_template: Optional[str] = None
    status: Optional[AutomationStatusLiteral] = None


class AutomationResponse(AutomationBase):
    """Automation data returned to the frontend."""

    id: int
    status: AutomationStatusLiteral
    total_applied: int = 0
    applications_today: Optional[int] = None  # Set by API when listing/getting
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AutomationRunResultResponse(BaseModel):
    """Response after running an automation (apply to matching jobs)."""

    applied_count: int
    limit_reached: bool
    message: str
    applications_today: int

