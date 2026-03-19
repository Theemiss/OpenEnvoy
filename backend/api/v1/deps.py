"""API dependencies."""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...core.database import db_manager
from ...core.config import settings

security = HTTPBearer()


async def get_db() -> AsyncGenerator:
    """Get database session."""
    async with db_manager.session() as session:
        yield session


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """Verify API key."""
    api_key = credentials.credentials
    
    if api_key != settings.API_KEY.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True


async def get_current_profile():
    """Get current active profile."""
    from ...models.profile import Profile
    from sqlalchemy import select
    
    async with db_manager.session() as session:
        result = await session.execute(
            select(Profile).where(Profile.is_active == True)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active profile found"
            )
        
        return profile