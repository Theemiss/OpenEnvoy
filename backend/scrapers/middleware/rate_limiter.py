"""Rate limiting for scrapers."""

import asyncio
import time
from typing import Dict, Optional, List
from collections import defaultdict


class RateLimiter:
    """Rate limiter for scraping requests."""
    
    def __init__(self):
        self.request_times: Dict[str, list] = defaultdict(list)
        self.delays: Dict[str, float] = defaultdict(lambda: 1.0)
        self.max_requests_per_minute = 30
        self.max_consecutive_failures = 3
        self.failure_counts: Dict[str, int] = defaultdict(int)
    
    async def wait_if_needed(self, source: str):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Clean old entries
        self.request_times[source] = [
            t for t in self.request_times[source] 
            if now - t < 60
        ]
        
        # Check rate
        if len(self.request_times[source]) >= self.max_requests_per_minute:
            # Wait until oldest request expires
            oldest = min(self.request_times[source])
            wait_time = 60 - (now - oldest)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Apply custom delay
        delay = self.delays.get(source, 1.0)
        if delay > 1.0:
            await asyncio.sleep(delay)
        
        # Record request
        self.request_times[source].append(time.time())
    
    def record_success(self, source: str):
        """Record successful request."""
        self.failure_counts[source] = max(0, self.failure_counts[source] - 1)
        
        # Decrease delay on success
        if self.delays[source] > 1.0:
            self.delays[source] = max(1.0, self.delays[source] * 0.5)
    
    def record_failure(self, source: str):
        """Record failed request."""
        self.failure_counts[source] += 1
        
        # Increase delay on failures
        if self.failure_counts[source] >= self.max_consecutive_failures:
            self.delays[source] = min(
                self.delays[source] * 2,
                3600  # Max 1 hour
            )
            self.failure_counts[source] = 0
    
    def get_delay(self, source: str) -> float:
        """Get current delay for source."""
        return self.delays.get(source, 1.0)
    
    def reset_delay(self, source: str):
        """Reset delay for source."""
        self.delays[source] = 1.0
        self.failure_counts[source] = 0
    
    async def batch_wait(self, sources: List[str]):
        """Wait for multiple sources."""
        for source in sources:
            await self.wait_if_needed(source)


rate_limiter = RateLimiter()