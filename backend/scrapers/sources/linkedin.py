"""LinkedIn job scraper implementation."""

import httpx
import asyncio
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import quote_plus, urlencode
import json

from playwright.async_api import async_playwright, Page, Browser
from tenacity import retry, stop_after_attempt, wait_exponential

from ..base import BaseScraper, JobPosting
from ...core.config import settings


class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn jobs."""
    
    def __init__(self, headless: bool = True):
        super().__init__("linkedin")
        self.headless = headless
        self.base_url = "https://www.linkedin.com"
        self.jobs_url = f"{self.base_url}/jobs/search"
        self.browser: Optional[Browser] = None
        
        # Rate limiting
        self.request_delay = settings.RATE_LIMIT_DELAY
        self.last_request_time = 0
    
    async def ensure_browser(self):
        """Ensure browser instance is running."""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
    
    async def close(self):
        """Close browser instance."""
        if self.browser:
            await self.browser.close()
    
    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        now = datetime.now().timestamp()
        time_since_last = now - self.last_request_time
        if time_since_last < self.request_delay:
            await asyncio.sleep(self.request_delay - time_since_last)
        self.last_request_time = datetime.now().timestamp()
    
    async def _create_page(self) -> Page:
        """Create a new page with anti-detection measures."""
        await self.ensure_browser()
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Add stealth scripts
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        return await context.new_page()
    
    async def scrape(self, keywords: Optional[List[str]] = None, 
                     location: Optional[str] = None,
                     max_pages: int = 5) -> List[JobPosting]:
        """Scrape LinkedIn jobs based on keywords and location."""
        
        search_params = {
            'keywords': ' '.join(keywords) if keywords else 'software engineer',
            'location': location or 'United States',
            'f_TPR': 'r2592000',  # Past 30 days
            'f_WT': '2',  # Remote jobs
            'start': 0
        }
        
        all_jobs = []
        
        for page in range(max_pages):
            search_params['start'] = page * 25  # LinkedIn shows 25 per page
            url = f"{self.jobs_url}?{urlencode(search_params)}"
            
            self.logger.info(f"Scraping page {page + 1}: {url}")
            
            jobs = await self._scrape_search_page(url)
            if not jobs:
                break
            
            all_jobs.extend(jobs)
            
            # Be respectful
            await asyncio.sleep(self.request_delay * 2)
        
        self.logger.info(f"Found {len(all_jobs)} jobs total")
        return all_jobs
    
    async def _scrape_search_page(self, url: str) -> List[JobPosting]:
        """Scrape a single search results page."""
        page = None
        try:
            page = await self._create_page()
            
            # Navigate to search page
            await self._rate_limit()
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for job cards to load
            await page.wait_for_selector('.job-card-container', timeout=10000)
            
            # Scroll to load more
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            # Extract job links
            job_links = await page.evaluate("""
                () => {
                    const links = [];
                    document.querySelectorAll('.job-card-container__link').forEach(link => {
                        if (link.href) links.push(link.href);
                    });
                    return [...new Set(links)];  // Deduplicate
                }
            """)
            
            self.logger.info(f"Found {len(job_links)} job links")
            
            # Scrape each job details
            jobs = []
            for link in job_links[:10]:  # Limit to 10 per page to avoid rate limits
                try:
                    job = await self.scrape_job_details(link)
                    if job:
                        jobs.append(job)
                    await asyncio.sleep(self.request_delay)
                except Exception as e:
                    self.logger.error(f"Error scraping job {link}: {str(e)}")
            
            return jobs
            
        finally:
            if page:
                await page.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=20)
    )
    async def scrape_job_details(self, url: str) -> Optional[JobPosting]:
        """Scrape detailed information for a specific job."""
        page = None
        try:
            page = await self._create_page()
            
            # Navigate to job page
            await self._rate_limit()
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for job details to load
            await page.wait_for_selector('.jobs-details', timeout=10000)
            
            # Extract job data using evaluate
            job_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // Title
                    const titleEl = document.querySelector('.jobs-details-top-card__job-title');
                    if (titleEl) data.title = titleEl.innerText.trim();
                    
                    // Company
                    const companyEl = document.querySelector('.jobs-details-top-card__company-url');
                    if (companyEl) data.company = companyEl.innerText.trim();
                    
                    // Location
                    const locationEl = document.querySelector('.jobs-details-top-card__bullet');
                    if (locationEl) data.location = locationEl.innerText.trim();
                    
                    // Description
                    const descEl = document.querySelector('.jobs-description');
                    if (descEl) {
                        data.description = descEl.innerText.trim();
                        data.description_html = descEl.innerHTML;
                    }
                    
                    // Posted date
                    const postedEl = document.querySelector('.jobs-details-top-card__posted-date');
                    if (postedEl) {
                        const text = postedEl.innerText.toLowerCase();
                        if (text.includes('hours') || text.includes('day') || text.includes('week') || text.includes('month')) {
                            data.posted_date_text = text;
                        }
                    }
                    
                    // Extract job type and experience from description
                    const fullText = data.description || '';
                    
                    // Experience level patterns
                    const expPatterns = {
                        'entry': ['entry level', 'junior', 'graduate', 'new grad'],
                        'mid': ['mid-level', 'mid level', 'experienced'],
                        'senior': ['senior', 'lead', 'principal', 'staff']
                    };
                    
                    for (const [level, patterns] of Object.entries(expPatterns)) {
                        if (patterns.some(p => fullText.toLowerCase().includes(p))) {
                            data.experience_level = level;
                            break;
                        }
                    }
                    
                    // Job type
                    if (fullText.toLowerCase().includes('full-time') || 
                        fullText.toLowerCase().includes('full time')) {
                        data.job_type = 'full-time';
                    } else if (fullText.toLowerCase().includes('part-time') || 
                               fullText.toLowerCase().includes('part time')) {
                        data.job_type = 'part-time';
                    } else if (fullText.toLowerCase().includes('contract')) {
                        data.job_type = 'contract';
                    }
                    
                    return data;
                }
            """)
            
            if not job_data.get('title') or not job_data.get('company'):
                self.logger.warning(f"Missing required data for job: {url}")
                return None
            
            # Parse posted date if available
            posted_at = None
            if job_data.get('posted_date_text'):
                posted_at = self._parse_posted_date(job_data['posted_date_text'])
            
            # Extract requirements and skills
            requirements = self._extract_requirements(job_data.get('description', ''))
            skills = self._extract_skills(job_data.get('description', ''))
            
            # Create job posting
            job = JobPosting(
                source=self.source_name,
                source_id=self._extract_job_id(url),
                url=url,
                title=job_data['title'],
                company=job_data['company'],
                location=job_data.get('location'),
                description=job_data.get('description', ''),
                description_html=job_data.get('description_html'),
                job_type=job_data.get('job_type'),
                experience_level=job_data.get('experience_level'),
                requirements=requirements,
                skills=skills,
                posted_at=posted_at
            )
            
            return job
            
        except Exception as e:
            self.logger.error(f"Error scraping job details from {url}: {str(e)}")
            return None
            
        finally:
            if page:
                await page.close()
    
    def _extract_job_id(self, url: str) -> Optional[str]:
        """Extract job ID from LinkedIn URL."""
        # Pattern: /jobs/view/{job-id}/
        match = re.search(r'/jobs/view/(\d+)', url)
        if match:
            return match.group(1)
        
        # Pattern: ?currentJobId={job-id}
        match = re.search(r'currentJobId=(\d+)', url)
        if match:
            return match.group(1)
        
        return None
    
    def _parse_posted_date(self, date_text: str) -> Optional[datetime]:
        """Parse LinkedIn's relative date text."""
        now = datetime.now()
        text = date_text.lower()
        
        if 'hour' in text:
            # Posted hours ago
            match = re.search(r'(\d+)\s*hour', text)
            hours = int(match.group(1)) if match else 1
            return now.replace(hour=now.hour - hours)
        
        elif 'day' in text:
            # Posted days ago
            match = re.search(r'(\d+)\s*day', text)
            days = int(match.group(1)) if match else 1
            return now.replace(day=now.day - days)
        
        elif 'week' in text:
            # Posted weeks ago
            match = re.search(r'(\d+)\s*week', text)
            weeks = int(match.group(1)) if match else 1
            return now.replace(day=now.day - (weeks * 7))
        
        elif 'month' in text:
            # Posted months ago
            match = re.search(r'(\d+)\s*month', text)
            months = int(match.group(1)) if match else 1
            return now.replace(month=now.month - months)
        
        return None
    
    def _extract_requirements(self, description: str) -> List[str]:
        """Extract requirements section from description."""
        requirements = []
        
        # Look for requirements section
        patterns = [
            r'(?:requirements|qualifications|what you\'ll need)[:\s]+(.*?)(?:\n\n|\Z)',
            r'(?:required|must have)[:\s]+(.*?)(?:\n\n|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(1)
                # Split by bullet points or newlines
                items = re.split(r'[•\-\n]', section)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 10:  # Avoid single words
                        requirements.append(item)
                break
        
        return requirements
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills mentioned in description."""
        common_skills = [
            'python', 'javascript', 'typescript', 'java', 'c\\+\\+', 'c#', 'ruby', 'php', 'go', 'rust',
            'react', 'angular', 'vue', 'node\\.js', 'django', 'flask', 'fastapi', 'spring',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins',
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'git', 'github', 'gitlab', 'jira'
        ]
        
        found_skills = []
        desc_lower = description.lower()
        
        for skill in common_skills:
            if re.search(r'\b' + skill + r'\b', desc_lower):
                # Clean up the skill name (remove escape chars)
                clean_skill = skill.replace('\\+\\+', '++').replace('\\.', '.')
                found_skills.append(clean_skill)
        
        return list(set(found_skills))