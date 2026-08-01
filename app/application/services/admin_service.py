from typing import List, Optional, Union

from app.presentation.api.schemas import RoleCreate, OnlyUserPermission, TaskUpdate, TasksPagination
from app.domain.enums import TaskStatus
from app.core.exceptions import UserNotFoundError, RoleNotFoundError, PermissionDeniedError, RoleAlreadyExistsError, TaskNotFoundError
from app.domain.entities import User, Role, Task
from app.domain.interfaces import UserRepository, AdminRepository, TaskRepository


class AdminService:
    """Service layer for admin-specific business logic."""

    def __init__(self, user_repository: UserRepository, admin_repository: AdminRepository, task_repository: TaskRepository):
        self.user_repository = user_repository
        self.admin_repository = admin_repository
        self.task_repository = task_repository

    async def get_users_service(
            self,
            username: Optional[str],
            limit: Optional[int],
            offset: Optional[int]
    ) -> Union[List[User], User]:
        """Get users - returns list if no username filter, single user if username provided."""

        if username is None:
            return await self.admin_repository.get_users(limit=limit, offset=offset)

        # Offset not supported when filtering by username
        if offset is not None:
            return []

        user = await self.user_repository.get_user_by_username(username=username)
        if user is None:
            raise UserNotFoundError("User not found")

        return user

    async def get_user_service(self, user_id: int) -> User:
        """Get a single user by ID."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        return user

    async def permission_user_service(self, user_id: int, role_name: Optional[str], is_active: Optional[bool]) -> User:
        """Update user permissions (is_active status and role)."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        if user.role is None:
            raise RoleNotFoundError("User role not found")

        # Prevent admins from modifying other admins' permissions
        if user.role.name == "admin":
            raise PermissionDeniedError("Not enough permissions")

        # Resolve role name to role ID if role is being updated
        role_id = None
        if role_name is not None:
            role = await self.admin_repository.get_role_id_by_name(role_name)
            if role is None:
                raise RoleNotFoundError("Role not found")
            role_id = role

        user_permission = OnlyUserPermission(is_active=is_active, role_id=role_id)
        return await self.admin_repository.user_perm(user=user, user_permission=user_permission)

    async def delete_user_service(self, user_id: int) -> None:
        """Delete a user."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        # Prevent deletion of admin users
        if user.role is None or user.role.name == "admin":
            raise PermissionDeniedError("Not enough permissions")

        await self.user_repository.delete_user(user=user)

    async def create_role_service(self, new_role: RoleCreate) -> Role:
        """Create a new role."""

        role_exist = await self.admin_repository.get_role_id_by_name(name=new_role.name)
        if role_exist is not None:
            raise RoleAlreadyExistsError("Role already exists")

        role = await self.admin_repository.create_role(new_role=new_role)

        return role

    async def get_roles_service(self) -> List[Role]:
        """Get all roles."""

        return await self.admin_repository.get_roles()

    async def get_tasks_service(self, user_id: int, task_status: Optional[TaskStatus], pagination: TasksPagination) -> List[Task]:
        """Get tasks for a user with admin protection."""

        # Check if user exists
        target_user = await self.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError("User not found")

        # Prevent admins from accessing other admins' tasks
        if target_user.role and target_user.role.name == "admin":
            raise PermissionDeniedError("Not enough permissions")

        # Route to appropriate repository method based on whether status filter is provided
        if task_status is not None:
            return await self.task_repository.get_tasks_by_status(
                user_id=user_id,
                task_status=task_status,
                pagination=pagination
            )
        else:
            return await self.task_repository.get_tasks(
                user_id=user_id,
                pagination=pagination
            )

    async def get_task_service(self, task_id: int, user_id: int) -> Task:
        """Get a single task for a user with admin protection."""

        # Check if user exists
        target_user = await self.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError("User not found")

        # Prevent admins from accessing other admins' tasks
        if target_user.role and target_user.role.name == "admin":
            raise PermissionDeniedError("Not enough permissions")

        task = await self.task_repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        return task

    async def update_task_service(self, task_id: int, user_id: int, task_update: TaskUpdate) -> Task:
        """Update a task for a user with admin protection."""

        # Check if user exists
        target_user = await self.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError("User not found")

        # Prevent admins from updating other admins' tasks
        if target_user.role and target_user.role.name == "admin":
            raise PermissionDeniedError("Not enough permissions")

        task = await self.task_repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        return await self.task_repository.update_task(task=task, task_update=task_update)

    async def delete_task_service(self, task_id: int, user_id: int) -> None:
        """Delete a task for a user with admin protection."""

        # Check if user exists
        target_user = await self.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError("User not found")

        # Prevent admins from deleting other admins' tasks
        if target_user.role and target_user.role.name == "admin":
            raise PermissionDeniedError("Not enough permissions")

        task = await self.task_repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError("Task not found")

        await self.task_repository.delete_task(task_id=task_id, user_id=user_id)

