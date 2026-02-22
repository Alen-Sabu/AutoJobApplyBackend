"""
Dashboard service – stats, campaigns, and activity for the user dashboard.
"""

from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.automation import Automation
from app.models.user_job import UserJob, UserJobStatus
from app.schemas.dashboard import (
    DashboardStat,
    DashboardCampaign,
    DashboardActivityItem,
)


def _parse_locations(locations_str: str | None) -> List[str]:
    if not locations_str or not locations_str.strip():
        return []
    return [s.strip() for s in locations_str.split(",") if s.strip()]


def _format_relative_time(dt: datetime | None) -> str:
    if not dt:
        return ""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
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
    return dt.strftime("%b %d")


class DashboardService:
    """User dashboard aggregates."""

    def __init__(self, db: Session):
        self.db = db

    def get_stats(self, user_id: int) -> List[DashboardStat]:
        """
        Dashboard stat cards: applications today, this week, interviews, active automations.
        """
        tz = timezone.utc
        today_start = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        fourteen_days_ago = today_start - timedelta(days=14)

        base = self.db.query(UserJob).filter(UserJob.user_id == user_id)

        applications_today = (
            base.filter(
                UserJob.status == UserJobStatus.SUBMITTED,
                UserJob.applied_at >= today_start,
            ).count()
        )
        applications_this_week = (
            base.filter(
                UserJob.status == UserJobStatus.SUBMITTED,
                UserJob.applied_at >= week_start,
            ).count()
        )
        interviews = (
            base.filter(
                UserJob.status == UserJobStatus.INTERVIEW,
                UserJob.updated_at >= fourteen_days_ago,
            ).count()
        )
        active_automations = (
            self.db.query(Automation)
            .filter(Automation.user_id == user_id, Automation.status == "running")
            .count()
        )

        return [
            DashboardStat(
                label="Applications today",
                value=str(applications_today),
                change="+0 vs yesterday",
                key="applications_today",
            ),
            DashboardStat(
                label="This week",
                value=str(applications_this_week),
                change="Last 7 days",
                key="this_week",
            ),
            DashboardStat(
                label="Interviews booked",
                value=str(interviews),
                change="Last 14 days",
                key="interviews",
            ),
            DashboardStat(
                label="Active automations",
                value=str(active_automations),
                change="Across job boards",
                key="active_automations",
            ),
        ]

    def get_campaigns(self, user_id: int) -> List[DashboardCampaign]:
        """
        List automations as dashboard campaigns (Running/Paused, locations list, dailyLimit string).
        Includes applicationsToday and dailyLimitNumber for "limit exceeded" UI.
        """
        from app.services.automation_service import AutomationService

        automations = (
            self.db.query(Automation)
            .filter(Automation.user_id == user_id)
            .order_by(Automation.created_at.desc())
            .all()
        )
        automation_service = AutomationService(self.db)
        result: List[DashboardCampaign] = []
        for a in automations:
            locations = _parse_locations(a.locations)
            status = "Running" if (a.status or "").lower() == "running" else "Paused"
            daily_limit_num = a.daily_limit or 0
            applications_today = automation_service.get_applications_today_count(a.id)
            result.append(
                DashboardCampaign(
                    id=str(a.id),
                    name=a.name or "Untitled",
                    targetTitle=a.target_titles or "—",
                    locations=locations,
                    dailyLimit=f"{daily_limit_num} / day",
                    platforms=a.platforms or [],
                    status=status,
                    applicationsToday=applications_today,
                    dailyLimitNumber=daily_limit_num,
                )
            )
        return result

    def get_activity(self, user_id: int, limit: int = 20) -> List[DashboardActivityItem]:
        """Recent activity from user_jobs (applications, status changes)."""
        rows = (
            self.db.query(UserJob)
            .options(joinedload(UserJob.job))
            .filter(UserJob.user_id == user_id)
            .order_by(
                func.coalesce(
                    UserJob.updated_at,
                    UserJob.applied_at,
                    UserJob.created_at,
                ).desc()
            )
            .limit(limit)
            .all()
        )
        items: List[DashboardActivityItem] = []
        for uj in rows:
            time_str = _format_relative_time(uj.updated_at or uj.applied_at or uj.created_at)
            job_title = (uj.job.title if uj.job else "") or "Job"
            company = (uj.job.company if uj.job else "") or ""
            target = f"{job_title} @ {company}".strip(" @") or "Job"

            if uj.status == UserJobStatus.INTERVIEW:
                title = "Interview scheduled"
                description = target
            elif uj.status == UserJobStatus.SUBMITTED:
                title = f"Applied to {job_title}"
                description = company or "Application submitted"
            elif uj.status == UserJobStatus.REJECTED:
                title = "Application update"
                description = f"{target} – not moving forward"
            else:
                title = "Application update"
                description = target

            items.append(
                DashboardActivityItem(
                    id=str(uj.id),
                    time=time_str,
                    title=title,
                    description=description,
                )
            )
        return items

"""
Dashboard service – stats, campaigns, and activity for the user dashboard.
"""
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.automation import Automation
from app.models.user_job import UserJob, UserJobStatus
from app.schemas.dashboard import (
    DashboardStat,
    DashboardCampaign,
    DashboardActivityItem,
)


def _parse_locations(locations_str: str | None) -> List[str]:
    if not locations_str or not locations_str.strip():
        return []
    return [s.strip() for s in locations_str.split(",") if s.strip()]


def _format_relative_time(dt: datetime | None) -> str:
    if not dt:
        return ""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
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
    return dt.strftime("%b %d")


class DashboardService:
    """User dashboard aggregates."""

    def __init__(self, db: Session):
        self.db = db

    def get_stats(self, user_id: int) -> List[DashboardStat]:
        """Dashboard stat cards: applications today, this week, interviews, active automations."""
        tz = timezone.utc
        today_start = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        fourteen_days_ago = today_start - timedelta(days=14)

        base = self.db.query(UserJob).filter(UserJob.user_id == user_id)

        applications_today = (
            base.filter(
                UserJob.status == UserJobStatus.SUBMITTED,
                UserJob.applied_at >= today_start,
            ).count()
        )
        applications_this_week = (
            base.filter(
                UserJob.status == UserJobStatus.SUBMITTED,
                UserJob.applied_at >= week_start,
            ).count()
        )
        interviews = (
            base.filter(
                UserJob.status == UserJobStatus.INTERVIEW,
                UserJob.updated_at >= fourteen_days_ago,
            ).count()
        )
        active_automations = (
            self.db.query(Automation)
            .filter(Automation.user_id == user_id, Automation.status == "running")
            .count()
        )

        return [
            DashboardStat(
                label="Applications today",
                value=str(applications_today),
                change="+0 vs yesterday",
                key="applications_today",
            ),
            DashboardStat(
                label="This week",
                value=str(applications_this_week),
                change="Last 7 days",
                key="this_week",
            ),
            DashboardStat(
                label="Interviews booked",
                value=str(interviews),
                change="Last 14 days",
                key="interviews",
            ),
            DashboardStat(
                label="Active automations",
                value=str(active_automations),
                change="Across job boards",
                key="active_automations",
            ),
        ]

    def get_campaigns(self, user_id: int) -> List[DashboardCampaign]:
        """List automations as dashboard campaigns (Running/Paused, locations list, dailyLimit string)."""
        automations = (
            self.db.query(Automation)
            .filter(Automation.user_id == user_id)
            .order_by(Automation.created_at.desc())
            .all()
        )
        result: List[DashboardCampaign] = []
        for a in automations:
            locations = _parse_locations(a.locations)
            status = "Running" if (a.status or "").lower() == "running" else "Paused"
            result.append(
                DashboardCampaign(
                    id=str(a.id),
                    name=a.name or "Untitled",
                    targetTitle=a.target_titles or "—",
                    locations=locations,
                    dailyLimit=f"{a.daily_limit or 0} / day",
                    platforms=a.platforms or [],
                    status=status,
                )
            )
        return result

    def get_activity(self, user_id: int, limit: int = 20) -> List[DashboardActivityItem]:
        """Recent activity from user_jobs (applications, status changes)."""
        rows = (
            self.db.query(UserJob)
            .options(joinedload(UserJob.job))
            .filter(UserJob.user_id == user_id)
            .order_by(
                func.coalesce(
                    UserJob.updated_at,
                    UserJob.applied_at,
                    UserJob.created_at,
                ).desc()
            )
            .limit(limit)
            .all()
        )
        items: List[DashboardActivityItem] = []
        for uj in rows:
            time_str = _format_relative_time(uj.updated_at or uj.applied_at or uj.created_at)
            job_title = (uj.job.title if uj.job else "") or "Job"
            company = (uj.job.company if uj.job else "") or ""
            target = f"{job_title} @ {company}".strip(" @") or "Job"

            if uj.status == UserJobStatus.INTERVIEW:
                title = "Interview scheduled"
                description = target
            elif uj.status == UserJobStatus.SUBMITTED:
                title = f"Applied to {job_title}"
                description = company or "Application submitted"
            elif uj.status == UserJobStatus.REJECTED:
                title = "Application update"
                description = f"{target} – not moving forward"
            else:
                title = "Application update"
                description = target

            items.append(
                DashboardActivityItem(
                    id=str(uj.id),
                    time=time_str,
                    title=title,
                    description=description,
                )
            )
        return items
