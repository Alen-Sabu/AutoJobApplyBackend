"""
Company service – company profile and job management.
"""
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.company import Company
from app.models.job import Job
from app.models.user import User
from app.models.user_job import UserJob, UserJobStatus
from app.schemas.job import JobCreate


class CompanyService:
    def __init__(self, db: Session):
        self.db = db

    def get_company_by_user_id(self, user_id: int) -> Optional[Company]:
        return self.db.query(Company).filter(Company.user_id == user_id).first()

    def get_stats(self, company_id: int) -> dict:
        """Return total_jobs and total_applicants for the company."""
        total_jobs = self.db.query(Job).filter(Job.company_id == company_id).count()
        total_applicants = (
            self.db.query(UserJob.id)
            .join(Job, UserJob.job_id == Job.id)
            .filter(Job.company_id == company_id)
            .count()
        )
        return {"total_jobs": total_jobs, "total_applicants": total_applicants}

    def list_jobs_for_company(self, company_id: int) -> List[Job]:
        return (
            self.db.query(Job)
            .filter(Job.company_id == company_id)
            .order_by(Job.created_at.desc())
            .all()
        )

    def get_job_for_company(self, job_id: int, company_id: int) -> Optional[Job]:
        return (
            self.db.query(Job)
            .filter(Job.id == job_id, Job.company_id == company_id)
            .first()
        )

    def create_job_for_company(self, company_id: int, company_name: str, payload: JobCreate) -> Job:
        data = payload.model_dump()
        if "status" not in data or data["status"] is None:
            data["status"] = "pending"
        data["company"] = company_name
        data["company_id"] = company_id
        job = Job(**data)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_applicants_for_job(self, job_id: int, company_id: int) -> List[UserJob]:
        job = self.get_job_for_company(job_id, company_id)
        if not job:
            return []
        return (
            self.db.query(UserJob)
            .options(
                joinedload(UserJob.user).joinedload(User.user_setup),
                joinedload(UserJob.job),
            )
            .filter(UserJob.job_id == job_id)
            .order_by(UserJob.applied_at.desc().nullslast(), UserJob.created_at.desc())
            .all()
        )

    def get_applicant_user_job(
        self, job_id: int, applicant_id: int, company_id: int
    ) -> Optional[UserJob]:
        """Get a single applicant (user_job) for a job owned by this company."""
        job = self.get_job_for_company(job_id, company_id)
        if not job:
            return None
        return (
            self.db.query(UserJob)
            .options(joinedload(UserJob.user), joinedload(UserJob.job))
            .filter(
                UserJob.id == applicant_id,
                UserJob.job_id == job_id,
            )
            .first()
        )

    def update_application_status(
        self,
        job_id: int,
        applicant_id: int,
        company_id: int,
        new_status: UserJobStatus,
    ) -> Optional[UserJob]:
        """Update an application's status (e.g. accept/reject). Only for company's job."""
        uj = self.get_applicant_user_job(job_id, applicant_id, company_id)
        if not uj:
            return None
        allowed = {
            UserJobStatus.REVIEWING,
            UserJobStatus.INTERVIEW,
            UserJobStatus.ACCEPTED,
            UserJobStatus.REJECTED,
        }
        if new_status not in allowed:
            return None
        uj.status = new_status
        self.db.add(uj)
        self.db.commit()
        self.db.refresh(uj)
        return uj
