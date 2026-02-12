"""
User profile endpoints.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from app.services.profile_service import ProfileService
from app.api.dependencies import get_current_user
from app.models.profile import Profile

router = APIRouter()


def _profile_to_response(profile: Profile, user_full_name: str | None) -> ProfileResponse:
    """Build ProfileResponse with computed full_name and initials."""
    full_name = None
    if profile.first_name or profile.last_name:
        full_name = f"{profile.first_name or ''} {profile.last_name or ''}".strip() or None
    if not full_name and user_full_name:
        full_name = user_full_name
    initials = ""
    if full_name:
        parts = full_name.strip().split()
        if len(parts) >= 2:
            initials = (parts[0][0] + parts[-1][0]).upper()
        elif parts:
            initials = parts[0][:2].upper() if len(parts[0]) >= 2 else parts[0][0].upper()
    prefs = profile.matching_preferences
    if isinstance(prefs, str):
        try:
            prefs = json.loads(prefs) if prefs else []
        except json.JSONDecodeError:
            prefs = []
    elif prefs is None:
        prefs = []
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        phone=profile.phone,
        address=profile.address,
        resume_path=profile.resume_path,
        cover_letter_path=profile.cover_letter_path,
        linkedin_url=profile.linkedin_url,
        github_url=profile.github_url,
        portfolio_url=profile.portfolio_url,
        bio=profile.bio,
        headline=profile.headline,
        primary_location=profile.primary_location,
        years_experience=profile.years_experience,
        compensation_currency=profile.compensation_currency,
        top_skills=profile.top_skills,
        cover_letter_tone=profile.cover_letter_tone,
        matching_preferences=prefs,
        full_name=full_name,
        initials=initials,
    )


@router.get("/me", response_model=ProfileResponse)
async def get_current_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's profile."""
    profile_service = ProfileService(db)
    profile = profile_service.get_or_create_profile(current_user.id, current_user.full_name)
    return _profile_to_response(profile, current_user.full_name)


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile: ProfileCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new profile."""
    profile_service = ProfileService(db)
    created = profile_service.create_profile(profile, current_user.id)
    return _profile_to_response(created, current_user.full_name)


@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    profile_update: ProfileUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's profile."""
    profile_service = ProfileService(db)
    profile = profile_service.update_profile(current_user.id, profile_update)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return _profile_to_response(profile, current_user.full_name)

