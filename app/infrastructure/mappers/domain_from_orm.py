"""ORM to Domain model mappers."""
from app.domain.entities import User, Role, Task, RefreshToken
from app.infrastructure.models.users_model import User as UserORM
from app.infrastructure.models.roles_model import Role as RoleORM
from app.infrastructure.models.tasks_model import Task as TaskORM
from app.infrastructure.models.refresh_tokens_model import RefreshToken as RefreshTokenORM


def role_from_orm(orm_role: RoleORM) -> Role:
    """Convert ORM Role to domain Role."""
    return Role(
        id=orm_role.id,
        name=orm_role.name
    )


def user_from_orm(orm_user: UserORM) -> User:
    """Convert ORM User to domain User."""
    role = role_from_orm(orm_user.role) if orm_user.role else None
    return User(
        id=orm_user.id,
        username=orm_user.username,
        hashed_password=orm_user.hashed_password,
        is_active=orm_user.is_active,
        role_id=orm_user.role_id,
        role=role
    )


def task_from_orm(orm_task: TaskORM) -> Task:
    """Convert ORM Task to domain Task."""
    return Task(
        id=orm_task.id,
        title=orm_task.title,
        content=orm_task.content,
        status=orm_task.status,
        user_id=orm_task.user_id
    )


def refresh_token_from_orm(orm_token: RefreshTokenORM) -> RefreshToken:
    """Convert ORM RefreshToken to domain RefreshToken."""
    return RefreshToken(
        id=orm_token.id,
        user_id=orm_token.user_id,
        token_hash=orm_token.token_hash,
        family_id=orm_token.family_id,
        expires_at=orm_token.expires_at,
        created_at=orm_token.created_at,
        revoked_at=orm_token.revoked_at,
        replaced_by=orm_token.replaced_by,
        family_created_at=orm_token.family_created_at
    )
