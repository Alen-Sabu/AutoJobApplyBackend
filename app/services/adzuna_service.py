"""
Adzuna API client for fetching job listings.
"""
from typing import Any, Optional

import httpx

from app.core.config import settings


class AdzunaService:
    """Service for fetching jobs from Adzuna API."""

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.app_id = app_id or settings.ADZUNA_APP_ID
        self.app_key = app_key or settings.ADZUNA_API_KEY
        self.base_url = (base_url or settings.ADZUNA_BASE_URL).rstrip("/")

    def _normalize_job(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Map Adzuna job payload to our Job model fields."""
        company = raw.get("company") or {}
        location = raw.get("location") or {}
        salary_min = raw.get("salary_min")
        salary_max = raw.get("salary_max")
        salary_range = None
        if salary_min is not None or salary_max is not None:
            parts = []
            if salary_min is not None:
                parts.append(str(salary_min))
            if salary_max is not None:
                parts.append(str(salary_max))
            salary_range = " - ".join(parts) if parts else None

        return {
            "title": raw.get("title") or "",
            "company": company.get("display_name", "") if isinstance(company, dict) else str(company),
            "location": location.get("display_name") if isinstance(location, dict) else (location or None),
            "description": raw.get("description") or None,
            "job_url": raw.get("redirect_url") or None,
            "salary_range": salary_range,
            "job_type": raw.get("contract_type") or raw.get("contract_time") or None,
            "source": "adzuna",
        }

    async def fetch_jobs(
        self,
        country: str = "us",
        keyword: str = "python",
        location: str = "new york",
        page: int = 1,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Fetch job listings from Adzuna.

        Returns:
            Tuple of (list of normalized job dicts for DB, total count from API).
        """
        if not self.app_id or not self.app_key:
            raise ValueError("ADZUNA_APP_ID and ADZUNA_API_KEY must be set in config or .env")

        url = f"{self.base_url}/{country}/search/{page}"
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "what": keyword,
            "where": location,
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        results = data.get("results") or []
        total = data.get("count", 0)
        normalized = [self._normalize_job(j) for j in results]
        return normalized, total
