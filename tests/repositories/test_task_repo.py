"""Tests for SQLAlchemyTaskRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories import SQLAlchemyTaskRepository
from app.domain.value_objects import TaskPaginationData, UpdateTaskData
from app.domain.enums import TaskStatus

from tests.factories import TaskFactory, UserFactory


@pytest.mark.unit
@pytest.mark.tasks
class TestTaskRepository:
    """Test suite for SQLAlchemyTaskRepository."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, db_session: AsyncSession, test_user):
        """Test successful task creation."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        task = await repo.create_task(
            title="Test Task",
            content="Test Content",
            status=TaskStatus.todo,
            user_id=test_user.id
        )
        
        assert task.id is not None
        assert task.title == "Test Task"
        assert task.content == "Test Content"
        assert task.status == TaskStatus.todo
        assert task.user_id == test_user.id
    
    @pytest.mark.asyncio
    async def test_create_task_with_default_status(self, db_session: AsyncSession, test_user):
        """Test task creation with default status."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        task = await repo.create_task(
            title="Test Task",
            content="Test content",
            status=TaskStatus.todo,
            user_id=test_user.id
        )
        
        assert task.status == TaskStatus.todo
    
    @pytest.mark.asyncio
    async def test_get_tasks_no_filters(self, db_session: AsyncSession, test_user):
        """Test getting all tasks without filters."""
        repo = SQLAlchemyTaskRepository(db_session)
        await TaskFactory.create_many_in_db(db_session, count=5, user_id=test_user.id)
        
        pagination = TaskPaginationData()
        page = await repo.get_tasks(test_user.id, pagination, task_status=None)
        
        assert len(page.items) == 5
        assert page.total_items == 5
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_limit(self, db_session: AsyncSession, test_user):
        """Test getting tasks with limit."""
        repo = SQLAlchemyTaskRepository(db_session)
        await TaskFactory.create_many_in_db(db_session, count=10, user_id=test_user.id)
        
        pagination = TaskPaginationData(limit=3)
        page = await repo.get_tasks(test_user.id, pagination, task_status=None)
        
        assert len(page.items) == 3
        assert page.page_size == 3
        assert page.total_items == 10
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_offset(self, db_session: AsyncSession, test_user):
        """Test getting tasks with offset."""
        repo = SQLAlchemyTaskRepository(db_session)
        await TaskFactory.create_many_in_db(db_session, count=10, user_id=test_user.id)
        
        pagination = TaskPaginationData(offset=5)
        page = await repo.get_tasks(test_user.id, pagination, task_status=None)
        
        assert len(page.items) == 5
        assert page.page == 1
        assert page.total_items == 10
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_limit_and_offset(self, db_session: AsyncSession, test_user):
        """Test getting tasks with both limit and offset."""
        repo = SQLAlchemyTaskRepository(db_session)
        await TaskFactory.create_many_in_db(db_session, count=10, user_id=test_user.id)
        
        pagination = TaskPaginationData(limit=3, offset=2)
        page = await repo.get_tasks(test_user.id, pagination, task_status=None)
        
        assert len(page.items) == 3
        assert page.page == 1
        assert page.page_size == 3
    
    @pytest.mark.asyncio
    async def test_get_tasks_ascending_order(self, db_session: AsyncSession, test_user):
        """Test getting tasks in ascending order (default)."""
        repo = SQLAlchemyTaskRepository(db_session)
        tasks = await TaskFactory.create_many_in_db(db_session, count=5, user_id=test_user.id)
        
        pagination = TaskPaginationData(from_newest=False)
        page = await repo.get_tasks(test_user.id, pagination, task_status=None)
        retrieved_tasks = page.items
        
        assert retrieved_tasks[0].id == tasks[0].id
        assert retrieved_tasks[-1].id == tasks[-1].id
    
    @pytest.mark.asyncio
    async def test_get_tasks_descending_order(self, db_session: AsyncSession, test_user):
        """Test getting tasks in descending order (newest first)."""
        repo = SQLAlchemyTaskRepository(db_session)
        tasks = await TaskFactory.create_many_in_db(db_session, count=5, user_id=test_user.id)
        
        pagination = TaskPaginationData(from_newest=True)
        page = await repo.get_tasks(test_user.id, pagination, task_status=None)
        retrieved_tasks = page.items
        
        assert retrieved_tasks[0].id == tasks[-1].id
        assert retrieved_tasks[-1].id == tasks[0].id
    
    @pytest.mark.asyncio
    async def test_get_tasks_user_isolation(self, db_session: AsyncSession):
        """Test that users can only see their own tasks."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        await TaskFactory.create_many_in_db(db_session, count=3, user_id=user1.id)
        await TaskFactory.create_many_in_db(db_session, count=5, user_id=user2.id)
        
        pagination = TaskPaginationData()
        user1_page = await repo.get_tasks(user1.id, pagination, task_status=None)
        user2_page = await repo.get_tasks(user2.id, pagination, task_status=None)
        user1_tasks = user1_page.items
        user2_tasks = user2_page.items
        
        assert len(user1_tasks) == 3
        assert len(user2_tasks) == 5
        assert all(task.user_id == user1.id for task in user1_tasks)
        assert all(task.user_id == user2.id for task in user2_tasks)
    
    @pytest.mark.asyncio
    async def test_get_tasks_by_status(self, db_session: AsyncSession, test_user):
        """Test getting tasks filtered by status."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.in_progress)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.done)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        
        pagination = TaskPaginationData()
        todo_page = await repo.get_tasks(test_user.id, pagination, task_status=TaskStatus.todo)
        in_progress_page = await repo.get_tasks(test_user.id, pagination, task_status=TaskStatus.in_progress)
        done_page = await repo.get_tasks(test_user.id, pagination, task_status=TaskStatus.done)
        todo_tasks = todo_page.items
        in_progress_tasks = in_progress_page.items
        done_tasks = done_page.items
        
        assert len(todo_tasks) == 2
        assert len(in_progress_tasks) == 1
        assert len(done_tasks) == 1
        assert all(task.status == TaskStatus.todo for task in todo_tasks)
        assert all(task.status == TaskStatus.in_progress for task in in_progress_tasks)
        assert all(task.status == TaskStatus.done for task in done_tasks)
    
    @pytest.mark.asyncio
    async def test_get_tasks_by_status_with_pagination(self, db_session: AsyncSession, test_user):
        """Test getting tasks by status with pagination."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        for _ in range(5):
            await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        
        pagination = TaskPaginationData(limit=2, offset=1)
        page = await repo.get_tasks(test_user.id, pagination, task_status=TaskStatus.todo)
        
        assert len(page.items) == 2
        assert page.total_items == 5
    
    @pytest.mark.asyncio
    async def test_get_task_by_id_success(self, db_session: AsyncSession, test_user):
        """Test getting a specific task by ID."""
        repo = SQLAlchemyTaskRepository(db_session)
        created_task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        retrieved_task = await repo.get_task(created_task.id, test_user.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title
    
    @pytest.mark.asyncio
    async def test_get_task_by_id_not_found(self, db_session: AsyncSession, test_user):
        """Test getting a non-existent task returns None."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        task = await repo.get_task(99999, test_user.id)
        
        assert task is None
    
    @pytest.mark.asyncio
    async def test_get_task_user_isolation(self, db_session: AsyncSession):
        """Test that users cannot access other users' tasks."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        task = await TaskFactory.create_in_db(db_session, user_id=user1.id)
        
        # User2 trying to access user1's task
        retrieved_task = await repo.get_task(task.id, user2.id)
        
        assert retrieved_task is None
    
    @pytest.mark.asyncio
    async def test_update_task_all_fields(self, db_session: AsyncSession, test_user):
        """Test updating all task fields."""
        repo = SQLAlchemyTaskRepository(db_session)
        task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        update_data = UpdateTaskData(
            title="Updated Title",
            content="Updated Content",
            status=TaskStatus.done
        )
        
        updated_task = await repo.update_task(task, update_data)
        
        assert updated_task.title == "Updated Title"
        assert updated_task.content == "Updated Content"
        assert updated_task.status == TaskStatus.done
    
    @pytest.mark.asyncio
    async def test_update_task_partial_fields(self, db_session: AsyncSession, test_user):
        """Test updating only some task fields."""
        repo = SQLAlchemyTaskRepository(db_session)
        original_task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        update_data = UpdateTaskData(title="Updated Title Only")
        
        updated_task = await repo.update_task(original_task, update_data)
        
        assert updated_task.title == "Updated Title Only"
        assert updated_task.content == original_task.content
        assert updated_task.status == original_task.status
    
    @pytest.mark.asyncio
    async def test_update_task_no_changes(self, db_session: AsyncSession, test_user):
        """Test updating task with no changes."""
        repo = SQLAlchemyTaskRepository(db_session)
        task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        update_data = UpdateTaskData()
        
        updated_task = await repo.update_task(task, update_data)
        
        assert updated_task.title == task.title
        assert updated_task.content == task.content
        assert updated_task.status == task.status
    
    @pytest.mark.asyncio
    async def test_delete_task_success(self, db_session: AsyncSession, test_user):
        """Test successful task deletion."""
        repo = SQLAlchemyTaskRepository(db_session)
        task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        await repo.delete_task(task.id, test_user.id)
        
        deleted_task = await repo.get_task(task.id, test_user.id)
        assert deleted_task is None
    
    @pytest.mark.asyncio
    async def test_delete_task_user_isolation(self, db_session: AsyncSession):
        """Test that users cannot delete other users' tasks."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        task = await TaskFactory.create_in_db(db_session, user_id=user1.id)
        
        # User2 trying to delete user1's task
        await repo.delete_task(task.id, user2.id)
        
        # Task should still exist
        retrieved_task = await repo.get_task(task.id, user1.id)
        assert retrieved_task is not None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_task(self, db_session: AsyncSession, test_user):
        """Test deleting a non-existent task (should not raise error)."""
        repo = SQLAlchemyTaskRepository(db_session)
        
        # Should not raise an error
        await repo.delete_task(99999, test_user.id)
