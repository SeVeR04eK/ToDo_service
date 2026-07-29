from fastapi import APIRouter, Depends, status, Path, Query, HTTPException, Body
from typing import Annotated, Optional, Union, List

from app.domain.entities import User
from app.schemas import UserRead, TaskRead, TaskUpdate, RoleRead, UserPermission, RoleCreate, TasksPagination
from app.domain.enums import TaskStatus
from app.api.dependencies import db, require_role, tasks_pagination
from app.services import AdminService
from app.core.exceptions import UserNotFoundError, RoleNotFoundError, PermissionDeniedError, TaskNotFoundError, RoleAlreadyExistsError
from app.schemas.user_schema import UserRole

# Admin router - all endpoints require admin role authentication
admin_router = APIRouter(prefix = "/admin", tags = ["admin"])

@admin_router.get("/users", status_code=status.HTTP_200_OK, response_model=Union[List[UserRead], UserRead], summary="Get all users", response_description="Returns a single user if username filter is provided, otherwise returns a list of users")
async def get_users(
        # Underscore indicates we only need the dependency for authentication, not the actual user object
        _: Annotated[
            User,
            Depends(require_role("admin"))
        ],
        session: db,
        username: Annotated[
            Optional[str],
            Query(title="Username")
        ] = None,
        limit: Annotated[
            Optional[int],
            Query(title="Limit of users", ge=1, le=100)
        ] = None,
        offset: Annotated[
            Optional[int],
            Query(title="Offset for pagination", ge=1, le=100)
        ] = None
) -> Union[list[UserRead], UserRead]:
    """
    Get all users with optional filtering by username and _pagination_:

    - **username**: Filter users by username
    - **limit**: Limit the number of users returned
    - **offset**: Offset for pagination
    """

    service = AdminService(session)

    # Returns single UserRead if username is provided, otherwise returns list of UserRead
    result = await service.get_users_service(
        username=username,
        limit=limit,
        offset=offset
    )
    
    if isinstance(result, list):
        return [
            UserRead(
                id=user.id,
                username=user.username,
                is_active=user.is_active,
                role=UserRole(name=user.role.name) if user.role else None
            )
            for user in result
        ]
    return UserRead(
        id=result.id,
        username=result.username,
        is_active=result.is_active,
        role=UserRole(name=result.role.name) if result.role else None
    )

@admin_router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead, summary="Get specific user")
async def get_user(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        session: db
) -> UserRead:
    """Get a specific user by ID."""

    try:
        service = AdminService(session=session)
        user = await service.get_user_service(user_id)
        return UserRead(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            role=UserRole(name=user.role.name) if user.role else None
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@admin_router.patch("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead, summary="Update user permissions")
async def user_permission(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        user_perm: Annotated[
            UserPermission,
            Body(
                openapi_examples={
                    "full": {
                        "summary": "Update user permissions with all fields.",
                        "description": "Update user profile with all fields: is_active, role",
                        "value": {
                            "is_active": False,
                            "role": "admin"
                        }
                    },
                    "partial_is_active": {
                        "summary": "Update user profile with only the provided is_active field.",
                        "description": "Update user profile with only the provided field: is_active",
                        "value": {
                            "is_active": False
                        }
                    },
                    "partial_role": {
                        "summary": "Update user profile with only the provided role.",
                        "description": "Update user profile with only the provided field: role",
                        "value": {
                            "role": "admin"
                        }
                    },
                        "no_changes": {
                        "summary": "No fields provided",
                        "description": "PATCH request with no fields. Nothing will be updated.",
                        "value": {}
                    }
                }
            )
        ],
        session: db
) -> UserRead:
    """Update user permissions (_Partial update_)."""

    try:
        service = AdminService(session=session)
        user = await service.permission_user_service(user_id=user_id, role_name=user_perm.role, is_active=user_perm.is_active)
        return UserRead(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            role=UserRole(name=user.role.name) if user.role else None
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except RoleNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
async def delete_user(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        session: db
) -> None:
    """Delete a specific user by ID."""

    try:
        service = AdminService(session=session)
        await service.delete_user_service(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

@admin_router.get("/users/{user_id}/tasks", status_code=status.HTTP_200_OK, response_model=List[TaskRead], summary="Get user tasks")
async def get_tasks(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        session: db,
        task_status: Annotated[
            Optional[TaskStatus],
            Query(title="Task Status")
        ] = None,
        pagination: TasksPagination = Depends(tasks_pagination),
) -> List[TaskRead]:
    """Get tasks for a specific user by ID with optional _filtering_ and _pagination_:
    - **task_status**: Filter tasks by status
    - **limit**: Limit the number of tasks returned
    - **offset**: Offset for pagination
    - **from_newest**: Boolean to sort tasks from the newest first
    """

    try:
        service = AdminService(session=session)
        tasks = await service.get_tasks_service(
            user_id=user_id,
            task_status=task_status,
            pagination=pagination
        )
        return [
            TaskRead(
                id=task.id,
                title=task.title,
                content=task.content,
                status=task.status,
                user_id=task.user_id
            )
            for task in tasks
        ]
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

@admin_router.get("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead, summary="Get specific user task")
async def get_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        user_id: Annotated[int, Path(..., title="User ID")],
        task_id: Annotated[int, Path(..., title="Task ID")],
        session: db
) -> TaskRead:
    """Get a specific task for a user by ID."""

    try:
        service = AdminService(session=session)
        task = await service.get_task_service(task_id=task_id, user_id=user_id)
        return TaskRead(
            id=task.id,
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=task.user_id
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

@admin_router.patch("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead, summary="Update user task")
async def update_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        user_id: Annotated[int, Path(..., title="User ID")],
        task_update: Annotated[
            TaskUpdate,
            Body(
                openapi_examples={
                    "full": {
                        "summary": "Update user task with all fields.",
                        "description": "Update user task with all fields: title, content, status",
                        "value": {
                            "title": "example new title",
                            "content": "example new content ",
                            "status": "done"
                        }
                    },
                    "partial_title": {
                        "summary": "Update user task with only the provided title.",
                        "description": "Update user task with only the provided field: title",
                        "value": {
                            "title": "example new title"
                        }
                    },
                    "partial_сontent": {
                        "summary": "Update user task with only the provided content.",
                        "description": "Update user task with only the provided field: content",
                        "value": {
                            "content": "example new content "
                        }
                    },
                    "partial_status": {
                        "summary": "Update user task with only the provided status.",
                        "description": "Update user task with only the provided field: status",
                        "value": {
                            "status": "done"
                        }
                    },
                    "partial_two_fields": {
                        "summary": "Update user task with only provided two fields.",
                        "description": "Update user task with only the provided field: title, status",
                        "value": {
                            "title": "example new title",
                            "status": "done"
                        }
                    },
                    "no_changes": {
                        "summary": "No fields provided",
                        "description": "PATCH request with no fields. Nothing will be updated.",
                        "value": {}
                    }
                }
            )
        ],
        session: db
) -> TaskRead:
    """Update a specific task for a user by ID (_Partial update_")."""

    try:
        service = AdminService(session=session)
        task = await service.update_task_service(task_id=task_id, user_id=user_id, task_update=task_update)
        return TaskRead(
            id=task.id,
            title=task.title,
            content=task.content,
            status=task.status,
            user_id=task.user_id
        )
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

@admin_router.delete("/users/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user task")
async def delete_task(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        task_id: Annotated[int, Path(..., title="Task ID")],
        user_id: Annotated[int, Path(..., title="User ID")],
        session: db
) -> None:
    """Delete a specific task for a user by ID."""

    try:
        service = AdminService(session=session)
        await service.delete_task_service(task_id=task_id, user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except TaskNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

@admin_router.post("/roles", status_code=status.HTTP_201_CREATED, response_model=RoleRead, summary="Create new role")
async def create_role(
        _: Annotated[
                    User,
                    Depends(require_role("admin"))
                ],
        new_role: RoleCreate,
        session: db
) -> RoleRead:
    """Create a new role."""

    try:
        service = AdminService(session=session)
        role = await service.create_role_service(new_role=new_role)
        return RoleRead(
            id=role.id,
            name=role.name
        )
    except RoleAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")

@admin_router.get("/roles", status_code=status.HTTP_200_OK, response_model=List[RoleRead])
async def get_roles(
        _: Annotated[
            User,
            Depends(require_role("admin"))
        ],
        session: db
) -> List[RoleRead]:

    service = AdminService(session=session)
    roles = await service.get_roles_service()
    return [
        RoleRead(
            id=role.id,
            name=role.name
        )
        for role in roles
    ]


