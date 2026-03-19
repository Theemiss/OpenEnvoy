"""Adzuna job board scraper."""

import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

from ..base import BaseScraper, JobPosting
from ...core.config import settings


class AdzunaScraper(BaseScraper):
    """Scraper for Adzuna job board API."""
    
    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        super().__init__("adzuna")
        self.app_id = app_id or settings.ADZUNA_APP_ID
        self.app_key = app_key or settings.ADZUNA_API_KEY
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.country = "us"  # Can be configured
        
        if not self.app_id or not self.app_key:
            self.logger.warning("Adzuna API credentials not configured")
    
    async def scrape(self, keywords: Optional[List[str]] = None, 
                     location: Optional[str] = None,
                     max_pages: int = 5) -> List[JobPosting]:
        """Scrape jobs from Adzuna API."""
        
        if not self.app_id or not self.app_key:
            self.logger.error("Adzuna API not configured")
            return []
        
        all_jobs = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"{self.base_url}/{self.country}/search/{page}"
                
                params = {
                    "app_id": self.app_id,
                    "app_key": self.app_key,
                    "results_per_page": 50,
                    "content_type": "application/json"
                }
                
                if keywords:
                    params["what"] = " ".join(keywords)
                
                if location:
                    params["where"] = location
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    jobs = await self._parse_response(data)
                    all_jobs.extend(jobs)
                    
                    self.logger.info(f"Adzuna page {page}: found {len(jobs)} jobs")
                    
                    # Check if last page
                    if page >= data.get("pages", 0):
                        break
                    
            except Exception as e:
                self.logger.error(f"Error scraping Adzuna page {page}: {str(e)}")
                continue
        
        return all_jobs
    
    async def scrape_job_details(self, url: str) -> Optional[JobPosting]:
        """Adzuna API includes full details in search results, so this is not needed."""
        return None
    
    async def _parse_response(self, data: Dict[str, Any]) -> List[JobPosting]:
        """Parse Adzuna API response."""
        jobs = []
        
        for item in data.get("results", []):
            try:
                # Parse salary
                salary_min = item.get("salary_min")
                salary_max = item.get("salary_max")
                salary_currency = item.get("salary_currency", "USD")
                
                # Parse date
                posted_at = None
                if item.get("created"):
                    try:
                        posted_at = datetime.fromisoformat(item["created"].replace("Z", "+00:00"))
                    except ValueError as e:
                        self.logger.debug(f"Error parsing date for job: {e}")
                posted_at = None
                if item.get("created"):
                    try:
                        posted_at = datetime.fromisoformat(item["created"].replace("Z", "+00:00"))
                    except:
                        pass
                
                # Extract description
                description = item.get("description", "")
                
                # Extract contract type from title/description
                job_type = self._extract_job_type(item.get("title", "") + " " + description)
                
                job = JobPosting(
                    source=self.source_name,
                    source_id=str(item.get("id")),
                    url=item.get("redirect_url") or item.get("url"),
                    title=item.get("title"),
                    company=item.get("company", {}).get("display_name") if isinstance(item.get("company"), dict) else item.get("company"),
                    location=item.get("location", {}).get("display_name") if isinstance(item.get("location"), dict) else item.get("location"),
                    description=description,
                    salary_min=int(salary_min) if salary_min else None,
                    salary_max=int(salary_max) if salary_max else None,
                    salary_currency=salary_currency,
                    job_type=job_type,
                    posted_at=posted_at
                )
                
                jobs.append(job)
                
            except Exception as e:
                self.logger.error(f"Error parsing Adzuna job: {str(e)}")
                continue
        
        return jobs
    
    def _extract_job_type(self, text: str) -> Optional[str]:
        """Extract job type from text."""
        text_lower = text.lower()
        
        if "full-time" in text_lower or "full time" in text_lower:
            return "full-time"
        elif "part-time" in text_lower or "part time" in text_lower:
            return "part-time"
        elif "contract" in text_lower:
            return "contract"
        elif "temporary" in text_lower:
            return "temporary"
        elif "intern" in text_lower:
            return "internship"
        
        return None