import asyncio

import structlog
from celery import Task

from app.core.config import settings
from app.infrastructure.celery.celery_app import celery_app
from app.infrastructure.redis.client import get_redis_client
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


async def _send_welcome_email(
    email_service: EmailService,
    redis,
    username: str,
    email: str,
    idempotency_key: str,
) -> bool:
    """Send welcome email with Redis-based idempotency."""

    # Check whether the email was already sent.
    if await redis.exists(idempotency_key):
        return True

    # Send the email.
    result = await email_service.send_welcome_email(
        username,
        email,
    )

    # Mark as sent only after successful delivery.
    if result:
        await redis.set(
            idempotency_key,
            "sent",
            ex=60 * 60 * 24 * 30,
        )

    return result


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

    Redis is used for idempotency. A key is created only after
    the email has been successfully sent.

    Args:
        username: Username of the new user.
        email: Email address of the new user.

    Returns:
        True if the email was sent successfully or was already sent.
        False if the email service intentionally did not send it.

    Raises:
        Exception: If Redis or the email service raises an exception.
            Celery will automatically retry the task.
    """

    idempotency_key = f"welcome-email:{email}"
    redis = get_redis_client()

    try:
        logger.info(
            "Processing welcome email task",
            username=username,
            email=email,
            task_id=self.request.id,
            retry_count=self.request.retries,
        )

        result = asyncio.run(
            _send_welcome_email(
                email_service=self.email_service,
                redis=redis,
                username=username,
                email=email,
                idempotency_key=idempotency_key,
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
            "Failed to process welcome email task",
            username=username,
            email=email,
            task_id=self.request.id,
            retry_count=self.request.retries,
        )

        # The exception must escape the task so that
        # autoretry_for can retry it.
        raise