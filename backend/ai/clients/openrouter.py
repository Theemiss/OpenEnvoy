"""OpenRouter API client - Free tier AI models."""

import time
import tiktoken
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI

from .base import AIClient, AIResponse
from ...core.config import settings


class OpenRouterClient(AIClient):
    """Client for OpenRouter free tier models.

    OpenRouter provides access to various free models including:
    - google/gemini-2.0-flash-thinking-exp-01-21
    - deepseek/deepseek-chat-v3-0324
    - qwen/qwen2.5-72b-instruct
    - anthropic/claude-3.5-haiku
    - mistralai/mistral-nemo
    """

    # OpenRouter base URL
    BASE_URL = "https://openrouter.ai/api/v1"

    # Free model pricing (OpenRouter free models - $0 cost)
    PRICING = {
        # Free tier models - no cost
        "google/gemini-2.0-flash-thinking-exp-01-21": {"input": 0.0, "output": 0.0},
        "deepseek/deepseek-chat-v3-0324": {"input": 0.0, "output": 0.0},
        "qwen/qwen2.5-72b-instruct": {"input": 0.0, "output": 0.0},
        "anthropic/claude-3.5-haiku": {"input": 0.0, "output": 0.0},
        "mistralai/mistral-nemo": {"input": 0.0, "output": 0.0},
        # Other popular free models
        "google/gemini-pro-1.5-exp": {"input": 0.0, "output": 0.0},
        "meta-llama/llama-3-8b-instruct": {"input": 0.0, "output": 0.0},
        "microsoft_phi-3-mini-128k-instruct": {"input": 0.0, "output": 0.0},
    }

    # Default free model
    DEFAULT_MODEL = "google/gemini-2.0-flash-thinking-exp-01-21"

    def __init__(self, model_name: str = None):
        model = model_name or self.DEFAULT_MODEL
        super().__init__(model)

        # Initialize OpenAI-compatible client with OpenRouter URL
        self.client = AsyncOpenAI(
            base_url=self.BASE_URL,
            api_key=settings.OPENROUTER_API_KEY.get_secret_value(),
        )
        self.encoder = tiktoken.encoding_for_model("gpt-4")

    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text from prompt."""
        start_time = time.time()

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000),
            **kwargs,
        )

        latency = time.time() - start_time

        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

        cost = self.calculate_cost(usage)

        return AIResponse(
            content=response.choices[0].message.content,
            model=self.model_name,
            usage=usage,
            cost=cost,
            latency=latency,
        )

    async def generate_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate JSON response using response_format."""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=kwargs.get("temperature", 0.7),
            **kwargs,
        )

        import json

        return json.loads(response.choices[0].message.content)

    def calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate cost based on token usage.

        Free models have $0 cost.
        """
        if self.model_name not in self.PRICING:
            # Default to $0 for unknown models (likely free tier)
            return 0.0

        pricing = self.PRICING[self.model_name]
        input_cost = (usage["prompt_tokens"] / 1000) * pricing["input"]
        output_cost = (usage["completion_tokens"] / 1000) * pricing["output"]

        return round(input_cost + output_cost, 6)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
