"""
Job search and management endpoints.
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.job import JobCreate, JobResponse, JobSearchParams
from app.services.job_service import JobService
from app.services.user_job_service import UserJobService
from app.services.adzuna_service import AdzunaService
from app.models.user_job import UserJobStatus
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    query: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List jobs from the catalog with optional filters."""
    job_service = JobService(db)
    params = JobSearchParams(query=query, location=location, job_type=job_type, source=source)
    return job_service.list_jobs(params, skip=skip, limit=limit)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a job by ID from the catalog."""
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a job in the catalog (e.g. manual entry)."""
    job_service = JobService(db)
    return job_service.create_job(job)


@router.post("/fetch-adzuna", response_model=List[JobResponse])
async def fetch_adzuna_and_save(
    country: str = Query("us", description="Adzuna country code"),
    keyword: str = Query("python", description="Search keyword"),
    location: str = Query("new york", description="Location"),
    page: int = Query(1, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Fetch jobs from Adzuna, add to catalog, and add them to current user's list as SAVED."""
    adzuna = AdzunaService()
    try:
        jobs_data, _ = await adzuna.fetch_jobs(
            country=country, keyword=keyword, location=location, page=page
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Adzuna is not configured. Set ADZUNA_APP_ID and ADZUNA_API_KEY in .env.",
        ) from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Adzuna API error: {e.response.status_code}",
        ) from e
    job_service = JobService(db)
    user_job_service = UserJobService(db)
    jobs = job_service.add_jobs_from_list(jobs_data)
    user_job_service.add_user_jobs_for_jobs(current_user.id, jobs, status=UserJobStatus.SAVED)
    return jobs
