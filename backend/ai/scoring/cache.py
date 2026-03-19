"""Scoring cache management."""

import hashlib
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from ...core.cache import cache


class ScoringCache:
    """Cache manager for job scores."""
    
    def __init__(self, ttl_days: int = 7):
        self.ttl = ttl_days * 86400  # Convert to seconds
    
    def _generate_key(self, job_id: int, profile_id: int, context: str = "") -> str:
        """Generate cache key from inputs."""
        base = f"{job_id}:{profile_id}:{context}"
        hash_obj = hashlib.sha256(base.encode())
        return f"score:{hash_obj.hexdigest()[:16]}"
    
    async def get_score(self, job_id: int, profile_id: int) -> Optional[Dict[str, Any]]:
        """Get cached score if available."""
        key = self._generate_key(job_id, profile_id)
        cached = await cache.get(key)
        
        if cached:
            return json.loads(cached)
        return None
    
    async def set_score(self, job_id: int, profile_id: int, score_data: Dict[str, Any]):
        """Cache score data."""
        key = self._generate_key(job_id, profile_id)
        await cache.set(
            key,
            json.dumps(score_data),
            ttl=self.ttl
        )
    
    async def invalidate(self, job_id: int, profile_id: int):
        """Invalidate cache for a specific job-profile pair."""
        key = self._generate_key(job_id, profile_id)
        await cache.delete(key)
    
    async def get_or_score(self, job_id: int, profile_id: int, 
                           scoring_func, **kwargs) -> Dict[str, Any]:
        """Get cached score or compute and cache new one."""
        cached = await self.get_score(job_id, profile_id)
        
        if cached:
            return cached
        
        score_data = await scoring_func(**kwargs)
        await self.set_score(job_id, profile_id, score_data)
        
        return score_data
    
    async def get_batch_scores(self, job_ids: List[int], profile_id: int) -> Dict[int, Optional[Dict]]:
        """Get scores for multiple jobs at once."""
        keys = [self._generate_key(job_id, profile_id) for job_id in job_ids]
        
        # Use Redis mget for efficiency
        cached_values = await cache.mget(keys)
        
        results = {}
        for job_id, cached in zip(job_ids, cached_values):
            if cached:
                results[job_id] = json.loads(cached)
            else:
                results[job_id] = None
        
        return results