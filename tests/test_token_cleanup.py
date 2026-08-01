"""Tests for token cleanup module."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.infrastructure.background_tasks import clean_tokens_task


@pytest.mark.unit
class TestTokenCleanup:
    """Test token cleanup background task."""

    @pytest.mark.asyncio
    async def test_clean_tokens_task_success(self):
        """Test successful token cleanup."""
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_repo = AsyncMock()
        mock_repo.delete_expired_tokens = AsyncMock()
        
        with patch('app.infrastructure.background_tasks.token_cleanup.SessionLocal', return_value=mock_session):
            with patch('app.infrastructure.background_tasks.token_cleanup.get_refresh_token_repository_raw', return_value=mock_repo):
                # Run one iteration and cancel
                task = asyncio.create_task(clean_tokens_task())
                await asyncio.sleep(0.1)  # Let it run one iteration
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                mock_repo.delete_expired_tokens.assert_called_once()

    @pytest.mark.asyncio
    async def test_clean_tokens_task_handles_exception(self):
        """Test that task handles exceptions gracefully."""
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_repo = AsyncMock()
        mock_repo.delete_expired_tokens = AsyncMock(side_effect=Exception("Database error"))
        
        with patch('app.infrastructure.background_tasks.token_cleanup.SessionLocal', return_value=mock_session):
            with patch('app.infrastructure.background_tasks.token_cleanup.get_refresh_token_repository_raw', return_value=mock_repo):
                # Run one iteration and cancel
                task = asyncio.create_task(clean_tokens_task())
                await asyncio.sleep(0.1)  # Let it run one iteration
                task.cancel()
                
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
                # Should not raise exception, just log it
                mock_repo.delete_expired_tokens.assert_called_once()
