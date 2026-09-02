import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services import UserService
from app.application.dto import CreateUserDTO, UpdateUserDTO
from app.application.interfaces import UserCache
from app.domain.interfaces import UnitOfWork, PasswordValidator, PasswordHasher
from app.domain.entities import User, Role
from app.domain.exceptions import UsernameAlreadyExistsError, UserNotFoundError


@pytest.mark.unit
class TestUserService:
    """Test UserService business logic."""

    @pytest.mark.asyncio
    async def test_create_user_service_success(self):
        """Test creating a new user."""
        # Setup mock repository
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_username.return_value = None
        
        mock_user = User(id=1, username="newuser", hashed_password="hashed", is_active=True, role_id=1, role=Role(id=1, name="user"))
        mock_uow.user_repository.create_user.return_value = mock_user
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None
        
        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        user_data = CreateUserDTO(
            username="newuser",
            password="SecurePassword123",
            password_confirm="SecurePassword123"
        )
        
        user = await service.create_user_service(user_data)
        
        assert user.username == "newuser"
        assert user.id is not None
        assert user.role.name == "user"
        mock_uow.user_repository.get_user_by_username.assert_called_once_with(username="newuser")
        mock_uow.user_repository.create_user.assert_called_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_user_service_success(self):
        """Test getting user info."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user

        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        mock_user_cache.get_user.return_value = None
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        user = await service.get_user_service(1)

        assert user.id == 1
        assert user.username == "testuser"
        mock_user_cache.get_user.assert_called_once_with(1)
        mock_uow.user_repository.get_user_by_id.assert_called_once_with(user_id=1)
        mock_user_cache.set_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_service_username(self):
        """Test updating user username."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        mock_uow.user_repository.get_user_by_username.return_value = None

        updated_user = User(id=1, username="updated_user", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.update_user.return_value = updated_user
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None

        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        user_update = UpdateUserDTO(username="updated_user")

        result = await service.update_user_service(1, user_update)

        assert result.username == "updated_user"
        mock_uow.user_repository.get_user_by_id.assert_called_once_with(user_id=1)
        mock_uow.user_repository.get_user_by_username.assert_called_once_with(username="updated_user")
        mock_uow.user_repository.update_user.assert_called_once()
        mock_uow.commit.assert_awaited_once()
        mock_user_cache.delete_user.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_update_user_service_password(self):
        """Test updating user password."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user

        updated_user = User(id=1, username="testuser", hashed_password="new_hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.update_user.return_value = updated_user
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None

        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        user_update = UpdateUserDTO(
            password="NewSecurePass123",
            password_confirm="NewSecurePass123",
            previous_password="oldpassword"
        )

        result = await service.update_user_service(1, user_update)

        assert result.id == 1
        mock_uow.user_repository.get_user_by_id.assert_called_once_with(user_id=1)
        mock_uow.user_repository.update_user.assert_called_once()
        mock_uow.commit.assert_awaited_once()
        mock_user_cache.delete_user.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_update_user_service_both_fields(self):
        """Test updating both username and password."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        mock_uow.user_repository.get_user_by_username.return_value = None

        updated_user = User(id=1, username="updated_user", hashed_password="new_hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.update_user.return_value = updated_user
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None

        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        user_update = UpdateUserDTO(
            username="updated_user",
            password="NewSecurePass123",
            password_confirm="NewSecurePass123",
            previous_password="oldpassword"
        )

        result = await service.update_user_service(1, user_update)

        assert result.username == "updated_user"
        mock_uow.user_repository.get_user_by_id.assert_called_once_with(user_id=1)
        mock_uow.user_repository.get_user_by_username.assert_called_once_with(username="updated_user")
        mock_uow.user_repository.update_user.assert_called_once()
        mock_uow.commit.assert_awaited_once()
        mock_user_cache.delete_user.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_user_service_success(self):
        """Test deleting a user."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="to_delete", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        mock_uow.user_repository.delete_user.return_value = None
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None

        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        await service.delete_user_service(1)

        mock_uow.user_repository.get_user_by_id.assert_called_once_with(user_id=1)
        mock_uow.user_repository.delete_user.assert_called_once_with(user=mock_user)
        mock_uow.commit.assert_awaited_once()
        mock_user_cache.delete_user.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_create_user_service_username_exists(self):
        """Test creating user with existing username raises UsernameAlreadyExistsError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="existing", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_username.return_value = mock_user
        mock_uow.__aenter__.return_value = mock_uow
        
        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        user_data = CreateUserDTO(
            username="existing",
            password="SecurePassword123",
            password_confirm="SecurePassword123"
        )
        
        with pytest.raises(UsernameAlreadyExistsError):
            await service.create_user_service(user_data)
        
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_user_service_not_found(self):
        """Test updating non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        mock_uow.__aenter__.return_value = mock_uow
        
        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        user_update = UpdateUserDTO(username="updated")
        
        with pytest.raises(UserNotFoundError):
            await service.update_user_service(99999, user_update)
        
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_user_service_not_found(self):
        """Test deleting non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        mock_uow.__aenter__.return_value = mock_uow
        
        mock_password_validator = MagicMock(spec=PasswordValidator)
        mock_password_validator.validate.return_value = (True, "")
        mock_password_hasher = MagicMock(spec=PasswordHasher)
        mock_password_hasher.verify.return_value = True
        mock_user_cache = AsyncMock(spec=UserCache)
        service = UserService(unit_of_work=mock_uow, password_validator=mock_password_validator, password_hasher=mock_password_hasher, user_cache=mock_user_cache)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_user_service(99999)
        
        mock_uow.commit.assert_not_awaited()
