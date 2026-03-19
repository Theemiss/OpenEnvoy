"""Anthropic Claude API client."""

import time
from typing import Dict, Any, Optional
import anthropic

from .base import AIClient, AIResponse
from ...core.config import settings


class AnthropicClient(AIClient):
    """Client for Anthropic Claude models."""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }
    
    def __init__(self, model_name: str = "claude-3-haiku"):
        super().__init__(model_name)
        self.client = anthropic.AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY.get_secret_value()
        )
    
    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text from prompt."""
        start_time = time.time()
        
        response = await self.client.messages.create(
            model=self.model_name,
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.7),
            messages=[{"role": "user", "content": prompt}]
        )
        
        latency = time.time() - start_time
        
        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens
        }
        
        cost = self.calculate_cost(usage)
        
        return AIResponse(
            content=response.content[0].text,
            model=self.model_name,
            usage=usage,
            cost=cost,
            latency=latency
        )
    
    async def generate_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate JSON response."""
        prompt_with_instruction = f"""
        {prompt}
        
        Provide your response as a valid JSON object.
        """
        
        response = await self.generate(prompt_with_instruction, **kwargs)
        
        import json
        return json.loads(response.content)
    
    def calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate cost based on token usage."""
        if self.model_name not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[self.model_name]
        input_cost = (usage["prompt_tokens"] / 1000) * pricing["input"]
        output_cost = (usage["completion_tokens"] / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 6)