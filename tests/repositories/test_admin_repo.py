import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import SQLAlchemyAdminRepository
from app.schemas import OnlyUserPermission, RoleCreate
from tests.factories import UserFactory, RoleFactory


@pytest.mark.unit
class TestAdminRepository:
    """Test SQLAlchemyAdminRepository data access layer."""

    @pytest.mark.asyncio
    async def test_get_users_no_filters(self, db_session: AsyncSession):
        """Test getting all users without filters."""
        await UserFactory.create_in_db(db_session, username="user1")
        await UserFactory.create_in_db(db_session, username="user2")
        
        repo = SQLAlchemyAdminRepository(session=db_session)
        users = await repo.get_users(limit=None, offset=None)
        
        assert len(users) >= 2

    @pytest.mark.asyncio
    async def test_get_users_with_limit(self, db_session: AsyncSession):
        """Test getting users with limit."""
        for i in range(5):
            await UserFactory.create_in_db(db_session, username=f"user{i}")
        
        repo = SQLAlchemyAdminRepository(session=db_session)
        users = await repo.get_users(limit=3, offset=None)
        
        assert len(users) == 3

    @pytest.mark.asyncio
    async def test_get_users_with_offset(self, db_session: AsyncSession):
        """Test getting users with offset."""
        for i in range(5):
            await UserFactory.create_in_db(db_session, username=f"user{i}")
        
        repo = SQLAlchemyAdminRepository(session=db_session)
        users = await repo.get_users(limit=None, offset=2)
        
        assert len(users) >= 3

    @pytest.mark.asyncio
    async def test_get_users_with_limit_and_offset(self, db_session: AsyncSession):
        """Test getting users with both limit and offset."""
        for i in range(10):
            await UserFactory.create_in_db(db_session, username=f"user{i}")
        
        repo = SQLAlchemyAdminRepository(session=db_session)
        users = await repo.get_users(limit=3, offset=5)
        
        assert len(users) == 3

    @pytest.mark.asyncio
    async def test_user_perm_update_is_active(self, db_session: AsyncSession, test_user):
        """Test updating user is_active field."""
        repo = SQLAlchemyAdminRepository(session=db_session)
        user_perm = OnlyUserPermission(is_active=False, role_id=None)
        
        updated_user = await repo.user_perm(test_user, user_perm)
        
        assert updated_user.is_active is False

    @pytest.mark.asyncio
    async def test_user_perm_update_role_id(self, db_session: AsyncSession, test_user):
        """Test updating user role_id."""
        admin_role = await RoleFactory.create_in_db(db_session, name="admin")
        
        repo = SQLAlchemyAdminRepository(session=db_session)
        user_perm = OnlyUserPermission(is_active=True, role_id=admin_role.id)
        
        updated_user = await repo.user_perm(test_user, user_perm)
        
        assert updated_user.role_id == admin_role.id

    @pytest.mark.asyncio
    async def test_user_perm_update_both_fields(self, db_session: AsyncSession, test_user):
        """Test updating both is_active and role_id."""
        admin_role = await RoleFactory.create_in_db(db_session, name="admin")
        
        repo = SQLAlchemyAdminRepository(session=db_session)
        user_perm = OnlyUserPermission(is_active=False, role_id=admin_role.id)
        
        updated_user = await repo.user_perm(test_user, user_perm)
        
        assert updated_user.is_active is False
        assert updated_user.role_id == admin_role.id

    @pytest.mark.asyncio
    async def test_user_perm_no_changes(self, db_session: AsyncSession, test_user):
        """Test updating with no changes."""
        repo = SQLAlchemyAdminRepository(session=db_session)
        user_perm = OnlyUserPermission(is_active=None, role_id=None)
        
        updated_user = await repo.user_perm(test_user, user_perm)
        
        assert updated_user.id == test_user.id

    @pytest.mark.asyncio
    async def test_create_role_success(self, db_session: AsyncSession):
        """Test creating a new role."""
        repo = SQLAlchemyAdminRepository(session=db_session)
        new_role = RoleCreate(name="moderator")
        
        role = await repo.create_role(new_role)
        
        assert role.name == "moderator"
        assert role.id is not None

    @pytest.mark.asyncio
    async def test_get_roles_success(self, db_session: AsyncSession):
        """Test getting all roles."""
        await RoleFactory.create_in_db(db_session, name="role1")
        await RoleFactory.create_in_db(db_session, name="role2")
        
        repo = SQLAlchemyAdminRepository(session=db_session)
        roles = await repo.get_roles()
        
        assert len(roles) >= 2

    @pytest.mark.asyncio
    async def test_get_role_id_by_name_success(self, db_session: AsyncSession):
        """Test getting role ID by name."""
        role = await RoleFactory.create_in_db(db_session, name="test_role")
        
        repo = SQLAlchemyAdminRepository(session=db_session)
        role_id = await repo.get_role_id_by_name("test_role")
        
        assert role_id == role.id

    @pytest.mark.asyncio
    async def test_get_role_id_by_name_not_found(self, db_session: AsyncSession):
        """Test getting role ID for non-existent role."""
        repo = SQLAlchemyAdminRepository(session=db_session)
        role_id = await repo.get_role_id_by_name("nonexistent")
        
        assert role_id is None
