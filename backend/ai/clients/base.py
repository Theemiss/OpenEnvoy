"""Base AI client interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class AIResponse:
    """Standardized AI response format."""
    
    content: str
    model: str
    usage: Dict[str, int]
    cost: float
    latency: float


class AIClient(ABC):
    """Base class for AI model clients."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    async def generate_with_json(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate JSON response."""
        pass
    
    def calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate cost based on token usage."""
        # To be implemented by specific clients
        return 0.0