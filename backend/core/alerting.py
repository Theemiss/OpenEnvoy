"""Alerting and notification system."""

import logging
import smtplib
import json
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .config import settings
from .cache import cache
from .database import db_manager

logger = logging.getLogger(__name__)


class AlertManager:
    """Manage system alerts and notifications."""

    def __init__(self):
        self.alert_channels: List[AlertChannel] = []
        self.alert_history_key = "alerts:history"
        self.alert_cooldown: Dict[str, datetime] = {}

        if settings.SLACK_WEBHOOK_URL:
            self.alert_channels.append(SlackChannel(settings.SLACK_WEBHOOK_URL))

        if settings.EMAIL_ALERTS_ENABLED:
            self.alert_channels.append(EmailAlertChannel())

    async def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict] = None,
    ):
        """Send alert through all configured channels."""

        alert_key = f"{severity}:{title}"
        if alert_key in self.alert_cooldown:
            last_sent = self.alert_cooldown[alert_key]
            if datetime.now() - last_sent < timedelta(minutes=15):
                logger.debug(f"Alert {title} suppressed (cooldown)")
                return

        alert = {
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        for channel in self.alert_channels:
            try:
                await channel.send(alert)
            except Exception as e:
                logger.error(
                    f"Failed to send alert via {channel.__class__.__name__}: {str(e)}"
                )

        await self._record_alert(alert)
        self.alert_cooldown[alert_key] = datetime.now()

        logger.info(f"Alert sent: {title} ({severity})")

    async def _record_alert(self, alert: Dict[str, Any]):
        """Record alert in history."""
        await cache.lpush(self.alert_history_key, json.dumps(alert))
        await cache.ltrim(self.alert_history_key, 0, 999)

    async def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts."""
        alerts = await cache.lrange(self.alert_history_key, 0, -1)

        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []

        for alert_json in alerts:
            try:
                alert = json.loads(alert_json)
                alert_time = datetime.fromisoformat(alert["timestamp"])
                if alert_time >= cutoff:
                    recent.append(alert)
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Failed to parse alert JSON")

        return recent

    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""

        health: Dict[str, Any] = {"status": "healthy", "checks": {}, "alerts": []}

        # Check database
        try:
            async with db_manager.session() as session:
                from sqlalchemy import text

                await session.execute(text("SELECT 1"))
            health["checks"]["database"] = {"status": "ok"}
        except Exception as e:
            health["status"] = "degraded"
            health["checks"]["database"] = {"status": "error", "error": str(e)}
            await self.send_alert(
                "Database Connection Failed",
                f"Database health check failed: {str(e)}",
                severity="critical",
            )

        # Check Redis
        try:
            await cache.ping()
            health["checks"]["redis"] = {"status": "ok"}
        except Exception as e:
            health["status"] = "degraded"
            health["checks"]["redis"] = {"status": "error", "error": str(e)}
            await self.send_alert(
                "Redis Connection Failed",
                f"Redis health check failed: {str(e)}",
                severity="critical",
            )

        # Check queue sizes
        try:
            queue_sizes: Dict[str, int] = {}
            for queue in ["job_queue", "email_queue", "scraping_queue"]:
                size = await cache.llen(queue)
                queue_sizes[queue] = size

                if size > 1000:
                    health["alerts"].append(f"Queue {queue} has {size} items")

            health["checks"]["queues"] = {"status": "ok", "sizes": queue_sizes}
        except Exception as e:
            health["checks"]["queues"] = {"status": "error", "error": str(e)}

        # Check recent failures
        failures = await self._check_recent_failures()
        if failures:
            health["alerts"].extend(failures)
            health["status"] = "degraded" if len(failures) < 5 else "critical"

        return health

    async def _check_recent_failures(self) -> List[str]:
        """Check for recent system failures."""
        failures: List[str] = []

        async with db_manager.session() as session:
            from sqlalchemy import select
            from ..models.job import Job

            stmt = (
                select(Job)
                .where(Job.process_attempts >= 3, Job.is_active == True)
                .limit(10)
            )

            result = await session.execute(stmt)
            failed_jobs = result.scalars().all()

            if failed_jobs:
                failures.append(
                    f"{len(failed_jobs)} jobs have failed processing 3+ times"
                )

        return failures


class AlertChannel:
    """Base class for alert channels."""

    async def send(self, alert: Dict[str, Any]):
        """Send alert through this channel."""
        raise NotImplementedError


class SlackChannel(AlertChannel):
    """Send alerts to Slack."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.client = httpx.AsyncClient()

    async def send(self, alert: Dict[str, Any]):
        """Send alert to Slack."""

        colors = {
            "info": "#36a64f",
            "warning": "#ffcc00",
            "error": "#ff9900",
            "critical": "#ff0000",
        }

        color = colors.get(alert["severity"], "#36a64f")

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": alert["title"],
                    "text": alert["message"],
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert["severity"],
                            "short": True,
                        },
                        {"title": "Time", "value": alert["timestamp"], "short": True},
                    ],
                    "footer": "Job Automation System",
                }
            ]
        }

        if alert["metadata"]:
            payload["attachments"][0]["fields"].append(
                {
                    "title": "Metadata",
                    "value": json.dumps(alert["metadata"], indent=2),
                    "short": False,
                }
            )

        response = await self.client.post(self.webhook_url, json=payload)
        response.raise_for_status()

    async def close(self):
        await self.client.aclose()


class EmailAlertChannel(AlertChannel):
    """Send alerts via email."""

    async def send(self, alert: Dict[str, Any]):
        """Send alert via email."""

        msg = MIMEMultipart()
        msg["Subject"] = f"[{alert['severity'].upper()}] {alert['title']}"
        msg["From"] = settings.ALERTS_FROM_EMAIL
        msg["To"] = settings.ALERTS_TO_EMAIL

        body = f"""
Alert: {alert['title']}
Severity: {alert['severity']}
Time: {alert['timestamp']}

Message:
{alert['message']}
        """

        if alert["metadata"]:
            body += f"\n\nMetadata:\n{json.dumps(alert['metadata'], indent=2)}"

        msg.attach(MIMEText(body, "plain"))

        # Send via SMTP
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)


alert_manager = AlertManager()
