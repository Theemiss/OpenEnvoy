"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.database import Base
from backend.models import *
from backend.core.config import settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_profile_data():
    """Sample profile data for tests."""
    return {
        "full_name": "John Developer",
        "email": "john@example.com",
        "title": "Senior Software Engineer",
        "summary": "Experienced full-stack developer",
        "skills": ["Python", "JavaScript", "React", "FastAPI", "AWS"],
        "languages": ["Python", "JavaScript"],
        "tools": ["Docker", "Git"],
        "domains": ["FinTech", "E-commerce"]
    }


@pytest.fixture
async def test_profile(session, sample_profile_data):
    """Create a test profile."""
    profile = Profile(**sample_profile_data)
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@pytest.fixture
def sample_job_data():
    """Sample job data for tests."""
    return {
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "description": "Looking for a Python developer with FastAPI experience. 5+ years required.",
        "location": "Remote",
        "url": "https://example.com/job/1",
        "source": "linkedin",
        "salary_min": 120000,
        "salary_max": 150000,
        "salary_currency": "USD",
        "job_type": "full-time",
        "experience_level": "senior"
    }


@pytest.fixture
async def test_job(session, sample_job_data):
    """Create a test job."""
    job = Job(**sample_job_data)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


@pytest.fixture
def sample_resume_path():
    """Path to sample resume file."""
    # Create a temporary test resume
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        John Developer
        john@example.com | 555-123-4567
        
        SUMMARY
        Experienced software engineer with 8 years in full-stack development.
        
        EXPERIENCE
        Senior Developer at Tech Corp (2021-Present)
        • Led development of microservices architecture
        • Implemented CI/CD pipelines reducing deployment time by 40%
        
        SKILLS
        Python, JavaScript, React, FastAPI, AWS, Docker
        
        EDUCATION
        BS Computer Science, University of Technology (2014-2018)
        """)
        return Path(f.name)


@pytest.fixture
def sample_github_response():
    """Sample GitHub API response."""
    return [
        {
            "id": 123456,
            "name": "awesome-project",
            "full_name": "user/awesome-project",
            "description": "An awesome project",
            "html_url": "https://github.com/user/awesome-project",
            "stargazers_count": 42,
            "forks_count": 10,
            "language": "Python",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "pushed_at": "2024-01-01T00:00:00Z",
            "size": 1000,
            "default_branch": "main",
            "fork": False,
            "topics": ["python", "api", "automation"],
            "license": {"name": "MIT"}
        }
    ]


@pytest.fixture
def sample_languages_response():
    """Sample GitHub languages response."""
    return {
        "Python": 10000,
        "JavaScript": 5000,
        "HTML": 1000
    }


@pytest.fixture
def mock_ai_response():
    """Mock AI response for testing."""
    return {
        "score": 85,
        "reasoning": "Good match for skills",
        "strengths": ["Python", "FastAPI"],
        "weaknesses": ["No Kubernetes experience"],
        "skill_match_percentage": 80
    }


@pytest.fixture
def mock_email_response():
    """Mock email draft response."""
    return {
        "subject": "Application for Senior Python Developer",
        "body": "Dear Hiring Manager,\n\nI am writing to apply...",
        "generated_at": datetime.now().isoformat()
    }


@pytest.fixture
def cleanup_files():
    """Clean up temporary files after tests."""
    files_to_cleanup = []
    yield files_to_cleanup
    for file_path in files_to_cleanup:
        try:
            Path(file_path).unlink()
        except:
            pass