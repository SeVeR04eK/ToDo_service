import pytest
from unittest.mock import AsyncMock

from app.application.services import AdminService
from app.domain.interfaces import UnitOfWork
from app.domain.entities import User, Role, Task
from app.domain.enums import TaskStatus
from app.application.dto import TaskPaginationDTO, UpdateTaskDTO, CreateRoleDTO
from app.domain.exceptions import UserNotFoundError, RoleNotFoundError, PermissionDeniedError, RoleAlreadyExistsError, InvalidPaginationParameters


@pytest.mark.unit
class TestAdminService:
    """Test AdminService business logic."""

    @pytest.mark.asyncio
    async def test_get_users_service_with_offset(self):
        """Test that offset without username returns paginated result."""
        from app.domain.value_objects import Page
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.admin_repository = AsyncMock()

        mock_uow.admin_repository.get_users.return_value = Page.create(items=[], page=1, page_size=10, total_items=0)

        service = AdminService(unit_of_work=mock_uow)
        result = await service.get_users_service(username=None, limit=None, offset=1)

        assert isinstance(result, Page)
        assert result.items == []

    @pytest.mark.asyncio
    async def test_get_users_service_username_with_pagination_raises_error(self):
        """Test that username with pagination parameters raises InvalidPaginationParameters."""
        mock_uow = AsyncMock(spec=UnitOfWork)

        service = AdminService(unit_of_work=mock_uow)

        with pytest.raises(InvalidPaginationParameters):
            await service.get_users_service(username="testuser", limit=10, offset=None)

        with pytest.raises(InvalidPaginationParameters):
            await service.get_users_service(username="testuser", limit=None, offset=5)

        with pytest.raises(InvalidPaginationParameters):
            await service.get_users_service(username="testuser", limit=10, offset=5)

    @pytest.mark.asyncio
    async def test_get_user_service_success(self):
        """Test getting user by ID."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        
        service = AdminService(unit_of_work=mock_uow)
        user = await service.get_user_service(1)
        
        assert user.id == 1
        assert user.username == "testuser"
        mock_uow.user_repository.get_user_by_id.assert_called_once_with(user_id=1)

    @pytest.mark.asyncio
    async def test_get_user_service_not_found(self):
        """Test getting non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(UserNotFoundError):
            await service.get_user_service(99999)

    @pytest.mark.asyncio
    async def test_permission_user_service_update_role(self):
        """Test updating user role."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.admin_repository = AsyncMock()
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        mock_uow.admin_repository.get_role_id_by_name.return_value = 2
        
        updated_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=Role(id=2, name="admin"))
        mock_uow.admin_repository.user_perm.return_value = updated_user
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        updated = await service.permission_user_service(user_id=1, role_name="admin", is_active=None)
        
        assert updated.role.name == "admin"
        mock_uow.admin_repository.get_role_id_by_name.assert_called_once_with("admin")
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_permission_user_service_update_is_active(self):
        """Test updating user is_active status."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.admin_repository = AsyncMock()
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        
        updated_user = User(id=1, username="testuser", hashed_password="hashed", is_active=False, role_id=1, role=mock_role)
        mock_uow.admin_repository.user_perm.return_value = updated_user
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        updated = await service.permission_user_service(user_id=1, role_name=None, is_active=False)
        
        assert updated.is_active is False
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_permission_user_service_role_not_found(self):
        """Test updating with non-existent role raises RoleNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.admin_repository = AsyncMock()
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        mock_uow.admin_repository.get_role_id_by_name.return_value = None
        mock_uow.__aenter__.return_value = mock_uow
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(RoleNotFoundError):
            await service.permission_user_service(user_id=1, role_name="nonexistent", is_active=None)
        
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_permission_user_service_user_not_found(self):
        """Test updating non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        mock_uow.__aenter__.return_value = mock_uow
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(UserNotFoundError):
            await service.permission_user_service(user_id=99999, role_name="user", is_active=None)
        
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_user_service_admin_forbidden(self):
        """Test that deleting admin user raises PermissionDeniedError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.task_repository = AsyncMock()
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        mock_uow.__aenter__.return_value = mock_uow
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(PermissionDeniedError):
            await service.delete_user_service(1)
        
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_user_service_user_not_found(self):
        """Test deleting non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        mock_uow.__aenter__.return_value = mock_uow
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_user_service(99999)
        
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_create_role_service_success(self):
        """Test creating a new role."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.admin_repository = AsyncMock()
        
        mock_uow.admin_repository.get_role_id_by_name.return_value = None
        mock_role = Role(id=1, name="moderator")
        mock_uow.admin_repository.create_role.return_value = mock_role
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        new_role = CreateRoleDTO(name="moderator")
        role = await service.create_role_service(new_role)
        
        assert role.name == "moderator"
        mock_uow.admin_repository.create_role.assert_called_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_role_service_duplicate(self):
        """Test creating duplicate role raises error."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.admin_repository = AsyncMock()
        
        mock_uow.admin_repository.get_role_id_by_name.return_value = 1
        mock_uow.__aenter__.return_value = mock_uow
        
        service = AdminService(unit_of_work=mock_uow)
        new_role = CreateRoleDTO(name="moderator")
        
        with pytest.raises(RoleAlreadyExistsError):
            await service.create_role_service(new_role)
        
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_tasks_service_user_not_found(self):
        """Test getting tasks for non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(UserNotFoundError):
            await service.get_tasks_service(user_id=99999, task_status=None, pagination=TaskPaginationDTO())

    @pytest.mark.asyncio
    async def test_get_tasks_service_permission_denied(self):
        """Test getting tasks for admin user raises PermissionDeniedError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(PermissionDeniedError):
            await service.get_tasks_service(user_id=1, task_status=None, pagination=TaskPaginationDTO())

    @pytest.mark.asyncio
    async def test_get_task_service_user_not_found(self):
        """Test getting task for non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(UserNotFoundError):
            await service.get_task_service(task_id=1, user_id=99999)

    @pytest.mark.asyncio
    async def test_get_task_service_permission_denied(self):
        """Test getting task for admin user raises PermissionDeniedError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(PermissionDeniedError):
            await service.get_task_service(task_id=1, user_id=1)

    @pytest.mark.asyncio
    async def test_update_task_service_user_not_found(self):
        """Test updating task for non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(UserNotFoundError):
            await service.update_task_service(task_id=1, user_id=99999, task_update=UpdateTaskDTO())

    @pytest.mark.asyncio
    async def test_update_task_service_permission_denied(self):
        """Test updating task for admin user raises PermissionDeniedError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(PermissionDeniedError):
            await service.update_task_service(task_id=1, user_id=1, task_update=UpdateTaskDTO())
        
        mock_uow.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_task_service_success(self):
        """Test updating a task through admin service."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.task_repository = AsyncMock()
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        
        mock_task = Task(id=1, title="Task", content="Content", status=TaskStatus.todo, user_id=1)
        mock_uow.task_repository.get_task.return_value = mock_task
        
        updated_task = Task(id=1, title="Updated Title", content="Updated Content", status=TaskStatus.done, user_id=1)
        mock_uow.task_repository.update_task.return_value = updated_task
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        update_data = UpdateTaskDTO(title="Updated Title", content="Updated Content", status=TaskStatus.done)
        
        result = await service.update_task_service(task_id=1, user_id=1, task_update=update_data)
        
        assert result.id == 1
        assert result.title == "Updated Title"
        mock_uow.task_repository.update_task.assert_called_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_task_service_success(self):
        """Test deleting a task through admin service."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.task_repository = AsyncMock()
        
        mock_role = Role(id=1, name="user")
        mock_user = User(id=1, username="testuser", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        
        mock_task = Task(id=1, title="Task", content="Content", status=TaskStatus.todo, user_id=1)
        mock_uow.task_repository.get_task.return_value = mock_task
        mock_uow.task_repository.delete_task.return_value = None
        mock_uow.__aenter__.return_value = mock_uow
        mock_uow.commit.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        await service.delete_task_service(task_id=1, user_id=1)
        
        mock_uow.task_repository.delete_task.assert_called_once()
        mock_uow.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_task_service_user_not_found(self):
        """Test deleting task for non-existent user raises UserNotFoundError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        mock_uow.user_repository.get_user_by_id.return_value = None
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(UserNotFoundError):
            await service.delete_task_service(task_id=1, user_id=99999)

    @pytest.mark.asyncio
    async def test_delete_task_service_permission_denied(self):
        """Test deleting task for admin user raises PermissionDeniedError."""
        mock_uow = AsyncMock(spec=UnitOfWork)
        mock_uow.user_repository = AsyncMock()
        
        mock_role = Role(id=1, name="admin")
        mock_user = User(id=1, username="admin", hashed_password="hashed", is_active=True, role_id=1, role=mock_role)
        mock_uow.user_repository.get_user_by_id.return_value = mock_user
        
        service = AdminService(unit_of_work=mock_uow)
        
        with pytest.raises(PermissionDeniedError):
            await service.delete_task_service(task_id=1, user_id=1)
