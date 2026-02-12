"""
User settings service: account, email, password, 2FA, delete account.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.settings import SettingsDataOut, UpdateAccountRequest, UpdateEmailRequest, ChangePasswordRequest
from app.services.auth_service import AuthService


def _format_password_changed(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    now = datetime.now(timezone.utc)
    dt_utc = dt.replace(tzinfo=timezone.utc) if dt.tzinfo else dt
    delta = now - dt_utc
    days = delta.days
    if days < 1:
        return "Today"
    if days == 1:
        return "1 day ago"
    if days < 30:
        return f"{days} days ago"
    if days < 60:
        return "1 month ago"
    if days < 365:
        return f"{days // 30} months ago"
    return f"{days // 365} year(s) ago"


class SettingsService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(db)

    def get_settings(self, user: User) -> SettingsDataOut:
        """Build settings payload for the current user."""
        return SettingsDataOut(
            display_name=user.full_name or "",
            username=user.username or "",
            email=user.email,
            email_verified=bool(user.email_verified),
            password_last_changed=_format_password_changed(user.password_changed_at),
            two_factor_enabled=bool(user.two_factor_enabled),
        )

    def update_account(self, user: User, payload: UpdateAccountRequest) -> User:
        """Update display name and/or username."""
        if payload.display_name is not None:
            user.full_name = payload.display_name.strip() or None
        if payload.username is not None:
            username = payload.username.strip().lower() or None
            if username:
                existing = self.db.query(User).filter(User.username == username, User.id != user.id).first()
                if existing:
                    raise ValueError("Username already taken.")
            user.username = username
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_email(self, user: User, new_email: str) -> User:
        """Update user email. Caller should re-issue token or ask user to re-login."""
        new_email = new_email.strip().lower()
        existing = self.db.query(User).filter(User.email == new_email).first()
        if existing and existing.id != user.id:
            raise ValueError("Email already in use.")
        user.email = new_email
        user.email_verified = False  # require re-verification
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        """Change password after verifying current one."""
        if not self.auth_service.verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect.")
        user.hashed_password = self.auth_service.get_password_hash(new_password)
        user.password_changed_at = datetime.now(timezone.utc)
        self.db.commit()

    def enable_2fa(self, user: User) -> None:
        """Stub: mark 2FA as enabled (real implementation would set up TOTP)."""
        user.two_factor_enabled = True
        self.db.commit()
        self.db.refresh(user)

    def delete_account(self, user: User, confirmation: str) -> None:
        """Soft-delete: deactivate the account. Require confirmation string 'DELETE'."""
        if confirmation != "DELETE":
            raise ValueError("Invalid confirmation. Type DELETE to confirm.")
        user.is_active = False
        self.db.commit()
