"""Hashing utilities for caching and deduplication."""

import hashlib
import json
from typing import Any


def hash_content(content: Any) -> str:
    """Generate SHA256 hash of content."""
    if not isinstance(content, str):
        content = json.dumps(content, sort_keys=True)
    
    return hashlib.sha256(content.encode()).hexdigest()


def generate_cache_key(*parts: Any) -> str:
    """Generate cache key from parts."""
    combined = ":".join(str(p) for p in parts)
    return f"cache:{hashlib.md5(combined.encode()).hexdigest()[:16]}"


def hash_url(url: str) -> str:
    """Generate hash from URL for deduplication."""
    # Normalize URL
    url = url.split('?')[0]  # Remove query parameters
    url = url.rstrip('/')  # Remove trailing slash
    
    return hashlib.md5(url.encode()).hexdigest()


def hash_job(job_data: dict) -> str:
    """Generate hash for job deduplication."""
    # Use title, company, and description snippet
    key_parts = [
        job_data.get("title", ""),
        job_data.get("company", ""),
        job_data.get("description", "")[:200]  # First 200 chars
    ]
    
    return hash_content("|".join(key_parts))