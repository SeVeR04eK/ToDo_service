import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import UserService
from app.schemas import UserCreate, UserUpdate
from tests.factories import UserFactory, RoleFactory


@pytest.mark.unit
class TestUserService:
    """Test UserService business logic."""

    @pytest.mark.asyncio
    async def test_create_user_service_success(self, db_session: AsyncSession):
        """Test creating a new user."""
        _user_role = await RoleFactory.create_in_db(db_session, name="user")
        
        service = UserService(session=db_session)
        user_data = UserCreate(
            username="newuser",
            password="password123",
            password_confirm="password123"
        )
        
        user = await service.create_user_service(user_data)
        
        assert user["username"] == "newuser"
        assert user["id"] is not None
        assert user["role"]["name"] == "user"

    @pytest.mark.asyncio
    async def test_get_user_service_success(self, db_session: AsyncSession, test_user):
        """Test getting user info."""
        service = UserService(session=db_session)
        user = await service.get_user_service(test_user.id)
        
        assert user["id"] == test_user.id
        assert user["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_update_user_service_username(self, db_session: AsyncSession, test_user):
        """Test updating user username."""
        service = UserService(session=db_session)
        user_update = UserUpdate(username="updated_user")
        
        updated_user = await service.update_user_service(test_user.id, user_update)
        
        assert updated_user["username"] == "updated_user"

    @pytest.mark.asyncio
    async def test_update_user_service_password(self, db_session: AsyncSession, test_user):
        """Test updating user password."""
        service = UserService(session=db_session)
        user_update = UserUpdate(
            password="newpassword123",
            password_confirm="newpassword123"
        )
        
        updated_user = await service.update_user_service(test_user.id, user_update)
        
        assert updated_user["id"] == test_user.id

    @pytest.mark.asyncio
    async def test_update_user_service_both_fields(self, db_session: AsyncSession, test_user):
        """Test updating both username and password."""
        service = UserService(session=db_session)
        user_update = UserUpdate(
            username="updated_user",
            password="newpassword123",
            password_confirm="newpassword123"
        )
        
        updated_user = await service.update_user_service(test_user.id, user_update)
        
        assert updated_user["username"] == "updated_user"

    @pytest.mark.asyncio
    async def test_delete_user_service_success(self, db_session: AsyncSession):
        """Test deleting a user."""
        user = await UserFactory.create_in_db(db_session, username="to_delete")
        
        service = UserService(session=db_session)
        await service.delete_user_service(user.id)
        
        # Verify user is deleted
        from app.repositories import UserRepository
        user_repo = UserRepository(session=db_session)
        deleted_user = await user_repo.get_user_by_id(user.id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_create_user_service_username_exists(self, db_session: AsyncSession):
        """Test creating user with existing username raises UsernameAlreadyExistsError."""
        from app.core.exceptions import UsernameAlreadyExistsError
        from app.schemas import UserCreate
        
        await UserFactory.create_in_db(db_session, username="existing")
        
        service = UserService(session=db_session)
        user_data = UserCreate(
            username="existing",
            password="password123",
            password_confirm="password123"
        )
        
        with pytest.raises(UsernameAlreadyExistsError):
            await service.create_user_service(user_data)

    @pytest.mark.asyncio
    async def test_update_user_service_not_found(self, db_session: AsyncSession):
        """Test updating non-existent user raises UserNotFoundError."""
        from app.core.exceptions import UserNotFoundError
        from app.schemas import UserUpdate
        
        service = UserService(session=db_session)
        user_update = UserUpdate(username="updated")
        
        with pytest.raises(UserNotFoundError):
            await service.update_user_service(99999, user_update)

    @pytest.mark.asyncio
    async def test_delete_user_service_not_found(self, db_session: AsyncSession):
        """Test deleting non-existent user raises UserNotFoundError."""
        from app.core.exceptions import UserNotFoundError
        
        service = UserService(session=db_session)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_user_service(99999)
