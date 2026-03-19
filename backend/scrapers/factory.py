"""Scraper factory for creating configured scrapers."""

from typing import Dict, Type, Optional, List
from .base import BaseScraper

from ..core.config import settings


class ScraperFactory:
    """Factory for creating job scrapers."""

    _scrapers_cache: Dict[str, Type[BaseScraper]] = {}

    @classmethod
    def _get_scraper_class(cls, source: str) -> Type[BaseScraper]:
        """Lazy load scraper class."""
        if source in cls._scrapers_cache:
            return cls._scrapers_cache[source]

        # Import lazily to avoid circular imports
        from .sources import (
            LinkedInScraper,
            AdzunaScraper,
            RemotiveScraper,
            ArbeitnowScraper,
            RSSJobScraper,
        )

        scrapers = {
            "linkedin": LinkedInScraper,
            "adzuna": AdzunaScraper,
            "remotive": RemotiveScraper,
            "arbeitnow": ArbeitnowScraper,
        }

        cls._scrapers_cache.update(scrapers)
        return cls._scrapers_cache[source]

    @classmethod
    def create_scraper(cls, source: str, **kwargs) -> Optional[BaseScraper]:
        """Create a scraper instance for the given source."""

        scraper_class = cls._get_scraper_class(source)

        if source == "adzuna":
            return scraper_class(
                app_id=settings.ADZUNA_APP_ID, app_key=settings.ADZUNA_API_KEY
            )
        elif source == "linkedin":
            return scraper_class(headless=kwargs.get("headless", True))
        else:
            return scraper_class()

    @classmethod
    def create_rss_scraper(cls, feed_urls: List[str]):
        """Create an RSS scraper with multiple feeds."""
        from .sources import RSSJobScraper

        return RSSJobScraper(feed_urls, source_name="rss")

    @classmethod
    def get_all_scrapers(cls, **kwargs) -> Dict[str, BaseScraper]:
        """Create instances of all configured scrapers."""
        scrapers = {}

        if settings.LINKEDIN_ENABLED:
            scrapers["linkedin"] = cls.create_scraper("linkedin", **kwargs)

        if settings.ADZUNA_ENABLED and settings.ADZUNA_APP_ID:
            scrapers["adzuna"] = cls.create_scraper("adzuna")

        if settings.REMOTIVE_ENABLED:
            scrapers["remotive"] = cls.create_scraper("remotive")

        if settings.ARBEITNOW_ENABLED:
            scrapers["arbeitnow"] = cls.create_scraper("arbeitnow")

        if settings.RSS_FEEDS:
            scrapers["rss"] = cls.create_rss_scraper(settings.RSS_FEEDS)

        return scrapers
