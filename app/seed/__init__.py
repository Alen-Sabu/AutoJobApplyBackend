"""
Seed package: load sample data into all tables.
Run from project root: python -m app.seed.run
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from sqlalchemy.orm import Session

__all__ = ["run_all"]


def run_all(db: "Session", *, reset: bool = False, job_count: int = 250) -> None:
	from app.seed.run import run_all as _run_all

	_run_all(db, reset=reset, job_count=job_count)
