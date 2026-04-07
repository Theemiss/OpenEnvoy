"""IMAP email client for monitoring replies."""

import imaplib
import email
from email.header import decode_header
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ...core.config import settings
from ...core.database import db_manager
from ...ai.classification.reply_classifier import ReplyClassifier

logger = logging.getLogger(__name__)


class IMAPEmailClient:
    """IMAP client for monitoring email replies."""

    def __init__(self, host: str = None, port: int = 993,
                 username: str = None, password: str = None,
                 folder: str = "INBOX"):
        self.host = host or settings.IMAP_HOST
        self.port = port or settings.IMAP_PORT
        self.username = username or settings.IMAP_USERNAME
        self.password = password or settings.IMAP_PASSWORD
        self.folder = folder
        self.classifier = ReplyClassifier()
        self.connection = None

    def connect(self):
        """Establish IMAP connection."""
        try:
            self.connection = imaplib.IMAP4_SSL(self.host, self.port)
            self.connection.login(self.username, self.password)
            logger.info(f"Connected to IMAP server {self.host}")
        except Exception as e:
            logger.error(f"Failed to connect to IMAP: {e}")
            raise

    def disconnect(self):
        """Close IMAP connection."""
        if self.connection:
            try:
                self.connection.logout()
            except:
                pass
            self.connection = None

    def _decode_header_value(self, value: str) -> str:
        """Decode email header value."""
        if not value:
            return ""
        decoded_parts = decode_header(value)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(encoding or 'utf-8', errors='replace'))
            else:
                result.append(part)
        return ''.join(result)

    def _parse_email(self, raw_email: bytes) -> Dict[str, Any]:
        """Parse raw email bytes into structured format."""
        msg = email.message_from_bytes(raw_email)

        subject = self._decode_header_value(msg.get('Subject', ''))
        from_addr = self._decode_header_value(msg.get('From', ''))
        to_addr = self._decode_header_value(msg.get('To', ''))
        date_str = msg.get('Date', '')
        message_id = msg.get('Message-ID', '')
        thread_id = msg.get('References', msg.get('In-Reply-To', ''))

        body_text = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        body_text = payload.decode(charset, errors='replace')
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or 'utf-8'
                body_text = payload.decode(charset, errors='replace')

        try:
            received_date = email.utils.parsedate_to_datetime(date_str)
        except:
            received_date = datetime.now()

        return {
            "message_id": message_id,
            "thread_id": thread_id,
            "subject": subject,
            "from_email": from_addr,
            "to_email": to_addr,
            "body_text": body_text[:5000],
            "date": received_date,
            "raw_email": raw_email,
        }

    async def fetch_unread_emails(self, since_datetime: datetime = None) -> List[Dict[str, Any]]:
        """Fetch unread emails from the inbox."""
        if not self.connection:
            self.connect()

        try:
            self.connection.select(self.folder, readonly=False)

            since_str = since_datetime.strftime("%d-%b-%Y") if since_datetime else None
            search_criteria = "UNSEEN"
            if since_str:
                search_criteria = f"UNSEEN SINCE {since_str}"

            status, message_ids = self.connection.search(None, search_criteria)

            if status != 'OK':
                logger.warning(f"IMAP search failed: {status}")
                return []

            email_list = []
            for msg_id in message_ids[0].split():
                try:
                    status, raw_data = self.connection.fetch(msg_id, '(RFC822)')
                    if status == 'OK' and raw_data[0]:
                        email_data = self._parse_email(raw_data[0][1])
                        email_list.append(email_data)

                        self.connection.store(msg_id, '-FLAGS', '\\Seen')
                except Exception as e:
                    logger.error(f"Error fetching email {msg_id}: {e}")

            return email_list

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    async def check_new_replies(self, since_minutes: int = 60) -> List[Dict[str, Any]]:
        """Check for new email replies."""
        since_datetime = datetime.now() - timedelta(minutes=since_minutes)
        emails = await self.fetch_unread_emails(since_datetime)

        replies = []
        for email_data in emails:
            classification = await self.classifier.classify_reply(
                email_data["body_text"],
                email_data["subject"]
            )
            email_data["classification"] = classification
            replies.append(email_data)

        if replies:
            await self._save_replies(replies)

        return replies

    async def _save_replies(self, replies: List[Dict[str, Any]]):
        """Save replies to database."""
        async with db_manager.session() as session:
            from sqlalchemy import select
            from ...models.email import Email

            for reply in replies:
                stmt = select(Email).where(Email.message_id == reply["message_id"])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    continue

                application_id = await self._find_application_from_thread(
                    session, reply["thread_id"]
                )

                email_record = Email(
                    application_id=application_id,
                    message_id=reply["message_id"],
                    thread_id=reply["thread_id"],
                    direction="inbound",
                    from_email=reply["from_email"],
                    to_email=reply["to_email"],
                    subject=reply["subject"],
                    body_text=reply["body_text"],
                    classification=reply["classification"].get("category"),
                    classification_confidence=reply["classification"].get("confidence"),
                    status="received",
                    sent_at=reply["date"]
                )

                session.add(email_record)

                if application_id:
                    from ...models.application import Application
                    app = await session.get(Application, application_id)

                    if app:
                        category = reply["classification"].get("category")
                        if category == "interview":
                            app.status = "interviewing"
                        elif category == "rejection":
                            app.status = "rejected"
                        elif category == "info_request":
                            app.status = "needs_info"

                        app.last_activity_at = datetime.now()

            await session.commit()

    async def _find_application_from_thread(self, session, thread_id: str) -> Optional[int]:
        """Find application ID from email thread."""
        from sqlalchemy import select
        from ...models.email import Email

        if not thread_id:
            return None

        stmt = select(Email).where(Email.thread_id == thread_id)
        result = await session.execute(stmt)
        email_record = result.scalar_one_or_none()

        if email_record and email_record.application_id:
            return email_record.application_id

        return None
