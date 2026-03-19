"""Mock GitHub API responses for testing."""

import json
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock


def mock_github_user_response(username: str = "testuser") -> Dict[str, Any]:
    """Mock GitHub user response."""
    return {
        "login": username,
        "id": 12345,
        "name": "Test User",
        "email": "test@example.com",
        "public_repos": 10,
        "followers": 100,
        "following": 50,
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


def mock_github_repos_response(count: int = 3) -> List[Dict[str, Any]]:
    """Mock GitHub repositories response."""
    repos = []
    for i in range(count):
        repos.append({
            "id": 1000 + i,
            "name": f"repo-{i}",
            "full_name": f"testuser/repo-{i}",
            "description": f"Test repository {i}",
            "html_url": f"https://github.com/testuser/repo-{i}",
            "stargazers_count": i * 10,
            "forks_count": i * 2,
            "language": "Python" if i % 2 == 0 else "JavaScript",
            "created_at": f"2023-01-0{i+1}T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "pushed_at": "2024-01-01T00:00:00Z",
            "size": 1000 + i,
            "default_branch": "main",
            "fork": False,
            "topics": ["python", "test", f"topic-{i}"],
            "license": {"name": "MIT"} if i % 2 == 0 else None
        })
    return repos


def mock_github_languages_response(repo_name: str = "repo-0") -> Dict[str, int]:
    """Mock GitHub languages response."""
    return {
        "Python": 15000,
        "JavaScript": 5000,
        "HTML": 2000,
        "CSS": 1000
    }


def mock_github_readme_response(repo_name: str = "repo-0") -> str:
    """Mock GitHub README content."""
    return f"""# {repo_name}
        ```bash
        pip install {repo_name}
        Usage
        python
        import {repo_name}
        License
        MIT
"""

def mock_github_commit_activity() -> List[Dict[str, Any]]:
    """Mock GitHub commit activity response."""
    return [
    {
    "days": [0, 3, 5, 2, 1, 4, 2],
    "total": 17,
    "week": 1704067200
    },
    {
    "days": [2, 4, 6, 3, 2, 5, 3],
    "total": 25,
    "week": 1704672000
    }
    ]

class MockGitHubClient:
    """Mock GitHub client for testing."""

    def init(self, token: str = None):
    self.token = token
    self.get_user_repos = AsyncMock(return_value=mock_github_repos_response())
    self.get_repo_languages = AsyncMock(return_value=mock_github_languages_response())
    self.get_repo_readme = AsyncMock(return_value=mock_github_readme_response())
    self.get_commit_activity = AsyncMock(return_value=mock_github_commit_activity())

    async def aenter(self):
        return self

    async def aexit(self, exc_type, exc_val, exc_tb):
        pass

    async def close(self):
        pass

    def create_mock_github_client(token: str = None) -> MockGitHubClient:
        """Create a mock GitHub client."""
        return MockGitHubClient(token)

    @pytest.fixture
    def mock_github_client():
        """Fixture providing a mock GitHub client."""
        return create_mock_github_client("test-token")