"""Email drafting system."""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib

from ...models.job import Job
from ...models.profile import Profile
from ...models.application import Application
from ..clients.fallback import cheap_model_chain
from .prompt import (
    COVER_LETTER_PROMPT, INITIAL_OUTREACH_PROMPT,
    FOLLOW_UP_PROMPT, THANK_YOU_PROMPT, EMAIL_CACHE_KEY
)
from ...core.cache import cache

logger = logging.getLogger(__name__)


class EmailDrafter:
    """Generate personalized emails for job applications."""
    
    def __init__(self):
        self.client =cheap_model_chain()   # Use cheap model for emails
    
    async def draft_cover_letter(self, job: Job, profile: Profile) -> Dict[str, str]:
        """Draft a cover letter for a job application."""
        
        # Check cache
        cache_key = f"cover:{job.id}:{profile.id}"
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Prepare candidate summary
        current_role = next(
            (exp.title for exp in profile.experiences if exp.is_current),
            profile.title
        )
        
        skills_summary = ", ".join(profile.skills[:10])
        
        # Summarize projects
        projects = []
        for proj in profile.projects[:3]:
            tech = ", ".join(proj.technologies[:3]) if proj.technologies else ""
            projects.append(f"{proj.name} ({tech})")
        projects_summary = "; ".join(projects)
        
        # Summarize experience
        exp_summary = []
        for exp in profile.experiences[:2]:
            years = self._calculate_years(exp.start_date, exp.end_date)
            exp_summary.append(f"{exp.title} at {exp.company} ({years} years)")
        exp_summary_text = "; ".join(exp_summary)
        
        prompt = COVER_LETTER_PROMPT.format(
            company=job.company,
            position=job.title,
            job_description=job.description[:1000],
            name=profile.full_name.split()[0],  # First name only
            current_role=current_role,
            skills=skills_summary,
            projects_summary=projects_summary,
            experience_summary=exp_summary_text
        )
        
        try:
            response = await self.client.generate(prompt, temperature=0.7, max_tokens=800)
            
            result = {
                "cover_letter": response.content.strip(),
                "generated_at": datetime.now().isoformat(),
                "model": response.model,
                "tokens": response.usage
            }
            
            # Cache for 30 days
            await cache.set(cache_key, json.dumps(result), ttl=2592000)
            
            return result
            
        except Exception as e:
            logger.error(f"Error drafting cover letter: {str(e)}")
            return {
                "cover_letter": self._fallback_cover_letter(job, profile),
                "generated_at": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def draft_initial_email(self, job: Job, profile: Profile) -> Dict[str, str]:
        """Draft initial outreach email."""
        
        cache_key = f"email:initial:{job.id}:{profile.id}"
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Pick a highlight project
        highlight = ""
        if profile.projects:
            best_project = max(profile.projects, key=lambda p: p.stars or 0)
            highlight = f"my project {best_project.name}"
            if best_project.stars:
                highlight += f" (⭐ {best_project.stars} stars on GitHub)"
        
        prompt = INITIAL_OUTREACH_PROMPT.format(
            position=job.title,
            company=job.company,
            name=profile.full_name,
            highlight=highlight
        )
        
        try:
            response = await self.client.generate_with_json(prompt, temperature=0.7)
            
            result = {
                **response,
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-4o-mini"
            }
            
            await cache.set(cache_key, json.dumps(result), ttl=2592000)
            
            return result
            
        except Exception as e:
            logger.error(f"Error drafting initial email: {str(e)}")
            return {
                "subject": f"Application for {job.title} - {profile.full_name}",
                "body": self._fallback_initial_email(job, profile),
                "generated_at": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def draft_follow_up(self, application: Application, days_since: int) -> Dict[str, str]:
        """Draft follow-up email for an application."""
        
        job = application.job
        profile = await self._get_profile(application)
        
        # Get previous email if exists
        previous_email = None
        if application.emails:
            # Find the last sent email
            for email in sorted(application.emails, key=lambda e: e.sent_at or datetime.min, reverse=True):
                if email.direction == "outbound" and email.sent_at:
                    previous_email = email.body_text[:200] + "..."
                    break
        
        prompt = FOLLOW_UP_PROMPT.format(
            position=job.title,
            company=job.company,
            days_since=days_since,
            previous_email_preview=previous_email or "Initial application"
        )
        
        try:
            response = await self.client.generate_with_json(prompt, temperature=0.5)
            
            return {
                **response,
                "generated_at": datetime.now().isoformat(),
                "follow_up_number": days_since // 5  # Rough estimate
            }
            
        except Exception as e:
            logger.error(f"Error drafting follow-up: {str(e)}")
            return {
                "subject": f"Follow-up on {job.title} application",
                "body": self._fallback_follow_up(job, days_since),
                "generated_at": datetime.now().isoformat()
            }
    
    async def draft_thank_you(self, job: Job, profile: Profile, 
                               interviewer: Optional[str] = None,
                               discussion_points: Optional[List[str]] = None) -> Dict[str, str]:
        """Draft thank you email after interview."""
        
        prompt = THANK_YOU_PROMPT.format(
            position=job.title,
            company=job.company,
            interviewer_name=interviewer or "the hiring team",
            interview_date=datetime.now().strftime("%B %d, %Y"),
            discussion_points=", ".join(discussion_points) if discussion_points else "our conversation"
        )
        
        try:
            response = await self.client.generate_with_json(prompt, temperature=0.7)
            
            return {
                **response,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error drafting thank you: {str(e)}")
            return {
                "subject": f"Thank you - {job.title} interview",
                "body": self._fallback_thank_you(job, interviewer),
                "generated_at": datetime.now().isoformat()
            }
    
    async def draft_batch(self, jobs: List[Job], profile: Profile, 
                           email_type: str = "initial") -> List[Dict[str, Any]]:
        """Draft emails for multiple jobs."""
        results = []
        
        for job in jobs:
            if email_type == "initial":
                email = await self.draft_initial_email(job, profile)
            elif email_type == "cover":
                email = await self.draft_cover_letter(job, profile)
            else:
                email = await self.draft_initial_email(job, profile)
            
            results.append({
                "job_id": job.id,
                "job_title": job.title,
                "company": job.company,
                **email
            })
        
        return results
    
    def _calculate_years(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> float:
        """Calculate years between dates."""
        if not start_date:
            return 0
        
        end = end_date or datetime.now()
        delta = end - start_date
        return round(delta.days / 365.25, 1)
    
    async def _get_profile(self, application: Application) -> Optional[Profile]:
        """Get profile associated with application."""
        # This would need to be implemented based on your data model
        # For now, return None
        return None
    
    def _fallback_cover_letter(self, job: Job, profile: Profile) -> str:
        """Fallback template cover letter."""
        return f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {job.title} position at {job.company}. With my background in {', '.join(profile.skills[:5])}, I believe I would be a valuable addition to your team.

Throughout my career, I have developed strong skills in software development and problem-solving. I am particularly drawn to {job.company} because of your innovative work in the industry.

I have attached my resume for your review. I would welcome the opportunity to discuss how my experience aligns with your needs.

Thank you for your time and consideration.

Best regards,
{profile.full_name}
        """.strip()
    
    def _fallback_initial_email(self, job: Job, profile: Profile) -> str:
        """Fallback template initial email."""
        return f"""
Dear Hiring Manager,

I am writing to apply for the {job.title} position at {job.company}. With my experience in {', '.join(profile.skills[:3])}, I am confident I could contribute effectively to your team.

I have attached my resume for your review and would welcome the opportunity to discuss my qualifications further.

Best regards,
{profile.full_name}
        """.strip()
    
    def _fallback_follow_up(self, job: Job, days_since: int) -> str:
        """Fallback template follow-up."""
        return f"""
Dear Hiring Manager,

I hope this email finds you well. I'm writing to follow up on my application for the {job.title} position, which I submitted {days_since} days ago.

I remain very interested in this opportunity and would welcome the chance to discuss how my skills could benefit your team.

Thank you for your consideration.

Best regards,
[Your name]
        """.strip()
    
    def _fallback_thank_you(self, job: Job, interviewer: Optional[str]) -> str:
        """Fallback template thank you."""
        name = interviewer or "the team"
        return f"""
Dear {name},

Thank you so much for taking the time to interview me for the {job.title} position today. I truly enjoyed learning more about {job.company} and the exciting work you're doing.

Our conversation reinforced my interest in this role, and I'm confident that my skills and experience would make me a valuable contributor to your team.

Please don't hesitate to reach out if you need any additional information from me. I look forward to hearing about the next steps.

Best regards,
[Your name]
        """.strip()