"""
Service layer for Automation – user-defined auto-apply rules.
"""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.automation import Automation
from app.models.user import User
from app.models.user_job import UserJob, UserJobStatus
from app.schemas.automation import AutomationCreate, AutomationUpdate


@dataclass
class AutomationRunResult:
    """Result of running an automation (apply to matching jobs up to daily limit)."""

    applied_count: int
    limit_reached: bool
    message: str
    applications_today: int


class AutomationService:
    """CRUD and domain logic for Automation objects."""

    def __init__(self, db: Session):
        self.db = db

    def list_automations_for_user(self, user_id: int) -> List[Automation]:
        """Return all automations belonging to a user."""
        return (
            self.db.query(Automation)
            .filter(Automation.user_id == user_id)
            .order_by(Automation.created_at.desc())
            .all()
        )

    def get_automation_for_user(self, automation_id: int, user_id: int) -> Optional[Automation]:
        """Fetch a single automation by id for the given user."""
        return (
            self.db.query(Automation)
            .filter(Automation.id == automation_id, Automation.user_id == user_id)
            .first()
        )

    def count_automations_for_user(self, user_id: int) -> int:
        """Return number of automations the user has."""
        return self.db.query(Automation).filter(Automation.user_id == user_id).count()

    def get_applications_today_count(self, automation_id: int) -> int:
        """Count applications (SUBMITTED) for this automation today (UTC)."""
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return (
            self.db.query(UserJob)
            .filter(
                UserJob.automation_id == automation_id,
                UserJob.status == UserJobStatus.SUBMITTED,
                UserJob.applied_at >= today_start,
            )
            .count()
        )

    def create_automation(self, user_id: int, data: AutomationCreate) -> Automation:
        """Create a new automation for the given user (starts paused by default)."""
        automation = Automation(
            user_id=user_id,
            name=data.name or "Untitled automation",
            target_titles=data.target_titles,
            locations=data.locations,
            daily_limit=data.daily_limit,
            platforms=data.platforms or [],
            cover_letter_template=data.cover_letter_template,
            status="paused",
        )
        self.db.add(automation)
        self.db.commit()
        self.db.refresh(automation)
        return automation

    def update_automation(self, automation_id: int, user_id: int, update: AutomationUpdate) -> Optional[Automation]:
        """Update an existing automation for a user."""
        automation = self.get_automation_for_user(automation_id, user_id)
        if not automation:
            return None
        data = update.model_dump(exclude_unset=True)
        # Guard status to the two allowed values if present
        status = data.get("status")
        if status is not None and status not in ("running", "paused"):
            data.pop("status")
        for key, value in data.items():
            setattr(automation, key, value)
        self.db.commit()
        self.db.refresh(automation)
        return automation

    def set_status(self, automation_id: int, user_id: int, status: str) -> Optional[Automation]:
        """Convenience to pause/resume automation."""
        if status not in ("running", "paused"):
            return None
        automation = self.get_automation_for_user(automation_id, user_id)
        if not automation:
            return None
        automation.status = status
        self.db.commit()
        self.db.refresh(automation)
        return automation

    def increment_total_applied(self, automation_id: int, user_id: int, count: int = 1) -> Optional[Automation]:
        """
        Increment the total_applied counter.
        In a real worker, call this each time an application is successfully submitted.
        """
        automation = self.get_automation_for_user(automation_id, user_id)
        if not automation:
            return None
        automation.total_applied = (automation.total_applied or 0) + max(count, 0)
        self.db.commit()
        self.db.refresh(automation)
        return automation

    def list_all_for_admin(
        self,
        search: Optional[str] = None,
    ) -> List[Automation]:
        """List all automations with user loaded (for admin). Optional search by name or user email."""
        from sqlalchemy import or_

        query = (
            self.db.query(Automation)
            .options(joinedload(Automation.user))
            .join(User, Automation.user_id == User.id)
        )
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Automation.name.ilike(term),
                    User.email.ilike(term),
                    User.full_name.ilike(term),
                )
            )
        query = query.order_by(Automation.created_at.desc())
        return query.all()

    def get_automation_by_id(self, automation_id: int) -> Optional[Automation]:
        """Get any automation by id (for admin)."""
        return (
            self.db.query(Automation)
            .options(joinedload(Automation.user))
            .filter(Automation.id == automation_id)
            .first()
        )

    def update_automation_admin(
        self,
        automation_id: int,
        update: AutomationUpdate,
    ) -> Optional[Automation]:
        """Update any automation by id (admin)."""
        automation = self.get_automation_by_id(automation_id)
        if not automation:
            return None
        data = update.model_dump(exclude_unset=True)
        status_val = data.get("status")
        if status_val is not None and status_val not in ("running", "paused"):
            data.pop("status")
        for key, value in data.items():
            setattr(automation, key, value)
        self.db.commit()
        self.db.refresh(automation)
        return automation

    def set_status_admin(self, automation_id: int, status: str) -> Optional[Automation]:
        """Set status of any automation (admin)."""
        if status not in ("running", "paused"):
            return None
        automation = self.get_automation_by_id(automation_id)
        if not automation:
            return None
        automation.status = status
        self.db.commit()
        self.db.refresh(automation)
        return automation

    def run_automation(
        self,
        automation_id: int,
        user_id: int,
    ) -> Optional[AutomationRunResult]:
        """
        Run automation once: find matching jobs (by target_titles, locations),
        apply up to daily limit, return result with message for toast.
        Can be called by a background task or "Run now" button.
        """
        from app.services.job_service import JobService
        from app.services.user_job_service import UserJobService

        automation = self.get_automation_for_user(automation_id, user_id)
        if not automation:
            return None

        applications_today = self.get_applications_today_count(automation_id)
        daily_limit = automation.daily_limit or 25
        slots_left = max(0, daily_limit - applications_today)

        if slots_left == 0:
            return AutomationRunResult(
                applied_count=0,
                limit_reached=True,
                message=f"Daily limit exceeded ({applications_today}/{daily_limit}).",
                applications_today=applications_today,
            )

        job_service = JobService(self.db)
        user_job_service = UserJobService(self.db)
        exclude_job_ids = user_job_service.get_job_ids_for_user(user_id)
        matching_jobs = job_service.find_matching_jobs_for_automation(
            target_titles=automation.target_titles,
            locations=automation.locations,
            exclude_job_ids=exclude_job_ids,
            limit=slots_left,
        )

        if not matching_jobs:
            return AutomationRunResult(
                applied_count=0,
                limit_reached=False,
                message="No similar jobs available to apply to.",
                applications_today=applications_today,
            )

        job_ids = [j.id for j in matching_jobs]
        applied = user_job_service.apply_to_jobs(user_id, job_ids, automation_id)
        self.increment_total_applied(automation_id, user_id, len(applied))

        new_total_today = applications_today + len(applied)
        limit_reached = new_total_today >= daily_limit

        if len(applied) < slots_left:
            message = (
                f"Applied to {len(applied)} job(s) (only {len(applied)} similar job(s) available)."
            )
        else:
            message = (
                f"Applied to {len(applied)} job(s)."
                + (" Daily limit exceeded." if limit_reached else "")
            )

        return AutomationRunResult(
            applied_count=len(applied),
            limit_reached=limit_reached,
            message=message.strip(),
            applications_today=new_total_today,
        )

