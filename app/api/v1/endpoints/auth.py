"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import Token, UserCreate, UserResponse, UserInfo
from app.schemas.company import CompanyRegister
from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _user_info(user):
    role = getattr(user, "role", None) or "user"
    return UserInfo(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=role,
        is_superuser=user.is_superuser or False,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (job seeker)."""
    auth_service = AuthService(db)
    return auth_service.create_user(user)


@router.post("/register/company", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_company(payload: CompanyRegister, db: Session = Depends(get_db)):
    """Register a new company (employer) account and log in."""
    auth_service = AuthService(db)
    try:
        user = auth_service.create_company_user(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=_user_info(user),
    )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login and get access token; returns user info for redirect by role."""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=_user_info(user),
    )


@router.post("/admin-login", response_model=Token)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Admin-only login endpoint.

    Accepts the same form fields as /auth/login but only allows users with
    is_superuser=True to obtain a token.
    """
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin credentials required.",
        )
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role="user",
            is_superuser=True,
        ),
    )

