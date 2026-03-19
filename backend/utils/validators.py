"""Input validation utilities."""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def validate_salary(salary: Optional[int], min_val: int = 0, max_val: int = 1000000) -> bool:
    """Validate salary value."""
    if salary is None:
        return True
    return min_val <= salary <= max_val


def validate_phone(phone: str) -> bool:
    """Validate phone number (simple)."""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def validate_linkedin_url(url: str) -> bool:
    """Validate LinkedIn profile URL."""
    pattern = r'^https?:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-]+\/?$'
    return bool(re.match(pattern, url))


def validate_github_url(url: str) -> bool:
    """Validate GitHub profile URL."""
    pattern = r'^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9\-]+\/?$'
    return bool(re.match(pattern, url))