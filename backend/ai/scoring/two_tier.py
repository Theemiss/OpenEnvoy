"""Two-tier scoring system with cheap and premium models."""

import json
import logging
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime

from ...models.job import Job
from ...models.profile import Profile
from ..clients.fallback import FallbackChain
from .prompt import CHEAP_SCORING_PROMPT, JOB_SCORING_PROMPT, SCORE_CACHE_KEY
from ...core.cache import cache
from ...models.profile import Profile
from ..clients.base import AIClient
from ..clients.base import AIClient
from ..clients.fallback import FallbackChain
from .prompt import CHEAP_SCORING_PROMPT,JOB_SCORING_PROMPT,SCORE_CACHE_KEY
from ..clients.anthropic import AnthropicClient
from .prompt import JOB_SCORING_PROMPT, CHEAP_SCORING_PROMPT
from ...core.cache import cache
from ...core.config import settings

logger = logging.getLogger(__name__)


class JobScorer:
    """Two-tier job scoring system."""
    
    # Score thresholds
    CLEAR_REJECT = 30
    AMBIGUOUS_LOW = 40
    AMBIGUOUS_HIGH = 70
    CLEAR_ACCEPT = 80
    
    def __init__(self):
        # Cheap model with fallback: OpenAI → OpenRouter
        self.cheap_model = FallbackChain([
            ("openai", "gpt-4o-mini"),
            ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21"),
        ])
        
        # Premium model with fallback: OpenAI → Anthropic → OpenRouter
        self.premium_model = FallbackChain([
            ("openai", "gpt-4o"),
            ("anthropic", "claude-3-sonnet"),
            ("openrouter", "google/gemini-2.0-flash-thinking-exp-01-21"),
        ])
    
    async def score_job(self, job: Job, profile: Profile) -> Dict[str, Any]:
        """Score a job using two-tier approach."""
        
        # Check cache first
        cache_key = f"score:{job.id}:{profile.id}"
        cached = await cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for job {job.id}")
            return json.loads(cached)
        
        # Prepare profile summary
        profile_summary = self._prepare_profile_summary(profile)
        
        # Prepare job requirements summary
        job_summary = self._prepare_job_summary(job)
        
        # Step 1: Use cheap model
        cheap_result = await self._score_with_cheap_model(
            job, profile_summary, job_summary
        )
        
        score = cheap_result.get("score", 0)
        
        # Step 2: Check if we need premium model
        if self.AMBIGUOUS_LOW <= score <= self.AMBIGUOUS_HIGH and self.premium_model:
            logger.info(f"Ambiguous score {score} for job {job.id}, using premium model")
            premium_result = await self._score_with_premium_model(job, profile)
            
            # Merge results, preferring premium's score
            final_result = {
                **cheap_result,
                **premium_result,
                "model_used": "premium",
                "cheap_score": score,
                "premium_score": premium_result.get("score")
            }
        else:
            final_result = {
                **cheap_result,
                "model_used": "cheap",
                "escalated": False
            }
        
        # Add metadata
        final_result.update({
            "scored_at": datetime.now().isoformat(),
            "job_id": job.id,
            "profile_id": profile.id
        })
        
        # Cache the result
        await cache.set(
            cache_key,
            json.dumps(final_result),
            ttl=86400  # 24 hours
        )
        
        return final_result
    
    async def _score_with_cheap_model(self, job: Job, profile_summary: str, job_summary: str) -> Dict[str, Any]:
        """Score using cheap/fast model."""
        
        prompt = CHEAP_SCORING_PROMPT.format(
            job_title=job.title,
            job_company=job.company,
            job_requirements_summary=job_summary,
            candidate_skills=profile_summary,
            candidate_experience_summary=profile_summary
        )
        
        try:
            response = await self.cheap_model.generate_with_json(prompt, temperature=0.3)
            
            # Ensure response has required fields
            if "score" not in response:
                response["score"] = 50
            if "reasoning" not in response:
                response["reasoning"] = "No reasoning provided"
            
            # Log cost for tracking
            logger.debug(f"Cheap scoring cost: ${response.get('cost', 0):.6f}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in cheap scoring: {str(e)}")
            return {
                "score": 50,
                "reasoning": "Error in scoring, defaulting to medium score",
                "error": str(e)
            }
    
    async def _score_with_premium_model(self, job: Job, profile: Profile) -> Dict[str, Any]:
        """Score using premium model for ambiguous cases."""
        
        prompt = JOB_SCORING_PROMPT.format(
            profile_json=json.dumps(self._prepare_profile_json(profile), indent=2),
            job_title=job.title,
            job_company=job.company,
            job_location=job.location or "Not specified",
            job_description=job.description
        )
        
        try:
            response = await self.premium_model.generate_with_json(prompt, temperature=0.3)
            
            # Log cost for tracking
            if hasattr(self.premium_model, 'calculate_cost'):
                # Estimate cost based on token usage
                pass
            
            return response
            
        except Exception as e:
            logger.error(f"Error in premium scoring: {str(e)}")
            return {
                "score": 50,
                "reasoning": "Error in premium scoring",
                "strengths": [],
                "weaknesses": [],
                "skill_match_percentage": 50
            }
    
    def _prepare_profile_summary(self, profile: Profile) -> str:
        """Create a concise profile summary for cheap model."""
        skills = ", ".join(profile.skills[:10])
        
        # Get recent experience
        recent_exp = []
        for exp in sorted(profile.experiences, key=lambda x: x.start_date, reverse=True)[:2]:
            recent_exp.append(f"{exp.title} at {exp.company}")
        
        exp_summary = "; ".join(recent_exp) if recent_exp else "No experience listed"
        
        return f"Skills: {skills}. Recent: {exp_summary}"
    
    def _prepare_job_summary(self, job: Job) -> str:
        """Create a concise job summary for cheap model."""
        # Extract first 500 chars of description
        desc_preview = job.description[:500] + "..." if len(job.description) > 500 else job.description
        
        return f"Title: {job.title}. Location: {job.location}. Description: {desc_preview}"
    
    def _prepare_profile_json(self, profile: Profile) -> Dict[str, Any]:
        """Prepare full profile data for premium model."""
        return {
            "name": profile.full_name,
            "title": profile.title,
            "summary": profile.summary,
            "skills": profile.skills,
            "languages": profile.languages,
            "tools": profile.tools,
            "domains": profile.domains,
            "experience": [
                {
                    "title": exp.title,
                    "company": exp.company,
                    "start_date": exp.start_date.isoformat() if exp.start_date else None,
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "is_current": exp.is_current,
                    "description": exp.description,
                    "achievements": exp.achievements,
                    "skills_used": exp.skills_used
                }
                for exp in profile.experiences
            ],
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field": edu.field,
                    "dates": f"{edu.start_date.year if edu.start_date else ''} - {edu.end_date.year if edu.end_date else 'Present'}"
                }
                for edu in profile.education
            ],
            "projects": [
                {
                    "name": proj.name,
                    "description": proj.description,
                    "technologies": proj.technologies,
                    "highlights": proj.highlights
                }
                for proj in profile.projects
            ]
        }
    
    async def score_batch(self, jobs: List[Job], profile: Profile) -> List[Dict[str, Any]]:
        """Score multiple jobs in batch for efficiency."""
        results = []
        for job in jobs:
            result = await self.score_job(job, profile)
            results.append(result)
        return results