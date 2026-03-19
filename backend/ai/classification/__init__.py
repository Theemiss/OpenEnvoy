"""Email classification package."""

from .reply_classifier import ReplyClassifier
from .prompt import REPLY_CLASSIFICATION_PROMPT, ACTION_EXTRACTION_PROMPT

__all__ = ["ReplyClassifier", "REPLY_CLASSIFICATION_PROMPT", "ACTION_EXTRACTION_PROMPT"]