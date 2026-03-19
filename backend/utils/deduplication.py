"""Deduplication utilities for jobs and applications."""

import hashlib
from typing import List, Dict, Any, Set, Optional
from datetime import datetime, timedelta

from ..core.cache import cache


class Deduplicator:
    """Deduplicate jobs and other entities."""
    
    def __init__(self):
        self.seen_urls_key = "dedup:urls"
        self.seen_hashes_key = "dedup:hashes"
    
    async def is_duplicate_url(self, url: str) -> bool:
        """Check if URL has been seen before."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return await cache.sismember(self.seen_urls_key, url_hash)
    
    async def mark_url_seen(self, url: str, ttl_days: int = 90):
        """Mark URL as seen."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        await cache.sadd(self.seen_urls_key, url_hash)
        
        # Set expiry if first item
        if await cache.scard(self.seen_urls_key) == 1:
            await cache.expire(self.seen_urls_key, ttl_days * 86400)
    
    async def find_duplicate_job(self, job_data: Dict[str, Any]) -> Optional[int]:
        """Find duplicate job by hash."""
        job_hash = self._generate_job_hash(job_data)
        
        # Check if hash exists
        existing_id = await cache.hget(self.seen_hashes_key, job_hash)
        if existing_id:
            return int(existing_id)
        
        return None
    
    async def record_job_hash(self, job_id: int, job_data: Dict[str, Any]):
        """Record job hash for future deduplication."""
        job_hash = self._generate_job_hash(job_data)
        await cache.hset(self.seen_hashes_key, job_hash, str(job_id))
    
    def _generate_job_hash(self, job_data: Dict[str, Any]) -> str:
        """Generate hash from job data."""
        # Normalize fields
        title = (job_data.get("title") or "").lower().strip()
        company = (job_data.get("company") or "").lower().strip()
        
        # Get description snippet
        desc = job_data.get("description") or ""
        desc_snippet = desc[:200].lower().strip()
        
        # Create hash
        hash_input = f"{title}|{company}|{desc_snippet}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    async def cleanup_old_entries(self, days: int = 90):
        """Clean up old deduplication entries."""
        # URLs set has TTL, so no need to clean manually
        # For hashes, we can't easily expire individual fields
        # This is a limitation of using Redis hashes
        pass
    
    async def batch_check_urls(self, urls: List[str]) -> List[bool]:
        """Check multiple URLs for duplicates."""
        results = []
        for url in urls:
            is_dup = await self.is_duplicate_url(url)
            results.append(is_dup)
        return results