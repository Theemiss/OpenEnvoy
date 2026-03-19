"""Email reply classification system."""

import json
import logging
from typing import Dict, Any, Optional
import re

from ..clients.fallback import cheap_model_chain
from .prompt import REPLY_CLASSIFICATION_PROMPT, ACTION_EXTRACTION_PROMPT
from ...core.cache import cache
from .prompt import REPLY_CLASSIFICATION_PROMPT, ACTION_EXTRACTION_PROMPT
from ...core.cache import cache

from ..clients.anthropic import AnthropicClient
from .prompt import REPLY_CLASSIFICATION_PROMPT, ACTION_EXTRACTION_PROMPT
from ...core.cache import cache

logger = logging.getLogger(__name__)


class ReplyClassifier:
    """Classify recruiter email replies."""
    
    def __init__(self):
        self.client = cheap_model_chain()  # OpenAI → OpenRouter fallback
    async def classify_reply(self, body: str, subject: str = "", 
                              from_email: str = "") -> Dict[str, Any]:
        """Classify an email reply."""
        
        # Generate cache key
        cache_key = f"classify:{hash(body[:200])}:{hash(subject)}"
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Truncate body if too long
        if len(body) > 2000:
            body = body[:2000] + "..."
        
        prompt = REPLY_CLASSIFICATION_PROMPT.format(
            subject=subject,
            from_email=from_email,
            body=body
        )
        
        try:
            response = await self.client.generate_with_json(
                prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            # Validate and normalize response
            normalized = self._normalize_response(response)
            
            # Cache for 24 hours
            await cache.set(cache_key, json.dumps(normalized), ttl=86400)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            
            # Fallback to rule-based classification
            return self._rule_based_fallback(body, subject)
    
    async def extract_actions(self, email_text: str) -> Dict[str, Any]:
        """Extract action items from email."""
        
        prompt = ACTION_EXTRACTION_PROMPT.format(email_text=email_text[:2000])
        
        try:
            response = await self.client.generate_with_json(prompt, temperature=0.3)
            return response
        except:
            return {
                "actions": [],
                "deadline": None,
                "contact_person": None,
                "next_steps": "Manual review needed"
            }
    
    def _normalize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize classification response."""
        
        # Ensure required fields
        defaults = {
            "category": "OTHER",
            "confidence": 50,
            "urgency": "medium",
            "requires_action": True,
            "requires_human": True,
            "sentiment": "neutral",
            "key_points": [],
            "suggested_response": ""
        }
        
        # Update with response
        for key in defaults:
            if key not in response:
                response[key] = defaults[key]
        
        # Validate category
        valid_categories = ["INTERVIEW", "REJECTION", "INFO_REQUEST", 
                           "ASSESSMENT", "FOLLOW_UP", "OFFER", "OTHER"]
        
        if response["category"] not in valid_categories:
            response["category"] = "OTHER"
        
        # Ensure confidence is int
        try:
            response["confidence"] = int(response["confidence"])
        except:
            response["confidence"] = 50
        
        return response
    
    def _rule_based_fallback(self, body: str, subject: str) -> Dict[str, Any]:
        """Rule-based classification when AI fails."""
        body_lower = body.lower()
        subject_lower = subject.lower()
        combined = body_lower + " " + subject_lower
        
        # Interview keywords
        if any(word in combined for word in ["interview", "schedule", "meet", "chat", "talk", "discuss"]):
            return {
                "category": "INTERVIEW",
                "confidence": 70,
                "urgency": "high",
                "requires_action": True,
                "requires_human": True,
                "sentiment": "positive",
                "key_points": ["Interview request detected"],
                "suggested_response": "Thank them and propose available times"
            }
        
        # Rejection keywords
        if any(word in combined for word in ["unfortunately", "regret", "not moving forward", "not selected", "other candidates"]):
            return {
                "category": "REJECTION",
                "confidence": 80,
                "urgency": "low",
                "requires_action": False,
                "requires_human": False,
                "sentiment": "negative",
                "key_points": ["Application rejected"],
                "suggested_response": "No response needed, update tracking"
            }
        
        # Info request keywords
        if any(word in combined for word in ["more information", "portfolio", "github", "samples", "availability", "rate"]):
            return {
                "category": "INFO_REQUEST",
                "confidence": 75,
                "urgency": "medium",
                "requires_action": True,
                "requires_human": True,
                "sentiment": "neutral",
                "key_points": ["Additional information requested"],
                "suggested_response": "Provide requested information"
            }
        
        # Assessment keywords
        if any(word in combined for word in ["assessment", "challenge", "test", "exercise", "hackerrank", "codility"]):
            return {
                "category": "ASSESSMENT",
                "confidence": 85,
                "urgency": "high",
                "requires_action": True,
                "requires_human": True,
                "sentiment": "neutral",
                "key_points": ["Technical assessment requested"],
                "suggested_response": "Acknowledge and confirm timeline"
            }
        
        # Default
        return {
            "category": "OTHER",
            "confidence": 50,
            "urgency": "low",
            "requires_action": True,
            "requires_human": True,
            "sentiment": "neutral",
            "key_points": [],
            "suggested_response": "Review manually"
        }
    
    async def should_auto_respond(self, classification: Dict[str, Any]) -> bool:
        """Determine if we should auto-respond to this email."""
        # Never auto-respond to rejections
        if classification["category"] == "REJECTION":
            return False
        
        # Auto-respond to info requests with low complexity
        if classification["category"] == "INFO_REQUEST" and classification["confidence"] > 80:
            # Check if it's a simple request
            if len(classification.get("key_points", [])) <= 2:
                return True
        
        # Never auto-respond to interviews (need human scheduling)
        if classification["category"] == "INTERVIEW":
            return False
        
        # Never auto-respond to offers
        if classification["category"] == "OFFER":
            return False
        
        # Assessment requests might have time constraints - human should handle
        if classification["category"] == "ASSESSMENT":
            return False
        
        return False