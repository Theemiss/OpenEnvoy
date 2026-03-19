"""SMTP email sending."""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from ...core.config import settings


class SMTPClient:
    """SMTP email client."""
    
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD.get_secret_value() if settings.SMTP_PASSWORD else None
        self.use_tls = settings.SMTP_USE_TLS
    
    async def send(self, to_email: str, subject: str, body: str,
                   html_body: Optional[str] = None,
                   from_email: Optional[str] = None) -> Dict[str, Any]:
        """Send email via SMTP."""
        
        # Create message
        msg = MIMEMultipart('alternative') if html_body else MIMEText(body, 'plain')
        msg['Subject'] = subject
        msg['From'] = from_email or self.username
        msg['To'] = to_email
        
        if html_body:
            msg.attach(MIMEText(body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
        
        try:
            response = await aiosmtplib.send(
                msg,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls
            )
            
            return {
                "success": True,
                "message_id": response
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def test_connection(self) -> bool:
        """Test SMTP connection."""
        try:
            await aiosmtplib.send(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls
            )
            return True
        except:
            return False