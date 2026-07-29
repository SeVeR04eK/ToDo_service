"""Tests for SQLAlchemyUserRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import SQLAlchemyUserRepository
from app.schemas import UserCreate, UserUpdate
from tests.factories import UserFactory


@pytest.mark.unit
@pytest.mark.auth
class TestSQLAlchemyUserRepository:
    """Test suite for SQLAlchemyUserRepository."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession, test_role):
        """Test successful user creation."""
        repo = SQLAlchemyUserRepository(db_session)
        user_data = UserCreate(
            username="testuser",
            password="TestPassword123!",
            password_confirm="TestPassword123!"
        )
        
        user = await repo.create_user(user_data)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.hashed_password is not None
        assert user.is_active is True
        assert user.role_id == test_role.id
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, db_session: AsyncSession, test_user):
        """Test getting user by username."""
        repo = SQLAlchemyUserRepository(db_session)
        
        user = await repo.get_user_by_username(test_user.username)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
        assert user.role is not None
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user by username."""
        repo = SQLAlchemyUserRepository(db_session)
        
        user = await repo.get_user_by_username("nonexistent")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, db_session: AsyncSession, test_user):
        """Test getting user by ID."""
        repo = SQLAlchemyUserRepository(db_session)
        
        user = await repo.get_user_by_id(test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
        assert user.role is not None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user by ID."""
        repo = SQLAlchemyUserRepository(db_session)
        
        user = await repo.get_user_by_id(99999)
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_role(self, db_session: AsyncSession, test_user):
        """Test getting user role name."""
        repo = SQLAlchemyUserRepository(db_session)
        
        role_name = await repo.get_user_role(test_user.id)
        
        assert role_name == "user"
    
    @pytest.mark.asyncio
    async def test_update_user_username(self, db_session: AsyncSession, test_user):
        """Test updating user username."""
        repo = SQLAlchemyUserRepository(db_session)
        update_data = UserUpdate(username="updated_username")
        
        updated_user = await repo.update_user(test_user, update_data)
        
        assert updated_user.username == "updated_username"
        assert updated_user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_password(self, db_session: AsyncSession, test_user):
        """Test updating user password."""
        repo = SQLAlchemyUserRepository(db_session)
        old_password = test_user.hashed_password
        update_data = UserUpdate(
            password="NewPassword123!",
            password_confirm="NewPassword123!"
        )
        
        updated_user = await repo.update_user(test_user, update_data)
        
        assert updated_user.hashed_password != old_password
        assert updated_user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_both_fields(self, db_session: AsyncSession, test_user):
        """Test updating both username and password."""
        repo = SQLAlchemyUserRepository(db_session)
        old_password = test_user.hashed_password
        update_data = UserUpdate(
            username="new_username",
            password="NewPassword123!",
            password_confirm="NewPassword123!"
        )
        
        updated_user = await repo.update_user(test_user, update_data)
        
        assert updated_user.username == "new_username"
        assert updated_user.hashed_password != old_password
        assert updated_user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, db_session: AsyncSession, test_user):
        """Test updating user with no changes."""
        repo = SQLAlchemyUserRepository(db_session)
        update_data = UserUpdate()
        
        updated_user = await repo.update_user(test_user, update_data)
        
        assert updated_user.username == test_user.username
        assert updated_user.hashed_password == test_user.hashed_password
        assert updated_user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session: AsyncSession, test_user):
        """Test successful user deletion."""
        repo = SQLAlchemyUserRepository(db_session)
        user_id = test_user.id
        
        await repo.delete_user(test_user)
        
        deleted_user = await repo.get_user_by_id(user_id)
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_username_uniqueness(self, db_session: AsyncSession, test_role):
        """Test that usernames must be unique."""
        repo = SQLAlchemyUserRepository(db_session)
        user_data = UserCreate(
            username="duplicate_user",
            password="TestPassword123!",
            password_confirm="TestPassword123!"
        )
        
        await repo.create_user(user_data)
        
        # Attempt to create another user with same username
        with pytest.raises(Exception):  # Should raise integrity error
            await repo.create_user(user_data)
