"""Rule-based job filtering system."""

import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
import yaml
from pathlib import Path

from ...models.job import Job
from ...core.config import settings


@dataclass
class FilterResult:
    """Result of applying filters to a job."""
    
    passed: bool
    score: float = 0.0
    reasons: List[str] = field(default_factory=list)
    filter_name: Optional[str] = None


class RuleBasedFilter:
    """Apply deterministic rules to filter jobs before AI scoring."""
    
    def __init__(self, rules_path: Optional[Path] = None):
        self.rules = self._load_rules(rules_path)
        
    def _load_rules(self, rules_path: Optional[Path]) -> Dict[str, Any]:
        """Load filter rules from YAML file."""
        if rules_path and rules_path.exists():
            with open(rules_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default rules from settings
        return settings.DEFAULT_FILTER_RULES
    
    async def apply(self, job: Job) -> FilterResult:
        """Apply all rules to a job."""
        reasons = []
        score = 100.0  # Start with perfect score, deduct for issues
        
        # Check location
        location_result = self._check_location(job)
        if not location_result.passed:
            return location_result
        
        # Check salary
        salary_result = self._check_salary(job)
        score *= salary_result.score
        reasons.extend(salary_result.reasons)
        
        # Check keywords
        keyword_result = self._check_keywords(job)
        score *= keyword_result.score
        reasons.extend(keyword_result.reasons)
        
        # Check excluded keywords
        excluded_result = self._check_excluded_keywords(job)
        if not excluded_result.passed:
            return excluded_result
        
        # Check experience level
        exp_result = self._check_experience(job)
        score *= exp_result.score
        reasons.extend(exp_result.reasons)
        
        # Normalize score to 0-100
        final_score = max(0, min(100, score))
        
        return FilterResult(
            passed=final_score >= 50,  # Minimum threshold to pass filter
            score=final_score,
            reasons=reasons[:3]  # Keep top 3 reasons
        )
    
    def _check_location(self, job: Job) -> FilterResult:
        """Check if job location is acceptable."""
        excluded = self.rules.get("excluded_locations", [])
        
        if not excluded or not job.location:
            return FilterResult(passed=True)
        
        job_loc = job.location.lower()
        
        for exclude in excluded:
            if exclude.lower() in job_loc:
                return FilterResult(
                    passed=False,
                    reasons=[f"Location excluded: {job.location}"]
                )
        
        return FilterResult(passed=True)
    
    def _check_salary(self, job: Job) -> FilterResult:
        """Check if salary meets minimum requirements."""
        min_salary = self.rules.get("min_salary")
        
        if not min_salary or not job.salary_min:
            return FilterResult(passed=True, score=1.0)
        
        # If salary is in different currency, assume conversion needed
        if job.salary_currency and job.salary_currency != "USD":
            # Simple conversion for common currencies
            conversion = {
                "EUR": 1.1,
                "GBP": 1.25,
                "CAD": 0.75,
                "AUD": 0.65
            }
            rate = conversion.get(job.salary_currency.upper(), 1.0)
            salary_usd = job.salary_min * rate
        else:
            salary_usd = job.salary_min
        
        if salary_usd >= min_salary:
            # Bonus points for higher salary
            bonus = min(0.2, (salary_usd - min_salary) / min_salary * 0.1)
            return FilterResult(
                passed=True,
                score=1.0 + bonus,
                reasons=[f"Salary meets requirement: ${salary_usd:,.0f}"]
            )
        else:
            # Penalty for lower salary
            penalty = (min_salary - salary_usd) / min_salary * 0.5
            return FilterResult(
                passed=True,  # Still pass, but with penalty
                score=max(0.5, 1.0 - penalty),
                reasons=[f"Salary below preferred: ${salary_usd:,.0f}"]
            )
    
    def _check_keywords(self, job: Job) -> FilterResult:
        """Check for preferred keywords in job."""
        keywords = self.rules.get("preferred_keywords", [])
        
        if not keywords:
            return FilterResult(passed=True, score=1.0)
        
        # Combine title and description for search
        text = f"{job.title} {job.description}".lower()
        
        found = []
        for keyword in keywords:
            if keyword.lower() in text:
                found.append(keyword)
        
        if found:
            # Score based on percentage of keywords found
            match_ratio = len(found) / len(keywords)
            score = 0.8 + (match_ratio * 0.2)  # 0.8-1.0 range
            
            return FilterResult(
                passed=True,
                score=score,
                reasons=[f"Found keywords: {', '.join(found[:3])}"]
            )
        else:
            return FilterResult(
                passed=True,
                score=0.7,  # Still pass, but lower score
                reasons=["No preferred keywords found"]
            )
    
    def _check_excluded_keywords(self, job: Job) -> FilterResult:
        """Check for excluded keywords that would disqualify the job."""
        excluded = self.rules.get("excluded_keywords", [])
        
        if not excluded:
            return FilterResult(passed=True)
        
        text = f"{job.title} {job.description}".lower()
        
        for keyword in excluded:
            if keyword.lower() in text:
                return FilterResult(
                    passed=False,
                    reasons=[f"Excluded keyword found: {keyword}"]
                )
        
        return FilterResult(passed=True)
    
    def _check_experience(self, job: Job) -> FilterResult:
        """Check if experience level matches."""
        max_years = self.rules.get("max_years_experience")
        
        if not max_years:
            return FilterResult(passed=True, score=1.0)
        
        # Try to extract years of experience from description
        years = self._extract_years_experience(job.description)
        
        if years is None:
            # Use experience level as proxy
            if job.experience_level:
                level_map = {
                    "entry": 2,
                    "mid": 5,
                    "senior": 8,
                    "lead": 10,
                    "principal": 12
                }
                years = level_map.get(job.experience_level.lower(), 5)
            else:
                return FilterResult(passed=True, score=1.0)
        
        if years <= max_years:
            return FilterResult(
                passed=True,
                score=1.0,
                reasons=[f"Experience level matches: {years} years"]
            )
        else:
            # Penalty for requiring more experience
            penalty = (years - max_years) / max_years * 0.3
            return FilterResult(
                passed=True,
                score=max(0.5, 1.0 - penalty),
                reasons=[f"Requires {years}+ years experience"]
            )
    
    def _extract_years_experience(self, text: str) -> Optional[int]:
        """Extract years of experience requirement from text."""
        patterns = [
            r'(\d+)[\+]?\s*years?.*experience',
            r'experience.*?(\d+)[\+]?\s*years?',
            r'(\d+)[\+]?\s*yrs?.*exp',
            r'minimum.*?(\d+).*?years'
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        
        return None


class FilterPipeline:
    """Pipeline for applying multiple filters in sequence."""
    
    def __init__(self):
        self.filters = [
            RuleBasedFilter()
        ]
    
    async def process_job(self, job: Job) -> FilterResult:
        """Apply all filters to a job."""
        for filter_obj in self.filters:
            result = await filter_obj.apply(job)
            if not result.passed:
                return result
        
        return FilterResult(passed=True, score=100.0)
    
    async def process_batch(self, jobs: List[Job]) -> List[FilterResult]:
        """Apply filters to multiple jobs."""
        results = []
        for job in jobs:
            result = await self.process_job(job)
            results.append(result)
        return results