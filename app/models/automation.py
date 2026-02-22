"""
Automation model – stores user-defined auto-apply rules.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Automation(Base):
    """Automation rules for continuously applying to jobs for a user."""

    __tablename__ = "automations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Human-friendly name the user sees in the dashboard
    name = Column(String, nullable=False)

    # Search / targeting configuration
    target_titles = Column(Text, nullable=True)  # raw text, e.g. "React, Frontend Engineer"
    locations = Column(Text, nullable=True)  # raw text, e.g. "Remote, EU, UK"
    daily_limit = Column(Integer, nullable=False, default=25)  # max applications per day

    # Job boards / platforms (JSON array of strings, e.g. ["LinkedIn", "Indeed"])
    platforms = Column(JSON, nullable=False, default=list)

    # Optional cover letter template used when applying
    cover_letter_template = Column(Text, nullable=True)

    # Status: "running" or "paused" (string for simplicity)
    status = Column(String, nullable=False, default="paused", index=True)

    # Simple counter of how many applications this automation has driven
    total_applied = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="automations")
    user_jobs = relationship("UserJob", back_populates="automation")

