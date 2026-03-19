"""Engine package for core automation logic."""

from .filters import RuleBasedFilter, FilterPipeline
from .email import EmailSender, EmailMonitor, FollowUpManager
from .tracking import ApplicationLogger

__all__ = [
    "RuleBasedFilter",
    "FilterPipeline",
    "EmailSender",
    "EmailMonitor",
    "FollowUpManager",
    "ApplicationLogger"
]