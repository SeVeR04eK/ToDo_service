from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces import (
    UnitOfWork,
    UserRepository,
    RefreshTokenRepository,
    TaskRepository,
    AdminRepository,
    PasswordHasher,
)
from app.infrastructure.repositories import (
    SQLAlchemyUserRepository,
    SQLAlchemyRefreshTokenRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyAdminRepository,
)


class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of Unit of Work.

    This class manages transaction boundaries and provides access to all
    repositories that share the same AsyncSession. This ensures that multiple
    repository operations can participate in a single atomic transaction.

    The application layer controls when to commit or rollback through
    the commit() and rollback() methods, or by using the async context manager.
    """

    def __init__(
        self,
        session: AsyncSession,
        password_hasher: PasswordHasher,
    ):
        self._session = session
        self._password_hasher = password_hasher
        self._user_repository: UserRepository | None = None
        self._task_repository: TaskRepository | None = None
        self._admin_repository: AdminRepository | None = None
        self._refresh_token_repository: RefreshTokenRepository | None = None

    @property
    def session(self) -> AsyncSession:
        return self._session

    @property
    def user_repository(self) -> UserRepository:
        if self._user_repository is None:
            self._user_repository = SQLAlchemyUserRepository(
                self._session, self._password_hasher
            )
        return self._user_repository

    @property
    def task_repository(self) -> TaskRepository:
        if self._task_repository is None:
            self._task_repository = SQLAlchemyTaskRepository(self._session)
        return self._task_repository

    @property
    def admin_repository(self) -> AdminRepository:
        if self._admin_repository is None:
            self._admin_repository = SQLAlchemyAdminRepository(self._session)
        return self._admin_repository

    @property
    def refresh_token_repository(self) -> RefreshTokenRepository:
        if self._refresh_token_repository is None:
            self._refresh_token_repository = SQLAlchemyRefreshTokenRepository(
                self._session
            )
        return self._refresh_token_repository

    async def __aenter__(self):
        """Enter the Unit of Work context."""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the Unit of Work context.

        Automatically rolls back if an exception occurred.
        """
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        """Commit the transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the transaction."""
        await self.session.rollback()
