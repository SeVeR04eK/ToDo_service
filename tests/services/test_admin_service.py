import pytest
from unittest.mock import AsyncMock
from typing import List

from app.services import AdminService
from app.domain.interfaces import UserRepository, AdminRepository, TaskRepository
from app.domain.entities import User, Role, Task
from app.schemas import RoleCreate, OnlyUserPermission, TaskUpdate, TasksPagination
from app.core.exceptions import UserNotFoundError, RoleNotFoundError, PermissionDeniedError, RoleAlreadyExistsError, TaskNotFoundError
from app.domain.enums import TaskStatus


@pytest.mark.unit
class TestAdminService:
    """Test AdminService business logic."""

    @pytest.mark.asyncio
    async def test_get_users_service_with_offset(self):
        """Test that offset with username returns empty list."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        result = await service.get_users_service(username="test", limit=None, offset=1)
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_service_success(self):
        """Test getting user by ID."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        user = await service.get_user_service(1)
        
        assert user.id == 1
        assert user.username == "testuser"
        mock_user_repo.get_user_by_id.assert_called_once_with(user_id=1)

    @pytest.mark.asyncio
    async def test_get_user_service_not_found(self):
        """Test getting non-existent user raises UserNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        mock_user_repo.get_user_by_id.return_value = None
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.get_user_service(99999)

    @pytest.mark.asyncio
    async def test_permission_user_service_update_role(self):
        """Test updating user role."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_admin_repo.get_role_id_by_name.return_value = 2
        
        updated_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=Role(id=2, name="admin"))
        mock_admin_repo.user_perm.return_value = updated_user
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        updated = await service.permission_user_service(user_id=1, role_name="admin", is_active=None)
        
        assert updated.role.name == "admin"
        mock_admin_repo.get_role_id_by_name.assert_called_once_with("admin")

    @pytest.mark.asyncio
    async def test_permission_user_service_update_is_active(self):
        """Test updating user is_active status."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        updated_user = User(id=1, username="testuser", hashed_password="hashed", is_active=False, role_id=1, role=mock_role)
        mock_admin_repo.user_perm.return_value = updated_user
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        updated = await service.permission_user_service(user_id=1, role_name=None, is_active=False)
        
        assert updated.is_active is False

    @pytest.mark.asyncio
    async def test_permission_user_service_role_not_found(self):
        """Test updating with non-existent role raises RoleNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_admin_repo.get_role_id_by_name.return_value = None
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(RoleNotFoundError):
            await service.permission_user_service(user_id=1, role_name="nonexistent", is_active=None)

    @pytest.mark.asyncio
    async def test_permission_user_service_user_not_found(self):
        """Test updating non-existent user raises UserNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        mock_user_repo.get_user_by_id.return_value = None
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.permission_user_service(user_id=99999, role_name="user", is_active=None)

    @pytest.mark.asyncio
    async def test_delete_user_service_admin_forbidden(self):
        """Test that deleting admin user raises PermissionDeniedError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(PermissionDeniedError):
            await service.delete_user_service(1)

    @pytest.mark.asyncio
    async def test_delete_user_service_user_not_found(self):
        """Test deleting non-existent user raises UserNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        mock_user_repo.get_user_by_id.return_value = None
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_user_service(99999)

    @pytest.mark.asyncio
    async def test_create_role_service_success(self):
        """Test creating a new role."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_admin_repo.get_role_id_by_name.return_value = None
        mock_role = Role(id=1, name="moderator")
        mock_admin_repo.create_role.return_value = mock_role
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        new_role = RoleCreate(name="moderator")
        role = await service.create_role_service(new_role)
        
        assert role.name == "moderator"
        mock_admin_repo.create_role.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_role_service_duplicate(self):
        """Test creating duplicate role raises error."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_admin_repo.get_role_id_by_name.return_value = 1
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        new_role = RoleCreate(name="moderator")
        
        with pytest.raises(RoleAlreadyExistsError):
            await service.create_role_service(new_role)

    @pytest.mark.asyncio
    async def test_get_tasks_service_user_not_found(self):
        """Test getting tasks for non-existent user raises UserNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        mock_user_repo.get_user_by_id.return_value = None
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.get_tasks_service(user_id=99999, task_status=None, pagination=TasksPagination())

    @pytest.mark.asyncio
    async def test_get_tasks_service_permission_denied(self):
        """Test getting tasks for admin user raises PermissionDeniedError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(PermissionDeniedError):
            await service.get_tasks_service(user_id=1, task_status=None, pagination=TasksPagination())

    @pytest.mark.asyncio
    async def test_get_task_service_user_not_found(self):
        """Test getting task for non-existent user raises UserNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        mock_user_repo.get_user_by_id.return_value = None
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.get_task_service(task_id=1, user_id=99999)

    @pytest.mark.asyncio
    async def test_get_task_service_permission_denied(self):
        """Test getting task for admin user raises PermissionDeniedError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(PermissionDeniedError):
            await service.get_task_service(task_id=1, user_id=1)

    @pytest.mark.asyncio
    async def test_update_task_service_user_not_found(self):
        """Test updating task for non-existent user raises UserNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        mock_user_repo.get_user_by_id.return_value = None
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.update_task_service(task_id=1, user_id=99999, task_update=TaskUpdate())

    @pytest.mark.asyncio
    async def test_update_task_service_permission_denied(self):
        """Test updating task for admin user raises PermissionDeniedError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(PermissionDeniedError):
            await service.update_task_service(task_id=1, user_id=1, task_update=TaskUpdate())

    @pytest.mark.asyncio
    async def test_delete_task_service_user_not_found(self):
        """Test deleting task for non-existent user raises UserNotFoundError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        mock_user_repo.get_user_by_id.return_value = None
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_task_service(task_id=1, user_id=99999)

    @pytest.mark.asyncio
    async def test_delete_task_service_permission_denied(self):
        """Test deleting task for admin user raises PermissionDeniedError."""
        mock_user_repo = AsyncMock(spec=UserRepository)
        mock_admin_repo = AsyncMock(spec=AdminRepository)
        mock_task_repo = AsyncMock(spec=TaskRepository)
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        service = AdminService(user_repository=mock_user_repo, admin_repository=mock_admin_repo, task_repository=mock_task_repo)
        
        with pytest.raises(PermissionDeniedError):
            await service.delete_task_service(task_id=1, user_id=1)
