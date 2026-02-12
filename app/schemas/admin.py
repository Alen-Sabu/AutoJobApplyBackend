"""
Admin-facing schemas (users, jobs, stats, etc.).
"""
from typing import Literal

from pydantic import BaseModel


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

