"""Rate limiting utilities."""

import time
import asyncio
from typing import Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta


class RateLimiter:
    """Rate limiter for API calls and scraping."""
    
    def __init__(self):
        self.rates: Dict[str, list] = defaultdict(list)
        self.default_rate = 60  # requests per minute
        self.delays: Dict[str, float] = defaultdict(float)
    
    def check_rate(self, key: str, rate: Optional[int] = None) -> bool:
        """Check if rate limit is exceeded."""
        now = time.time()
        rate_limit = rate or self.default_rate
        
        # Clean old entries
        self.rates[key] = [t for t in self.rates[key] if now - t < 60]
        
        # Check rate
        if len(self.rates[key]) >= rate_limit:
            return False
        
        # Add request
        self.rates[key].append(now)
        return True
    
    async def wait_if_needed(self, key: str, rate: Optional[int] = None):
        """Wait if rate limit is exceeded."""
        while not self.check_rate(key, rate):
            await asyncio.sleep(1)
    
    def get_delay(self, key: str) -> float:
        """Get current delay for key."""
        return self.delays.get(key, 1.0)
    
    def increase_delay(self, key: str, factor: float = 2.0):
        """Increase delay (for backoff)."""
        current = self.delays.get(key, 1.0)
        self.delays[key] = min(current * factor, 3600)  # Max 1 hour
    
    def reset_delay(self, key: str):
        """Reset delay to default."""
        self.delays[key] = 1.0


class TokenBucket:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from bucket."""
        async with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_refill = now


rate_limiter = RateLimiter()