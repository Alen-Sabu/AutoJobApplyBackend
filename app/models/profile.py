"""
User profile database model.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Profile(Base):
    """Profile model."""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    resume_path = Column(String, nullable=True)
    cover_letter_path = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    headline = Column(String, nullable=True)
    primary_location = Column(String, nullable=True)
    years_experience = Column(String, nullable=True)
    compensation_currency = Column(String, nullable=True)
    top_skills = Column(Text, nullable=True)
    cover_letter_tone = Column(Text, nullable=True)
    matching_preferences = Column(Text, nullable=True)  # JSON array of strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")

