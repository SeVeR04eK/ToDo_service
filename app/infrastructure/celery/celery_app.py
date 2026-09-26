import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "todo_service",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.infrastructure.celery.email_task", "app.infrastructure.celery.token_cleanup_task"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=settings.celery_task_track_started,
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    worker_prefetch_multiplier=settings.celery_worker_prefetch_multiplier,
    worker_max_tasks_per_child=settings.celery_worker_max_tasks_per_child,
    result_expires=3600,  # Results expire after 1 hour
    task_acks_late=True,  # Ack only after task execution
    task_reject_on_worker_lost=True,  # Requeue task if worker dies
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "clean-expired-tokens": {
        "task": "app.infrastructure.celery.token_cleanup_task.clean_expired_tokens_task",
        "schedule": settings.celery_token_cleanup_interval_hours * 3600,  # Convert hours to seconds
    },
}
