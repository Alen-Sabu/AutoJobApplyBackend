"""
Job service 
"""
from typing import Any, List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate, JobSearchParams


class JobService:
    """Service for job catalog operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_job(self, job_id: int) -> Optional[Job]:
        """Get a job by ID."""
        return self.db.query(Job).filter(Job.id == job_id).first()

    def list_jobs(
        self,
        search_params: JobSearchParams,
        skip: int = 0,
        limit: int = 10,
    ) -> List[Job]:
        """List jobs from the catalog with optional filters."""
        query = self.db.query(Job)
        if search_params.query:
            q = f"%{search_params.query}%"
            query = query.filter(
                or_(
                    Job.title.ilike(q),
                    (Job.description.isnot(None) & Job.description.ilike(q)),
                )
            )
        if search_params.location:
            query = query.filter(Job.location.ilike(f"%{search_params.location}%"))
        if search_params.job_type:
            query = query.filter(Job.job_type == search_params.job_type)
        if search_params.source:
            query = query.filter(Job.source == search_params.source)
        return query.offset(skip).limit(limit).all()

    def create_job(self, job_create: JobCreate) -> Job:
        """Create a job in the catalog (e.g. manual add)."""
        data = job_create.model_dump()
        # Default status to pending if not provided
        if not data.get("status"):
            data["status"] = "pending"
        db_job = Job(**data)
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        return db_job

    def update_job(self, job_id: int, data: dict) -> Optional[Job]:
        """Update a job's fields."""
        job = self.get_job(job_id)
        if not job:
            return None
        for key, value in data.items():
            if hasattr(job, key) and value is not None:
                setattr(job, key, value)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, job_id: int) -> bool:
        """Delete a job."""
        job = self.get_job(job_id)
        if not job:
            return False
        self.db.delete(job)
        self.db.commit()
        return True

    def get_or_create_by_url(
        self,
        title: str,
        company: str,
        job_url: Optional[str] = None,
        **kwargs: Any,
    ) -> Job:
        """Get existing job by job_url or create. Used when ingesting from Adzuna."""
        if job_url:
            existing = self.db.query(Job).filter(Job.job_url == job_url).first()
            if existing:
                return existing
        db_job = Job(
            title=title,
            company=company,
            job_url=job_url,
            **kwargs,
        )
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        return db_job

    def add_jobs_from_list(
        self,
        jobs: List[dict[str, Any]],
        skip_duplicate_url: bool = True,
    ) -> List[Job]:
        """
        Add job dicts (e.g. from Adzuna) to the job catalog.
        Returns the list of Job instances (existing or newly created).
        """
        result: List[Job] = []
        for j in jobs:
            job_url = j.get("job_url")
            if skip_duplicate_url and job_url:
                existing = self.db.query(Job).filter(Job.job_url == str(job_url)).first()
                if existing:
                    result.append(existing)
                    continue
            db_job = Job(
                title=j.get("title") or "Untitled",
                company=j.get("company") or "Unknown",
                location=j.get("location"),
                description=j.get("description"),
                job_url=str(job_url) if job_url else None,
                salary_range=j.get("salary_range"),
                job_type=j.get("job_type"),
                source=j.get("source") or "adzuna",
                external_id=j.get("external_id"),
            )
            self.db.add(db_job)
            result.append(db_job)
        self.db.commit()
        for db_job in result:
            self.db.refresh(db_job)
        return result
