"""Gmail API integration for monitoring and sending."""

import os
import pickle
import base64
import logging
from typing import List, Dict, Any, Optional
import pickle
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...core.config import settings
from ...core.database import db_manager
from ...models.email import Email
from ...ai.classification.reply_classifier import ReplyClassifier

logger = logging.getLogger(__name__)


class GmailClient:
    """Gmail API client for monitoring and sending."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    def __init__(self):
        self.service = None
        self.classifier = ReplyClassifier()
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Token file stores user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.GMAIL_CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API authenticated")
    
    async def check_new_replies(self, since_minutes: int = 60) -> List[Dict[str, Any]]:
        """Check for new email replies."""
        try:
            # Calculate time threshold
            after_date = datetime.now() - timedelta(minutes=since_minutes)
            query = f'after:{after_date.strftime("%Y/%m/%d")} is:unread'
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            
            replies = []
            for msg in messages:
                # Get full message
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Parse email data
                email_data = self._parse_message(message)
                
                # Classify the reply
                classification = await self.classifier.classify_reply(
                    email_data["body_text"],
                    email_data["subject"]
                )
                
                email_data["classification"] = classification
                
                # Mark as read
                self.service.users().messages().modify(
                    userId='me',
                    id=msg['id'],
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                
                replies.append(email_data)
            
            # Save to database
            await self._save_replies(replies)
            
            return replies
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            return []
    
    def _parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into structured format."""
        headers = message['payload']['headers']
        
        # Extract headers
        subject = next(
            (h['value'] for h in headers if h['name'].lower() == 'subject'),
            'No Subject'
        )
        from_email = next(
            (h['value'] for h in headers if h['name'].lower() == 'from'),
            ''
        )
        to_email = next(
            (h['value'] for h in headers if h['name'].lower() == 'to'),
            ''
        )
        date_str = next(
            (h['value'] for h in headers if h['name'].lower() == 'date'),
            ''
        )
        
        # Extract body
        body_text = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        elif message['payload']['mimeType'] == 'text/plain':
            data = message['payload']['body'].get('data', '')
            if data:
                body_text = base64.urlsafe_b64decode(data).decode('utf-8')
        
        # Parse date
        from email.utils import parsedate_to_datetime
        try:
            date = parsedate_to_datetime(date_str)
        except:
            date = datetime.now()
        
        return {
            "message_id": message['id'],
            "thread_id": message['threadId'],
            "subject": subject,
            "from_email": from_email,
            "to_email": to_email,
            "body_text": body_text,
            "date": date,
            "labels": message.get('labelIds', [])
        }
    
    async def _save_replies(self, replies: List[Dict[str, Any]]):
        """Save replies to database."""
        async with db_manager.session() as session:
            for reply in replies:
                # Check if already exists
                from sqlalchemy import select
                stmt = select(Email).where(Email.message_id == reply["message_id"])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    continue
                
                # Try to find associated application
                application_id = await self._find_application_from_thread(reply["thread_id"])
                
                # Create email record
                email = Email(
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
                
                session.add(email)
                
                # Update application status based on classification
                if application_id and reply["classification"].get("category"):
                    from ....models.application import Application
                    app = await session.get(Application, application_id)
                    
                    if app:
                        if reply["classification"]["category"] == "interview":
                            app.status = "interviewing"
                        elif reply["classification"]["category"] == "rejection":
                            app.status = "rejected"
                        elif reply["classification"]["category"] == "info_request":
                            app.status = "needs_info"
                        
                        app.last_activity_at = datetime.now()
            
            await session.commit()
    
    async def _find_application_from_thread(self, thread_id: str) -> Optional[int]:
        """Find application ID from email thread."""
        async with db_manager.session() as session:
            from sqlalchemy import select
            stmt = select(Email).where(Email.thread_id == thread_id)
            result = await session.execute(stmt)
            email = result.scalar_one_or_none()
            
            if email and email.application_id:
                return email.application_id
            
            return None
    
    async def monitor_continuously(self, interval_minutes: int = 15):
        """Continuously monitor for new emails."""
        while True:
            try:
                replies = await self.check_new_replies(interval_minutes)
                
                if replies:
                    logger.info(f"Found {len(replies)} new replies")
                    
                    # Process replies that need action
                    for reply in replies:
                        if reply["classification"].get("requires_action"):
                            await self._handle_actionable_reply(reply)
                
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in email monitoring: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _handle_actionable_reply(self, reply: Dict[str, Any]):
        """Handle replies that require action."""
        # Queue for human review if needed
        if reply["classification"].get("requires_human"):
            from ...engine.workflow.temporal.activities import queue_for_human_review
            
            await queue_for_human_review(
                application_id=reply.get("application_id"),
                review_type="email_reply",
                data=reply
            )
        
        # Auto-draft response for info requests
        if reply["classification"].get("category") == "info_request":
            from ...ai.email.drafter import EmailDrafter
            
            drafter = EmailDrafter()
            # Draft response (would need application and job context)
            # This is a placeholder