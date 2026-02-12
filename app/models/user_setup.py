"""
User setup (onboarding) model: personal details + resume before applying to jobs.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserSetup(Base):
    """One-time setup per user: personal details and resume."""
    __tablename__ = "user_setups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    years_experience = Column(String, nullable=True)
    top_skills = Column(Text, nullable=True)
    resume_file_name = Column(String, nullable=True)
    resume_file_path = Column(String, nullable=True)
    setup_complete = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="user_setup")

