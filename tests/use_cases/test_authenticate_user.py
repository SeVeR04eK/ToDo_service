"""Tests for AuthenticateUserUseCase."""
import pytest
from unittest.mock import AsyncMock

from app.application.use_cases.authenticate_user import AuthenticateUserUseCase
from app.domain.interfaces import UserRepository, PasswordHasher
from app.domain.entities import User, Role
from app.domain.exceptions import InvalidCredentialsError


@pytest.mark.unit
@pytest.mark.auth
class TestAuthenticateUserUseCase:
    """Test suite for AuthenticateUserUseCase."""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful authentication."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_hasher = AsyncMock(spec=PasswordHasher)
        
        mock_role = Role(id=1, name="user")
        mock_user = User(
            id=1,
            username="testuser",
            hashed_password="hashed_password",
            is_active=True,
            role_id=1,
            role=mock_role
        )
        mock_repo.get_user_by_username.return_value = mock_user
        mock_hasher.verify.return_value = True
        
        use_case = AuthenticateUserUseCase(
            repository=mock_repo,
            password_hasher=mock_hasher
        )
        
        result = await use_case.execute("testuser", "password123")
        
        assert result.id == 1
        assert result.username == "testuser"
        mock_repo.get_user_by_username.assert_called_once_with("testuser")
        mock_hasher.verify.assert_called_once_with("password123", "hashed_password")

    @pytest.mark.asyncio
    async def test_execute_user_not_found(self):
        """Test authentication with non-existent user."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_hasher = AsyncMock(spec=PasswordHasher)
        
        mock_repo.get_user_by_username.return_value = None
        
        use_case = AuthenticateUserUseCase(
            repository=mock_repo,
            password_hasher=mock_hasher
        )
        
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute("nonexistent", "password123")
        
        mock_repo.get_user_by_username.assert_called_once_with("nonexistent")
        mock_hasher.verify.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_wrong_password(self):
        """Test authentication with wrong password."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_hasher = AsyncMock(spec=PasswordHasher)
        
        mock_role = Role(id=1, name="user")
        mock_user = User(
            id=1,
            username="testuser",
            hashed_password="hashed_password",
            is_active=True,
            role_id=1,
            role=mock_role
        )
        mock_repo.get_user_by_username.return_value = mock_user
        mock_hasher.verify.return_value = False
        
        use_case = AuthenticateUserUseCase(
            repository=mock_repo,
            password_hasher=mock_hasher
        )
        
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute("testuser", "wrongpassword")
        
        mock_repo.get_user_by_username.assert_called_once_with("testuser")
        mock_hasher.verify.assert_called_once_with("wrongpassword", "hashed_password")
