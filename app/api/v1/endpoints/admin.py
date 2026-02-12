"""
Admin endpoints (users etc.).
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_admin
from app.models.user import User
from app.models.job import Job
from app.schemas.admin import AdminUserOut, AdminJobOut
from app.schemas.job import JobCreate
from app.services.job_service import JobService

router = APIRouter()


def _map_user_to_admin_out(user: User) -> AdminUserOut:
    name = user.full_name or user.username or user.email.split("@")[0]
    role = "admin" if user.is_superuser else "user"
    status_val = "active" if user.is_active else "suspended"
    joined = (
        user.created_at.date().isoformat()
        if user.created_at is not None
        else ""
    )
    return AdminUserOut(
        id=user.id,
        name=name,
        email=user.email,
        role=role,
        status=status_val,  # type: ignore[arg-type]
        joined=joined,
    )


def _map_job_to_admin_out(job: Job) -> AdminJobOut:
    posted = job.created_at.date().isoformat() if job.created_at else ""
    status_val: str = job.status or "pending"
    if status_val not in ("pending", "approved", "rejected"):
        status_val = "pending"
    return AdminJobOut(
        id=job.id,
        title=job.title,
        company=job.company,
        status=status_val,  # type: ignore[arg-type]
        posted=posted,
        location=job.location,
        salary=job.salary_range,
        jobType=job.job_type,
        description=job.description,
        jobUrl=job.job_url,
        source=job.source,
    )


@router.get("/users", response_model=List[AdminUserOut])
async def admin_list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    status: Optional[str] = Query(None, description="Filter by status: active|suspended"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    List users for the admin panel with optional search and status filters.
    """
    query = db.query(User)
    if search:
        s = f"%{search.lower()}%"
        query = query.filter(
            (User.email.ilike(s))
            | (User.full_name.isnot(None) & User.full_name.ilike(s))
        )
    if status == "active":
        query = query.filter(User.is_active.is_(True))
    elif status == "suspended":
        query = query.filter(User.is_active.is_(False))

    users = query.order_by(User.created_at.desc().nullslast()).all()
    return [_map_user_to_admin_out(u) for u in users]


@router.post("/users/{user_id}/suspend", status_code=status.HTTP_204_NO_CONTENT)
async def admin_suspend_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Suspend a user (set is_active = False).
    Admin cannot suspend themselves.
    """
    if admin.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot suspend your own admin account.",
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_active = False
    db.commit()


@router.post("/users/{user_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def admin_activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Activate a user (set is_active = True).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_active = True
    db.commit()


@router.get("/jobs", response_model=List[AdminJobOut])
async def admin_list_jobs(
    search: Optional[str] = Query(None, description="Search by title or company"),
    status: Optional[str] = Query(None, description="Filter by status: pending|approved|rejected"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    List jobs for moderation in the admin panel.
    """
    query = db.query(Job)
    if search:
        s = f"%{search.lower()}%"
        query = query.filter(
            (Job.title.ilike(s))
            | (Job.company.ilike(s))
        )
    if status in ("pending", "approved", "rejected"):
        query = query.filter(Job.status == status)

    jobs = query.order_by(Job.created_at.desc().nullslast()).all()
    return [_map_job_to_admin_out(j) for j in jobs]


@router.post("/jobs", response_model=AdminJobOut, status_code=status.HTTP_201_CREATED)
async def admin_create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Create a new job listing in the catalog.
    """
    service = JobService(db)
    job = service.create_job(payload)
    return _map_job_to_admin_out(job)


@router.put("/jobs/{job_id}", response_model=AdminJobOut)
async def admin_update_job(
    job_id: int,
    payload: JobCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Update an existing job listing.
    """
    service = JobService(db)
    data = payload.model_dump(exclude_unset=True)
    job = service.update_job(job_id, data)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return _map_job_to_admin_out(job)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Delete a job listing.
    """
    service = JobService(db)
    ok = service.delete_job(job_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")


@router.post("/jobs/{job_id}/approve", status_code=status.HTTP_204_NO_CONTENT)
async def admin_approve_job(
    job_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Mark job as approved.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    job.status = "approved"
    db.commit()


@router.post("/jobs/{job_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def admin_reject_job(
    job_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Mark job as rejected.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    job.status = "rejected"
    db.commit()

