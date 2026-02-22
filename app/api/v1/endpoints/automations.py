"""
Automation endpoints: create/list and pause/resume user auto-apply rules.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.automation import (
    AutomationCreate,
    AutomationResponse,
    AutomationRunResultResponse,
)
from app.schemas.user_job import UserJobResponseWithJob
from app.schemas.job import JobResponse
from app.services.automation_service import AutomationService
from app.services.user_job_service import UserJobService
from app.services.site_settings_service import SiteSettingsService

router = APIRouter()


def _automation_response(automation, applications_today: int) -> AutomationResponse:
    """Build AutomationResponse with applications_today set."""
    resp = AutomationResponse.model_validate(automation)
    return resp.model_copy(update={"applications_today": applications_today})


def _user_job_with_job(uj):
    """Build UserJobResponseWithJob from UserJob ORM (job relationship loaded)."""
    return UserJobResponseWithJob(
        id=uj.id,
        user_id=uj.user_id,
        job_id=uj.job_id,
        automation_id=getattr(uj, "automation_id", None),
        status=uj.status,
        notes=uj.notes,
        resume_path=uj.resume_path,
        cover_letter_path=uj.cover_letter_path,
        applied_at=uj.applied_at,
        created_at=uj.created_at,
        updated_at=uj.updated_at,
        job=JobResponse.model_validate(uj.job),
    )


@router.get("/", response_model=List[AutomationResponse])
async def list_my_automations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return all automations for the authenticated user (with applications_today)."""
    service = AutomationService(db)
    automations = service.list_automations_for_user(current_user.id)
    return [
        _automation_response(a, service.get_applications_today_count(a.id))
        for a in automations
    ]


@router.get("/{automation_id}", response_model=AutomationResponse)
async def get_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a single automation by id (must belong to current user)."""
    service = AutomationService(db)
    automation = service.get_automation_for_user(automation_id, current_user.id)
    if not automation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found")
    return _automation_response(
        automation, service.get_applications_today_count(automation_id)
    )


@router.post(
    "/",
    response_model=AutomationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_automation(
    payload: AutomationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a new automation for the current user.
    Fails if user already has max_automations_per_user (site setting).

    New automations start in a paused state; the user must explicitly resume them.
    """
    automation_service = AutomationService(db)
    settings_service = SiteSettingsService(db)
    settings = settings_service.get_settings()
    max_automations = getattr(settings, "max_automations_per_user", 10) or 10
    count = automation_service.count_automations_for_user(current_user.id)
    if count >= max_automations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum automations ({max_automations}) reached. Delete an existing automation to create a new one.",
        )
    automation = automation_service.create_automation(current_user.id, payload)
    return _automation_response(
        automation, automation_service.get_applications_today_count(automation.id)
    )


@router.post(
    "/{automation_id}/run",
    response_model=AutomationRunResultResponse,
)
async def run_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Run automation once: find matching jobs (by target titles/locations),
    apply up to daily limit. Returns applied count and message for toast.
    """
    service = AutomationService(db)
    result = service.run_automation(automation_id, current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found")
    return AutomationRunResultResponse(
        applied_count=result.applied_count,
        limit_reached=result.limit_reached,
        message=result.message,
        applications_today=result.applications_today,
    )


@router.post("/{automation_id}/pause", response_model=AutomationResponse)
async def pause_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Pause a running automation."""
    service = AutomationService(db)
    automation = service.set_status(automation_id, current_user.id, "paused")
    if not automation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found")
    return _automation_response(
        automation, service.get_applications_today_count(automation_id)
    )


@router.post("/{automation_id}/resume", response_model=AutomationResponse)
async def resume_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Resume a paused automation."""
    service = AutomationService(db)
    automation = service.set_status(automation_id, current_user.id, "running")
    if not automation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found")
    return _automation_response(
        automation, service.get_applications_today_count(automation_id)
    )


@router.get("/{automation_id}/jobs", response_model=List[UserJobResponseWithJob])
async def list_automation_jobs(
    automation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List jobs applied (or saved) for this automation. Automation must belong to current user."""
    automation_service = AutomationService(db)
    automation = automation_service.get_automation_for_user(automation_id, current_user.id)
    if not automation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found")
    user_job_service = UserJobService(db)
    user_jobs = user_job_service.get_user_jobs_for_automation(
        current_user.id, automation_id, skip=skip, limit=limit
    )
    return [_user_job_with_job(uj) for uj in user_jobs]

