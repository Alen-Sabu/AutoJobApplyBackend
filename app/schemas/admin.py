"""
Admin-facing schemas (users, jobs, automations, stats, etc.).
"""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class AdminAutomationOut(BaseModel):
    """Automation row for admin panel with user details."""

    id: int
    user_id: int
    user_email: str
    user_name: str
    name: str
    target_titles: Optional[str] = None
    locations: Optional[str] = None
    daily_limit: int
    platforms: List[str]
    cover_letter_template: Optional[str] = None
    status: Literal["running", "paused"]
    total_applied: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None


class AdminAutomationUpdate(BaseModel):
    """Admin can update any automation field."""

    name: Optional[str] = None
    target_titles: Optional[str] = None
    locations: Optional[str] = None
    daily_limit: Optional[int] = None
    platforms: Optional[List[str]] = None
    cover_letter_template: Optional[str] = None
    status: Optional[Literal["running", "paused"]] = None


class AdminUserOut(BaseModel):
    """User as seen in the admin panel."""

    id: int
    name: str
    email: str
    role: Literal["user", "admin"]
    status: Literal["active", "suspended"]
    joined: str


class AdminJobOut(BaseModel):
    """Job row as seen in the admin Jobs table."""

    id: int
    title: str
    company: str
    status: Literal["pending", "approved", "rejected"]
    posted: str
    location: str | None = None
    salary: str | None = None
    jobType: str | None = None
    description: str | None = None
    jobUrl: str | None = None
    source: str | None = None


class AdminSiteSettingsOut(BaseModel):
    """Site-wide settings for admin panel (API response)."""

    maintenance_mode: bool = False
    new_user_registration: bool = True
    require_email_verification: bool = False
    max_automations_per_user: int = 10
    site_name: str = "CrypGo"
    support_email: str = "support@crypgo.com"


class AdminSiteSettingsUpdate(BaseModel):
    """Update payload for site settings."""

    maintenance_mode: Optional[bool] = None
    new_user_registration: Optional[bool] = None
    require_email_verification: Optional[bool] = None
    max_automations_per_user: Optional[int] = None
    site_name: Optional[str] = None
    support_email: Optional[str] = None


# —— Admin dashboard ——

class AdminStatCard(BaseModel):
    """Stat card for admin dashboard."""

    label: str
    value: str
    change: str
    key: str


class AdminActivityItem(BaseModel):
    """Recent activity item for admin dashboard."""

    id: str
    time: str
    action: str
    detail: str
    type: str


class AdminAlert(BaseModel):
    """Alert for admin dashboard (e.g. pending jobs, suspended users)."""

    id: str
    message: str
    severity: str
    href: str


class AdminAuditEntry(BaseModel):
    """Audit log entry for admin UI."""

    id: int
    time: str
    actor: str
    action: str
    target: str
    ip: str


