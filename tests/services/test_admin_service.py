import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.services import AdminService
from app.schemas import UserPermission, RoleCreate
from tests.factories import UserFactory, RoleFactory


@pytest.mark.unit
class TestAdminService:
    """Test AdminService business logic."""

    @pytest.mark.asyncio
    async def test_get_users_service_with_offset(self, db_session: AsyncSession):
        """Test that offset with username returns empty list."""
        service = AdminService(session=db_session)
        result = await service.get_users_service(username="test", limit=None, offset=1)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_service_success(self, db_session: AsyncSession, test_user):
        """Test getting user by ID."""
        service = AdminService(session=db_session)
        user = await service.get_user_service(test_user.id)
        
        assert user.id == test_user.id
        assert user.username == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_service_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user raises 404."""
        service = AdminService(session=db_session)
        
        with pytest.raises(HTTPException) as exc:
            await service.get_user_service(99999)
        
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_permission_user_service_update_role(self, db_session: AsyncSession, test_user):
        """Test updating user role."""
        admin_role = await RoleFactory.create_in_db(db_session, name="admin")
        
        service = AdminService(session=db_session)
        user_perm = UserPermission(is_active=True, role="admin")
        updated_user = await service.permission_user_service(test_user.id, user_perm)
        
        assert updated_user.role.name == "admin"

    @pytest.mark.asyncio
    async def test_permission_user_service_update_is_active(self, db_session: AsyncSession, test_user):
        """Test updating user is_active status."""
        service = AdminService(session=db_session)
        user_perm = UserPermission(is_active=False, role=None)
        updated_user = await service.permission_user_service(test_user.id, user_perm)
        
        assert updated_user.is_active is False

    @pytest.mark.asyncio
    async def test_permission_user_service_role_not_found(self, db_session: AsyncSession, test_user):
        """Test updating with non-existent role raises 404."""
        service = AdminService(session=db_session)
        user_perm = UserPermission(is_active=True, role="nonexistent")
        
        with pytest.raises(HTTPException) as exc:
            await service.permission_user_service(test_user.id, user_perm)
        
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_permission_user_service_user_not_found(self, db_session: AsyncSession):
        """Test updating non-existent user raises 404."""
        service = AdminService(session=db_session)
        user_perm = UserPermission(is_active=True, role="user")
        
        with pytest.raises(HTTPException) as exc:
            await service.permission_user_service(99999, user_perm)
        
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_service_admin_forbidden(self, db_session: AsyncSession, test_admin_user):
        """Test that deleting admin user raises 403."""
        service = AdminService(session=db_session)
        
        with pytest.raises(HTTPException) as exc:
            await service.delete_user_service(test_admin_user.id)
        
        assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_user_service_user_not_found(self, db_session: AsyncSession):
        """Test deleting non-existent user raises 404."""
        service = AdminService(session=db_session)
        
        with pytest.raises(HTTPException) as exc:
            await service.delete_user_service(99999)
        
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_role_service_success(self, db_session: AsyncSession):
        """Test creating a new role."""
        service = AdminService(session=db_session)
        new_role = RoleCreate(name="moderator")
        role = await service.create_role_service(new_role)
        
        assert role.name == "moderator"

    @pytest.mark.asyncio
    async def test_create_role_service_duplicate(self, db_session: AsyncSession):
        """Test creating duplicate role raises error."""
        await RoleFactory.create_in_db(db_session, name="moderator")
        
        service = AdminService(session=db_session)
        new_role = RoleCreate(name="moderator")
        
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            await service.create_role_service(new_role)
