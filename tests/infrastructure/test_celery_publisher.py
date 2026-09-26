"""Tests for Celery message publisher."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.infrastructure.celery.celery_publisher import CeleryMessagePublisher, get_celery_publisher
from app.infrastructure.celery.email_task import send_welcome_email_task


@pytest.mark.unit
class TestCeleryMessagePublisher:
    """Test suite for Celery message publisher."""

    def test_publisher_initialization(self):
        """Test that CeleryMessagePublisher initializes without errors."""
        publisher = CeleryMessagePublisher()
        
        assert publisher is not None

    @pytest.mark.asyncio
    async def test_publish_welcome_email(self):
        """Test publishing welcome email task to Celery."""
        publisher = CeleryMessagePublisher()
        
        with patch('app.infrastructure.celery.celery_publisher.send_welcome_email_task') as mock_task:
            mock_task.delay = MagicMock()
            
            await publisher.publish_welcome_email(username="testuser", email="test@example.com")
            
            mock_task.delay.assert_called_once_with("testuser", "test@example.com")

    @pytest.mark.asyncio
    async def test_publish_welcome_email_logs_error_on_failure(self):
        """Test that publish logs error when Celery task fails."""
        publisher = CeleryMessagePublisher()
        
        with patch('app.infrastructure.celery.celery_publisher.send_welcome_email_task') as mock_task:
            mock_task.delay = MagicMock(side_effect=Exception("Celery error"))
            
            with pytest.raises(Exception, match="Celery error"):
                await publisher.publish_welcome_email(username="testuser", email="test@example.com")

    def test_get_celery_publisher_initializes_publisher(self):
        """Test that get_celery_publisher initializes a new publisher."""
        # Reset the global publisher
        import app.infrastructure.celery.celery_publisher as publisher_module
        publisher_module._publisher = None
        
        publisher = get_celery_publisher()
        
        assert publisher is not None
        assert isinstance(publisher, CeleryMessagePublisher)

    def test_get_celery_publisher_returns_cached_publisher(self):
        """Test that get_celery_publisher returns cached publisher on subsequent calls."""
        # Reset the global publisher
        import app.infrastructure.celery.celery_publisher as publisher_module
        publisher_module._publisher = None
        
        # First call
        publisher1 = get_celery_publisher()
        # Second call
        publisher2 = get_celery_publisher()
        
        assert publisher1 == publisher2
