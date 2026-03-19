"""Tests for rule-based filters."""

import pytest
from datetime import datetime

from backend.models.job import Job
from backend.engine.filters.rule_based import RuleBasedFilter, FilterResult


@pytest.fixture
def sample_job():
    """Create a sample job for testing."""
    return Job(
        id=1,
        title="Python Developer",
        company="Tech Corp",
        location="Remote",
        description="Looking for a Python developer with FastAPI experience",
        salary_min=90000,
        salary_max=120000,
        salary_currency="USD",
        job_type="full-time",
        experience_level="mid",
        posted_at=datetime.now(),
        is_active=True
    )


@pytest.mark.asyncio
async def test_location_filter_accepts_valid():
    """Test location filter accepts valid locations."""
    filter = RuleBasedFilter()
    
    job = Job(location="Remote - US")
    result = await filter._check_location(job)
    assert result.passed is True


@pytest.mark.asyncio
async def test_location_filter_rejects_excluded():
    """Test location filter rejects excluded locations."""
    filter = RuleBasedFilter()
    
    job = Job(location="Remote India")
    result = await filter._check_location(job)
    assert result.passed is False
    assert "Location excluded" in result.reasons[0]


@pytest.mark.asyncio
async def test_salary_filter_above_threshold():
    """Test salary filter accepts salaries above threshold."""
    filter = RuleBasedFilter()
    
    job = Job(salary_min=100000, salary_currency="USD")
    result = await filter._check_salary(job)
    assert result.passed is True
    assert result.score > 1.0


@pytest.mark.asyncio
async def test_salary_filter_below_threshold():
    """Test salary filter penalizes but accepts below threshold."""
    filter = RuleBasedFilter()
    
    job = Job(salary_min=60000, salary_currency="USD")
    result = await filter._check_salary(job)
    assert result.passed is True
    assert result.score < 1.0


@pytest.mark.asyncio
async def test_keyword_filter_finds_matches():
    """Test keyword filter finds preferred keywords."""
    filter = RuleBasedFilter()
    
    job = Job(
        title="Python Developer",
        description="Looking for FastAPI developer with AWS experience"
    )
    result = await filter._check_keywords(job)
    assert result.passed is True
    assert result.score > 0.8
    assert "Found keywords" in result.reasons[0]


@pytest.mark.asyncio
async def test_keyword_filter_no_matches():
    """Test keyword filter handles no matches."""
    filter = RuleBasedFilter()
    
    job = Job(
        title="Java Developer",
        description="Looking for Spring Boot developer"
    )
    result = await filter._check_keywords(job)
    assert result.passed is True
    assert result.score == 0.7


@pytest.mark.asyncio
async def test_excluded_keywords_rejection():
    """Test excluded keywords cause rejection."""
    filter = RuleBasedFilter()
    
    job = Job(
        title="Senior Python Developer",
        description="Looking for a senior developer"
    )
    result = await filter._check_excluded_keywords(job)
    assert result.passed is False
    assert "Excluded keyword" in result.reasons[0]


@pytest.mark.asyncio
async def test_experience_extraction():
    """Test years of experience extraction."""
    filter = RuleBasedFilter()
    
    test_cases = [
        ("5+ years of experience required", 5),
        ("Minimum 3 years experience", 3),
        ("Looking for someone with 7 years of Python", 7),
        ("No experience requirement", None)
    ]
    
    for text, expected in test_cases:
        result = filter._extract_years_experience(text)
        assert result == expected


@pytest.mark.asyncio
async def test_full_filter_pipeline(sample_job):
    """Test complete filter pipeline."""
    filter = RuleBasedFilter()
    
    result = await filter.apply(sample_job)
    
    assert result.passed is True
    assert result.score > 0
    assert len(result.reasons) > 0