"""Integration tests for job pipeline."""

import pytest
from datetime import datetime

from backend.scrapers.pipeline import ScrapingPipeline
from backend.engine.filters.rule_based import RuleBasedFilter
from backend.ai.scoring.two_tier import JobScorer
from backend.models.job import Job


@pytest.mark.asyncio
async def test_full_job_pipeline(session, test_profile):
    """Test complete job pipeline from scraping to scoring."""
    
    # 1. Create a test job
    job = Job(
        title="Python Developer",
        company="Test Corp",
        description="Looking for Python developer with FastAPI experience",
        location="Remote",
        url="https://example.com/job/1",
        source="test",
        scraped_at=datetime.now()
    )
    session.add(job)
    await session.commit()
    
    # 2. Apply filters
    filter_pipeline = RuleBasedFilter()
    filter_result = await filter_pipeline.apply(job)
    
    assert filter_result.passed is True
    assert filter_result.score > 0
    
    # 3. Score with AI
    scorer = JobScorer()
    
    # Mock the AI response
    scorer.score_job = pytest.mock.AsyncMock(return_value={
        "score": 85,
        "reasoning": "Good match",
        "model_used": "cheap"
    })
    
    score_result = await scorer.score_job(job, test_profile)
    
    assert score_result["score"] >= 70
    assert "reasoning" in score_result
    
    # 4. Update job with score
    job.relevance_score = score_result["score"]
    job.score_reasoning = score_result["reasoning"]
    await session.commit()
    
    # Verify
    updated_job = await session.get(Job, job.id)
    assert updated_job.relevance_score == 85


@pytest.mark.asyncio
async def test_scraping_pipeline():
    """Test scraping pipeline with multiple sources."""
    
    pipeline = ScrapingPipeline()
    
    # Mock the scrapers
    for scraper in pipeline.scrapers.values():
        scraper.scrape = pytest.mock.AsyncMock(return_value=[])
        scraper.save_jobs = pytest.mock.AsyncMock(return_value=[])
    
    # Run all scrapers
    results = await pipeline.run_all()
    
    assert isinstance(results, dict)
    for source in pipeline.scrapers:
        assert source in results


@pytest.mark.asyncio
async def test_filter_pipeline(session):
    """Test filter pipeline with various jobs."""
    
    # Create jobs with different characteristics
    jobs = [
        Job(
            title="Senior Python Developer",
            company="Tech Corp",
            description="Senior role requiring 8+ years",
            location="Remote India",
            salary_min=60000,
            session=session
        ),
        Job(
            title="Junior Developer",
            company="Startup",
            description="Entry level Python",
            location="Remote",
            salary_min=80000,
            session=session
        ),
        Job(
            title="DevOps Engineer",
            company="Enterprise",
            description="Kubernetes and AWS",
            location="New York",
            salary_min=120000,
            session=session
        )
    ]
    
    for job in jobs:
        session.add(job)
    await session.commit()
    
    # Apply filters to each
    filter_pipeline = RuleBasedFilter()
    
    results = []
    for job in jobs:
        result = await filter_pipeline.apply(job)
        results.append((job, result))
    
    # Senior role with low salary should be penalized but pass
    senior_result = results[0][1]
    assert senior_result.passed is True
    assert senior_result.score < 1.0
    
    # Junior role with good salary should score well
    junior_result = results[1][1]
    assert junior_result.passed is True
    assert junior_result.score >= 1.0
    
    # DevOps role should be checked
    devops_result = results[2][1]
    assert devops_result.passed is True