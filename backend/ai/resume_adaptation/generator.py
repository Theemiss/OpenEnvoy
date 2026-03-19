"""Resume adaptation generator."""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

from ...models.profile import Profile, Resume
from ...models.job import Job
from ..clients.openai import OpenAIClient
from ..clients.anthropic import AnthropicClient
from .prompt import RESUME_ADAPTATION_PROMPT, SUMMARY_ADAPTATION_PROMPT
from ...core.cache import cache
from ...core.database import db_manager
from ...core.storage import storage_manager

logger = logging.getLogger(__name__)


class ResumeAdapter:
    """Generate tailored resumes for specific jobs."""
    
    def __init__(self):
        self.client = OpenAIClient("gpt-4o")  # Use strong model for resumes
        self.cheap_client = OpenAIClient("gpt-4o-mini")
    
    async def generate_tailored_resume(self, job: Job, profile: Profile) -> Dict[str, Any]:
        """Generate a tailored resume for a specific job."""
        
        # Check cache first
        cache_key = self._generate_cache_key(job, profile)
        cached = await cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for resume: job {job.id}")
            return json.loads(cached)
        
        # Prepare canonical resume
        canonical_resume = await self._get_canonical_resume(profile)
        if not canonical_resume:
            raise ValueError(f"No canonical resume found for profile {profile.id}")
        
        # Extract key requirements from job
        key_requirements = self._extract_requirements(job.description)
        
        # Generate adapted resume
        prompt = RESUME_ADAPTATION_PROMPT.format(
            job_title=job.title,
            job_company=job.company,
            job_description=job.description[:3000],  # Limit length
            key_requirements=json.dumps(key_requirements, indent=2),
            canonical_resume_json=json.dumps(canonical_resume, indent=2)
        )
        
        try:
            response = await self.client.generate_with_json(
                prompt,
                temperature=0.5,
                max_tokens=3000
            )
            
            # Validate response structure
            if "adapted_resume" not in response:
                # Try to extract from malformed response
                response = self._validate_response(response, canonical_resume)
            
            # Add metadata
            result = {
                **response,
                "generated_at": datetime.now().isoformat(),
                "job_id": job.id,
                "profile_id": profile.id,
                "model_used": self.client.model_name
            }
            
            # Cache the result
            await cache.set(cache_key, json.dumps(result), ttl=2592000)  # 30 days
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating tailored resume: {str(e)}")
            
            # Fall back to reordering only
            return await self._fallback_adaptation(job, profile, canonical_resume)
    
    async def _get_canonical_resume(self, profile: Profile) -> Optional[Dict[str, Any]]:
        """Get the canonical resume for a profile."""
        async with db_manager.session() as session:
            from sqlalchemy import select
            from ...models.profile import Resume
            
            stmt = select(Resume).where(
                Resume.profile_id == profile.id,
                Resume.is_canonical == True
            )
            result = await session.execute(stmt)
            resume = result.scalar_one_or_none()
            
            if resume:
                return resume.content_json
            
            # Create canonical resume from profile if none exists
            return self._create_canonical_from_profile(profile)
    
    def _create_canonical_from_profile(self, profile: Profile) -> Dict[str, Any]:
        """Create canonical resume JSON from profile data."""
        return {
            "personal": {
                "name": profile.full_name,
                "email": profile.email,
                "phone": profile.phone,
                "location": profile.location,
                "linkedin": profile.linkedin_url,
                "github": profile.github_url
            },
            "summary": profile.summary,
            "skills": profile.skills,
            "languages": profile.languages,
            "tools": profile.tools,
            "experience": [
                {
                    "company": exp.company,
                    "title": exp.title,
                    "location": exp.location,
                    "start_date": exp.start_date.strftime("%B %Y") if exp.start_date else None,
                    "end_date": exp.end_date.strftime("%B %Y") if exp.end_date else "Present" if exp.is_current else None,
                    "is_current": exp.is_current,
                    "description": exp.description,
                    "achievements": exp.achievements,
                    "skills_used": exp.skills_used
                }
                for exp in sorted(profile.experiences, key=lambda x: x.start_date or datetime.min, reverse=True)
            ],
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field": edu.field,
                    "start_date": edu.start_date.strftime("%Y") if edu.start_date else None,
                    "end_date": edu.end_date.strftime("%Y") if edu.end_date else None,
                    "achievements": edu.achievements
                }
                for edu in profile.education
            ],
            "projects": [
                {
                    "name": proj.name,
                    "description": proj.description,
                    "url": proj.url,
                    "technologies": proj.technologies,
                    "highlights": proj.highlights,
                    "stars": proj.stars,
                    "forks": proj.forks
                }
                for proj in profile.projects
            ],
            "certifications": [
                {
                    "name": cert.name,
                    "issuing_org": cert.issuing_org,
                    "credential_id": cert.credential_id,
                    "credential_url": cert.credential_url,
                    "issue_date": cert.issue_date.strftime("%B %Y") if cert.issue_date else None
                }
                for cert in profile.certifications
            ]
        }
    
    def _extract_requirements(self, description: str) -> List[str]:
        """Extract key requirements from job description."""
        # Simple extraction - look for bullet points and requirements sections
        requirements = []
        
        # Look for common requirement section headers
        lines = description.split('\n')
        in_requirements = False
        
        for line in lines:
            line_lower = line.lower()
            
            # Check for section headers
            if any(header in line_lower for header in ['requirements:', 'qualifications:', 'what you\'ll need:', 'required:']):
                in_requirements = True
                continue
            
            # Check for bullet points
            if in_requirements and line.strip().startswith(('•', '-', '*')):
                req = line.strip()[1:].strip()
                if len(req) > 10:  # Avoid single words
                    requirements.append(req)
            
            # Exit section on empty line or new header
            if in_requirements and not line.strip():
                in_requirements = False
        
        # If no requirements found, take first 5 sentences
        if not requirements:
            import re
            sentences = re.split(r'[.!?]+', description)
            requirements = [s.strip() for s in sentences if len(s.strip()) > 30][:5]
        
        return requirements[:10]  # Limit to 10 requirements
    
    def _validate_response(self, response: Dict, canonical: Dict) -> Dict:
        """Ensure response has required structure."""
        if "adapted_resume" not in response:
            # Try to use the whole response as adapted_resume
            if isinstance(response, dict) and "personal" in response:
                return {
                    "adapted_resume": response,
                    "changes_made": "Auto-detected structure",
                    "targeted_skills": [],
                    "confidence": 80
                }
            else:
                # Fall back to canonical
                return {
                    "adapted_resume": canonical,
                    "changes_made": "Using canonical resume (adaptation failed)",
                    "targeted_skills": [],
                    "confidence": 50
                }
        return response
    
    async def _fallback_adaptation(self, job: Job, profile: Profile, 
                                    canonical: Dict) -> Dict[str, Any]:
        """Fallback adaptation when full generation fails."""
        # Just reorder skills based on job keywords
        job_keywords = set(self._extract_keywords(job.description))
        
        # Reorder skills
        skills = canonical.get("skills", [])
        scored_skills = []
        for skill in skills:
            score = 0
            if skill.lower() in job_keywords:
                score = 2
            elif any(keyword in skill.lower() for keyword in job_keywords):
                score = 1
            scored_skills.append((score, skill))
        
        scored_skills.sort(reverse=True)
        reordered_skills = [skill for _, skill in scored_skills]
        
        # Create adapted resume
        adapted = canonical.copy()
        adapted["skills"] = reordered_skills
        
        return {
            "adapted_resume": adapted,
            "changes_made": "Basic skill reordering only",
            "targeted_skills": [s for s in reordered_skills[:5] if s.lower() in job_keywords],
            "confidence": 60,
            "fallback": True
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple keyword extraction - can be improved
        words = text.lower().split()
        # Remove common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'with', 'by', 'from', 'as', 'of', 'it', 'this', 'that', 'is', 'are'}
        
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        return list(set(keywords))[:20]  # Return unique keywords
    
    def _generate_cache_key(self, job: Job, profile: Profile) -> str:
        """Generate cache key for resume."""
        # Include job description hash and profile version
        job_hash = hashlib.sha256(job.description.encode()).hexdigest()[:16]
        return f"resume:{profile.id}:{job_hash}"
    
    async def save_tailored_resume(self, adapted_data: Dict[str, Any], 
                                   job: Job, profile: Profile) -> int:
        """Save tailored resume to database and storage."""
        
        async with db_manager.session() as session:
            from ...models.profile import Resume
            
            # Create resume record
            resume = Resume(
                profile_id=profile.id,
                version="tailored",
                name=f"Tailored for {job.company} - {job.title}",
                is_canonical=False,
                file_path="",  # Will update after storage
                file_type="json",
                file_size=len(json.dumps(adapted_data["adapted_resume"])),
                content_json=adapted_data["adapted_resume"],
                job_id=job.id,
                prompt_used=RESUME_ADAPTATION_PROMPT[:500],  # Store first 500 chars
                model_used=adapted_data.get("model_used", "gpt-4o")
            )
            
            session.add(resume)
            await session.flush()
            
            # Also store as PDF for download? (optional)
            # Would need PDF generation here
            
            await session.commit()
            await session.refresh(resume)
            
            return resume.id