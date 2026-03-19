"""GitHub ingestion package."""

from .client import GitHubClient
from .parser import GitHubParser

__all__ = ["GitHubClient", "GitHubParser"]