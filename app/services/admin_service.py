from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Union

from app.repositories import AdminRepository, UserRepository
from app.schemas import RoleCreate, OnlyUserPermission, TaskUpdate, TaskStatus, TasksPagination
from app.core.exceptions import UserNotFoundError, RoleNotFoundError, PermissionDeniedError
from app.services import TaskService


class AdminService:
    """Service layer for admin-specific business logic."""

    def __init__(self, session: AsyncSession):
        self.admin_repository = AdminRepository(session)
        self.user_repository = UserRepository(session)
        self.session = session
        self.task_service = TaskService(session)

    async def get_users_service(
            self,
            username: Optional[str],
            limit: Optional[int],
            offset: Optional[int]
    ) -> Union[List[Dict], Dict]:
        """Get users - returns list if no username filter, single user if username provided."""

        if username is None:
            users = await self.admin_repository.get_users(limit=limit, offset=offset)

            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "is_active": user.is_active,
                    "role": {"name": user.role.name} if user.role else None  # type: ignore
                }
                for user in users
            ]

        # Offset not supported when filtering by username
        if offset is not None:
            return []

        user = await self.user_repository.get_user_by_username(username=username)
        if user is None:
            raise UserNotFoundError("User not found")

        return {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "role": {"name": user.role.name} if user.role else None  # type: ignore
        }

    async def get_user_service(self, user_id: int) -> Dict:
        """Get a single user by ID."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        return {
            "id": user.id,
            "username": user.username,
            "is_active": user.is_active,
            "role": {"name": user.role.name} if user.role else None  # type: ignore
        }

    async def permission_user_service(self, user_id: int, role_name: Optional[str], is_active: Optional[bool]) -> Dict:
        """Update user permissions (is_active status and role)."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        if user.role is None:
            raise RoleNotFoundError("User role not found")

        # Prevent admins from modifying other admins' permissions
        if user.role.name == "admin":  # type: ignore
            raise PermissionDeniedError("Not enough permissions")

        # Resolve role name to role ID if role is being updated
        role_id = None
        if role_name is not None:
            role = await self.admin_repository.get_role_id_by_name(role_name)
            if role is None:
                raise RoleNotFoundError("Role not found")
            role_id = role

        user_permission = OnlyUserPermission(is_active=is_active, role_id=role_id)
        user_updated = await self.admin_repository.user_perm(user=user, user_permission=user_permission)

        return {
            "id": user_updated.id,
            "username": user_updated.username,
            "is_active": user_updated.is_active,
            "role": {"name": user_updated.role.name} if user_updated.role else None  # type: ignore
        }

    async def delete_user_service(self, user_id: int) -> None:
        """Delete a user."""

        user = await self.user_repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        # Prevent deletion of admin users
        if user.role is None or user.role.name == "admin":  # type: ignore
            raise PermissionDeniedError("Not enough permissions")

        await self.user_repository.delete_user(user=user)

    async def create_role_service(self, new_role: RoleCreate) -> Dict:
        """Create a new role."""

        role = await self.admin_repository.create_role(new_role=new_role)
        if role is None:
            raise RoleNotFoundError("Failed to create role")

        return {
            "id": role.id,
            "name": role.name  # type: ignore
        }

    async def get_roles_service(self) -> List[Dict]:
        """Get all roles."""

        roles = await self.admin_repository.get_roles()

        return [
            {
                "id": role.id,
                "name": role.name  # type: ignore
            }
            for role in roles
        ]

    async def get_tasks_service(self, user_id: int, task_status: Optional[TaskStatus], pagination: TasksPagination) -> List[Dict]:
        """Get tasks for a user with admin protection."""

        # Check if user exists
        target_user = await self.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError("User not found")

        # Prevent admins from accessing other admins' tasks
        if target_user.role and target_user.role.name == "admin":  # type: ignore
            raise PermissionDeniedError("Not enough permissions")

        return await self.task_service.get_tasks_service(user_id=user_id, task_status=task_status, pagination=pagination)

    async def get_task_service(self, task_id: int, user_id: int) -> Dict:
        """Get a single task for a user with admin protection."""

        # Check if user exists
        target_user = await self.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError("User not found")

        # Prevent admins from accessing other admins' tasks
        if target_user.role and target_user.role.name == "admin":  # type: ignore
            raise PermissionDeniedError("Not enough permissions")

        return await self.task_service.get_task_service(task_id=task_id, user_id=user_id)

    async def update_task_service(self, task_id: int, user_id: int, task_update: TaskUpdate) -> Dict:
        """Update a task for a user with admin protection."""

        # Check if user exists
        target_user = await self.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError("User not found")

        # Prevent admins from updating other admins' tasks
        if target_user.role and target_user.role.name == "admin":  # type: ignore
            raise PermissionDeniedError("Not enough permissions")

        return await self.task_service.update_task_service(task_id=task_id, user_id=user_id, task_update=task_update)

    async def delete_task_service(self, task_id: int, user_id: int) -> None:
        """Delete a task for a user with admin protection."""

        # Check if user exists
        target_user = await self.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError("User not found")

        # Prevent admins from deleting other admins' tasks
        if target_user.role and target_user.role.name == "admin":  # type: ignore
            raise PermissionDeniedError("Not enough permissions")

        await self.task_service.delete_task_service(task_id=task_id, user_id=user_id)

