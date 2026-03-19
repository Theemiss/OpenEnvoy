"""Arbeitnow job scraper (European/German market)."""

import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..base import BaseScraper, JobPosting


class ArbeitnowScraper(BaseScraper):
    """Scraper for Arbeitnow job board (European market)."""
    
    def __init__(self):
        super().__init__("arbeitnow")
        self.base_url = "https://www.arbeitnow.com/api/job-board-api"
    
    async def scrape(self, limit: int = 100, **kwargs) -> List[JobPosting]:
        """Scrape jobs from Arbeitnow API."""
        
        try:
            params = {
                "limit": min(limit, 100)  # API max is 100
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                jobs = await self._parse_response(data)
                self.logger.info(f"Arbeitnow: found {len(jobs)} jobs")
                
                return jobs
                
        except Exception as e:
            self.logger.error(f"Error scraping Arbeitnow: {str(e)}")
            return []
    
    async def scrape_job_details(self, url: str) -> Optional[JobPosting]:
        """Arbeitnow API includes full details."""
        return None
    
    async def _parse_response(self, data: Dict[str, Any]) -> List[JobPosting]:
        """Parse Arbeitnow API response."""
        jobs = []
        
        for item in data.get("data", []):
            try:
                # Parse salary (in EUR)
                salary = item.get("salary")
                salary_min = None
                salary_max = None
                
                if salary:
                    # Format: "40k - 60k EUR"
                    import re
                    match = re.search(r'(\d+)(?:k)?\s*-\s*(\d+)(?:k)?', salary)
                    if match:
                        salary_min = int(match.group(1)) * 1000
                        salary_max = int(match.group(2)) * 1000
                
                # Parse tags/skills
                tags = item.get("tags", [])
                skills = [tag for tag in tags if len(tag) < 30]  # Filter out long phrases
                
                # Parse date
                posted_at = None
                if item.get("created_at"):
                    try:
                        posted_at = datetime.fromtimestamp(item["created_at"])
                    except (ValueError, OSError) as e:
                        self.logger.debug(f"Error parsing timestamp for job: {e}")
                        posted_at = datetime.fromtimestamp(item["created_at"])
                    except:
                        pass
                
                job = JobPosting(
                    source=self.source_name,
                    source_id=str(item.get("slug")),
                    url=item.get("url"),
                    title=item.get("title"),
                    company=item.get("company_name"),
                    location=item.get("location"),
                    description=item.get("description", ""),
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency="EUR",
                    job_type=item.get("job_type"),
                    skills=skills,
                    posted_at=posted_at,
                    company_logo=item.get("company_logo")
                )
                
                jobs.append(job)
                
            except Exception as e:
                self.logger.error(f"Error parsing Arbeitnow job: {str(e)}")
                continue
        
        return jobs