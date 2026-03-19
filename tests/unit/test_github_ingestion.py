"""Tests for GitHub ingestion."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

from backend.ingestion.github.client import GitHubClient
from backend.ingestion.github.parser import GitHubParser


@pytest.mark.asyncio
async def test_github_client_init():
    """Test GitHub client initialization."""
    client = GitHubClient(token="test-token")
    assert client.token == "test-token"
    assert client.client is not None


@pytest.mark.asyncio
async def test_github_client_get_headers():
    """Test GitHub client headers."""
    client = GitHubClient(token="test-token")
    headers = client._get_headers()
    
    assert headers["Authorization"] == "token test-token"
    assert "Accept" in headers
    assert "User-Agent" in headers


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_get_user_repos(mock_get, sample_github_response):
    """Test fetching user repositories."""
    mock_response = AsyncMock()
    mock_response.json.return_value = sample_github_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    client = GitHubClient(token="test-token")
    repos = await client.get_user_repos("testuser")
    
    assert len(repos) == 1
    assert repos[0]["name"] == "awesome-project"
    assert repos[0]["stargazers_count"] == 42


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_get_repo_languages(mock_get, sample_languages_response):
    """Test fetching repository languages."""
    mock_response = AsyncMock()
    mock_response.json.return_value = sample_languages_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    client = GitHubClient(token="test-token")
    languages = await client.get_repo_languages("testuser", "repo")
    
    assert len(languages) == 3
    assert languages["Python"] == 10000


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_get_repo_readme(mock_get):
    """Test fetching repository README."""
    mock_response = AsyncMock()
    mock_response.text = "# Test README\n\nThis is a test."
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    client = GitHubClient(token="test-token")
    readme = await client.get_repo_readme("testuser", "repo")
    
    assert readme == "# Test README\n\nThis is a test."


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_get_repo_readme_not_found(mock_get):
    """Test fetching README when none exists."""
    from httpx import HTTPStatusError, Request, Response
    
    mock_response = Response(404, request=Request("GET", "url"))
    mock_get.side_effect = HTTPStatusError("Not found", request=Mock(), response=mock_response)
    
    client = GitHubClient(token="test-token")
    readme = await client.get_repo_readme("testuser", "repo")
    
    assert readme is None


def test_github_parser_parse_repo(sample_github_response, sample_languages_response):
    """Test parsing repository data."""
    parser = GitHubParser(profile_id=1)
    
    repo_data = sample_github_response[0]
    result = parser.parse_repo(repo_data, sample_languages_response)
    
    assert result["profile_id"] == 1
    assert result["name"] == "awesome-project"
    assert result["stars"] == 42
    assert result["forks"] == 10
    assert result["source"] == "github"
    assert result["source_id"] == "123456"
    assert len(result["technologies"]) == 3


def test_github_parser_aggregate_languages():
    """Test language aggregation."""
    parser = GitHubParser(profile_id=1)
    
    projects = [
        {"technologies": [{"name": "Python"}, {"name": "JavaScript"}]},
        {"technologies": [{"name": "Python"}, {"name": "TypeScript"}]},
        {"technologies": [{"name": "Python"}]}
    ]
    
    result = parser.aggregate_languages(projects)
    
    assert result["primary_language"] == "Python"
    assert len(result["languages"]) == 3
    
    # Find Python
    python = next(l for l in result["languages"] if l["name"] == "Python")
    assert python["count"] == 3
    assert python["percentage"] == 50.0


@pytest.mark.asyncio
async def test_save_projects(session, test_profile, sample_github_response, sample_languages_response):
    """Test saving projects to database."""
    from backend.models.profile import Project
    
    parser = GitHubParser(profile_id=test_profile.id)
    
    repo_data = sample_github_response[0]
    project_data = parser.parse_repo(repo_data, sample_languages_response)
    
    saved_ids = await parser.save_projects([project_data])
    
    assert len(saved_ids) == 1
    
    # Verify saved
    saved = await session.get(Project, saved_ids[0])
    assert saved is not None
    assert saved.name == "awesome-project"
    assert saved.stars == 42