"""Base scraper classes and interfaces."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class JobPosting:
    """Canonical job posting data structure."""
    
    # Required fields
    source: str
    url: str
    title: str
    company: str
    description: str
    
    # Optional fields
    source_id: Optional[str] = None
    company_url: Optional[str] = None
    company_logo: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    description_html: Optional[str] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    posted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class BaseScraper(ABC):
    """Base class for all job scrapers."""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"{__name__}.{source_name}")
    
    @abstractmethod
    async def scrape(self, **kwargs) -> List[JobPosting]:
        """Scrape jobs from the source."""
        pass
    
    @abstractmethod
    async def scrape_job_details(self, url: str) -> Optional[JobPosting]:
        """Scrape details for a specific job URL."""
        pass
    
    def normalize_job(self, raw_data: Dict[str, Any]) -> JobPosting:
        """Normalize raw scraped data to canonical format."""
        return JobPosting(
            source=self.source_name,
            **raw_data
        )
    
    async def save_jobs(self, jobs: List[JobPosting]) -> List[int]:
        """Save scraped jobs to database."""
        from ..models.job import Job
        from ..core.database import db_manager
        from sqlalchemy import select
        
        saved_ids = []
        
        async with db_manager.session() as session:
            for job in jobs:
                # Check for duplicate by URL
                stmt = select(Job).where(Job.url == job.url)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update existing job
                    self.logger.debug(f"Job already exists: {job.url}")
                    
                    # Update fields that might have changed
                    existing.title = job.title
                    existing.description = job.description
                    existing.location = job.location
                    existing.salary_min = job.salary_min
                    existing.salary_max = job.salary_max
                    existing.job_type = job.job_type
                    existing.experience_level = job.experience_level
                    existing.is_active = True
                    existing.scraped_at = datetime.now()
                    
                    saved_ids.append(existing.id)
                else:
                    # Create new job
                    job_data = job.to_dict()
                    job_data.pop('source', None)  # Remove from dict, we set it separately
                    
                    db_job = Job(
                        source=self.source_name,
                        **job_data
                    )
                    session.add(db_job)
                    await session.flush()
                    saved_ids.append(db_job.id)
                    self.logger.info(f"Saved new job: {job.title} at {job.company}")
            
            await session.commit()
        
        return saved_ids
    
    async def close(self) -> None:
        """Clean up resources. Override in subclasses that need cleanup."""
        pass