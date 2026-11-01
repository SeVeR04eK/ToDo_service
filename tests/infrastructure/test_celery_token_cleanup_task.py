"""Tests for Celery token cleanup task."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.infrastructure.celery.token_cleanup_task import (
    TokenCleanupTask,
    clean_expired_tokens_task,
)


@pytest.mark.unit
class TestCeleryTokenCleanupTask:
    """Test suite for Celery token cleanup task."""

    def test_token_cleanup_task_initialization(self):
        """Test that TokenCleanupTask base class initializes correctly."""
        task = TokenCleanupTask()

        assert task is not None

    @patch("app.infrastructure.celery.token_cleanup_task.TokenCleanupTask.loop")
    @patch(
        "app.infrastructure.celery.token_cleanup_task.SessionLocal"
    )
    @patch(
        "app.infrastructure.celery.token_cleanup_task.SQLAlchemyRefreshTokenRepository"
    )
    def test_clean_expired_tokens_task_success(
        self,
        mock_repo_class,
        mock_session_local,
        mock_loop,
    ):
        """Test successful token cleanup via Celery task."""
        mock_session = AsyncMock()
        mock_session_local.return_value = mock_session

        mock_repo = AsyncMock()
        mock_repo_class.return_value = mock_repo

        mock_loop.run_until_complete.return_value = 0

        result = clean_expired_tokens_task()

        assert result == 0
        mock_loop.run_until_complete.assert_called_once()

    @patch("app.infrastructure.celery.token_cleanup_task.TokenCleanupTask.loop")
    def test_clean_expired_tokens_task_database_error(
        self,
        mock_loop,
    ):
        """Test that database errors are propagated."""
        mock_loop.run_until_complete.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            clean_expired_tokens_task()

        mock_loop.run_until_complete.assert_called_once()

    @patch("app.infrastructure.celery.token_cleanup_task.TokenCleanupTask.loop")
    def test_clean_expired_tokens_task_session_error(
        self,
        mock_loop,
    ):
        """Test that session errors are propagated."""
        mock_loop.run_until_complete.side_effect = Exception("Session error")

        with pytest.raises(Exception, match="Session error"):
            clean_expired_tokens_task()

        mock_loop.run_until_complete.assert_called_once()