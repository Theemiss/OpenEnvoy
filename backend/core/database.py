from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session
)
from sqlalchemy.orm import declarative_base, declared_attr
from asyncio import current_task
import re

from .config import settings


class CustomBase:
    """Base model class with automatic tablename generation."""
    
    @declared_attr
    def __tablename__(cls):
        """Convert CamelCase to snake_case for table name."""
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return name


Base = declarative_base(cls=CustomBase)


class DatabaseManager:
    """Manages database engine and session factories."""
    
    def __init__(self, database_url: str):
        self.engine: Optional[AsyncEngine] = None
        self.async_session_maker: Optional[async_sessionmaker] = None
        self.database_url = database_url
    
    async def initialize(self):
        """Create engine and session factory."""
        self.engine = create_async_engine(
            self.database_url,
            echo=settings.DEBUG,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True
        )
        
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def close(self):
        """Dispose of the engine."""
        if self.engine:
            await self.engine.dispose()
    
    def get_scoped_session(self):
        """Get a scoped session for the current task."""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized")
        
        return async_scoped_session(
            self.async_session_maker,
            scopefunc=current_task
        )
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session as a context manager."""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized")
        
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session."""
    async with db_manager.session() as session:
        yield session


db_manager = DatabaseManager(str(settings.DATABASE_URL))