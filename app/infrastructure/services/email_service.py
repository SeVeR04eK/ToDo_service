import aiosmtplib
import email.message
import structlog
from typing import Optional

from app.core.config import settings

logger = structlog.get_logger(__name__)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_from_email = settings.smtp_from_email
        self.smtp_use_tls = settings.smtp_use_tls

    async def send_welcome_email(self, username: str, to_email: str) -> bool:
        """Send welcome email to a new user."""
        try:
            message = email.message.EmailMessage()
            message["From"] = self.smtp_from_email
            message["To"] = to_email
            message["Subject"] = "Welcome!"
            
            body = f"""Hello {username},

Welcome! Your account has been successfully created.

Best regards"""
            
            message.set_content(body)
            
            if not self.smtp_username or not self.smtp_password:
                logger.warning(
                    "SMTP credentials not configured, skipping email send",
                    to_email=to_email
                )
                return False
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_username,
                password=self.smtp_password,
                start_tls=self.smtp_use_tls
            )
            
            logger.info(
                "Welcome email sent successfully",
                username=username,
                to_email=to_email
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send welcome email",
                username=username,
                to_email=to_email,
                error=str(e)
            )
            return False
