"""Profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ....core.database import db_manager, get_db
from ....models.profile import Profile, Resume
from ....schemas.profile import ProfileResponse, ProfileUpdate
from ....schemas.resume import ResumeResponse

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
async def get_profile(
    session: AsyncSession = Depends(get_db)
):
    """Get active profile."""
    result = await session.execute(
        select(Profile).where(Profile.is_active == True)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="No active profile found")

    return ProfileResponse.model_validate(profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_update: ProfileUpdate,
    session: AsyncSession = Depends(get_db)
):
    """Update profile."""
    result = await session.execute(
        select(Profile).where(Profile.is_active == True)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="No active profile found")

    for key, value in profile_update.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    await session.commit()
    await session.refresh(profile)

    return ProfileResponse.model_validate(profile)


@router.get("/resumes", response_model=List[ResumeResponse])
async def list_resumes(
    session: AsyncSession = Depends(get_db)
):
    """List all resumes."""
    result = await session.execute(select(Resume))
    resumes = result.scalars().all()

    return [ResumeResponse.model_validate(r) for r in resumes]


@router.post("/resumes", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    is_canonical: bool = True,
    session: AsyncSession = Depends(get_db)
):
    """Upload and parse a resume."""
    result = await session.execute(
        select(Profile).where(Profile.is_active == True)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="No active profile found")

    import tempfile
    from pathlib import Path

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        from ....ingestion.resume.parser import ResumeStorage

        storage = ResumeStorage()
        file_type = Path(file.filename).suffix[1:]

        resume_id = await storage.store_canonical_resume(
            Path(tmp_path),
            file_type,
            profile.id
        )

        resume = await session.get(Resume, resume_id)
        return ResumeResponse.model_validate(resume)

    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    session: AsyncSession = Depends(get_db)
):
    """Get resume by ID."""
    resume = await session.get(Resume, resume_id)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return ResumeResponse.model_validate(resume)


@router.delete("/resumes/{resume_id}")
async def delete_resume(
    resume_id: int,
    session: AsyncSession = Depends(get_db)
):
    """Delete resume."""
    resume = await session.get(Resume, resume_id)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    await session.delete(resume)
    await session.commit()

    return {"message": "Resume deleted successfully"}
