"""
Audit service – create and query audit log entries.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.audit_log import AuditLog
from app.models.user import User


class AuditService:
    """Service for writing and reading audit log entries."""

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        actor: Optional[User],
        action: str,
        target: str,
        ip: str = "-",
    ) -> AuditLog:
        """
        Create a new audit entry.

        - actor.email is preferred; falls back to username or 'system'
        - action is a short machine code like 'user.suspended'
        - target is a short description like 'User #12' or 'Job #442'
        """
        if actor is None:
            actor_str = "system"
        else:
            actor_str = (
                actor.email
                or actor.full_name
                or actor.username
                or f"user:{actor.id}"
            )

        entry = AuditLog(
            actor=actor_str,
            action=action,
            target=target,
            ip=ip or "-",
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_entries(
        self,
        search: Optional[str] = None,
        action_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        """Return audit entries (most recent first) with optional search/action filters."""
        query = self.db.query(AuditLog)

        if search:
            s = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    AuditLog.actor.ilike(s),
                    AuditLog.action.ilike(s),
                    AuditLog.target.ilike(s),
                    AuditLog.ip.ilike(s),
                )
            )

        if action_filter:
            query = query.filter(AuditLog.action == action_filter)

        return (
            query.order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

