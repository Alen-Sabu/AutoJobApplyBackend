"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import jobs, user_jobs, profiles, auth, setup, settings, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(setup.router, prefix="/setup", tags=["setup"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(user_jobs.router, prefix="/user-jobs", tags=["user-jobs"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

