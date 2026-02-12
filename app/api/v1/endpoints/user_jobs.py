"""
User jobs endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.user_job import (
    UserJobCreate,
    UserJobUpdate,
    UserJobResponseWithJob,
)
from app.schemas.job import JobResponse
from app.services.user_job_service import UserJobService
from app.api.dependencies import get_current_user

router = APIRouter()


def _user_job_with_job(uj):
    """Build UserJobResponseWithJob from UserJob ORM (job relationship loaded)."""
    return UserJobResponseWithJob(
        id=uj.id,
        user_id=uj.user_id,
        job_id=uj.job_id,
        status=uj.status,
        notes=uj.notes,
        resume_path=uj.resume_path,
        cover_letter_path=uj.cover_letter_path,
        applied_at=uj.applied_at,
        created_at=uj.created_at,
        updated_at=uj.updated_at,
        job=JobResponse.model_validate(uj.job),
    )


@router.get("/", response_model=List[UserJobResponseWithJob])
async def get_my_user_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get current user's saved/applied jobs with job details."""
    service = UserJobService(db)
    user_jobs = service.get_user_jobs(
        current_user.id, skip=skip, limit=limit, status_filter=status_filter
    )
    return [_user_job_with_job(uj) for uj in user_jobs]


@router.post("/", response_model=UserJobResponseWithJob, status_code=status.HTTP_201_CREATED)
async def add_user_job(
    payload: UserJobCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Save a job to the user's list (or start an application)."""
    service = UserJobService(db)
    uj = service.add_user_job(current_user.id, payload)
    # Reload with job relationship
    uj = service.get_user_job(uj.id, current_user.id)
    return _user_job_with_job(uj)


@router.get("/{user_job_id}", response_model=UserJobResponseWithJob)
async def get_user_job(
    user_job_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a single user_job by ID."""
    service = UserJobService(db)
    uj = service.get_user_job(user_job_id, current_user.id)
    if not uj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return _user_job_with_job(uj)


@router.put("/{user_job_id}", response_model=UserJobResponseWithJob)
async def update_user_job(
    user_job_id: int,
    payload: UserJobUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a user_job (status, notes, resume, cover letter)."""
    service = UserJobService(db)
    uj = service.update_user_job(user_job_id, current_user.id, payload)
    if not uj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    uj = service.get_user_job(uj.id, current_user.id)
    return _user_job_with_job(uj)


@router.post("/{user_job_id}/submit", response_model=UserJobResponseWithJob)
async def submit_user_job(
    user_job_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Mark a user_job as submitted."""
    service = UserJobService(db)
    uj = service.submit_user_job(user_job_id, current_user.id)
    if not uj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    uj = service.get_user_job(uj.id, current_user.id)
    return _user_job_with_job(uj)


@router.delete("/{user_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_job(
    user_job_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove a job from the user's list."""
    service = UserJobService(db)
    ok = service.delete_user_job(user_job_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
