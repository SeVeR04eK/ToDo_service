import pytest
from unittest.mock import AsyncMock

from app.application.services import UserService
from app.domain.interfaces import UserRepository
from app.domain.entities import User, Role
from app.presentation.api.schemas import UserCreate, UserUpdate
from app.core.exceptions import UsernameAlreadyExistsError, UserNotFoundError


@pytest.mark.unit
class TestUserService:
    """Test UserService business logic."""

    @pytest.mark.asyncio
    async def test_create_user_service_success(self):
        """Test creating a new user."""
        # Setup mock repository
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_username.return_value = None
        
        mock_user = User(id=1, username="newuser", hashed_password="hashed", is_active=True, role_id=1, role=Role(id=1, name="user"))
        mock_repo.create_user.return_value = mock_user
        
        service = UserService(repository=mock_repo)
        user_data = UserCreate(
            username="newuser",
            password="password123",
            password_confirm="password123"
        )
        
        user = await service.create_user_service(user_data)
        
        assert user.username == "newuser"
        assert user.id is not None
        assert user.role.name == "user"
        mock_repo.get_user_by_username.assert_called_once_with(username="newuser")
        mock_repo.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_service_success(self):
        """Test getting user info."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.get_user_by_id.return_value = mock_user
        
        service = UserService(repository=mock_repo)
        user = await service.get_user_service(1)
        
        assert user.id == 1
        assert user.username == "testuser"
        mock_repo.get_user_by_id.assert_called_once_with(user_id=1)

    @pytest.mark.asyncio
    async def test_update_user_service_username(self):
        """Test updating user username."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.get_user_by_id.return_value = mock_user
        mock_repo.get_user_by_username.return_value = None
        
        updated_user = User(id=1, username="updated_user", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.update_user.return_value = updated_user
        
        service = UserService(repository=mock_repo)
        user_update = UserUpdate(username="updated_user")
        
        result = await service.update_user_service(1, user_update)
        
        assert result.username == "updated_user"
        mock_repo.get_user_by_id.assert_called_once_with(user_id=1)
        mock_repo.get_user_by_username.assert_called_once_with(username="updated_user")
        mock_repo.update_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_service_password(self):
        """Test updating user password."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.get_user_by_id.return_value = mock_user
        
        updated_user = User(id=1, username="testuser", hashed_password="new_hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.update_user.return_value = updated_user
        
        service = UserService(repository=mock_repo)
        user_update = UserUpdate(
            password="newpassword123",
            password_confirm="newpassword123"
        )
        
        result = await service.update_user_service(1, user_update)
        
        assert result.id == 1
        mock_repo.get_user_by_id.assert_called_once_with(user_id=1)
        mock_repo.update_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_service_both_fields(self):
        """Test updating both username and password."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.get_user_by_id.return_value = mock_user
        mock_repo.get_user_by_username.return_value = None
        
        updated_user = User(id=1, username="updated_user", hashed_password="new_hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.update_user.return_value = updated_user
        
        service = UserService(repository=mock_repo)
        user_update = UserUpdate(
            username="updated_user",
            password="newpassword123",
            password_confirm="newpassword123"
        )
        
        result = await service.update_user_service(1, user_update)
        
        assert result.username == "updated_user"
        mock_repo.get_user_by_id.assert_called_once_with(user_id=1)
        mock_repo.get_user_by_username.assert_called_once_with(username="updated_user")
        mock_repo.update_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_service_success(self):
        """Test deleting a user."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="to_delete", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.get_user_by_id.return_value = mock_user
        mock_repo.delete_user.return_value = None
        
        service = UserService(repository=mock_repo)
        await service.delete_user_service(1)
        
        mock_repo.get_user_by_id.assert_called_once_with(user_id=1)
        mock_repo.delete_user.assert_called_once_with(user=mock_user)

    @pytest.mark.asyncio
    async def test_create_user_service_username_exists(self):
        """Test creating user with existing username raises UsernameAlreadyExistsError."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="existing", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_repo.get_user_by_username.return_value = mock_user
        
        service = UserService(repository=mock_repo)
        user_data = UserCreate(
            username="existing",
            password="password123",
            password_confirm="password123"
        )
        
        with pytest.raises(UsernameAlreadyExistsError):
            await service.create_user_service(user_data)

    @pytest.mark.asyncio
    async def test_update_user_service_not_found(self):
        """Test updating non-existent user raises UserNotFoundError."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_id.return_value = None
        
        service = UserService(repository=mock_repo)
        user_update = UserUpdate(username="updated")
        
        with pytest.raises(UserNotFoundError):
            await service.update_user_service(99999, user_update)

    @pytest.mark.asyncio
    async def test_delete_user_service_not_found(self):
        """Test deleting non-existent user raises UserNotFoundError."""
        mock_repo = AsyncMock(spec=UserRepository)
        mock_repo.get_user_by_id.return_value = None
        
        service = UserService(repository=mock_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_user_service(99999)
