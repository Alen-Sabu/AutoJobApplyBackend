"""
AuditLog model – records admin and system actions for audit trail.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """Audit log entry (immutable)."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Who performed the action (email, username, or 'system')
    actor = Column(String, nullable=False, index=True)

    # Machine-readable action code, e.g. 'user.suspended', 'job.approved'
    action = Column(String, nullable=False, index=True)

    # Short human-readable description of target, e.g. 'User #12', 'Job #442'
    target = Column(String, nullable=False)

    # IP address if known, '-' or '' otherwise
    ip = Column(String, nullable=False, default="-")

