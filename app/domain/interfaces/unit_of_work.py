from abc import ABC, abstractmethod

from app.domain.interfaces import (
    UserRepository,
    TaskRepository,
    AdminRepository,
    RefreshTokenRepository,
)


class UnitOfWork(ABC):
    """Abstract Unit of Work interface for transaction management.

    The Unit of Work pattern ensures that multiple repository operations
    can be performed within a single transaction. The application layer
    controls transaction boundaries through this interface.

    Repositories accessed through the UnitOfWork should NOT commit or
    rollback independently - they only perform persistence operations.
    """

    @property
    @abstractmethod
    def user_repository(self) -> UserRepository:
        """User repository for user-related operations."""
        ...

    @property
    @abstractmethod
    def task_repository(self) -> TaskRepository:
        """Task repository for task-related operations."""
        ...

    @property
    @abstractmethod
    def admin_repository(self) -> AdminRepository:
        """Admin repository for admin-specific operations."""
        ...

    @property
    @abstractmethod
    def refresh_token_repository(self) -> RefreshTokenRepository:
        """Refresh token repository for token management."""
        ...

    @abstractmethod
    async def __aenter__(self):
        """Enter the Unit of Work context."""
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the Unit of Work context.

        Automatically rolls back if an exception occurred.
        """
        ...

    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction."""
        ...
