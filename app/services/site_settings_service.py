"""
Site-wide settings (single row, id=1) for admin.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.site_settings import SiteSettings
from app.schemas.admin import AdminSiteSettingsOut, AdminSiteSettingsUpdate


SINGLETON_ID = 1


class SiteSettingsService:
    """Get or update the single site_settings row."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self) -> SiteSettings:
        """Return the singleton row; create with defaults if missing."""
        row = self.db.query(SiteSettings).filter(SiteSettings.id == SINGLETON_ID).first()
        if row is None:
            row = SiteSettings(
                id=SINGLETON_ID,
                maintenance_mode=False,
                new_user_registration=True,
                require_email_verification=False,
                max_automations_per_user=10,
                site_name="CrypGo",
                support_email="support@crypgo.com",
            )
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
        return row

    def get_settings(self) -> AdminSiteSettingsOut:
        """Return current site settings as API output."""
        row = self.get_or_create()
        return AdminSiteSettingsOut(
            maintenance_mode=row.maintenance_mode,
            new_user_registration=row.new_user_registration,
            require_email_verification=row.require_email_verification,
            max_automations_per_user=row.max_automations_per_user,
            site_name=row.site_name or "CrypGo",
            support_email=row.support_email or "support@crypgo.com",
        )

    def update_settings(self, update: AdminSiteSettingsUpdate) -> AdminSiteSettingsOut:
        """Update site settings and return new state."""
        row = self.get_or_create()
        data = update.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(row, key, value)
        self.db.commit()
        self.db.refresh(row)
        return self.get_settings()
