"""Data formatting utilities."""

from datetime import datetime
from typing import Optional
import re


def format_currency(amount: Optional[float], currency: str = "USD") -> str:
    """Format currency amount."""
    if amount is None:
        return "Not specified"
    
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "CAD": "C$",
        "AUD": "A$",
        "JPY": "¥"
    }
    
    symbol = symbols.get(currency.upper(), "$")
    
    if amount >= 1000000:
        return f"{symbol}{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"{symbol}{amount/1000:.0f}K"
    else:
        return f"{symbol}{amount:,.0f}"


def format_date(date: Optional[datetime], format: str = "%B %Y") -> str:
    """Format date."""
    if date is None:
        return "Present"
    return date.strftime(format)


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_years_from_text(text: str) -> Optional[int]:
    """Extract years of experience from text."""
    patterns = [
        r'(\d+)[\+]?\s*years?.*experience',
        r'experience.*?(\d+)[\+]?\s*years?',
        r'(\d+)[\+]?\s*yrs?.*exp'
    ]
    
    text_lower = text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1))
    
    return None


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    
    # Remove non-alphanumeric characters
    text = re.sub(r'[^a-z0-9\-]', '', text)
    
    # Remove multiple hyphens
    text = re.sub(r'-+', '-', text)
    
    # Strip hyphens from ends
    return text.strip('-')


def mask_email(email: str) -> str:
    """Mask email for display."""
    if '@' not in email:
        return email
    
    local, domain = email.split('@')
    
    if len(local) <= 2:
        masked_local = local[0] + '*' * len(local[1:])
    else:
        masked_local = local[:2] + '*' * (len(local) - 2)
    
    # Mask domain
    domain_parts = domain.split('.')
    masked_domain = '*.' + domain_parts[-1]
    
    return f"{masked_local}@{masked_domain}"