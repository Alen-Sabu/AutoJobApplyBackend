"""
Setup (onboarding) endpoints: personal details, resume upload, completion.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.user_setup_service import UserSetupService
from app.schemas.user_setup import (
    SetupStatusResponse,
    SetupDataOut,
    SetupPersonalDetails,
    SetupResumeOut,
    SetupCompleteResponse,
)

router = APIRouter()

ALLOWED_RESUME_TYPES = {"application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


def _setup_to_data_out(setup) -> Optional[SetupDataOut]:
    if not setup:
        return None
    personal = SetupPersonalDetails(
        full_name=setup.full_name,
        email=setup.email,
        phone=setup.phone,
        location=setup.location,
        linkedin_url=setup.linkedin_url,
        years_experience=setup.years_experience,
        top_skills=setup.top_skills,
    )
    resume_out: Optional[SetupResumeOut] = None
    if setup.resume_file_name and setup.resume_file_path:
        resume_out = SetupResumeOut(
            fileName=setup.resume_file_name,
            uploadedAt=setup.updated_at.isoformat() if setup.updated_at else datetime.utcnow().isoformat(),
            url="/api/v1/setup/resume",  # frontend uses this to download
        )
    return SetupDataOut(personal=personal, resume=resume_out)


@router.get("/status", response_model=SetupStatusResponse)
async def get_setup_status(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's setup status and data."""
    service = UserSetupService(db)
    setup = service.get_by_user_id(current_user.id)
    if not setup:
        return SetupStatusResponse(complete=False, data=None)
    return SetupStatusResponse(
        complete=bool(setup.setup_complete),
        data=_setup_to_data_out(setup),
    )


@router.put("/personal", response_model=SetupDataOut)
async def save_personal_details(
    personal: SetupPersonalDetails,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save personal details (step 1)."""
    service = UserSetupService(db)
    setup = service.update_personal(
        current_user.id,
        full_name=personal.full_name,
        email=personal.email,
        phone=personal.phone,
        location=personal.location,
        linkedin_url=personal.linkedin_url,
        years_experience=personal.years_experience,
        top_skills=personal.top_skills,
    )
    data = _setup_to_data_out(setup)
    return data


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload or replace resume file (PDF or DOCX). Max 5MB. Re-uploading overwrites the previous file."""
    if file.content_type and file.content_type not in ALLOWED_RESUME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOC/DOCX files are allowed.",
        )
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB.",
        )
    service = UserSetupService(db)
    file_name, _ = service.save_resume(current_user.id, content, file.filename or "resume")
    return {
        "fileName": file_name,
        "uploadedAt": datetime.utcnow().isoformat(),
        "url": "/api/v1/setup/resume",
    }


@router.post("/complete", response_model=SetupCompleteResponse)
async def complete_setup(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark setup as complete. Requires resume and name/email."""
    service = UserSetupService(db)
    try:
        service.complete_setup(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return SetupCompleteResponse(complete=True)


@router.get("/resume")
async def download_resume(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download current user's uploaded resume."""
    service = UserSetupService(db)
    result = service.get_resume_path(current_user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No resume uploaded.")
    original_name, path = result
    media_type = "application/pdf" if (original_name or "").lower().endswith(".pdf") else "application/octet-stream"
    return FileResponse(
        path=str(path),
        filename=original_name,
        media_type=media_type,
    )
