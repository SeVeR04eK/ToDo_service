import structlog
from typing import List, Optional, Union

from app.application.dto import TaskPaginationDTO, UpdateTaskDTO, CreateRoleDTO
from app.domain.value_objects import TaskPaginationData, UpdateTaskData, UserPermissionData, Page
from app.domain.enums import TaskStatus
from app.domain.exceptions import UserNotFoundError, RoleNotFoundError, PermissionDeniedError, RoleAlreadyExistsError, TaskNotFoundError, InvalidPaginationParameters
from app.domain.entities import User, Role, Task
from app.domain.interfaces import UnitOfWork

logger = structlog.get_logger(__name__)


class AdminService:
    """Service layer for admin-specific business logic."""

    def __init__(self, unit_of_work: UnitOfWork):
        self.unit_of_work = unit_of_work

    async def get_users_service(
            self,
            username: Optional[str],
            limit: Optional[int],
            offset: Optional[int]
    ) -> Union[Page[User], User]:
        """Get users - returns paginated list if no username filter, single user if username provided."""

        if username is None:
            return await self.unit_of_work.admin_repository.get_users(limit=limit, offset=offset)

        # Pagination parameters not allowed when filtering by username
        if limit is not None or offset is not None:
            logger.warning(
                "Pagination parameters provided with username filter",
                username=username,
                limit=limit,
                offset=offset,
            )
            raise InvalidPaginationParameters()

        user = await self.unit_of_work.user_repository.get_user_by_username(username=username)
        if user is None:
            raise UserNotFoundError()

        return user

    async def get_user_service(self, user_id: int) -> User:
        """Get a single user by ID."""

        user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
        if user is None:
            raise UserNotFoundError()

        return user

    async def permission_user_service(self, user_id: int, role_name: Optional[str], is_active: Optional[bool]) -> User:
        """Update user permissions (is_active status and role)."""

        logger.info(
            "Updating user permissions",
            user_id=user_id,
            role_name=role_name,
            is_active=is_active,
        )
        
        async with self.unit_of_work:
            user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
            if user is None:
                logger.warning(
                    "User not found for permission update",
                    user_id=user_id,
                )
                raise UserNotFoundError()

            if user.role is None:
                logger.warning(
                    "User has no role",
                    user_id=user_id,
                )
                raise RoleNotFoundError()

            # Prevent admins from modifying other admins' permissions
            if user.role.name == "admin":
                logger.warning(
                    "Attempted to modify admin permissions",
                    user_id=user_id,
                    username=user.username,
                )
                raise PermissionDeniedError()

            # Resolve role name to role ID if role is being updated
            role_id = None
            if role_name is not None:
                role = await self.unit_of_work.admin_repository.get_role_id_by_name(role_name)
                if role is None:
                    logger.warning(
                        "Role not found for permission update",
                        role_name=role_name,
                    )
                    raise RoleNotFoundError()
                role_id = role

            user_permission = UserPermissionData(is_active=is_active, role_id=role_id)
            updated_user = await self.unit_of_work.admin_repository.user_perm(user=user, user_permission=user_permission)
            
            await self.unit_of_work.commit()
        
        logger.info(
            "User permissions updated",
            user_id=user_id,
            username=user.username,
        )
        
        return updated_user

    async def delete_user_service(self, user_id: int) -> None:
        """Delete a user."""

        logger.info(
            "Admin deleting user",
            user_id=user_id,
        )
        
        async with self.unit_of_work:
            user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
            if user is None:
                logger.warning(
                    "User not found for deletion by admin",
                    user_id=user_id,
                )
                raise UserNotFoundError()

            # Prevent deletion of admin users
            if user.role is None or user.role.name == "admin":
                logger.warning(
                    "Attempted to delete admin user",
                    user_id=user_id,
                    username=user.username,
                )
                raise PermissionDeniedError()

            await self.unit_of_work.user_repository.delete_user(user=user)
            
            await self.unit_of_work.commit()
        
        logger.info(
            "User deleted by admin",
            user_id=user_id,
            username=user.username,
        )

    async def create_role_service(self, new_role: CreateRoleDTO) -> Role:
        """Create a new role."""

        logger.info(
            "Creating role",
            role_name=new_role.name,
        )
        
        role_name = new_role.name

        async with self.unit_of_work:
            role_exist = await self.unit_of_work.admin_repository.get_role_id_by_name(name=role_name)
            if role_exist is not None:
                logger.warning(
                    "Role already exists",
                    role_name=role_name,
                )
                raise RoleAlreadyExistsError()

            role = await self.unit_of_work.admin_repository.create_role(name=role_name)
            
            await self.unit_of_work.commit()
        
        logger.info(
            "Role created",
            role_id=role.id,
            role_name=role.name,
        )

        return role

    async def get_roles_service(self) -> List[Role]:
        """Get all roles."""

        return await self.unit_of_work.admin_repository.get_roles()

    async def get_tasks_service(self, user_id: int, task_status: Optional[TaskStatus], pagination: TaskPaginationDTO) -> Page[Task]:
        """Get tasks for a user with admin protection."""

        # Check if user exists
        target_user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError()

        # Prevent admins from accessing other admins' tasks
        if target_user.role and target_user.role.name == "admin":
            raise PermissionDeniedError()

        pagination = TaskPaginationData(
            limit=pagination.limit,
            offset=pagination.offset,
            from_newest=pagination.from_newest,
        )

        return await self.unit_of_work.task_repository.get_tasks(
            user_id=user_id,
            task_status=task_status,
            pagination=pagination)


    async def get_task_service(self, task_id: int, user_id: int) -> Task:
        """Get a single task for a user with admin protection."""

        # Check if user exists
        target_user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
        if target_user is None:
            raise UserNotFoundError()

        # Prevent admins from accessing other admins' tasks
        if target_user.role and target_user.role.name == "admin":
            raise PermissionDeniedError()

        task = await self.unit_of_work.task_repository.get_task(task_id=task_id, user_id=user_id)
        if task is None:
            raise TaskNotFoundError()

        return task

    async def update_task_service(self, task_id: int, user_id: int, task_update: UpdateTaskDTO) -> Task:
        """Update a task for a user with admin protection."""

        logger.info(
            "Admin updating task",
            task_id=task_id,
            user_id=user_id,
        )

        async with self.unit_of_work:
            # Check if user exists
            target_user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
            if target_user is None:
                raise UserNotFoundError()

            # Prevent admins from updating other admins' tasks
            if target_user.role and target_user.role.name == "admin":
                raise PermissionDeniedError()

            task = await self.unit_of_work.task_repository.get_task(task_id=task_id, user_id=user_id)
            if task is None:
                raise TaskNotFoundError()

            task_update = UpdateTaskData(
                title=task_update.title,
                content=task_update.content,
                status=task_update.status
            )

            updated_task = await self.unit_of_work.task_repository.update_task(task=task, task_update=task_update)

            await self.unit_of_work.commit()

        logger.info(
            "Task updated by admin",
            task_id=task_id,
            user_id=user_id,
        )

        return updated_task

    async def delete_task_service(self, task_id: int, user_id: int) -> None:
        """Delete a task for a user with admin protection."""

        logger.info(
            "Admin deleting task",
            task_id=task_id,
            user_id=user_id,
        )

        async with self.unit_of_work:
            # Check if user exists
            target_user = await self.unit_of_work.user_repository.get_user_by_id(user_id=user_id)
            if target_user is None:
                raise UserNotFoundError()

            # Prevent admins from deleting other admins' tasks
            if target_user.role and target_user.role.name == "admin":
                raise PermissionDeniedError()

            task = await self.unit_of_work.task_repository.get_task(task_id=task_id, user_id=user_id)
            if task is None:
                raise TaskNotFoundError()

            await self.unit_of_work.task_repository.delete_task(task_id=task_id, user_id=user_id)

            await self.unit_of_work.commit()

        logger.info(
            "Task deleted by admin",
            task_id=task_id,
            user_id=user_id,
        )

