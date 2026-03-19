"""Email sending functionality."""

import base64
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiosmtplib

from ...core.config import settings
from ...core.database import db_manager
from ...models.email import Email
from ...core.cache import cache

logger = logging.getLogger(__name__)


class EmailSender:
    """Send emails via SMTP or Gmail API."""
    
    def __init__(self, use_gmail_api: bool = True):
        self.use_gmail_api = use_gmail_api and settings.GMAIL_CREDENTIALS_FILE
        self.smtp_config = None
        
        if not self.use_gmail_api:
            self.smtp_config = {
                "hostname": settings.SMTP_HOST,
                "port": settings.SMTP_PORT,
                "username": settings.SMTP_USER,
                "password": settings.SMTP_PASSWORD.get_secret_value() if settings.SMTP_PASSWORD else None,
                "use_tls": settings.SMTP_PORT == 587
            }
        
        # Rate limiting
        self.sent_today = 0
        self.max_per_day = 50
        self.last_send_time = 0
        self.min_interval = 60  # seconds between emails
    
    async def send_email(self, to_email: str, subject: str, body: str, 
                         html_body: Optional[str] = None,
                         attachments: Optional[List[Dict]] = None,
                         application_id: Optional[int] = None) -> Dict[str, Any]:
        """Send an email."""
        
        # Rate limiting
        await self._check_rate_limits()
        
        if self.use_gmail_api:
            result = await self._send_via_gmail(to_email, subject, body, html_body, attachments)
        else:
            result = await self._send_via_smtp(to_email, subject, body, html_body, attachments)
        
        # Save to database
        email_id = await self._save_to_db(
            to_email=to_email,
            subject=subject,
            body_text=body,
            body_html=html_body,
            application_id=application_id,
            message_id=result.get("message_id"),
            status="sent" if result.get("success") else "failed"
        )
        
        # Update rate limiting
        self.sent_today += 1
        self.last_send_time = asyncio.get_event_loop().time()
        
        return {
            "success": result.get("success", False),
            "message_id": result.get("message_id"),
            "email_id": email_id,
            "error": result.get("error")
        }
    
    async def _send_via_smtp(self, to_email: str, subject: str, body: str,
                              html_body: Optional[str] = None,
                              attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send email via SMTP."""
        if not self.smtp_config or not self.smtp_config["hostname"]:
            return {"success": False, "error": "SMTP not configured"}
        
        # Create message
        msg = MIMEMultipart('alternative') if html_body else MIMEText(body, 'plain')
        msg['Subject'] = subject
        msg['From'] = self.smtp_config["username"]
        msg['To'] = to_email
        
        if html_body:
            # Attach both plain and HTML versions
            msg.attach(MIMEText(body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                part = MIMEApplication(attachment["content"])
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=attachment["filename"]
                )
                msg.attach(part)
        
        try:
            # Send via SMTP
            response = await aiosmtplib.send(
                msg,
                hostname=self.smtp_config["hostname"],
                port=self.smtp_config["port"],
                username=self.smtp_config["username"],
                password=self.smtp_config["password"],
                use_tls=self.smtp_config["use_tls"]
            )
            
            return {
                "success": True,
                "message_id": response
            }
            
        except Exception as e:
            logger.error(f"SMTP send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_via_gmail(self, to_email: str, subject: str, body: str,
                               html_body: Optional[str] = None,
                               attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send email via Gmail API."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            
            # Load credentials
            creds = Credentials.from_authorized_user_file(
                settings.GMAIL_CREDENTIALS_FILE,
                ['https://www.googleapis.com/auth/gmail.send']
            )
            
            # Build service
            service = build('gmail', 'v1', credentials=creds)
            
            # Create message
            message = MIMEMultipart('alternative') if html_body else MIMEText(body, 'plain')
            message['to'] = to_email
            message['from'] = 'me'
            message['subject'] = subject
            
            if html_body:
                message.attach(MIMEText(body, 'plain'))
                message.attach(MIMEText(html_body, 'html'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(attachment["content"])
                    part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=attachment["filename"]
                    )
                    message.attach(part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "success": True,
                "message_id": sent_message['id']
            }
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return {
                "success": False,
                "error": str(error)
            }
        except Exception as e:
            logger.error(f"Gmail send failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _save_to_db(self, to_email: str, subject: str, body_text: str,
                          body_html: Optional[str], application_id: Optional[int],
                          message_id: Optional[str], status: str) -> Optional[int]:
        """Save email record to database."""
        async with db_manager.session() as session:
            email = Email(
                application_id=application_id,
                message_id=message_id,
                direction="outbound",
                from_email=settings.SMTP_USER or "me",
                to_email=to_email,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                status=status,
                sent_at=datetime.now() if status == "sent" else None,
                ai_generated=False  # Set to True if generated by AI
            )
            
            session.add(email)
            await session.commit()
            await session.refresh(email)
            
            return email.id
    
    async def _check_rate_limits(self):
        """Check and enforce rate limits."""
        # Check daily limit
        if self.sent_today >= self.max_per_day:
            raise Exception(f"Daily email limit reached ({self.max_per_day})")
        
        # Check interval between sends
        now = asyncio.get_event_loop().time()
        time_since_last = now - self.last_send_time
        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)
        
        # Check Redis for global limits
        redis_key = f"email:sent_today:{datetime.now().strftime('%Y%m%d')}"
        sent_today = await cache.get(redis_key) or 0
        
        if sent_today >= self.max_per_day:
            raise Exception(f"Global daily email limit reached ({self.max_per_day})")
        
        await cache.incr(redis_key)
        await cache.expire(redis_key, 86400)  # 24 hours
    
    async def send_batch(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Send multiple emails with rate limiting."""
        results = []
        
        for email_data in emails:
            try:
                result = await self.send_email(**email_data)
                results.append(result)
                
                # Add jitter between sends
                await asyncio.sleep(self.min_interval + (hash(email_data["to_email"]) % 10))
                
            except Exception as e:
                logger.error(f"Batch send failed for {email_data.get('to_email')}: {str(e)}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "email": email_data
                })
        
        return results