"""
UserJob service.
"""
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.job import Job
from app.models.user_job import UserJob, UserJobStatus
from app.schemas.user_job import UserJobCreate, UserJobUpdate


class UserJobService:
    """Service for user–job associations (saved/applied jobs)."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_job(self, user_job_id: int, user_id: int) -> Optional[UserJob]:
        """Get a user_job by ID for the given user (with job loaded)."""
        return (
            self.db.query(UserJob)
            .options(joinedload(UserJob.job))
            .filter(UserJob.id == user_job_id, UserJob.user_id == user_id)
            .first()
        )

    def get_user_jobs(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        status_filter: Optional[str] = None,
        automation_id: Optional[int] = None,
    ) -> List[UserJob]:
        """Get user's saved/applied jobs (with job loaded)."""
        query = (
            self.db.query(UserJob)
            .options(joinedload(UserJob.job))
            .filter(UserJob.user_id == user_id)
        )
        if status_filter:
            try:
                status_enum = UserJobStatus(status_filter)
                query = query.filter(UserJob.status == status_enum)
            except ValueError:
                pass
        if automation_id is not None:
            query = query.filter(UserJob.automation_id == automation_id)
        return query.offset(skip).limit(limit).all()

    def get_user_jobs_for_automation(
        self,
        user_id: int,
        automation_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[UserJob]:
        """Get user_jobs linked to a specific automation (with job loaded)."""
        return self.get_user_jobs(
            user_id=user_id,
            skip=skip,
            limit=limit,
            automation_id=automation_id,
        )

    def get_by_user_and_job(self, user_id: int, job_id: int) -> Optional[UserJob]:
        """Get user_job by user and job."""
        return (
            self.db.query(UserJob)
            .filter(UserJob.user_id == user_id, UserJob.job_id == job_id)
            .first()
        )

    def get_job_ids_for_user(self, user_id: int) -> List[int]:
        """Return list of job_ids the user has any user_job for (any status)."""
        rows = (
            self.db.query(UserJob.job_id)
            .filter(UserJob.user_id == user_id)
            .distinct()
            .all()
        )
        return [r[0] for r in rows]

    def apply_to_jobs(
        self,
        user_id: int,
        job_ids: List[int],
        automation_id: int,
    ) -> List[UserJob]:
        """
        Create or update user_jobs as SUBMITTED with applied_at and automation_id.
        Returns the list of UserJob records created or updated.
        """
        now = datetime.now(timezone.utc)
        result: List[UserJob] = []
        for job_id in job_ids:
            existing = self.get_by_user_and_job(user_id, job_id)
            if existing:
                existing.status = UserJobStatus.SUBMITTED
                existing.applied_at = now
                existing.automation_id = automation_id
                self.db.add(existing)
                result.append(existing)
            else:
                uj = UserJob(
                    user_id=user_id,
                    job_id=job_id,
                    automation_id=automation_id,
                    status=UserJobStatus.SUBMITTED,
                    applied_at=now,
                )
                self.db.add(uj)
                result.append(uj)
        self.db.commit()
        for uj in result:
            self.db.refresh(uj)
        return result

    def add_user_job(self, user_id: int, user_job_create: UserJobCreate) -> UserJob:
        """Add a job to the user's list (save or start application). If automation_id given and row exists, link it."""
        existing = self.get_by_user_and_job(user_id, user_job_create.job_id)
        if existing:
            if user_job_create.automation_id is not None:
                existing.automation_id = user_job_create.automation_id
                self.db.commit()
                self.db.refresh(existing)
            return existing
        db_user_job = UserJob(
            user_id=user_id,
            **user_job_create.model_dump(),
        )
        self.db.add(db_user_job)
        self.db.commit()
        self.db.refresh(db_user_job)
        return db_user_job

    def add_user_jobs_for_jobs(
        self,
        user_id: int,
        jobs: List[Job],
        status: UserJobStatus = UserJobStatus.SAVED,
    ) -> List[UserJob]:
        """Create UserJob for each job for the user (e.g. after fetching from Adzuna)."""
        created: List[UserJob] = []
        for job in jobs:
            if self.get_by_user_and_job(user_id, job.id):
                continue
            uj = UserJob(user_id=user_id, job_id=job.id, status=status)
            self.db.add(uj)
            created.append(uj)
        self.db.commit()
        for uj in created:
            self.db.refresh(uj)
        return created

    def update_user_job(
        self,
        user_job_id: int,
        user_id: int,
        update: UserJobUpdate,
    ) -> Optional[UserJob]:
        """Update a user_job."""
        uj = self.get_user_job(user_job_id, user_id)
        if not uj:
            return None
        data = update.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(uj, k, v)
        self.db.commit()
        self.db.refresh(uj)
        return uj

    def submit_user_job(self, user_job_id: int, user_id: int) -> Optional[UserJob]:
        """Mark user_job as submitted."""
        uj = self.get_user_job(user_job_id, user_id)
        if not uj:
            return None
        uj.status = UserJobStatus.SUBMITTED
        uj.applied_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(uj)
        return uj

    def delete_user_job(self, user_job_id: int, user_id: int) -> bool:
        """Remove a job from the user's list."""
        uj = self.get_user_job(user_job_id, user_id)
        if not uj:
            return False
        self.db.delete(uj)
        self.db.commit()
        return True
