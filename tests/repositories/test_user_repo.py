"""Tests for SQLAlchemyUserRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories import SQLAlchemyUserRepository
from app.domain.value_objects import UserUpdateData
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher

password_hasher = BcryptPasswordHasher()


@pytest.mark.unit
@pytest.mark.auth
class TestSQLAlchemyUserRepository:
    """Test suite for SQLAlchemyUserRepository."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession, test_role):
        """Test successful user creation."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        
        user = await repo.create_user(
            username="testuser",
            password="TestPassword123!"
        )
        await db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.hashed_password is not None
        assert user.is_active is True
        assert user.role_id == test_role.id
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, db_session: AsyncSession, test_user):
        """Test getting user by username."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        
        user = await repo.get_user_by_username(test_user.username)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
        assert user.role is not None
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user by username."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        
        user = await repo.get_user_by_username("nonexistent")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, db_session: AsyncSession, test_user):
        """Test getting user by ID."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        
        user = await repo.get_user_by_id(test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.username == test_user.username
        assert user.role is not None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user by ID."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        
        user = await repo.get_user_by_id(99999)
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_role(self, db_session: AsyncSession, test_user):
        """Test getting user role name."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        
        role_name = await repo.get_user_role(test_user.id)
        
        assert role_name == "user"
    
    @pytest.mark.asyncio
    async def test_update_user_username(self, db_session: AsyncSession, test_user):
        """Test updating user username."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        update_data = UserUpdateData(username="updated_username")
        
        updated_user = await repo.update_user(test_user, update_data)
        await db_session.commit()
        
        assert updated_user.username == "updated_username"
        assert updated_user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_password(self, db_session: AsyncSession, test_user):
        """Test updating user password."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        old_password = test_user.hashed_password
        update_data = UserUpdateData(
            password="NewPassword123!",
            password_confirm="NewPassword123!"
        )
        
        updated_user = await repo.update_user(test_user, update_data)
        await db_session.commit()
        
        assert updated_user.hashed_password != old_password
        assert updated_user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_both_fields(self, db_session: AsyncSession, test_user):
        """Test updating both username and password."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        old_password = test_user.hashed_password
        update_data = UserUpdateData(
            username="new_username",
            password="NewPassword123!",
            password_confirm="NewPassword123!"
        )
        
        updated_user = await repo.update_user(test_user, update_data)
        await db_session.commit()
        
        assert updated_user.username == "new_username"
        assert updated_user.hashed_password != old_password
        assert updated_user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, db_session: AsyncSession, test_user):
        """Test updating user with no changes."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        update_data = UserUpdateData()
        
        updated_user = await repo.update_user(test_user, update_data)
        await db_session.commit()
        
        assert updated_user.username == test_user.username
        assert updated_user.hashed_password == test_user.hashed_password
        assert updated_user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session: AsyncSession, test_user):
        """Test successful user deletion."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        user_id = test_user.id
        
        await repo.delete_user(test_user)
        await db_session.commit()
        
        deleted_user = await repo.get_user_by_id(user_id)
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_username_uniqueness(self, db_session: AsyncSession, test_role):
        """Test that usernames must be unique."""
        repo = SQLAlchemyUserRepository(db_session, password_hasher)
        
        await repo.create_user(
            username="duplicate_user",
            password="TestPassword123!"
        )
        await db_session.commit()
        
        # Attempt to create another user with same username
        with pytest.raises(Exception):  # Should raise integrity error
            await repo.create_user(
                username="duplicate_user",
                password="TestPassword123!"
            )
