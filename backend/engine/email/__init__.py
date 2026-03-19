"""Email handling package."""

from .sender import EmailSender
from .monitor import EmailMonitor
from .followup import FollowUpManager
from .templates import EmailTemplates

__all__ = ["EmailSender", "EmailMonitor", "FollowUpManager", "EmailTemplates"]

__all__ = ["EmailSender", "EmailMonitor", "FollowUpManager", "EmailTemplate"]