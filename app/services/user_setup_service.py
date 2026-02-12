"""
User setup service: personal details, resume upload, completion.
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session
from app.models.user_setup import UserSetup
from app.models.user import User
from app.core.config import settings


class UserSetupService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR) / "resumes"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def get_or_create(self, user_id: int) -> UserSetup:
        setup = self.db.query(UserSetup).filter(UserSetup.user_id == user_id).first()
        if setup:
            return setup
        setup = UserSetup(user_id=user_id)
        self.db.add(setup)
        self.db.commit()
        self.db.refresh(setup)
        return setup

    def get_by_user_id(self, user_id: int) -> Optional[UserSetup]:
        return self.db.query(UserSetup).filter(UserSetup.user_id == user_id).first()

    def update_personal(
        self, user_id: int, full_name: Optional[str] = None, email: Optional[str] = None,
        phone: Optional[str] = None, location: Optional[str] = None,
        linkedin_url: Optional[str] = None, years_experience: Optional[str] = None,
        top_skills: Optional[str] = None,
    ) -> UserSetup:
        setup = self.get_or_create(user_id)
        if full_name is not None:
            setup.full_name = full_name
        if email is not None:
            setup.email = email
        if phone is not None:
            setup.phone = phone
        if location is not None:
            setup.location = location
        if linkedin_url is not None:
            setup.linkedin_url = linkedin_url
        if years_experience is not None:
            setup.years_experience = years_experience
        if top_skills is not None:
            setup.top_skills = top_skills
        self.db.commit()
        self.db.refresh(setup)
        return setup

    def save_resume(self, user_id: int, content: bytes, original_filename: str) -> tuple[str, str]:
        """Save uploaded file content to disk and update setup. Returns (file_name, file_path)."""
        setup = self.get_or_create(user_id)
        ext = Path(original_filename or "resume").suffix.lower()
        if ext not in (".pdf", ".doc", ".docx"):
            ext = ".pdf"
        unique_name = f"{user_id}_{uuid.uuid4().hex[:12]}{ext}"
        user_dir = self.upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = (user_dir / unique_name).resolve()
        file_path.write_bytes(content)

        if setup.resume_file_path:
            old_path = Path(setup.resume_file_path)
            if old_path.exists():
                try:
                    old_path.unlink()
                except OSError:
                    pass

        rel_path = str(file_path)
        setup.resume_file_name = original_filename or unique_name
        setup.resume_file_path = rel_path
        self.db.commit()
        self.db.refresh(setup)
        return setup.resume_file_name, rel_path

    def complete_setup(self, user_id: int) -> UserSetup:
        setup = self.get_by_user_id(user_id)
        if not setup:
            raise ValueError("Setup not found")
        if not setup.resume_file_path or not setup.resume_file_name:
            raise ValueError("Please upload your resume before completing setup.")
        if not (setup.full_name and setup.full_name.strip()) or not (setup.email and setup.email.strip()):
            raise ValueError("Please fill in required personal details (name and email).")
        setup.setup_complete = True
        self.db.commit()
        self.db.refresh(setup)
        return setup

    def get_resume_path(self, user_id: int) -> Optional[tuple[str, Path]]:
        """Returns (original_file_name, path_on_disk) or None."""
        setup = self.get_by_user_id(user_id)
        if not setup or not setup.resume_file_path:
            return None
        path = Path(setup.resume_file_path)
        if not path.exists():
            return None
        return (setup.resume_file_name or path.name, path)
