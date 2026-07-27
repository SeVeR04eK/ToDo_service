import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import AdminService
from app.schemas import RoleCreate
from app.core.exceptions import UserNotFoundError, RoleNotFoundError, PermissionDeniedError
from tests.factories import RoleFactory


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
        
        assert user["id"] == test_user.id
        assert user["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_service_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user raises UserNotFoundError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(UserNotFoundError):
            await service.get_user_service(99999)

    @pytest.mark.asyncio
    async def test_permission_user_service_update_role(self, db_session: AsyncSession, test_user):
        """Test updating user role."""
        _admin_role = await RoleFactory.create_in_db(db_session, name="admin")
        
        service = AdminService(session=db_session)
        updated_user = await service.permission_user_service(user_id=test_user.id, role_name="admin", is_active=None)
        
        assert updated_user["role"]["name"] == "admin"

    @pytest.mark.asyncio
    async def test_permission_user_service_update_is_active(self, db_session: AsyncSession, test_user):
        """Test updating user is_active status."""
        service = AdminService(session=db_session)
        updated_user = await service.permission_user_service(user_id=test_user.id, role_name=None, is_active=False)
        
        assert updated_user["is_active"] is False

    @pytest.mark.asyncio
    async def test_permission_user_service_role_not_found(self, db_session: AsyncSession, test_user):
        """Test updating with non-existent role raises RoleNotFoundError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(RoleNotFoundError):
            await service.permission_user_service(user_id=test_user.id, role_name="nonexistent", is_active=None)

    @pytest.mark.asyncio
    async def test_permission_user_service_user_not_found(self, db_session: AsyncSession):
        """Test updating non-existent user raises UserNotFoundError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(UserNotFoundError):
            await service.permission_user_service(user_id=99999, role_name="user", is_active=None)

    @pytest.mark.asyncio
    async def test_delete_user_service_admin_forbidden(self, db_session: AsyncSession, test_admin_user):
        """Test that deleting admin user raises PermissionDeniedError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(PermissionDeniedError):
            await service.delete_user_service(test_admin_user.id)

    @pytest.mark.asyncio
    async def test_delete_user_service_user_not_found(self, db_session: AsyncSession):
        """Test deleting non-existent user raises UserNotFoundError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_user_service(99999)

    @pytest.mark.asyncio
    async def test_create_role_service_success(self, db_session: AsyncSession):
        """Test creating a new role."""
        service = AdminService(session=db_session)
        new_role = RoleCreate(name="moderator")
        role = await service.create_role_service(new_role)
        
        assert role["name"] == "moderator"

    @pytest.mark.asyncio
    async def test_create_role_service_duplicate(self, db_session: AsyncSession):
        """Test creating duplicate role raises error."""
        await RoleFactory.create_in_db(db_session, name="moderator")
        
        service = AdminService(session=db_session)
        new_role = RoleCreate(name="moderator")
        
        with pytest.raises(Exception):  # SQLAlchemy integrity error
            await service.create_role_service(new_role)

    @pytest.mark.asyncio
    async def test_get_tasks_service_user_not_found(self, db_session: AsyncSession):
        """Test getting tasks for non-existent user raises UserNotFoundError."""
        service = AdminService(session=db_session)
        from app.schemas import TasksPagination
        
        with pytest.raises(UserNotFoundError):
            await service.get_tasks_service(user_id=99999, task_status=None, pagination=TasksPagination())

    @pytest.mark.asyncio
    async def test_get_tasks_service_permission_denied(self, db_session: AsyncSession, test_admin_user):
        """Test getting tasks for admin user raises PermissionDeniedError."""
        service = AdminService(session=db_session)
        from app.schemas import TasksPagination
        
        with pytest.raises(PermissionDeniedError):
            await service.get_tasks_service(user_id=test_admin_user.id, task_status=None, pagination=TasksPagination())

    @pytest.mark.asyncio
    async def test_get_task_service_user_not_found(self, db_session: AsyncSession):
        """Test getting task for non-existent user raises UserNotFoundError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(UserNotFoundError):
            await service.get_task_service(task_id=1, user_id=99999)

    @pytest.mark.asyncio
    async def test_get_task_service_permission_denied(self, db_session: AsyncSession, test_admin_user):
        """Test getting task for admin user raises PermissionDeniedError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(PermissionDeniedError):
            await service.get_task_service(task_id=1, user_id=test_admin_user.id)

    @pytest.mark.asyncio
    async def test_update_task_service_user_not_found(self, db_session: AsyncSession):
        """Test updating task for non-existent user raises UserNotFoundError."""
        service = AdminService(session=db_session)
        from app.schemas import TaskUpdate
        
        with pytest.raises(UserNotFoundError):
            await service.update_task_service(task_id=1, user_id=99999, task_update=TaskUpdate())

    @pytest.mark.asyncio
    async def test_update_task_service_permission_denied(self, db_session: AsyncSession, test_admin_user):
        """Test updating task for admin user raises PermissionDeniedError."""
        service = AdminService(session=db_session)
        from app.schemas import TaskUpdate
        
        with pytest.raises(PermissionDeniedError):
            await service.update_task_service(task_id=1, user_id=test_admin_user.id, task_update=TaskUpdate())

    @pytest.mark.asyncio
    async def test_delete_task_service_user_not_found(self, db_session: AsyncSession):
        """Test deleting task for non-existent user raises UserNotFoundError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_task_service(task_id=1, user_id=99999)

    @pytest.mark.asyncio
    async def test_delete_task_service_permission_denied(self, db_session: AsyncSession, test_admin_user):
        """Test deleting task for admin user raises PermissionDeniedError."""
        service = AdminService(session=db_session)
        
        with pytest.raises(PermissionDeniedError):
            await service.delete_task_service(task_id=1, user_id=test_admin_user.id)
