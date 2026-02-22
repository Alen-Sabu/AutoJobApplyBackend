"""
User dashboard endpoints: stats, campaigns (automations), activity, pause/resume.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardStat,
    DashboardCampaign,
    DashboardActivityItem,
)
from app.services.dashboard_service import DashboardService
from app.services.automation_service import AutomationService

router = APIRouter()


@router.get("/stats", response_model=List[DashboardStat])
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dashboard stat cards for the authenticated user."""
    service = DashboardService(db)
    return service.get_stats(current_user.id)


@router.get("/campaigns", response_model=List[DashboardCampaign])
async def get_dashboard_campaigns(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Active campaigns (automations) for the authenticated user."""
    service = DashboardService(db)
    return service.get_campaigns(current_user.id)


@router.get("/activity", response_model=List[DashboardActivityItem])
async def get_dashboard_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recent activity (applications, interviews) for the authenticated user."""
    service = DashboardService(db)
    return service.get_activity(current_user.id)


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pause an automation (campaign)."""
    automation_service = AutomationService(db)
    automation = automation_service.set_status(campaign_id, current_user.id, "paused")
    if not automation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return {"status": "paused", "id": automation.id}


@router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Resume an automation (campaign)."""
    automation_service = AutomationService(db)
    automation = automation_service.set_status(campaign_id, current_user.id, "running")
    if not automation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return {"status": "running", "id": automation.id}

"""
User dashboard endpoints: stats, campaigns (automations), activity, pause/resume.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardStat,
    DashboardCampaign,
    DashboardActivityItem,
)
from app.services.dashboard_service import DashboardService
from app.services.automation_service import AutomationService

router = APIRouter()


@router.get("/stats", response_model=List[DashboardStat])
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Dashboard stat cards for the authenticated user."""
    service = DashboardService(db)
    return service.get_stats(current_user.id)


@router.get("/campaigns", response_model=List[DashboardCampaign])
async def get_dashboard_campaigns(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Active campaigns (automations) for the authenticated user."""
    service = DashboardService(db)
    return service.get_campaigns(current_user.id)


@router.get("/activity", response_model=List[DashboardActivityItem])
async def get_dashboard_activity(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Recent activity (applications, interviews) for the authenticated user."""
    service = DashboardService(db)
    return service.get_activity(current_user.id)


@router.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Pause an automation (campaign)."""
    automation_service = AutomationService(db)
    automation = automation_service.set_status(campaign_id, current_user.id, "paused")
    if not automation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return {"status": "paused", "id": automation.id}


@router.post("/campaigns/{campaign_id}/resume")
async def resume_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """Resume an automation (campaign)."""
    automation_service = AutomationService(db)
    automation = automation_service.set_status(campaign_id, current_user.id, "running")
    if not automation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return {"status": "running", "id": automation.id}
