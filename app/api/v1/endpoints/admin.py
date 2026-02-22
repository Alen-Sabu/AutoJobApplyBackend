"""
Admin endpoints (users, jobs, automations, etc.).
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_admin
from app.models.user import User
from app.models.job import Job
from app.models.automation import Automation
from app.models.user_job import UserJob
from app.models.audit_log import AuditLog
from app.schemas.admin import (
    AdminUserOut,
    AdminJobOut,
    AdminAutomationOut,
    AdminSiteSettingsOut,
    AdminSiteSettingsUpdate,
    AdminStatCard,
    AdminActivityItem,
    AdminAlert,
    AdminAuditEntry,
)
from app.schemas.job import JobCreate
from app.schemas.automation import AutomationUpdate
from app.services.job_service import JobService
from app.services.automation_service import AutomationService
from app.services.site_settings_service import SiteSettingsService
from app.services.audit_service import AuditService

router = APIRouter()


def _audit_entry_to_admin(entry: AuditLog) -> AdminAuditEntry:
    """Map AuditLog ORM to AdminAuditEntry."""
    # Format time as ISO string for now; frontend can display directly
    time_str = (
        entry.created_at.isoformat(timespec="seconds")
        if entry.created_at is not None
        else ""
    )
    return AdminAuditEntry(
        id=entry.id,
        time=time_str,
        actor=entry.actor,
        action=entry.action,
        target=entry.target,
        ip=entry.ip,
    )


def _map_automation_to_admin_out(automation) -> AdminAutomationOut:
    user = automation.user
    user_name = (user.full_name or user.username or (user.email.split("@")[0] if user.email else "")) if user else ""
    user_email = user.email if user else ""
    return AdminAutomationOut(
        id=automation.id,
        user_id=automation.user_id,
        user_email=user_email,
        user_name=user_name,
        name=automation.name,
        target_titles=automation.target_titles,
        locations=automation.locations,
        daily_limit=automation.daily_limit,
        platforms=automation.platforms or [],
        cover_letter_template=automation.cover_letter_template,
        status=automation.status or "paused",
        total_applied=automation.total_applied or 0,
        created_at=automation.created_at,
        updated_at=automation.updated_at,
    )


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

    # Audit
    audit = AuditService(db)
    audit.log(
        actor=admin,
        action="user.suspended",
        target=f"User #{user_id}",
        ip="-",
    )


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

    # Audit
    audit = AuditService(db)
    audit.log(
        actor=admin,
        action="user.activated",
        target=f"User #{user_id}",
        ip="-",
    )


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

    # Audit
    audit = AuditService(db)
    audit.log(
        actor=admin,
        action="job.created",
        target=f"Job #{job.id}",
        ip="-",
    )

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

    # Audit
    audit = AuditService(db)
    changed_fields = ", ".join(data.keys()) or "job"
    audit.log(
        actor=admin,
        action="job.updated",
        target=f"Job #{job_id} ({changed_fields})",
        ip="-",
    )

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

    # Audit
    audit = AuditService(db)
    audit.log(
        actor=admin,
        action="job.deleted",
        target=f"Job #{job_id}",
        ip="-",
    )


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

    # Audit
    audit = AuditService(db)
    audit.log(
        actor=admin,
        action="job.approved",
        target=f"Job #{job_id}",
        ip="-",
    )


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

    # Audit
    audit = AuditService(db)
    audit.log(
        actor=admin,
        action="job.rejected",
        target=f"Job #{job_id}",
        ip="-",
    )


# —— Admin Automations ——

@router.get("/automations", response_model=List[AdminAutomationOut])
async def admin_list_automations(
    search: Optional[str] = Query(None, description="Search by automation name or user email/name"),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    List all automations across all users with user details.
    """
    service = AutomationService(db)
    automations = service.list_all_for_admin(search=search)
    return [_map_automation_to_admin_out(a) for a in automations]


@router.get("/automations/{automation_id}", response_model=AdminAutomationOut)
async def admin_get_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Get a single automation by id (any user).
    """
    service = AutomationService(db)
    automation = service.get_automation_by_id(automation_id)
    if not automation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found.")
    return _map_automation_to_admin_out(automation)


@router.put("/automations/{automation_id}", response_model=AdminAutomationOut)
async def admin_update_automation(
    automation_id: int,
    payload: AutomationUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Update an automation (name, targets, daily limit, platforms, status, etc.).
    """
    service = AutomationService(db)
    automation = service.update_automation_admin(automation_id, payload)
    if not automation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found.")
    automation = service.get_automation_by_id(automation_id)
    return _map_automation_to_admin_out(automation)


@router.post("/automations/{automation_id}/pause", response_model=AdminAutomationOut)
async def admin_pause_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Pause an automation (any user).
    """
    service = AutomationService(db)
    automation = service.set_status_admin(automation_id, "paused")
    if not automation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found.")

    # Audit
    audit = AuditService(db)
    audit.log(
        actor=admin,
        action="automation.paused",
        target=f"Automation #{automation_id}",
        ip="-",
    )

    return _map_automation_to_admin_out(automation)


@router.post("/automations/{automation_id}/resume", response_model=AdminAutomationOut)
async def admin_resume_automation(
    automation_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Resume an automation (any user).
    """
    service = AutomationService(db)
    automation = service.set_status_admin(automation_id, "running")
    if not automation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Automation not found.")

    # Audit
    audit = AuditService(db)
    audit.log(
        actor=admin,
        action="automation.resumed",
        target=f"Automation #{automation_id}",
        ip="-",
    )

    return _map_automation_to_admin_out(automation)


# —— Admin Site Settings ——

@router.get("/settings", response_model=AdminSiteSettingsOut)
async def admin_get_settings(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Get site-wide settings (maintenance mode, registration, limits, site name, support email).
    """
    service = SiteSettingsService(db)
    return service.get_settings()


@router.put("/settings", response_model=AdminSiteSettingsOut)
async def admin_update_settings(
    payload: AdminSiteSettingsUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Update site-wide settings.
    """
    service = SiteSettingsService(db)
    updated = service.update_settings(payload)

    # Audit
    audit = AuditService(db)
    changed_fields = ", ".join(
        [k for k, v in payload.model_dump(exclude_unset=True).items()]
    ) or "settings"
    audit.log(
        actor=admin,
        action="settings.updated",
        target=changed_fields,
        ip="-",
    )
    return updated


# —— Admin dashboard (stats, activity, alerts, audit) ——


@router.get("/stats", response_model=List[AdminStatCard])
async def admin_dashboard_stats(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    High-level stats for admin dashboard:
    - total users
    - active jobs (approved)
    - running automations
    - applications in last 30 days
    """
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

    total_users = db.query(User).count()
    active_jobs = db.query(Job).filter(Job.status == "approved").count()
    running_automations = (
        db.query(Automation).filter(Automation.status == "running").count()
    )
    applications_30d = (
        db.query(UserJob)
        .filter(UserJob.applied_at.isnot(None), UserJob.applied_at >= thirty_days_ago)
        .count()
    )

    return [
        AdminStatCard(
            label="Total users",
            value=f"{total_users:,}",
            change="+0 this month",
            key="users",
        ),
        AdminStatCard(
            label="Active jobs",
            value=f"{active_jobs:,}",
            change="Approved listings",
            key="jobs",
        ),
        AdminStatCard(
            label="Automations",
            value=f"{running_automations:,}",
            change="Running",
            key="automations",
        ),
        AdminStatCard(
            label="Applications (30d)",
            value=f"{applications_30d:,}",
            change="Last 30 days",
            key="applications",
        ),
    ]


@router.get("/activity", response_model=List[AdminActivityItem])
async def admin_dashboard_activity(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    Recent mixed activity: new users, jobs, automations, and applications.
    """
    tz = timezone.utc
    now = datetime.now(tz)

    def _rel(dt: datetime | None) -> str:
        if not dt:
            return ""
        if dt.tzinfo is None:
            dt_local = dt.replace(tzinfo=tz)
        else:
            dt_local = dt
        delta = now - dt_local
        if delta < timedelta(minutes=1):
            return "Just now"
        if delta < timedelta(hours=1):
            m = int(delta.total_seconds() / 60)
            return f"{m} min ago"
        if delta < timedelta(days=1):
            h = int(delta.total_seconds() / 3600)
            return f"{h} hr ago"
        if delta < timedelta(days=7):
            d = delta.days
            return f"{d} day{'s' if d != 1 else ''} ago"
        return dt_local.strftime("%b %d")

    items: List[AdminActivityItem] = []

    recent_users = (
        db.query(User)
        .order_by(User.created_at.desc().nullslast())
        .limit(10)
        .all()
    )
    for u in recent_users:
        items.append(
            AdminActivityItem(
                id=f"user-{u.id}",
                time=_rel(u.created_at),
                action="New user registered" if u.created_at else "User activity",
                detail=u.email,
                type="user",
            )
        )

    recent_jobs = (
        db.query(Job)
        .order_by(Job.created_at.desc().nullslast())
        .limit(10)
        .all()
    )
    for j in recent_jobs:
        items.append(
            AdminActivityItem(
                id=f"job-{j.id}",
                time=_rel(j.created_at),
                action=f"Job {j.status or 'pending'}",
                detail=f"{j.title} @ {j.company}",
                type="job",
            )
        )

    recent_automations = (
        db.query(Automation)
        .order_by(Automation.created_at.desc().nullslast())
        .limit(10)
        .all()
    )
    for a in recent_automations:
        items.append(
            AdminActivityItem(
                id=f"automation-{a.id}",
                time=_rel(a.created_at),
                action=f"Automation {a.status or 'created'}",
                detail=a.name or "Automation",
                type="automation",
            )
        )

    recent_apps = (
        db.query(UserJob)
        .order_by(UserJob.applied_at.desc().nullslast())
        .limit(10)
        .all()
    )
    for uj in recent_apps:
        items.append(
            AdminActivityItem(
                id=f"app-{uj.id}",
                time=_rel(uj.applied_at),
                action="Application submitted",
                detail=f"user_id={uj.user_id}, job_id={uj.job_id}",
                type="application",
            )
        )

    # Sort all by time descending (approximate: use created/applied dates already roughly ordered)
    items.sort(key=lambda i: i.time, reverse=True)
    return items[:30]


@router.get("/alerts", response_model=List[AdminAlert])
async def admin_dashboard_alerts(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    High-level alerts for admin dashboard.
    """
    pending_jobs = db.query(Job).filter(Job.status == "pending").count()
    suspended_users = db.query(User).filter(User.is_active.is_(False)).count()

    alerts: List[AdminAlert] = []
    if pending_jobs:
        alerts.append(
            AdminAlert(
                id="pending-jobs",
                message=f"{pending_jobs} job(s) pending review",
                severity="warning",
                href="/admin/jobs?status=pending",
            )
        )
    if suspended_users:
        alerts.append(
            AdminAlert(
                id="suspended-users",
                message=f"{suspended_users} suspended user account(s)",
                severity="info",
                href="/admin/users?status=suspended",
            )
        )

    return alerts


@router.get("/audit", response_model=List[AdminAuditEntry])
async def admin_audit_log(
    search: Optional[str] = Query(
        None, description="Search by actor, action, or target"
    ),
    action: Optional[str] = Query(None, description="Filter by action code"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """
    List audit log entries for admin UI.
    """
    service = AuditService(db)
    entries = service.list_entries(
        search=search,
        action_filter=action,
        skip=skip,
        limit=limit,
    )
    return [_audit_entry_to_admin(e) for e in entries]

