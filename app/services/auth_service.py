"""
Authentication service.
"""
import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from app.models.user import User
from app.schemas.auth import UserCreate
from app.core.config import settings


def _truncate_for_bcrypt(password: str, max_bytes: int = 72) -> bytes:
    """Bcrypt only supports passwords up to 72 bytes. Returns UTF-8 bytes."""
    encoded = password.encode("utf-8")
    return encoded[:max_bytes] if len(encoded) > max_bytes else encoded


def _hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(_truncate_for_bcrypt(password), bcrypt.gensalt()).decode("ascii")


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(
        _truncate_for_bcrypt(plain_password),
        hashed_password.encode("ascii"),
    )


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return _verify_password(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return _hash_password(password)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        hashed_password = self.get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

