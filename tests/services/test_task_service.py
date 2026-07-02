"""Tests for TaskService."""
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.task_service import TaskService
from app.schemas import TaskStatus
from tests.factories import TaskFactory, UserFactory


@pytest.mark.unit
@pytest.mark.tasks
class TestTaskService:
    """Test suite for TaskService."""
    
    @pytest.mark.asyncio
    async def test_create_task_service_success(self, db_session: AsyncSession, test_user):
        """Test successful task creation through service."""
        service = TaskService(db_session)
        task_data = TaskFactory.create_schema()
        
        task_read = await service.create_task_service(task_data, test_user.id)
        
        assert task_read.id is not None
        assert task_read.title == task_data.title
        assert task_read.content == task_data.content
        assert task_read.status == task_data.status
        assert task_read.user_id == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_no_filters(self, db_session: AsyncSession, test_user):
        """Test getting all tasks through service without filters."""
        service = TaskService(db_session)
        await TaskFactory.create_many_in_db(db_session, count=5, user_id=test_user.id)
        
        tasks = await service.get_tasks_service(
            user_id=test_user.id,
            task_status=None,
            limit=None,
            offset=None
        )
        
        assert len(tasks) == 5
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_status_filter(self, db_session: AsyncSession, test_user):
        """Test getting tasks filtered by status through service."""
        service = TaskService(db_session)
        
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.in_progress)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.done)
        
        todo_tasks = await service.get_tasks_service(
            user_id=test_user.id,
            task_status=TaskStatus.todo,
            limit=None,
            offset=None
        )
        
        assert len(todo_tasks) == 1
        assert todo_tasks[0].status == TaskStatus.todo
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_limit(self, db_session: AsyncSession, test_user):
        """Test getting tasks with limit through service."""
        service = TaskService(db_session)
        await TaskFactory.create_many_in_db(db_session, count=10, user_id=test_user.id)
        
        tasks = await service.get_tasks_service(
            user_id=test_user.id,
            task_status=None,
            limit=3,
            offset=None
        )
        
        assert len(tasks) == 3
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_offset(self, db_session: AsyncSession, test_user):
        """Test getting tasks with offset through service."""
        service = TaskService(db_session)
        await TaskFactory.create_many_in_db(db_session, count=10, user_id=test_user.id)
        
        tasks = await service.get_tasks_service(
            user_id=test_user.id,
            task_status=None,
            limit=None,
            offset=5
        )
        
        assert len(tasks) == 5
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_from_newest(self, db_session: AsyncSession, test_user):
        """Test getting tasks sorted by newest first through service."""
        service = TaskService(db_session)
        tasks = await TaskFactory.create_many_in_db(db_session, count=5, user_id=test_user.id)
        
        newest_tasks = await service.get_tasks_service(
            user_id=test_user.id,
            task_status=None,
            limit=None,
            offset=None,
            from_newest=True
        )
        
        assert newest_tasks[0].id == tasks[-1].id
        assert newest_tasks[-1].id == tasks[0].id
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_empty_result(self, db_session: AsyncSession, test_user):
        """Test getting tasks when user has no tasks."""
        service = TaskService(db_session)
        
        tasks = await service.get_tasks_service(
            user_id=test_user.id,
            task_status=None,
            limit=None,
            offset=None
        )
        
        assert tasks == []
    
    @pytest.mark.asyncio
    async def test_get_task_service_success(self, db_session: AsyncSession, test_user):
        """Test getting a specific task through service."""
        service = TaskService(db_session)
        created_task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        task_read = await service.get_task_service(created_task.id, test_user.id)
        
        assert task_read.id == created_task.id
        assert task_read.title == created_task.title
        assert task_read.content == created_task.content
    
    @pytest.mark.asyncio
    async def test_get_task_service_not_found(self, db_session: AsyncSession, test_user):
        """Test getting a non-existent task raises 404."""
        service = TaskService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_task_service(99999, test_user.id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_task_service_user_isolation(self, db_session: AsyncSession):
        """Test that users cannot access other users' tasks through service."""
        service = TaskService(db_session)
        
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        task = await TaskFactory.create_in_db(db_session, user_id=user1.id)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_task_service(task.id, user2.id)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_task_service_success(self, db_session: AsyncSession, test_user):
        """Test updating a task through service."""
        service = TaskService(db_session)
        task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        update_data = TaskFactory.create_update_schema(
            title="Updated Title",
            content="Updated Content",
            status=TaskStatus.done
        )
        
        updated_task = await service.update_task_service(task.id, update_data, test_user.id)
        
        assert updated_task.id == task.id
        assert updated_task.title == "Updated Title"
        assert updated_task.content == "Updated Content"
        assert updated_task.status == TaskStatus.done
    
    @pytest.mark.asyncio
    async def test_update_task_service_partial_update(self, db_session: AsyncSession, test_user):
        """Test partial task update through service."""
        service = TaskService(db_session)
        original_task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        update_data = TaskFactory.create_update_schema(title="Updated Title Only")
        
        updated_task = await service.update_task_service(task_id=original_task.id, task_update=update_data, user_id=test_user.id)
        
        assert updated_task.title == "Updated Title Only"
        assert updated_task.content == original_task.content
        assert updated_task.status == original_task.status
    
    @pytest.mark.asyncio
    async def test_update_task_service_not_found(self, db_session: AsyncSession, test_user):
        """Test updating a non-existent task raises 404."""
        service = TaskService(db_session)
        update_data = TaskFactory.create_update_schema()
        
        with pytest.raises(HTTPException) as exc_info:
            await service.update_task_service(99999, update_data, test_user.id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_update_task_service_user_isolation(self, db_session: AsyncSession):
        """Test that users cannot update other users' tasks through service."""
        service = TaskService(db_session)
        
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        task = await TaskFactory.create_in_db(db_session, user_id=user1.id)
        update_data = TaskFactory.create_update_schema(title="Hacked Title")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.update_task_service(task.id, update_data, user2.id)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_task_service_success(self, db_session: AsyncSession, test_user):
        """Test deleting a task through service."""
        service = TaskService(db_session)
        task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        await service.delete_task_service(task.id, test_user.id)
        
        # Verify task is deleted
        with pytest.raises(HTTPException) as exc_info:
            await service.get_task_service(task.id, test_user.id)
        
        assert exc_info.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_task_service_not_found(self, db_session: AsyncSession, test_user):
        """Test deleting a non-existent task raises 404."""
        service = TaskService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_task_service(99999, test_user.id)
        
        assert exc_info.value.status_code == 404
        assert "Task not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_delete_task_service_user_isolation(self, db_session: AsyncSession):
        """Test that users cannot delete other users' tasks through service."""
        service = TaskService(db_session)
        
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        task = await TaskFactory.create_in_db(db_session, user_id=user1.id)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.delete_task_service(task.id, user2.id)
        
        assert exc_info.value.status_code == 404
        
        # Verify task still exists for user1
        retrieved_task = await service.get_task_service(task.id, user1.id)
        assert retrieved_task.id == task.id
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_status_and_pagination(self, db_session: AsyncSession, test_user):
        """Test getting tasks with status filter and pagination."""
        service = TaskService(db_session)
        
        for _ in range(3):
            await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        for _ in range(5):
            await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.in_progress)
        
        tasks = await service.get_tasks_service(
            user_id=test_user.id,
            task_status=TaskStatus.in_progress,
            limit=2,
            offset=1
        )
        
        assert len(tasks) == 2
        assert all(task.status == TaskStatus.in_progress for task in tasks)
