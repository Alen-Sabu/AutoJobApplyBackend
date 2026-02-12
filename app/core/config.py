"""
Application configuration settings loaded from environment / .env.
"""
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Core app
    PROJECT_NAME: str = "AutoJobApply"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]

    # Database (configure in .env as DATABASE_URL=...)
    DATABASE_URL: Optional[str] = None

    # Security (set a strong SECRET_KEY in .env)
    SECRET_KEY: str = "change-me-in-env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Job Application Settings
    DEFAULT_RESUME_PATH: Optional[str] = None
    DEFAULT_COVER_LETTER_PATH: Optional[str] = None

    # Uploads (resumes stored under this directory)
    UPLOAD_DIR: str = "uploads"
    MAX_RESUME_SIZE_MB: int = 5

    # External Services (set real keys in .env)
    LINKEDIN_API_KEY: Optional[str] = None
    INDEED_API_KEY: Optional[str] = None

    # Adzuna API (set APP_ID/API_KEY in .env)
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_API_KEY: Optional[str] = None
    ADZUNA_BASE_URL: str = "https://api.adzuna.com/v1/api/jobs"

    # Email / SMTP (all should come from .env in real use)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "no-reply@example.com"
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        # .env lives in the app/ directory (e.g. app/.env)
        env_file = "app/.env"
        case_sensitive = True


settings = Settings()

