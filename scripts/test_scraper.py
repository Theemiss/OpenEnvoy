#!/usr/bin/env python3
"""Test script for job scrapers."""

import asyncio
import argparse
import sys
from pathlib import Path
from pprint import pprint

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.scrapers.factory import ScraperFactory
from backend.core.config import settings


async def test_linkedin(keywords: list, location: str):
    """Test LinkedIn scraper."""
    print(f"\n🔍 Testing LinkedIn scraper...")
    print(f"Keywords: {keywords}")
    print(f"Location: {location}")
    
    scraper = ScraperFactory.create_scraper("linkedin", headless=False)
    
    try:
        jobs = await scraper.scrape(keywords=keywords, location=location, max_pages=1)
        print(f"\n✅ Found {len(jobs)} jobs")
        
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n--- Job {i} ---")
            print(f"Title: {job.title}")
            print(f"Company: {job.company}")
            print(f"Location: {job.location}")
            print(f"URL: {job.url}")
            
    finally:
        await scraper.close()


async def test_adzuna(keywords: list, location: str):
    """Test Adzuna scraper."""
    print(f"\n🔍 Testing Adzuna scraper...")
    
    if not settings.ADZUNA_APP_ID:
        print("❌ Adzuna API not configured")
        return
    
    scraper = ScraperFactory.create_scraper("adzuna")
    
    jobs = await scraper.scrape(keywords=keywords, location=location, max_pages=1)
    
    print(f"\n✅ Found {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n--- Job {i} ---")
        print(f"Title: {job.title}")
        print(f"Company: {job.company}")
        print(f"Location: {job.location}")
        print(f"Salary: {job.salary_min}-{job.salary_max} {job.salary_currency}")


async def test_remotive(category: str = "software-development"):
    """Test Remotive scraper."""
    print(f"\n🔍 Testing Remotive scraper...")
    
    scraper = ScraperFactory.create_scraper("remotive")
    
    jobs = await scraper.scrape(category=category, limit=10)
    
    print(f"\n✅ Found {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n--- Job {i} ---")
        print(f"Title: {job.title}")
        print(f"Company: {job.company}")
        print(f"Location: {job.location}")
        print(f"Skills: {job.skills[:5] if job.skills else 'None'}")


async def test_arbeitnow():
    """Test Arbeitnow scraper."""
    print(f"\n🔍 Testing Arbeitnow scraper...")
    
    scraper = ScraperFactory.create_scraper("arbeitnow")
    
    jobs = await scraper.scrape(limit=10)
    
    print(f"\n✅ Found {len(jobs)} jobs")
    
    for i, job in enumerate(jobs[:3], 1):
        print(f"\n--- Job {i} ---")
        print(f"Title: {job.title}")
        print(f"Company: {job.company}")
        print(f"Location: {job.location}")
        print(f"Salary: {job.salary_min}-{job.salary_max} EUR")


async def test_all(keywords: list, location: str):
    """Test all configured scrapers."""
    print("=" * 50)
    print("Testing all job scrapers")
    print("=" * 50)
    
    await test_linkedin(keywords, location)
    print("\n" + "-" * 50)
    
    await test_adzuna(keywords, location)
    print("\n" + "-" * 50)
    
    await test_remotive()
    print("\n" + "-" * 50)
    
    await test_arbeitnow()


def main():
    parser = argparse.ArgumentParser(description="Test job scrapers")
    parser.add_argument("--source", choices=["linkedin", "adzuna", "remotive", "arbeitnow", "all"],
                       default="all", help="Scraper to test")
    parser.add_argument("--keywords", nargs="+", default=["python", "developer"],
                       help="Search keywords")
    parser.add_argument("--location", default="United States",
                       help="Location to search")
    
    args = parser.parse_args()
    
    if args.source == "all":
        asyncio.run(test_all(args.keywords, args.location))
    elif args.source == "linkedin":
        asyncio.run(test_linkedin(args.keywords, args.location))
    elif args.source == "adzuna":
        asyncio.run(test_adzuna(args.keywords, args.location))
    elif args.source == "remotive":
        asyncio.run(test_remotive())
    elif args.source == "arbeitnow":
        asyncio.run(test_arbeitnow())


if __name__ == "__main__":
    main()