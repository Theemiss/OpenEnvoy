"""Redis cache client."""

import json
from typing import Any, Optional, List
import redis.asyncio as redis

from .config import settings


class CacheClient:
    """Redis cache client wrapper."""
    
    def __init__(self):
        self.client = None
    
    async def initialize(self):
        """Initialize Redis connection."""
        self.client = await redis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True
        )
    
    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.client:
            await self.initialize()
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.client:
            await self.initialize()
        return await self.client.set(key, value, ex=ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            await self.initialize()
        return await self.client.delete(key) > 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.client:
            await self.initialize()
        return await self.client.exists(key) > 0
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key."""
        if not self.client:
            await self.initialize()
        return await self.client.expire(key, ttl)
    
    async def incr(self, key: str) -> int:
        """Increment counter."""
        if not self.client:
            await self.initialize()
        return await self.client.incr(key)
    
    async def lpush(self, key: str, *values: str) -> int:
        """Push to list from left."""
        if not self.client:
            await self.initialize()
        return await self.client.lpush(key, *values)
    
    async def rpush(self, key: str, *values: str) -> int:
        """Push to list from right."""
        if not self.client:
            await self.initialize()
        return await self.client.rpush(key, *values)
    
    async def lpop(self, key: str) -> Optional[str]:
        """Pop from list from left."""
        if not self.client:
            await self.initialize()
        return await self.client.lpop(key)
    
    async def rpop(self, key: str) -> Optional[str]:
        """Pop from list from right."""
        if not self.client:
            await self.initialize()
        return await self.client.rpop(key)
    
    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Get range from list."""
        if not self.client:
            await self.initialize()
        return await self.client.lrange(key, start, end)
    
    async def llen(self, key: str) -> int:
        """Get list length."""
        if not self.client:
            await self.initialize()
        return await self.client.llen(key)
    
    async def lrem(self, key: str, count: int, value: str) -> int:
        """Remove from list."""
        if not self.client:
            await self.initialize()
        return await self.client.lrem(key, count, value)
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim list."""
        if not self.client:
            await self.initialize()
        return await self.client.ltrim(key, start, end)
    
    async def hset(self, key: str, field: str, value: str) -> int:
        """Set hash field."""
        if not self.client:
            await self.initialize()
        return await self.client.hset(key, field, value)
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field."""
        if not self.client:
            await self.initialize()
        return await self.client.hget(key, field)
    
    async def hgetall(self, key: str) -> dict:
        """Get all hash fields."""
        if not self.client:
            await self.initialize()
        return await self.client.hgetall(key)
    
    async def hdel(self, key: str, *fields: str) -> int:
        """Delete hash fields."""
        if not self.client:
            await self.initialize()
        return await self.client.hdel(key, *fields)
    
    async def hincrbyfloat(self, key: str, field: str, increment: float) -> float:
        """Increment hash field by float."""
        if not self.client:
            await self.initialize()
        return await self.client.hincrbyfloat(key, field, increment)
    
    async def hkeys(self, key: str) -> List[str]:
        """Get all hash keys."""
        if not self.client:
            await self.initialize()
        return await self.client.hkeys(key)
    
    # Redis Set operations (for deduplication)
    async def sismember(self, key: str, value: str) -> bool:
        """Check if value is a member of set."""
        if not self.client:
            await self.initialize()
        return await self.client.sismember(key, value)
    
    async def sadd(self, key: str, *values: str) -> int:
        """Add values to set."""
        if not self.client:
            await self.initialize()
        return await self.client.sadd(key, *values)
    
    async def scard(self, key: str) -> int:
        """Get cardinality of set."""
        if not self.client:
            await self.initialize()
        return await self.client.scard(key)
    
    async def srem(self, key: str, *values: str) -> int:
        """Remove values from set."""
        if not self.client:
            await self.initialize()
        return await self.client.srem(key, *values)
    
    async def smembers(self, key: str) -> set:
        """Get all members of set."""
        if not self.client:
            await self.initialize()
        return await self.client.smembers(key)
    
    async def ping(self) -> bool:
        """Get all hash keys."""
        if not self.client:
            await self.initialize()
        return await self.client.hkeys(key)
    
    async def ping(self) -> bool:
        """Ping Redis server."""
        if not self.client:
            await self.initialize()
        return await self.client.ping()
    
    async def flushall(self) -> bool:
        """Flush all databases."""
        if not self.client:
            await self.initialize()
        return await self.client.flushall()


cache = CacheClient()