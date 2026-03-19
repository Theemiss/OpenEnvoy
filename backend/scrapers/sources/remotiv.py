"""Remotive job board scraper (remote jobs)."""

import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..base import BaseScraper, JobPosting


class RemotiveScraper(BaseScraper):
    def __init__(self):
        super().__init__("remotive")
        self.base_url = "https://remotive.com/api/remote-jobs"

    async def scrape(
        self, category: Optional[str] = None, limit: int = 100, **kwargs
    ) -> List[JobPosting]:
        try:
            params = {"limit": limit}

            if category:
                params["category"] = category

            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                jobs = await self._parse_response(data)
                self.logger.info(f"Remotive: found {len(jobs)} jobs")

                return jobs

        except httpx.HTTPError as e:
            self.logger.error(f"Error scraping Remotive: {str(e)}")
            return []

    async def scrape_job_details(self, url: str) -> Optional[JobPosting]:
        return None

    async def _parse_response(self, data: Dict[str, Any]) -> List[JobPosting]:
        jobs = []

        for item in data.get("jobs", []):
            try:
                salary = item.get("salary")
                salary_min = None
                salary_max = None

                if salary and isinstance(salary, str):
                    if "-" in salary:
                        parts = salary.replace(",", "").replace("$", "").split("-")
                        if len(parts) == 2:
                            try:
                                salary_min = int(parts[0].strip())
                                salary_max = int(parts[1].strip())
                            except ValueError:
                                pass

                posted_at = None
                if item.get("publication_date"):
                    try:
                        posted_at = datetime.fromisoformat(
                            item["publication_date"].replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                job_type = "full-time"
                if "contract" in item.get("job_type", "").lower():
                    job_type = "contract"

                job = JobPosting(
                    source=self.source_name,
                    source_id=str(item.get("id")),
                    url=item.get("url"),
                    title=item.get("title"),
                    company=item.get("company_name"),
                    location="Remote",
                    description=item.get("description", ""),
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency="USD",
                    job_type=job_type,
                    posted_at=posted_at,
                    company_logo=item.get("company_logo_url"),
                    skills=self._extract_skills(item.get("description", "")),
                )

                jobs.append(job)

            except Exception as e:
                self.logger.error(f"Error parsing Remotive job: {str(e)}")
                continue

        return jobs

    def _extract_skills(self, description: str) -> List[str]:
        common_skills = [
            "python",
            "javascript",
            "typescript",
            "java",
            "c++",
            "c#",
            "ruby",
            "php",
            "go",
            "rust",
            "react",
            "angular",
            "vue",
            "node.js",
            "django",
            "flask",
            "fastapi",
            "spring",
            "aws",
            "azure",
            "gcp",
            "docker",
            "kubernetes",
            "terraform",
            "jenkins",
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "elasticsearch",
            "git",
            "github",
            "gitlab",
            "jira",
        ]

        found = []
        desc_lower = description.lower()

        for skill in common_skills:
            if skill in desc_lower:
                found.append(skill)

        return found
