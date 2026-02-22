"""
Dashboard API schemas (user dashboard: stats, campaigns, activity).
"""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DashboardStat(BaseModel):
    """Single stat card for the user dashboard."""

    label: str
    value: str
    change: str
    key: str


class DashboardCampaign(BaseModel):
    """Campaign (automation) summary for the dashboard."""

    id: str
    name: str
    targetTitle: str = Field(..., description="Target titles / keywords")
    locations: List[str] = Field(default_factory=list)
    dailyLimit: str = Field(..., description="e.g. '25 / day'")
    platforms: List[str] = Field(default_factory=list)
    status: Literal["Running", "Paused"]
    applicationsToday: Optional[int] = None  # For "limit exceeded" UI
    dailyLimitNumber: Optional[int] = None  # Numeric limit (e.g. 25) for comparison


class DashboardActivityItem(BaseModel):
    """Single recent activity entry."""

    id: str
    time: str
    title: str
    description: str
