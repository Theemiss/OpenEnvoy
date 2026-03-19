"""Fallback chain for AI providers - tries providers in order until one succeeds."""

import logging
from typing import Dict, Any, Optional, List

from .base import AIClient, AIResponse
from ...core.config import settings

logger = logging.getLogger(__name__)


class AllProvidersFailedError(Exception):
    """Raised when all providers in the fallback chain fail."""

    pass


class FallbackChain(AIClient):
    """Try multiple AI providers in sequence until one succeeds.

    Usage:
        chain = FallbackChain([
            ("openai", "gpt-4o-mini"),
            ("anthropic", "claude-3-haiku"),
            ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21"),
        ])
        response = await chain.generate(prompt)
    """

    def __init__(self, providers: List[tuple]):
        """Initialize with list of (provider_name, model_name) tuples.

        Providers are tried in order. First available provider is used.

        Args:
            providers: List of (provider_type, model_name) tuples.
                      provider_type: "openai", "anthropic", "ollama", "openrouter"
        """
        self.providers = providers
        self.clients: List[AIClient] = []
        self._build_clients()

        # Use first client for model_name (for compatibility)
        super().__init__(providers[0][1] if providers else "")

    def _build_clients(self):
        """Build client instances for available providers."""
        # Lazy imports to avoid circular dependencies
        from .openai import OpenAIClient
        from .anthropic import AnthropicClient
        from .ollama import OllamaClient
        from .openrouter import OpenRouterClient

        provider_map = {
            "openai": (OpenAIClient, lambda k: settings.OPENAI_API_KEY),
            "anthropic": (AnthropicClient, lambda k: settings.ANTHROPIC_API_KEY),
            "ollama": (
                OllamaClient,
                lambda k: True,
            ),  # Ollama is local, always available
            "openrouter": (OpenRouterClient, lambda k: settings.OPENROUTER_API_KEY),
        }

        for provider_type, model_name in self.providers:
            if provider_type not in provider_map:
                logger.warning(f"Unknown provider type: {provider_type}")
                continue

            client_class, key_check = provider_map[provider_type]

            # Check if API key is available (skip for local providers like Ollama)
            if key_check(None) is not True and not key_check(None):
                logger.debug(f"Skipping {provider_type} - no API key configured")
                continue

            try:
                client = client_class(model_name)
                self.clients.append(client)
                logger.info(f"Added {provider_type}/{model_name} to fallback chain")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize {provider_type}/{model_name}: {e}"
                )

        if not self.clients:
            logger.warning("No AI providers available in fallback chain!")

    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Try each client until one succeeds."""
        errors = []

        for client in self.clients:
            try:
                response = await client.generate(prompt, **kwargs)
                logger.info(f"Used {client.__class__.__name__}/{client.model_name}")
                return response
            except Exception as e:
                logger.warning(f"{client.__class__.__name__} failed: {e}")
                errors.append(f"{client.__class__.__name__}: {str(e)}")

        raise AllProvidersFailedError(
            f"All {len(self.clients)} providers failed. Errors: {'; '.join(errors)}"
        )

    async def generate_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Try each client until one succeeds with JSON response."""
        errors = []

        for client in self.clients:
            try:
                # Try with JSON format if client supports it
                if hasattr(client, "generate_with_json"):
                    response = await client.generate_with_json(prompt, **kwargs)
                else:
                    # Fall back to regular generate and parse
                    response = await client.generate(prompt, **kwargs)
                    import json

                    response = json.loads(response.content)

                logger.info(
                    f"Used {client.__class__.__name__}/{client.model_name} for JSON generation"
                )
                return response
            except Exception as e:
                logger.warning(
                    f"{client.__class__.__name__} JSON generation failed: {e}"
                )
                errors.append(f"{client.__class__.__name__}: {str(e)}")

        raise AllProvidersFailedError(
            f"All providers failed for JSON generation. Errors: {'; '.join(errors)}"
        )

    def calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate cost - returns 0 since cost varies by provider."""
        return 0.0


# Convenience factory functions for common fallback chains


def cheap_model_chain() -> FallbackChain:
    """Create a fallback chain for cheap models.

    Priority: OpenAI gpt-4o-mini → OpenRouter free models
    """
    providers = [
        ("openai", "gpt-4o-mini"),
        ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21"),
    ]
    return FallbackChain(providers)


def premium_model_chain() -> FallbackChain:
    """Create a fallback chain for premium models.

    Priority: OpenAI gpt-4o → Anthropic → OpenRouter
    """
    providers = [
        ("openai", "gpt-4o"),
        ("anthropic", "claude-3-sonnet"),
        ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21"),
    ]
    return FallbackChain(providers)


def free_model_chain() -> FallbackChain:
    """Create a chain with only free models.

    Priority: Ollama (local) → OpenRouter free tier
    """
    providers = [
        ("ollama", "llama3"),
        ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21"),
    ]
    return FallbackChain(providers)
