"""Tests for AI scoring system."""

import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock

from backend.ai.scoring.two_tier import JobScorer
from backend.ai.scoring.cache import ScoringCache
from backend.ai.clients.openai import OpenAIClient


@pytest.mark.asyncio
async def test_job_scorer_init():
    """Test job scorer initialization."""
    scorer = JobScorer()
    assert scorer.cheap_model is not None
    assert scorer.cheap_model.model_name == "gpt-4o-mini"


@pytest.mark.asyncio
async def test_prepare_profile_summary(test_profile):
    """Test profile summary preparation."""
    scorer = JobScorer()
    
    summary = scorer._prepare_profile_summary(test_profile)
    
    assert "Skills:" in summary
    assert "Python" in summary
    assert "Recent:" in summary


@pytest.mark.asyncio
async def test_prepare_job_summary(test_job):
    """Test job summary preparation."""
    scorer = JobScorer()
    
    summary = scorer._prepare_job_summary(test_job)
    
    assert "Title: Senior Python Developer" in summary
    assert "Location: Remote" in summary
    assert "Description:" in summary


@pytest.mark.asyncio
@patch('backend.ai.clients.openai.OpenAIClient.generate_with_json')
async def test_score_with_cheap_model(mock_generate, test_job, test_profile):
    """Test scoring with cheap model."""
    scorer = JobScorer()
    
    # Mock response
    mock_generate.return_value = {
        "score": 85,
        "reasoning": "Good match"
    }
    
    profile_summary = scorer._prepare_profile_summary(test_profile)
    job_summary = scorer._prepare_job_summary(test_job)
    
    result = await scorer._score_with_cheap_model(test_job, profile_summary, job_summary)
    
    assert result["score"] == 85
    assert result["reasoning"] == "Good match"
    mock_generate.assert_called_once()


@pytest.mark.asyncio
@patch('backend.ai.clients.openai.OpenAIClient.generate_with_json')
async def test_score_job_clear_match(mock_generate, test_job, test_profile):
    """Test scoring a clear match."""
    scorer = JobScorer()
    
    # Mock cheap model response
    mock_generate.return_value = {
        "score": 85,
        "reasoning": "Good match"
    }
    
    result = await scorer.score_job(test_job, test_profile)
    
    assert result["score"] == 85
    assert result["model_used"] == "cheap"
    assert not result.get("escalated")


@pytest.mark.asyncio
@patch('backend.ai.clients.openai.OpenAIClient.generate_with_json')
async def test_score_job_ambiguous(mock_generate, test_job, test_profile):
    """Test scoring an ambiguous match."""
    scorer = JobScorer()
    scorer.premium_model = AsyncMock()
    scorer.premium_model.generate_with_json.return_value = {
        "score": 65,
        "reasoning": "Ambiguous match",
        "strengths": ["Python"],
        "weaknesses": ["No cloud"]
    }
    
    # Mock cheap model response with ambiguous score
    mock_generate.return_value = {
        "score": 55,
        "reasoning": "Ambiguous"
    }
    
    result = await scorer.score_job(test_job, test_profile)
    
    assert result["model_used"] == "premium"
    assert result["cheap_score"] == 55
    assert result["premium_score"] == 65


@pytest.mark.asyncio
async def test_scoring_cache():
    """Test scoring cache."""
    cache = ScoringCache(ttl_days=1)
    
    # Test key generation
    key = cache._generate_key(123, 456)
    assert key.startswith("score:")
    assert len(key) > 10
    
    # Different inputs produce different keys
    key2 = cache._generate_key(123, 457)
    assert key != key2


@pytest.mark.asyncio
@patch('backend.core.cache.cache.get')
@patch('backend.core.cache.cache.set')
async def test_cache_get_set(mock_set, mock_get):
    """Test cache get/set operations."""
    cache = ScoringCache()
    
    mock_get.return_value = json.dumps({"score": 85})
    
    # Test get
    result = await cache.get_score(123, 456)
    assert result["score"] == 85
    
    # Test set
    await cache.set_score(123, 456, {"score": 90})
    mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_score_batch(test_job, test_profile):
    """Test batch scoring."""
    scorer = JobScorer()
    
    # Mock the score_job method
    scorer.score_job = AsyncMock(return_value={"score": 85})
    
    jobs = [test_job, test_job]  # Same job twice
    results = await scorer.score_batch(jobs, test_profile)
    
    assert len(results) == 2
    assert scorer.score_job.call_count == 2