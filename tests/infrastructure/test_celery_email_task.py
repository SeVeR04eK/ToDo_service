"""Tests for Celery email task."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.celery.email_task import EmailTask, send_welcome_email_task


@pytest.mark.unit
class TestCeleryEmailTask:
    """Test suite for Celery email task."""

    def test_email_task_initialization(self):
        """Test that EmailTask base class initializes correctly."""
        task = EmailTask()

        assert task._email_service is None

    @patch("app.infrastructure.celery.email_task.EmailService")
    def test_email_service_lazy_initialization(self, mock_email_service_class):
        """Test that email service is lazily initialized."""
        task = EmailTask()

        service1 = task.email_service
        service2 = task.email_service

        assert service1 is service2
        assert service1 is not None
        mock_email_service_class.assert_called_once()

    @patch("app.infrastructure.celery.email_task.asyncio.run")
    @patch("app.infrastructure.celery.email_task.EmailService")
    def test_send_welcome_email_task_success(
        self,
        mock_email_service_class,
        mock_asyncio_run,
    ):
        """Test successful email sending via Celery task."""
        mock_email_service = MagicMock()
        mock_email_service_class.return_value = mock_email_service

        mock_asyncio_run.return_value = True

        result = send_welcome_email_task(
            "testuser",
            "test@example.com",
        )

        assert result is True

        mock_asyncio_run.assert_called_once()
        mock_email_service_class.assert_called_once()

    @patch("app.infrastructure.celery.email_task.asyncio.run")
    @patch("app.infrastructure.celery.email_task.EmailService")
    def test_send_welcome_email_task_no_credentials(
        self,
        mock_email_service_class,
        mock_asyncio_run,
    ):
        """Test email sending when credentials are not configured."""
        mock_email_service = MagicMock()
        mock_email_service_class.return_value = mock_email_service

        mock_asyncio_run.return_value = False

        result = send_welcome_email_task(
            "testuser",
            "test@example.com",
        )

        assert result is False

        mock_asyncio_run.assert_called_once()

    @patch("app.infrastructure.celery.email_task.asyncio.run")
    @patch("app.infrastructure.celery.email_task.EmailService")
    def test_send_welcome_email_task_failure_with_retry(
        self,
        mock_email_service_class,
        mock_asyncio_run,
    ):
        """Test email sending failure triggers exception for Celery retry."""
        mock_email_service = MagicMock()
        mock_email_service_class.return_value = mock_email_service

        mock_asyncio_run.side_effect = Exception("SMTP error")

        with pytest.raises(Exception, match="SMTP error"):
            send_welcome_email_task(
                "testuser",
                "test@example.com",
            )

        mock_asyncio_run.assert_called_once()

    @patch("app.infrastructure.celery.email_task.asyncio.run")
    @patch("app.infrastructure.celery.email_task.EmailService")
    def test_send_welcome_email_task_max_retries_exceeded(
        self,
        mock_email_service_class,
        mock_asyncio_run,
    ):
        """Test that task raises an exception when email sending fails."""
        mock_email_service = MagicMock()
        mock_email_service_class.return_value = mock_email_service

        mock_asyncio_run.side_effect = Exception("SMTP error")

        with pytest.raises(Exception, match="SMTP error"):
            send_welcome_email_task(
                "testuser",
                "test@example.com",
            )

        mock_asyncio_run.assert_called_once()