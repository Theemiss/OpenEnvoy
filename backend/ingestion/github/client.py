"""GitHub API client."""

import httpx
from typing import Optional, List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from ...core.config import settings

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for GitHub API interactions."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN.get_secret_value() if settings.GITHUB_TOKEN else None
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self._get_headers(),
            timeout=30.0
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Job-Automation/1.0"
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """Fetch all repositories for a user."""
        repos = []
        page = 1
        per_page = 100
        
        while True:
            response = await self.client.get(
                f"/users/{username}/repos",
                params={
                    "page": page,
                    "per_page": per_page,
                    "sort": "updated",
                    "direction": "desc"
                }
            )
            response.raise_for_status()
            
            page_repos = response.json()
            if not page_repos:
                break
            
            repos.extend(page_repos)
            page += 1
            
            # Check if we've fetched all pages
            if len(page_repos) < per_page:
                break
        
        logger.info(f"Fetched {len(repos)} repositories for user {username}")
        return repos
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_repo_languages(self, username: str, repo_name: str) -> Dict[str, int]:
        """Fetch language breakdown for a repository."""
        response = await self.client.get(
            f"/repos/{username}/{repo_name}/languages"
        )
        response.raise_for_status()
        return response.json()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_repo_readme(self, username: str, repo_name: str) -> Optional[str]:
        """Fetch README content for a repository."""
        try:
            response = await self.client.get(
                f"/repos/{username}/{repo_name}/readme",
                headers={"Accept": "application/vnd.github.v3.html"}
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.debug(f"No README found for {username}/{repo_name}")
                return None
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_commit_activity(self, username: str, repo_name: str) -> List[Dict[str, Any]]:
        """Fetch commit activity for the last year."""
        response = await self.client.get(
            f"/repos/{username}/{repo_name}/stats/commit_activity"
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()