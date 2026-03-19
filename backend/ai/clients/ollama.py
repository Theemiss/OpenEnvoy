"""Ollama local model client."""

import time
import httpx
import json
from typing import Dict, Any, Optional

from .base import AIClient, AIResponse


class OllamaClient(AIClient):
    """Client for local Ollama models."""
    
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        super().__init__(model_name)
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text from prompt."""
        start_time = time.time()
        
        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 1000)
                }
            }
        )
        response.raise_for_status()
        data = response.json()
        
        latency = time.time() - start_time
        
        # Estimate token counts (rough approximation)
        prompt_tokens = len(prompt.split())
        completion_tokens = len(data["response"].split())
        
        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }
        
        return AIResponse(
            content=data["response"],
            model=self.model_name,
            usage=usage,
            cost=0.0,  # Free for local models
            latency=latency
        )
    
    async def generate_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate JSON response."""
        prompt_with_instruction = f"""
        {prompt}
        
        Provide your response as a valid JSON object with no additional text.
        """
        
        response = await self.generate(prompt_with_instruction, **kwargs)
        
        # Try to extract JSON from response
        text = response.content
        try:
            # Find JSON object in text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # If JSON parsing fails, return empty dict
        return {}
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()