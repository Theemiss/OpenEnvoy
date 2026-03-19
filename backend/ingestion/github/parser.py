"""GitHub data parser and transformer."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from collections import Counter

from ...models.profile import Project
from ...core.database import db_manager

logger = logging.getLogger(__name__)


class GitHubParser:
    def __init__(self, profile_id: int):
        self.profile_id = profile_id

    def parse_repo(
        self,
        repo_data: Dict[str, Any],
        languages: Dict[str, int],
        readme: Optional[str] = None,
    ) -> Dict[str, Any]:
        total_bytes = sum(languages.values())
        language_list = []
        if total_bytes > 0:
            for lang, bytes_count in sorted(
                languages.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                percentage = (bytes_count / total_bytes) * 100
                language_list.append(
                    {
                        "name": lang,
                        "percentage": round(percentage, 1),
                        "bytes": bytes_count,
                    }
                )

        created_at = datetime.fromisoformat(
            repo_data["created_at"].replace("Z", "+00:00")
        )
        updated_at = datetime.fromisoformat(
            repo_data["updated_at"].replace("Z", "+00:00")
        )
        pushed_at = datetime.fromisoformat(
            repo_data["pushed_at"].replace("Z", "+00:00")
        )

        topics = repo_data.get("topics", [])

        description = repo_data.get("description") or ""
        if readme:
            if not description:
                lines = readme.strip().split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        description = line[:200]
                        break

        is_current = True
        start_date = created_at
        end_date = None

        days_since_update = (datetime.now(updated_at.tzinfo) - updated_at).days
        activity_level = (
            "high"
            if days_since_update < 30
            else "medium"
            if days_since_update < 90
            else "low"
        )

        return {
            "profile_id": self.profile_id,
            "name": repo_data["name"],
            "description": description,
            "url": repo_data["html_url"],
            "start_date": start_date,
            "end_date": end_date,
            "is_current": is_current,
            "technologies": language_list,
            "role": "Contributor" if repo_data.get("fork") else "Owner",
            "highlights": [
                f"{repo_data['stargazers_count']} stars"
                if repo_data["stargazers_count"] > 0
                else None,
                f"{repo_data['forks_count']} forks"
                if repo_data["forks_count"] > 0
                else None,
                f"Primary language: {repo_data['language']}"
                if repo_data["language"]
                else None,
                f"Last updated: {days_since_update} days ago",
            ],
            "source": "github",
            "source_id": str(repo_data["id"]),
            "stars": repo_data["stargazers_count"],
            "forks": repo_data["forks_count"],
            "language": repo_data["language"],
            "metadata": {
                "size": repo_data["size"],
                "default_branch": repo_data["default_branch"],
                "has_issues": repo_data["has_issues"],
                "has_wiki": repo_data["has_wiki"],
                "has_pages": repo_data["has_pages"],
                "has_discussions": repo_data.get("has_discussions", False),
                "is_archived": repo_data.get("archived", False),
                "is_template": repo_data.get("is_template", False),
                "topics": topics,
                "license": repo_data.get("license", {}).get("name")
                if repo_data.get("license")
                else None,
                "activity_level": activity_level,
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
                "pushed_at": pushed_at.isoformat() if pushed_at else None,
            },
        }

    def aggregate_languages(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_languages = []
        for project in projects:
            for lang_info in project.get("technologies", []):
                if isinstance(lang_info, dict):
                    all_languages.append(lang_info["name"])
                else:
                    all_languages.append(lang_info)

        language_counts = Counter(all_languages)
        total = len(all_languages)

        return {
            "languages": [
                {
                    "name": lang,
                    "count": count,
                    "percentage": round((count / total) * 100, 1),
                }
                for lang, count in language_counts.most_common()
            ],
            "primary_language": language_counts.most_common(1)[0][0]
            if language_counts
            else None,
        }

    async def save_projects(self, projects_data: List[Dict[str, Any]]) -> List[int]:
        async with db_manager.session() as session:
            from sqlalchemy import select
            from ...models.profile import Project

            saved_ids = []

            for project_data in projects_data:
                stmt = select(Project).where(
                    Project.source == "github",
                    Project.source_id == project_data["source_id"],
                )
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    for key, value in project_data.items():
                        setattr(existing, key, value)
                    saved_ids.append(existing.id)
                    logger.debug(f"Updated project: {project_data['name']}")
                else:
                    project = Project(**project_data)
                    session.add(project)
                    await session.flush()
                    saved_ids.append(project.id)
                    logger.info(f"Created new project: {project_data['name']}")

            await session.commit()
            return saved_ids
