"""Temporal workflow activities for job automation."""

from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging

from temporalio import activity

from ....models.job import Job
from ....models.profile import Profile
from ....core.database import db_manager
from ....engine.filters.rule_based import RuleBasedFilter
from ....ai.scoring.two_tier import JobScorer
from ....ai.resume_adaptation.generator import ResumeAdapter
from ....ai.email.drafter import EmailDrafter
from ....ai.cost_tracker import AICostTracker, AICallRecord

logger = logging.getLogger(__name__)


@activity.defn
async def fetch_unprocessed_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    activity.logger.info(f"Fetching up to {limit} unprocessed jobs")

    async with db_manager.session() as session:
        from sqlalchemy import select

        stmt = (
            select(Job)
            .where(
                Job.is_processed == False,
                Job.is_active == True,
                Job.process_attempts < 3,
            )
            .order_by(Job.scraped_at)
            .limit(limit)
        )

        result = await session.execute(stmt)
        jobs = result.scalars().all()

        return [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "salary_min": job.salary_min,
                "salary_max": job.salary_max,
                "job_type": job.job_type,
                "experience_level": job.experience_level,
                "url": job.url,
                "source": job.source,
            }
            for job in jobs
        ]


@activity.defn
async def apply_rule_filters(job_data: Dict[str, Any]) -> Dict[str, Any]:
    activity.logger.info(f"Applying filters to job {job_data['id']}")

    job = Job(
        id=job_data["id"],
        title=job_data["title"],
        company=job_data["company"],
        description=job_data["description"],
        location=job_data.get("location"),
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        job_type=job_data.get("job_type"),
        experience_level=job_data.get("experience_level"),
        url=job_data["url"],
        source=job_data["source"],
    )

    filter_pipeline = RuleBasedFilter()
    result = await filter_pipeline.apply(job)

    return {
        "job_id": job_data["id"],
        "passed": result.passed,
        "score": result.score,
        "reasons": result.reasons,
    }


@activity.defn
async def score_job_relevance(
    job_data: Dict[str, Any], profile_id: int
) -> Dict[str, Any]:
    activity.logger.info(f"Scoring job {job_data['id']} for profile {profile_id}")

    async with db_manager.session() as session:
        profile = await session.get(Profile, profile_id)
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

    job = Job(
        id=job_data["id"],
        title=job_data["title"],
        company=job_data["company"],
        description=job_data["description"],
        location=job_data.get("location"),
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        job_type=job_data.get("job_type"),
        experience_level=job_data.get("experience_level"),
        url=job_data["url"],
        source=job_data["source"],
    )

    scorer = JobScorer()
    start_time = asyncio.get_event_loop().time()
    latency = 0.0

    try:
        score_result = await scorer.score_job(job, profile)
        latency = asyncio.get_event_loop().time() - start_time

        tracker = AICostTracker()
        await tracker.record_call(
            AICallRecord(
                timestamp=datetime.now(),
                model=score_result.get("model_used", "unknown"),
                operation="scoring",
                prompt_tokens=score_result.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=score_result.get("usage", {}).get(
                    "completion_tokens", 0
                ),
                total_tokens=score_result.get("usage", {}).get("total_tokens", 0),
                cost=score_result.get("cost", 0),
                latency=latency,
                job_id=job.id,
                success=True,
            )
        )

        return {
            "job_id": job.id,
            "score": score_result.get("score", 0),
            "reasoning": score_result.get("reasoning", ""),
            "strengths": score_result.get("strengths", []),
            "weaknesses": score_result.get("weaknesses", []),
            "model_used": score_result.get("model_used", "unknown"),
            "escalated": score_result.get("escalated", False),
        }
    except Exception as e:
        activity.logger.error(f"Error scoring job {job.id}: {str(e)}")
        tracker = AICostTracker()
        await tracker.record_call(
            AICallRecord(
                timestamp=datetime.now(),
                model="unknown",
                operation="scoring",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost=0,
                latency=latency,
                job_id=job.id,
                success=False,
                error=str(e),
            )
        )
        return {"job_id": job.id, "score": 0, "error": str(e), "model_used": "none"}


@activity.defn
async def generate_tailored_resume(
    job_data: Dict[str, Any], profile_id: int, score_data: Dict[str, Any]
) -> Dict[str, Any]:
    activity.logger.info(f"Generating resume for job {job_data['id']}")

    async with db_manager.session() as session:
        profile = await session.get(Profile, profile_id)

    job = Job(
        id=job_data["id"],
        title=job_data["title"],
        company=job_data["company"],
        description=job_data["description"],
        location=job_data.get("location"),
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        job_type=job_data.get("job_type"),
        experience_level=job_data.get("experience_level"),
        url=job_data["url"],
        source=job_data["source"],
    )

    adapter = ResumeAdapter()
    start_time = asyncio.get_event_loop().time()

    try:
        resume_result = await adapter.generate_tailored_resume(job, profile)
        latency = asyncio.get_event_loop().time() - start_time

        resume_id = await adapter.save_tailored_resume(resume_result, job, profile)

        tracker = AICostTracker()
        await tracker.record_call(
            AICallRecord(
                timestamp=datetime.now(),
                model="gpt-4o",
                operation="resume_adaptation",
                prompt_tokens=resume_result.get("usage", {}).get("prompt_tokens", 1500),
                completion_tokens=resume_result.get("usage", {}).get(
                    "completion_tokens", 800
                ),
                total_tokens=2300,
                cost=0.03,
                latency=latency,
                job_id=job.id,
                success=True,
            )
        )

        return {
            "job_id": job.id,
            "resume_id": resume_id,
            "changes_made": resume_result.get("changes_made", ""),
            "confidence": resume_result.get("confidence", 0),
            "targeted_skills": resume_result.get("targeted_skills", []),
        }
    except Exception as e:
        activity.logger.error(f"Error generating resume: {str(e)}")
        return {"job_id": job.id, "error": str(e), "resume_id": None}


@activity.defn
async def draft_application_email(
    job_data: Dict[str, Any], profile_id: int, resume_data: Dict[str, Any]
) -> Dict[str, Any]:
    activity.logger.info(f"Drafting email for job {job_data['id']}")

    async with db_manager.session() as session:
        profile = await session.get(Profile, profile_id)

    job = Job(
        id=job_data["id"],
        title=job_data["title"],
        company=job_data["company"],
        description=job_data["description"],
        location=job_data.get("location"),
        salary_min=job_data.get("salary_min"),
        salary_max=job_data.get("salary_max"),
        job_type=job_data.get("job_type"),
        experience_level=job_data.get("experience_level"),
        url=job_data["url"],
        source=job_data["source"],
    )

    drafter = EmailDrafter()
    start_time = asyncio.get_event_loop().time()

    try:
        cover_letter = await drafter.draft_cover_letter(job, profile)
        initial_email = await drafter.draft_initial_email(job, profile)
        latency = asyncio.get_event_loop().time() - start_time

        tokens = (
            cover_letter.get("tokens", {}) if isinstance(cover_letter, dict) else {}
        )
        total_tokens = (
            tokens.get("total_tokens", 500) if isinstance(tokens, dict) else 500
        )
        cost = (total_tokens / 1000 * 0.00015) if total_tokens else 0.000075

        tracker = AICostTracker()
        await tracker.record_call(
            AICallRecord(
                timestamp=datetime.now(),
                model="gpt-4o-mini",
                operation="email_drafting",
                prompt_tokens=total_tokens,
                completion_tokens=0,
                total_tokens=total_tokens,
                cost=cost,
                latency=latency,
                job_id=job.id,
                success=True,
            )
        )

        cover_letter_text = (
            cover_letter.get("cover_letter", "")
            if isinstance(cover_letter, dict)
            else str(cover_letter)
        )
        email_subject = (
            initial_email.get("subject", "") if isinstance(initial_email, dict) else ""
        )
        email_body = (
            initial_email.get("body", "") if isinstance(initial_email, dict) else ""
        )

        return {
            "job_id": job.id,
            "cover_letter": cover_letter_text,
            "email_subject": email_subject,
            "email_body": email_body,
            "resume_id": resume_data.get("resume_id"),
        }
    except Exception as e:
        activity.logger.error(f"Error drafting email: {str(e)}")
        return {"job_id": job.id, "error": str(e)}


@activity.defn
async def create_application_record(
    job_data: Dict[str, Any],
    profile_id: int,
    score_data: Dict[str, Any],
    resume_data: Dict[str, Any],
    email_data: Dict[str, Any],
) -> int:
    activity.logger.info(f"Creating application for job {job_data['id']}")

    async with db_manager.session() as session:
        from ....models.application import Application, ApplicationTimeline
        from sqlalchemy import select

        stmt = select(Application).where(Application.job_id == job_data["id"])
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            activity.logger.info(f"Application already exists for job {job_data['id']}")
            return existing.id

        application = Application(
            job_id=job_data["id"],
            resume_id=resume_data.get("resume_id"),
            status="draft",
            relevance_score=score_data.get("score"),
            match_score=score_data.get("score"),
        )

        session.add(application)
        await session.flush()

        timeline = ApplicationTimeline(
            application_id=application.id,
            event_type="scored",
            description=f"Job scored {score_data.get('score')} - {score_data.get('reasoning', '')[:100]}",
            ai_generated=True,
            model_used=score_data.get("model_used"),
            metadata={"score": score_data, "resume": resume_data, "email": email_data},
        )

        session.add(timeline)
        await session.commit()
        await session.refresh(application)

        return application.id


@activity.defn
async def queue_for_human_review(
    application_id: int, review_type: str, data: Dict[str, Any]
) -> bool:
    activity.logger.info(
        f"Queuing application {application_id} for {review_type} review"
    )

    review_key = f"review:{review_type}:{application_id}"

    from ....core.cache import cache

    await cache.set(
        review_key,
        json.dumps(
            {
                "application_id": application_id,
                "type": review_type,
                "data": data,
                "created_at": datetime.now().isoformat(),
                "status": "pending",
            }
        ),
        ttl=604800,
    )

    await cache.rpush(f"review_queue:{review_type}", str(application_id))

    return True


@activity.defn
async def mark_job_processed(
    job_id: int, success: bool = True, error: Optional[str] = None
) -> None:
    activity.logger.info(f"Marking job {job_id} as processed")

    async with db_manager.session() as session:
        from ....models.job import Job

        job = await session.get(Job, job_id)

        if job:
            job.is_processed = True
            job.process_attempts += 1
            if error:
                job.last_error = error[:500]

            await session.commit()
