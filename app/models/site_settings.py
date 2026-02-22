"""
Site-wide settings (single row) editable by admin.
"""
from sqlalchemy import Column, Integer, Boolean, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class SiteSettings(Base):
    """Singleton-style site settings (use id=1)."""

    __tablename__ = "site_settings"

    id = Column(Integer, primary_key=True, index=True)
    maintenance_mode = Column(Boolean, default=False, nullable=False)
    new_user_registration = Column(Boolean, default=True, nullable=False)
    require_email_verification = Column(Boolean, default=False, nullable=False)
    max_automations_per_user = Column(Integer, default=10, nullable=False)
    site_name = Column(String, default="CrypGo", nullable=False)
    support_email = Column(String, default="support@crypgo.com", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

