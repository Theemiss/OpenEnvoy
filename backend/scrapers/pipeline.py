"""Job scraping pipeline orchestrator."""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .base import JobPosting
from .sources.linkedin import LinkedInScraper
from ..core.config import settings
from ..core.database import db_manager
from ..models.job import Job
from ..utils.deduplication import Deduplicator

logger = logging.getLogger(__name__)


class ScrapingPipeline:
    """Orchestrates multiple scrapers and handles the complete scraping flow."""
    
    def __init__(self):
        self.scrapers = {}
        self.deduplicator = Deduplicator()
        
        # Initialize scrapers
        self._init_scrapers()
    
    def _init_scrapers(self):
        """Initialize configured scrapers."""
        # Add LinkedIn scraper
        self.scrapers['linkedin'] = LinkedInScraper(headless=True)
        
        # Add more scrapers as they're implemented
    
    async def run_all(self, **kwargs) -> Dict[str, int]:
        """Run all configured scrapers."""
        results = {}
        
        for name, scraper in self.scrapers.items():
            try:
                logger.info(f"Starting {name} scraper")
                jobs = await scraper.scrape(**kwargs)
                
                # Save jobs
                saved_ids = await scraper.save_jobs(jobs)
                results[name] = len(saved_ids)
                
                logger.info(f"{name} scraper completed: {len(saved_ids)} new/updated jobs")
                
            except Exception as e:
                logger.error(f"Error in {name} scraper: {str(e)}")
                results[name] = 0
            
            finally:
                # Close scraper resources
                await scraper.close()
        
        return results
    
    async def run_source(self, source: str, **kwargs) -> int:
        """Run a specific scraper."""
        if source not in self.scrapers:
            raise ValueError(f"Unknown source: {source}")
        
        scraper = self.scrapers[source]
        try:
            jobs = await scraper.scrape(**kwargs)
            saved_ids = await scraper.save_jobs(jobs)
            return len(saved_ids)
        finally:
            await scraper.close()
    
    async def cleanup_old_jobs(self, days: int = 90):
        """Mark old jobs as inactive."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        async with db_manager.session() as session:
            from sqlalchemy import update
            
            stmt = update(Job).where(
                Job.scraped_at < cutoff_date,
                Job.is_active == True
            ).values(is_active=False)
            
            result = await session.execute(stmt)
            await session.commit()
            
            logger.info(f"Marked {result.rowcount} old jobs as inactive")
    
    async def run_periodic_scrape(self, interval_hours: int = None):
        """Run scraping on a schedule."""
        interval = interval_hours or settings.SCRAPE_INTERVAL_HOURS
        
        while True:
            try:
                logger.info(f"Starting periodic scrape (every {interval} hours)")
                
                # Run all scrapers
                results = await self.run_all()
                
                # Clean up old jobs
                await self.cleanup_old_jobs()
                
                logger.info(f"Periodic scrape completed: {results}")
                
            except Exception as e:
                logger.error(f"Error in periodic scrape: {str(e)}")
            
            # Wait for next interval
            await asyncio.sleep(interval * 3600)
    
    async def process_new_jobs(self) -> int:
        """Process newly scraped jobs (apply filters, queue for scoring)."""
        async with db_manager.session() as session:
            from sqlalchemy import select
            
            # Find unprocessed jobs
            stmt = select(Job).where(
                Job.is_processed == False,
                Job.is_active == True,
                Job.process_attempts < 3
            ).order_by(Job.scraped_at).limit(100)
            
            result = await session.execute(stmt)
            jobs = result.scalars().all()
            
            if not jobs:
                return 0
            
            # Queue for processing (via Redis)
            from ..core.cache import cache
            
            for job in jobs:
                await cache.rpush('job_queue', job.id)
                
                # Mark as queued
                job.is_processed = True
            
            await session.commit()
            
            logger.info(f"Queued {len(jobs)} jobs for processing")
            return len(jobs)