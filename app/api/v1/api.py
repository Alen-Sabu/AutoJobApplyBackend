"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    jobs,
    user_jobs,
    profiles,
    auth,
    setup,
    settings,
    admin,
    automations,
    dashboard,
    company,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(setup.router, prefix="/setup", tags=["setup"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(user_jobs.router, prefix="/user-jobs", tags=["user-jobs"])
api_router.include_router(automations.router, prefix="/automations", tags=["automations"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

