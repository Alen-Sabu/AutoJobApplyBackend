"""
Profile service.
"""
import json
from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    """Service for profile operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> Profile | None:
        """Get profile by user ID."""
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def get_or_create_profile(self, user_id: int, user_full_name: str | None) -> Profile:
        """Get existing profile or create one with defaults."""
        profile = self.get_profile_by_user_id(user_id)
        if profile:
            return profile
        parts = (user_full_name or "").strip().split(maxsplit=1)
        first_name = parts[0] if parts else None
        last_name = parts[1] if len(parts) > 1 else None
        db_profile = Profile(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
        )
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def _prepare_profile_data(self, data: dict) -> dict:
        """Convert matching_preferences to JSON string; full_name to first_name/last_name."""
        out = dict(data)
        if "full_name" in out:
            full = (out.pop("full_name") or "").strip()
            parts = full.split(maxsplit=1)
            out["first_name"] = parts[0] if parts else None
            out["last_name"] = parts[1] if len(parts) > 1 else None
        if "matching_preferences" in out and out["matching_preferences"] is not None:
            out["matching_preferences"] = json.dumps(out["matching_preferences"])
        return out

    def create_profile(self, profile_create: ProfileCreate, user_id: int) -> Profile:
        """Create a new profile."""
        raw = profile_create.model_dump(exclude_unset=True)
        db_profile = Profile(user_id=user_id, **self._prepare_profile_data(raw))
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def update_profile(self, user_id: int, profile_update: ProfileUpdate) -> Profile | None:
        """Update a profile."""
        db_profile = self.get_profile_by_user_id(user_id)
        if not db_profile:
            return None
        update_data = self._prepare_profile_data(profile_update.model_dump(exclude_unset=True))
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

