"""
Job database model.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Job(Base):
    """Job model."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)  # display name; may duplicate company_owner.company_name
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    job_url = Column(String, nullable=True, index=True)
    salary_range = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    source = Column(String, nullable=True)
    external_id = Column(String, nullable=True, index=True)
    status = Column(String, nullable=False, default="pending", index=True)  # pending | approved | rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company_owner = relationship("Company", back_populates="jobs")
    user_jobs = relationship("UserJob", back_populates="job")
