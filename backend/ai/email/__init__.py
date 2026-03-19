"""Email drafting package."""

from .drafter import EmailDrafter
from .prompt import COVER_LETTER_PROMPT, INITIAL_OUTREACH_PROMPT, FOLLOW_UP_PROMPT

__all__ = ["EmailDrafter", "COVER_LETTER_PROMPT", "INITIAL_OUTREACH_PROMPT", "FOLLOW_UP_PROMPT"]