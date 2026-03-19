"""AI model configuration service - reads from DB and builds client chains."""

import asyncio
import logging
from typing import Optional, Dict, Any, List

from ..models.ai_model_config import AIModelConfig
from ..models.user import User
from ..core.database import db_manager
from ..core.config import settings
from ..ai.clients.fallback import FallbackChain

logger = logging.getLogger(__name__)


class AIConfigService:
    """Service for loading AI model configs from DB and building client chains.

    Caches configs per profile with TTL. Call clear_cache() to invalidate.
    """

    def __init__(self):
        self._cache: Dict[int, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._cache_ttl: int = 300  # 5 minutes

    async def get_default_for_tier(
        self, profile_id: int, tier: str
    ) -> Optional[AIModelConfig]:
        """Get the default AI model config for a given tier."""
        configs = await self._get_configs(profile_id)
        for config in configs:
            if config.tier == tier and config.is_default and config.is_active:
                return config
        # Fall back to first active config for tier
        for config in configs:
            if config.tier == tier and config.is_active:
                return config
        return None

    async def get_provider_for_tier(
        self, profile_id: int, tier: str
    ) -> Optional[tuple[str, str]]:
        """Get (provider, model_name) tuple for the default config of a tier."""
        config = await self.get_default_for_tier(profile_id, tier)
        if config:
            return (config.provider, config.model_name)
        return None

    async def build_chain_for_tier(self, profile_id: int, tier: str) -> FallbackChain:
        """Build a FallbackChain from the profile's configured models."""
        configs = await self._get_configs(profile_id)

        # Filter to matching tier and active
        tier_configs = [c for c in configs if c.tier == tier and c.is_active]

        if not tier_configs:
            # Return default hardcoded chain
            return self._default_chain(tier)

        # Build provider list
        providers = [(c.provider, c.model_name) for c in tier_configs]

        # Add OpenRouter as final fallback if not already configured
        has_openrouter = any(p[0] == "openrouter" for p in providers)
        if not has_openrouter:
            providers.append(
                ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21")
            )

        return FallbackChain(providers)

    def _default_chain(self, tier: str) -> FallbackChain:
        """Return the default hardcoded chain."""
        if tier == "cheap":
            return FallbackChain(
                [
                    ("openai", "gpt-4o-mini"),
                    ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21"),
                ]
            )
        else:  # premium
            return FallbackChain(
                [
                    ("openai", "gpt-4o"),
                    ("anthropic", "claude-3-sonnet"),
                    ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21"),
                ]
            )

    async def _get_configs(self, profile_id: int) -> List[AIModelConfig]:
        """Get configs from cache or DB."""
        import time

        now = time.time()

        async with self._lock:
            if profile_id in self._cache:
                cached = self._cache[profile_id]
                if now - cached["fetched_at"] < self._cache_ttl:
                    return cached["configs"]

            # Fetch from DB
            async with db_manager.session() as session:
                from sqlalchemy import select

                stmt = select(AIModelConfig).where(
                    AIModelConfig.profile_id == profile_id,
                    AIModelConfig.is_active == True,
                )
                result = await session.execute(stmt)
                configs = list(result.scalars().all())

            self._cache[profile_id] = {
                "configs": configs,
                "fetched_at": now,
            }
            return configs

    def clear_cache(self, profile_id: int):
        """Clear cache for a profile."""
        self._cache.pop(profile_id, None)


# Singleton instance
ai_config_service = AIConfigService()
