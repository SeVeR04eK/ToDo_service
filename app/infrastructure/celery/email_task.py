import asyncio

import structlog
from celery import Task

from app.core.config import settings
from app.infrastructure.celery.celery_app import celery_app
from app.infrastructure.services.email_service import EmailService


logger = structlog.get_logger(__name__)


class EmailTask(Task):
    """Base task for email operations."""

    _email_service: EmailService | None = None

    @property
    def email_service(self) -> EmailService:
        """Lazy initialization of EmailService."""
        if self._email_service is None:
            self._email_service = EmailService()

        return self._email_service


@celery_app.task(
    bind=True,
    base=EmailTask,
    max_retries=settings.celery_email_max_retries,
    autoretry_for=(Exception,),
    retry_backoff=settings.celery_email_retry_backoff,
    retry_backoff_max=600,
    retry_jitter=True,
)
def send_welcome_email_task(
    self,
    username: str,
    email: str,
) -> bool:
    """Send welcome email to a new user using Celery.

    The task is automatically retried when an exception occurs.

    Args:
        username: Username of the new user.
        email: Email address of the new user.

    Returns:
        True if the email was sent successfully.
        False if the email service intentionally reports that
        the email was not sent.

    Important: no idempotency is implemented yet!
    """
    try:
        logger.info(
            "Sending welcome email via Celery",
            username=username,
            email=email,
            task_id=self.request.id,
            retry_count=self.request.retries,
        )

        result = asyncio.run(
            self.email_service.send_welcome_email(
                username,
                email,
            )
        )

        if result:
            logger.info(
                "Welcome email sent successfully via Celery",
                username=username,
                email=email,
                task_id=self.request.id,
            )
        else:
            logger.warning(
                "Welcome email was not sent",
                username=username,
                email=email,
                task_id=self.request.id,
            )

        return result

    except Exception:
        logger.exception(
            "Failed to send welcome email via Celery",
            username=username,
            email=email,
            task_id=self.request.id,
            retry_count=self.request.retries,
        )

        # Very important:
        # the exception must escape the task so that
        # Celery's autoretry_for can retry it.
        raise