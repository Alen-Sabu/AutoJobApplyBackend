"""
Company (employer) endpoints: profile, jobs, applicants, approve/reject, view resume.
"""
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_company
from app.models.company import Company
from app.models.user_job import UserJobStatus
from app.schemas.company import (
    CompanyResponse,
    CompanyUpdate,
    ApplicantSummary,
    ApplicationStatusUpdate,
    CompanyStats,
)
from app.schemas.job import JobCreate, JobResponse
from app.services.company_service import CompanyService
from app.services.user_setup_service import UserSetupService

router = APIRouter()


@router.get("/profile", response_model=CompanyResponse)
async def get_company_profile(
    company: Company = Depends(get_current_company),
):
    """Get current company profile."""
    return company


@router.put("/profile", response_model=CompanyResponse)
async def update_company_profile(
    payload: CompanyUpdate,
    db=Depends(get_db),
    company: Company = Depends(get_current_company),
):
    """Update company profile."""
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(company, k, v)
    db.commit()
    db.refresh(company)
    return company


@router.get("/stats", response_model=CompanyStats)
async def get_company_stats(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """Get dashboard stats: total jobs and total applicants."""
    service = CompanyService(db)
    stats = service.get_stats(company.id)
    return CompanyStats(**stats)


@router.get("/jobs", response_model=List[JobResponse])
async def list_company_jobs(
    company: Company = Depends(get_current_company),
    db=Depends(get_db),
):
    """List jobs posted by this company."""
    service = CompanyService(db)
    jobs = service.list_jobs_for_company(company.id)
    return jobs


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_company_job(
    payload: JobCreate,
    company: Company = Depends(get_current_company),
    db=Depends(get_db),
):
    """Create a job listing (owned by this company)."""
    service = CompanyService(db)
    job = service.create_job_for_company(
        company.id,
        company.company_name,
        payload,
    )
    return job


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_company_job(
    job_id: int,
    company: Company = Depends(get_current_company),
    db=Depends(get_db),
):
    """Get a single job owned by this company."""
    service = CompanyService(db)
    job = service.get_job_for_company(job_id, company.id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


def _applicant_has_resume(uj) -> bool:
    """True if this applicant has a resume we can show (user_job.resume_path or user_setup)."""
    if uj.resume_path and Path(uj.resume_path).exists():
        return True
    if uj.user and getattr(uj.user, "user_setup", None):
        setup = uj.user.user_setup
        if setup and setup.resume_file_path and Path(setup.resume_file_path).exists():
            return True
    return False


@router.get("/jobs/{job_id}/applicants", response_model=List[ApplicantSummary])
async def list_job_applicants(
    job_id: int,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """List users who applied to this job (user_jobs for this job)."""
    service = CompanyService(db)
    user_jobs = service.get_applicants_for_job(job_id, company.id)
    out = []
    for uj in user_jobs:
        u = uj.user
        name = (u.full_name or u.username or (u.email.split("@")[0] if u.email else "")) if u else ""
        out.append(
            ApplicantSummary(
                id=uj.id,
                user_id=uj.user_id,
                user_email=u.email if u else "",
                user_name=name,
                status=uj.status.value if hasattr(uj.status, "value") else str(uj.status),
                applied_at=uj.applied_at,
                created_at=uj.created_at,
                has_resume=_applicant_has_resume(uj),
            )
        )
    return out


@router.patch("/jobs/{job_id}/applicants/{applicant_id}")
async def update_application_status(
    job_id: int,
    applicant_id: int,
    payload: ApplicationStatusUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """Approve, reject, or update status of an application (reviewing, interview, accepted, rejected)."""
    try:
        new_status = UserJobStatus(payload.status.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Use: reviewing, interview, accepted, rejected",
        )
    service = CompanyService(db)
    uj = service.update_application_status(job_id, applicant_id, company.id, new_status)
    if not uj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application or job not found.",
        )
    return {
        "id": uj.id,
        "status": uj.status.value,
        "message": f"Application {uj.status.value}.",
    }


def _get_applicant_resume_path(uj, setup_service: UserSetupService):
    """Return (filename, Path) for applicant resume or None."""
    if uj.resume_path:
        p = Path(uj.resume_path)
        if p.exists():
            return (p.name, p)
    result = setup_service.get_resume_path(uj.user_id)
    return result  # (original_name, Path) or None


@router.get("/jobs/{job_id}/applicants/{applicant_id}/resume")
async def get_applicant_resume(
    job_id: int,
    applicant_id: int,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
):
    """Download an applicant's resume (PDF/doc). Only for jobs owned by this company."""
    service = CompanyService(db)
    setup_service = UserSetupService(db)
    uj = service.get_applicant_user_job(job_id, applicant_id, company.id)
    if not uj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application or job not found.",
        )
    result = _get_applicant_resume_path(uj, setup_service)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume available for this applicant.",
        )
    original_name, path = result
    media_type = (
        "application/pdf"
        if (original_name or "").lower().endswith(".pdf")
        else "application/octet-stream"
    )
    return FileResponse(
        path=str(path),
        filename=original_name,
        media_type=media_type,
    )
