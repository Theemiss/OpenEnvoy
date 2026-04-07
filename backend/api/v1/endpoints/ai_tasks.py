"""AI task endpoints for resume adaptation, email drafting, and reply classification."""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from ....ai.resume_adaptation.generator import ResumeAdapter
from ....ai.email.drafter import EmailDrafter
from ....ai.classification.reply_classifier import ReplyClassifier
from ....core.database import db_manager
from .deps import get_current_profile

router = APIRouter(prefix="/ai/tasks", tags=["ai-tasks"])


class ResumeAdaptRequest(BaseModel):
    job_id: int
    profile_id: Optional[int] = None


class ResumeAdaptResponse(BaseModel):
    resume_id: int
    adapted_resume: dict
    changes_made: str
    confidence: int
    targeted_skills: List[str]
    generated_at: str
    model_used: str


class EmailDraftRequest(BaseModel):
    job_id: int
    profile_id: Optional[int] = None
    email_type: str = "initial"


class EmailDraftResponse(BaseModel):
    subject: str
    body: str
    cover_letter: Optional[str] = None
    generated_at: str
    model: str


class ClassifyReplyRequest(BaseModel):
    body: str
    subject: Optional[str] = ""
    from_email: Optional[str] = ""


class ClassificationResponse(BaseModel):
    category: str
    confidence: int
    urgency: str
    requires_action: bool
    requires_human: bool
    sentiment: str
    key_points: List[str]
    suggested_response: str


@router.post("/resume-adapt", response_model=ResumeAdaptResponse)
async def adapt_resume(
    request: ResumeAdaptRequest,
    profile_id: int = Depends(get_current_profile)
):
    """Generate a tailored resume for a specific job."""

    async with db_manager.session() as session:
        from sqlalchemy import select
        from ....models.job import Job
        from ....models.profile import Profile

        job = await session.get(Job, request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        profile = await session.get(Profile, profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

    adapter = ResumeAdapter()

    try:
        result = await adapter.generate_tailored_resume(job, profile)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        resume_id = await adapter.save_tailored_resume(result, job, profile)

        return ResumeAdaptResponse(
            resume_id=resume_id,
            adapted_resume=result.get("adapted_resume", {}),
            changes_made=result.get("changes_made", ""),
            confidence=result.get("confidence", 0),
            targeted_skills=result.get("targeted_skills", []),
            generated_at=result.get("generated_at", datetime.now().isoformat()),
            model_used=result.get("model_used", "unknown")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email-draft", response_model=EmailDraftResponse)
async def draft_email(
    request: EmailDraftRequest,
    profile_id: int = Depends(get_current_profile)
):
    """Draft an application email for a job."""

    async with db_manager.session() as session:
        from sqlalchemy import select
        from ....models.job import Job
        from ....models.profile import Profile

        job = await session.get(Job, request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        profile = await session.get(Profile, profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

    drafter = EmailDrafter()

    try:
        if request.email_type == "cover":
            result = await drafter.draft_cover_letter(job, profile)
            return EmailDraftResponse(
                subject="",
                body="",
                cover_letter=result.get("cover_letter"),
                generated_at=result.get("generated_at", datetime.now().isoformat()),
                model=result.get("model", "unknown")
            )
        else:
            result = await drafter.draft_initial_email(job, profile)
            return EmailDraftResponse(
                subject=result.get("subject", ""),
                body=result.get("body", ""),
                cover_letter=None,
                generated_at=result.get("generated_at", datetime.now().isoformat()),
                model=result.get("model", "unknown")
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-reply", response_model=ClassificationResponse)
async def classify_email_reply(request: ClassifyReplyRequest):
    """Classify a recruiter email reply."""

    classifier = ReplyClassifier()

    try:
        result = await classifier.classify_reply(
            body=request.body,
            subject=request.subject,
            from_email=request.from_email
        )

        return ClassificationResponse(
            category=result.get("category", "OTHER"),
            confidence=result.get("confidence", 50),
            urgency=result.get("urgency", "medium"),
            requires_action=result.get("requires_action", True),
            requires_human=result.get("requires_human", True),
            sentiment=result.get("sentiment", "neutral"),
            key_points=result.get("key_points", []),
            suggested_response=result.get("suggested_response", "")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-draft")
async def batch_draft_emails(
    job_ids: List[int],
    email_type: str = "initial",
    profile_id: int = Depends(get_current_profile)
):
    """Draft emails for multiple jobs in batch."""

    async with db_manager.session() as session:
        from sqlalchemy import select
        from ....models.job import Job
        from ....models.profile import Profile

        profile = await session.get(Profile, profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        stmt = select(Job).where(Job.id.in_(job_ids))
        result = await session.execute(stmt)
        jobs = result.scalars().all()

    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found")

    drafter = EmailDrafter()

    try:
        results = await drafter.draft_batch(jobs, profile, email_type)

        return {
            "total": len(results),
            "emails": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
