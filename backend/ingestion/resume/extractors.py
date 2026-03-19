"""Specialized extractors for different resume sections."""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class DateExtractor:
    """Extract and parse dates from text."""
    
    MONTHS = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }
    
    @classmethod
    def extract_date_range(cls, text: str) -> Dict[str, Optional[datetime]]:
        """Extract start and end dates from a date range string."""
        # Pattern: Month YYYY - Month YYYY or YYYY - YYYY
        patterns = [
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\s*[-–]\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4}|present|current)',
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})\s*[-–]\s*(\d{4}|present|current)',
            r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 4:
                    # Full month-month pattern
                    start_month = cls.MONTHS.get(groups[0][:3], 1)
                    start_year = int(groups[1])
                    end_month = cls.MONTHS.get(groups[2][:3], 1)
                    end_year = groups[3]
                elif len(groups) == 3:
                    # Month-year to year pattern
                    start_month = cls.MONTHS.get(groups[0][:3], 1)
                    start_year = int(groups[1])
                    end_month = 12
                    end_year = groups[2]
                else:
                    # Year to year pattern
                    start_month = 1
                    start_year = int(groups[0])
                    end_month = 12
                    end_year = groups[1]
                
                start_date = datetime(start_year, start_month, 1)
                
                if str(end_year).lower() in ['present', 'current']:
                    end_date = None
                else:
                    end_date = datetime(int(end_year), end_month, 1)
                
                return {
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_current": end_date is None
                }
        
        return {"start_date": None, "end_date": None, "is_current": False}


class SkillExtractor:
    """Extract and categorize skills from text."""
    
    SKILL_CATEGORIES = {
        "languages": ["python", "javascript", "typescript", "java", "c++", "c#", "ruby", "php", "go", "rust", "swift", "kotlin"],
        "frameworks": ["react", "angular", "vue", "django", "flask", "fastapi", "spring", "express", "rails", "laravel"],
        "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "sqlite"],
        "cloud": ["aws", "azure", "gcp", "heroku", "digitalocean", "cloudflare"],
        "devops": ["docker", "kubernetes", "jenkins", "terraform", "ansible", "prometheus", "grafana"],
        "tools": ["git", "github", "gitlab", "jira", "confluence", "vscode", "vim"]
    }
    
    @classmethod
    def extract_with_categories(cls, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize extracted skills."""
        categorized = {category: [] for category in cls.SKILL_CATEGORIES}
        categorized["other"] = []
        
        for skill in skills:
            skill_lower = skill.lower()
            found = False
            
            for category, keywords in cls.SKILL_CATEGORIES.items():
                if any(keyword in skill_lower for keyword in keywords):
                    categorized[category].append(skill)
                    found = True
                    break
            
            if not found:
                categorized["other"].append(skill)
        
        return categorized