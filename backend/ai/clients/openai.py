"""OpenAI API client."""

import time
import tiktoken
from typing import Dict, Any, Optional, List
import openai
from openai import AsyncOpenAI

from .base import AIClient, AIResponse
from ...core.config import settings


class OpenAIClient(AIClient):
    """Client for OpenAI models."""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        super().__init__(model_name)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
        self.encoder = tiktoken.encoding_for_model("gpt-4")  # Use same encoder
    
    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text from prompt."""
        start_time = time.time()
        
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1000),
            **kwargs
        )
        
        latency = time.time() - start_time
        
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        
        cost = self.calculate_cost(usage)
        
        return AIResponse(
            content=response.choices[0].message.content,
            model=self.model_name,
            usage=usage,
            cost=cost,
            latency=latency
        )
    
    async def generate_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate JSON response using response_format."""
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=kwargs.get("temperature", 0.7),
            **kwargs
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    def calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate cost based on token usage."""
        if self.model_name not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[self.model_name]
        input_cost = (usage["prompt_tokens"] / 1000) * pricing["input"]
        output_cost = (usage["completion_tokens"] / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))