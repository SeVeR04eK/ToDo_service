"""Tests for email service."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.infrastructure.services.email_service import EmailService
from app.core.config import settings


@pytest.mark.unit
class TestEmailService:
    """Test suite for email service."""

    def test_email_service_initialization(self):
        """Test that EmailService initializes with settings."""
        service = EmailService()
        
        assert service.smtp_host == settings.smtp_host
        assert service.smtp_port == settings.smtp_port
        assert service.smtp_username == settings.smtp_username
        assert service.smtp_password == settings.smtp_password
        assert service.smtp_from_email == settings.smtp_from_email
        assert service.smtp_use_tls == settings.smtp_use_tls

    @pytest.mark.asyncio
    async def test_send_welcome_email_success(self):
        """Test sending welcome email successfully."""
        service = EmailService()
        service.smtp_username = "test@example.com"
        service.smtp_password = "password"
        
        with patch('app.infrastructure.services.email_service.aiosmtplib.send') as mock_send:
            mock_send.return_value = None
            
            result = await service.send_welcome_email("testuser", "user@example.com")
            
            assert result is True
            mock_send.assert_called_once()
            call_kwargs = mock_send.call_args[1]
            assert call_kwargs['hostname'] == settings.smtp_host
            assert call_kwargs['port'] == settings.smtp_port
            assert call_kwargs['username'] == "test@example.com"
            assert call_kwargs['password'] == "password"
            assert call_kwargs['start_tls'] == settings.smtp_use_tls

    @pytest.mark.asyncio
    async def test_send_welcome_email_no_credentials(self):
        """Test sending email when credentials are not configured."""
        service = EmailService()
        service.smtp_username = None
        service.smtp_password = None
        
        with patch('app.infrastructure.services.email_service.aiosmtplib.send') as mock_send:
            result = await service.send_welcome_email("testuser", "user@example.com")
            
            assert result is False
            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_welcome_email_empty_credentials(self):
        """Test sending email when credentials are empty strings."""
        service = EmailService()
        service.smtp_username = ""
        service.smtp_password = ""
        
        with patch('app.infrastructure.services.email_service.aiosmtplib.send') as mock_send:
            result = await service.send_welcome_email("testuser", "user@example.com")
            
            assert result is False
            mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_welcome_email_send_failure(self):
        """Test sending email when SMTP send fails."""
        service = EmailService()
        service.smtp_username = "test@example.com"
        service.smtp_password = "password"
        
        with patch('app.infrastructure.services.email_service.aiosmtplib.send') as mock_send:
            mock_send.side_effect = Exception("SMTP error")
            
            result = await service.send_welcome_email("testuser", "user@example.com")
            
            assert result is False
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_welcome_email_message_format(self):
        """Test that email message is formatted correctly."""
        service = EmailService()
        service.smtp_username = "test@example.com"
        service.smtp_password = "password"
        service.smtp_from_email = "noreply@example.com"
        
        with patch('app.infrastructure.services.email_service.aiosmtplib.send') as mock_send:
            mock_send.return_value = None
            
            await service.send_welcome_email("testuser", "user@example.com")
            
            # Get the message that was passed to send
            call_args = mock_send.call_args
            message = call_args[0][0]
            
            assert message["From"] == "noreply@example.com"
            assert message["To"] == "user@example.com"
            assert message["Subject"] == "Welcome!"
            assert "testuser" in str(message.get_content())
            assert "successfully created" in str(message.get_content())
