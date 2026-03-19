"""AI model configuration endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ....core.database import get_db
from ....models.ai_model_config import AIModelConfig
from ....schemas.ai_model_config import (
    AIModelConfigCreate,
    AIModelConfigUpdate,
    AIModelConfigResponse,
    AIModelConfigListResponse,
)
from ..deps import get_current_profile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-configs", tags=["ai-configs"])


@router.get("", response_model=AIModelConfigListResponse)
async def list_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tier: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    profile=Depends(get_current_profile),
):
    """List all AI model configurations for the current profile."""
    query = select(AIModelConfig).where(AIModelConfig.profile_id == profile.id)

    if tier:
        query = query.where(AIModelConfig.tier == tier)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0

    # Get items
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    configs = result.scalars().all()

    return AIModelConfigListResponse(
        items=[AIModelConfigResponse.model_validate(c) for c in configs],
        total=total,
    )


@router.get("/{config_id}", response_model=AIModelConfigResponse)
async def get_config(
    config_id: int,
    session: AsyncSession = Depends(get_db),
    profile=Depends(get_current_profile),
):
    """Get a specific AI model configuration."""
    config = await session.get(AIModelConfig, config_id)
    if not config or config.profile_id != profile.id:
        raise HTTPException(status_code=404, detail="Config not found")

    return AIModelConfigResponse.model_validate(config)


@router.post("", response_model=AIModelConfigResponse)
async def create_config(
    config_create: AIModelConfigCreate,
    session: AsyncSession = Depends(get_db),
    profile=Depends(get_current_profile),
):
    """Create a new AI model configuration."""
    profile_id = profile.id

    # If this is set as default, unset others for same tier
    if config_create.is_default:
        query = select(AIModelConfig).where(
            AIModelConfig.profile_id == profile_id,
            AIModelConfig.tier == config_create.tier,
            AIModelConfig.is_default == True,
        )
        result = await session.execute(query)
        for existing in result.scalars().all():
            existing.is_default = False

    config = AIModelConfig(
        profile_id=profile_id,
        name=config_create.name,
        provider=config_create.provider,
        model_name=config_create.model_name,
        tier=config_create.tier,
        temperature=config_create.temperature,
        max_tokens=config_create.max_tokens,
        is_default=config_create.is_default,
    )
    session.add(config)
    await session.commit()
    await session.refresh(config)

    # Invalidate AI config cache
    from ....ai.config_service import ai_config_service

    ai_config_service.clear_cache(profile_id)

    return AIModelConfigResponse.model_validate(config)


@router.patch("/{config_id}", response_model=AIModelConfigResponse)
async def update_config(
    config_id: int,
    config_update: AIModelConfigUpdate,
    session: AsyncSession = Depends(get_db),
    profile=Depends(get_current_profile),
):
    """Update an AI model configuration."""
    profile_id = profile.id
    config = await session.get(AIModelConfig, config_id)
    if not config or config.profile_id != profile_id:
        raise HTTPException(status_code=404, detail="Config not found")

    # If setting as default, unset others first
    if config_update.is_default is True:
        query = select(AIModelConfig).where(
            AIModelConfig.profile_id == profile_id,
            AIModelConfig.tier == (config_update.tier or config.tier),
            AIModelConfig.is_default == True,
            AIModelConfig.id != config_id,
        )
        result = await session.execute(query)
        for existing in result.scalars().all():
            existing.is_default = False

    # Apply updates
    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    await session.commit()
    await session.refresh(config)

    # Invalidate cache
    from ....ai.config_service import ai_config_service

    ai_config_service.clear_cache(profile_id)

    return AIModelConfigResponse.model_validate(config)


@router.delete("/{config_id}")
async def delete_config(
    config_id: int,
    session: AsyncSession = Depends(get_db),
    profile=Depends(get_current_profile),
):
    """Delete an AI model configuration."""
    profile_id = profile.id
    config = await session.get(AIModelConfig, config_id)
    if not config or config.profile_id != profile_id:
        raise HTTPException(status_code=404, detail="Config not found")

    await session.delete(config)
    await session.commit()

    # Invalidate cache
    from ....ai.config_service import ai_config_service

    ai_config_service.clear_cache(profile_id)

    return {"message": "Config deleted successfully"}
