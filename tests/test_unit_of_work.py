"""Tests for Unit of Work pattern transaction management."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork
from app.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from app.domain.exceptions import UserNotFoundError
from tests.factories import UserFactory, TaskFactory
from app.domain.enums import TaskStatus


@pytest.mark.integration
class TestUnitOfWorkTransactions:
    """Test Unit of Work transaction management."""

    @pytest.mark.asyncio
    async def test_commit_persists_changes(self, db_session: AsyncSession):
        """Test that commit persists changes to the database."""
        password_hasher = BcryptPasswordHasher()
        uow = SQLAlchemyUnitOfWork(db_session, password_hasher)

        async with uow:
            user = await uow.user_repository.create_user(
                username="testuser",
                password="TestPassword123!"
            )
            await uow.commit()

        # Verify user persists after commit
        retrieved_user = await uow.user_repository.get_user_by_username("testuser")
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser"

    @pytest.mark.asyncio
    async def test_rollback_discards_changes(self, db_session: AsyncSession):
        """Test that rollback discards uncommitted changes."""
        password_hasher = BcryptPasswordHasher()
        uow = SQLAlchemyUnitOfWork(db_session, password_hasher)

        async with uow:
            user = await uow.user_repository.create_user(
                username="tempuser",
                password="TestPassword123!"
            )
            await uow.rollback()

        # Verify user does not exist after rollback
        retrieved_user = await uow.user_repository.get_user_by_username("tempuser")
        assert retrieved_user is None

    @pytest.mark.asyncio
    async def test_exception_triggers_rollback(self, db_session: AsyncSession):
        """Test that exception in transaction triggers automatic rollback."""
        password_hasher = BcryptPasswordHasher()
        uow = SQLAlchemyUnitOfWork(db_session, password_hasher)

        with pytest.raises(ValueError):
            async with uow:
                await uow.user_repository.create_user(
                    username="baduser",
                    password="TestPassword123!"
                )
                raise ValueError("Simulated error")

        # Verify user does not exist after exception
        retrieved_user = await uow.user_repository.get_user_by_username("baduser")
        assert retrieved_user is None

    @pytest.mark.asyncio
    async def test_atomic_multiple_operations(self, db_session: AsyncSession):
        """Test that multiple operations in a single transaction are atomic."""
        from app.application.dto import TaskPaginationDTO
        password_hasher = BcryptPasswordHasher()
        uow = SQLAlchemyUnitOfWork(db_session, password_hasher)

        # Create a user first
        test_user = await UserFactory.create_in_db(db_session, username="taskuser")

        async with uow:
            # Create multiple tasks
            await uow.task_repository.create_task(
                title="Task 1",
                content="Content 1",
                status=TaskStatus.todo,
                user_id=test_user.id
            )
            await uow.task_repository.create_task(
                title="Task 2",
                content="Content 2",
                status=TaskStatus.in_progress,
                user_id=test_user.id
            )
            await uow.commit()

        # Verify both tasks exist
        from app.domain.value_objects import TaskPaginationData
        pagination = TaskPaginationData(limit=None, offset=None, from_newest=False)
        tasks_page = await uow.task_repository.get_tasks(
            user_id=test_user.id,
            pagination=pagination,
            task_status=None
        )
        assert len(tasks_page.items) == 2

    @pytest.mark.asyncio
    async def test_atomic_operation_failure_rolls_back_all(self, db_session: AsyncSession):
        """Test that failure in atomic operation rolls back all changes."""
        from app.application.dto import TaskPaginationDTO
        from app.domain.value_objects import TaskPaginationData
        password_hasher = BcryptPasswordHasher()
        
        # Create a user first
        test_user = await UserFactory.create_in_db(db_session, username="taskuser2")
        user_id = test_user.id

        # Get initial task count
        uow1 = SQLAlchemyUnitOfWork(db_session, password_hasher)
        pagination = TaskPaginationData(limit=None, offset=None, from_newest=False)
        initial_task_page = await uow1.task_repository.get_tasks(
            user_id=user_id,
            pagination=pagination,
            task_status=None
        )
        initial_task_count = len(initial_task_page.items)

        # Try to add tasks in a transaction that will fail
        uow2 = SQLAlchemyUnitOfWork(db_session, password_hasher)
        with pytest.raises(ValueError):
            async with uow2:
                # Create first task
                await uow2.task_repository.create_task(
                    title="Task 1",
                    content="Content 1",
                    status=TaskStatus.todo,
                    user_id=user_id
                )
                # Create second task
                await uow2.task_repository.create_task(
                    title="Task 2",
                    content="Content 2",
                    status=TaskStatus.in_progress,
                    user_id=user_id
                )
                # Simulate failure
                raise ValueError("Simulated error")

        # Verify no tasks were added using a new UnitOfWork
        uow3 = SQLAlchemyUnitOfWork(db_session, password_hasher)
        final_task_page = await uow3.task_repository.get_tasks(
            user_id=user_id,
            pagination=pagination,
            task_status=None
        )
        final_task_count = len(final_task_page.items)
        assert final_task_count == initial_task_count

    @pytest.mark.asyncio
    async def test_sequential_context_managers(self, db_session: AsyncSession):
        """Test that sequential UnitOfWork contexts work correctly."""
        password_hasher = BcryptPasswordHasher()

        async with SQLAlchemyUnitOfWork(db_session, password_hasher) as uow1:
            user1 = await uow1.user_repository.create_user(
                username="user1",
                password="TestPassword123!"
            )
            await uow1.commit()

        async with SQLAlchemyUnitOfWork(db_session, password_hasher) as uow2:
            user2 = await uow2.user_repository.create_user(
                username="user2",
                password="TestPassword123!"
            )
            await uow2.commit()

        # Verify both users exist
        retrieved_user1 = await uow2.user_repository.get_user_by_username("user1")
        retrieved_user2 = await uow2.user_repository.get_user_by_username("user2")
        assert retrieved_user1 is not None
        assert retrieved_user2 is not None
