#!/usr/bin/env python3
"""Scraper worker for continuous job collection."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.scrapers.pipeline import ScrapingPipeline
from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.core.alerting import alert_manager

logger = logging.getLogger(__name__)


async def run_scraper_cycle():
    """Run a single scraping cycle."""
    pipeline = ScrapingPipeline()
    
    try:
        logger.info("Starting scraping cycle")
        
        # Run all scrapers
        results = await pipeline.run_all(
            keywords=settings.SCRAPER_KEYWORDS,
            location=settings.SCRAPER_LOCATION
        )
        
        # Process new jobs
        queued = await pipeline.process_new_jobs()
        
        logger.info(f"Scraping cycle complete: {results}, queued: {queued}")
        
        # Send summary alert if configured
        total_jobs = sum(results.values())
        if total_jobs > 0:
            await alert_manager.send_alert(
                title="Scraping Cycle Complete",
                message=f"Found {total_jobs} new jobs, queued {queued} for processing",
                severity="info",
                metadata={"results": results, "queued": queued}
            )
        
    except Exception as e:
        logger.error(f"Scraping cycle failed: {str(e)}")
        await alert_manager.send_alert(
            title="Scraping Cycle Failed",
            message=str(e),
            severity="error",
            metadata={"error": str(e)}
        )
    finally:
        await pipeline.close()


async def main():
    """Main worker loop."""
    setup_logging("scraper_worker")
    
    logger.info("Starting scraper worker")
    
    interval = settings.SCRAPE_INTERVAL_HOURS * 3600
    
    while True:
        try:
            await run_scraper_cycle()
        except Exception as e:
            logger.error(f"Unhandled error in scraper worker: {str(e)}")
        
        logger.info(f"Waiting {interval} seconds until next scrape")
        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())