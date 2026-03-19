"""RSS feed job scraper."""

import feedparser
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from ..base import BaseScraper, JobPosting


class RSSJobScraper(BaseScraper):
    """Scraper for RSS job feeds."""
    
    def __init__(self, feed_urls: List[str], source_name: str = "rss"):
        super().__init__(source_name)
        self.feed_urls = feed_urls
    
    async def scrape(self, **kwargs) -> List[JobPosting]:
        """Scrape jobs from RSS feeds."""
        
        all_jobs = []
        
        for feed_url in self.feed_urls:
            try:
                jobs = await self._scrape_feed(feed_url)
                all_jobs.extend(jobs)
                self.logger.info(f"RSS feed {feed_url}: found {len(jobs)} jobs")
                
            except Exception as e:
                self.logger.error(f"Error scraping RSS feed {feed_url}: {str(e)}")
                continue
        
        return all_jobs
    
    async def scrape_job_details(self, url: str) -> Optional[JobPosting]:
        """RSS feeds usually have full content, but if not, we could scrape."""
        # For RSS feeds that only have summaries, we might need to scrape the actual page
        # This is a simplified version
        return None
    
    async def _scrape_feed(self, feed_url: str) -> List[JobPosting]:
        """Scrape a single RSS feed."""
        
        # Use feedparser (synchronous, but run in thread pool)
        import asyncio
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
        
        jobs = []
        
        for entry in feed.entries[:50]:  # Limit to 50 per feed
            try:
                # Extract description/summary
                description = entry.get('summary', '') or entry.get('description', '')
                
                # Clean HTML from description
                description = re.sub('<[^<]+?>', '', description)
                
                # Parse date
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                posted_at = None
                if published:
                    posted_at = datetime(*published[:6])
                
                # Try to extract company from title or content
                title = entry.get('title', '')
                company = self._extract_company(title, description)
                
                # Try to extract location
                location = self._extract_location(description)
                
                job = JobPosting(
                    source=self.source_name,
                    source_id=entry.get('id', entry.get('link')),
                    url=entry.get('link'),
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    posted_at=posted_at
                )
                
                jobs.append(job)
                
            except Exception as e:
                self.logger.error(f"Error parsing RSS entry: {str(e)}")
                continue
        
        return jobs
    
    def _extract_company(self, title: str, description: str) -> str:
        """Extract company name from title or description."""
        # Common patterns: "Job Title at Company" or "Company: Job Title"
        
        # Pattern: "Title at Company"
        match = re.search(r' at ([A-Z][A-Za-z0-9\s]+?)(?:\s*[-–—]|\s*$)', title)
        if match:
            return match.group(1).strip()
        
        # Pattern: "Company: Title"
        match = re.search(r'^([A-Z][A-Za-z0-9\s]+?):', title)
        if match:
            return match.group(1).strip()
        
        # Try to find in description
        lines = description.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if 'company' in line.lower():
                # Extract after "company:" or similar
                match = re.search(r'company:?\s*([A-Z][A-Za-z0-9\s]+)', line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return "Unknown Company"
    
    def _extract_location(self, description: str) -> Optional[str]:
        """Extract location from description."""
        # Common location patterns
        patterns = [
            r'location:?\s*([A-Za-z,\s]+)',
            r'remote(?:\s*[-–—]\s*([A-Za-z,\s]+))?',
            r'in ([A-Za-z,\s]+?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                location = match.group(1) if match.groups() else "Remote"
                return location.strip()
        
        return None