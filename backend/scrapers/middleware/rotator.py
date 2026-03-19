"""IP and user agent rotation for scraping."""

import random
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta


class ProxyRotator:
    """Rotate proxies for scraping."""
    
    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies or []
        self.current_index = 0
        self.failed_proxies = {}
        self.proxy_stats = {}
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation."""
        if not self.proxies:
            return None
        
        # Filter out failed proxies
        available = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not available:
            # Reset failed proxies after cooldown
            self.failed_proxies = {}
            available = self.proxies
        
        proxy = random.choice(available)
        
        # Update stats
        self.proxy_stats[proxy] = self.proxy_stats.get(proxy, 0) + 1
        
        return proxy
    
    def mark_failed(self, proxy: str):
        """Mark a proxy as failed."""
        self.failed_proxies[proxy] = datetime.now()
        
        # Clean up old failures after 1 hour
        cutoff = datetime.now() - timedelta(hours=1)
        self.failed_proxies = {
            p: t for p, t in self.failed_proxies.items() 
            if t > cutoff
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get proxy usage statistics."""
        return self.proxy_stats


class UserAgentRotator:
    """Rotate user agents for scraping."""
    
    USER_AGENTS = [
        # Chrome
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        
        # Firefox
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/121.0",
        
        # Safari
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        
        # Edge
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    ]
    
    def __init__(self):
        self.last_used = {}
        self.current = random.choice(self.USER_AGENTS)
    
    def get(self) -> str:
        """Get a user agent, rotating occasionally."""
        # Rotate every 10 requests on average
        if random.random() < 0.1:
            self.current = random.choice(self.USER_AGENTS)
        
        return self.current
    
    def get_for_domain(self, domain: str) -> str:
        """Get consistent user agent for a domain."""
        # Use same UA for same domain to avoid detection
        if domain not in self.last_used or random.random() < 0.2:
            self.last_used[domain] = random.choice(self.USER_AGENTS)
        
        return self.last_used[domain]