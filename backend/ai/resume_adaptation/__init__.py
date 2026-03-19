"""Resume adaptation package."""

from .generator import ResumeAdapter
from .differ import ResumeDiffer
from .prompt import RESUME_ADAPTATION_PROMPT, SUMMARY_ADAPTATION_PROMPT

__all__ = ["ResumeAdapter", "ResumeDiffer", "RESUME_ADAPTATION_PROMPT", "SUMMARY_ADAPTATION_PROMPT"]