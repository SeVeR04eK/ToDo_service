"""Tests for TaskService."""
import pytest
from unittest.mock import AsyncMock

from app.application.services import TaskService
from app.domain.interfaces import TaskRepository
from app.domain.entities import Task
from app.presentation.api.schemas import TasksPagination, TaskCreate, TaskUpdate
from app.domain.enums import TaskStatus
from app.core.exceptions import TaskNotFoundError


@pytest.mark.unit
@pytest.mark.tasks
class TestTaskService:
    """Test suite for TaskService."""
    
    @pytest.mark.asyncio
    async def test_create_task_service_success(self):
        """Test successful task creation through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_task = Task(id=1, title="Test Task", content="Test Content", status=TaskStatus.todo, user_id=1)
        mock_repo.create_task.return_value = mock_task
        
        service = TaskService(repository=mock_repo)
        task_data = TaskCreate(title="Test Task", content="Test Content", status=TaskStatus.todo)
        
        task_read = await service.create_task_service(task_data, 1)
        
        assert task_read.id is not None
        assert task_read.title == task_data.title
        assert task_read.content == task_data.content
        assert task_read.status == task_data.status
        assert task_read.user_id == 1
        mock_repo.create_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_no_filters(self):
        """Test getting all tasks through service without filters."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_tasks = [
            Task(id=i, title=f"Task {i}", content=f"Content {i}", status=TaskStatus.todo, user_id=1)
            for i in range(5)
        ]
        mock_repo.get_tasks.return_value = mock_tasks
        
        service = TaskService(repository=mock_repo)
        pagination = TasksPagination()
        tasks = await service.get_tasks_service(
            user_id=1,
            task_status=None,
            pagination=pagination
        )
        
        assert len(tasks) == 5
        mock_repo.get_tasks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_status_filter(self):
        """Test getting tasks filtered by status through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_tasks = [Task(id=1, title="Task", content="Content", status=TaskStatus.todo, user_id=1)]
        mock_repo.get_tasks_by_status.return_value = mock_tasks
        
        service = TaskService(repository=mock_repo)
        pagination = TasksPagination()
        todo_tasks = await service.get_tasks_service(
            user_id=1,
            task_status=TaskStatus.todo,
            pagination=pagination
        )
        
        assert len(todo_tasks) == 1
        assert todo_tasks[0].status == TaskStatus.todo
        mock_repo.get_tasks_by_status.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_limit(self):
        """Test getting tasks with limit through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_tasks = [
            Task(id=i, title=f"Task {i}", content=f"Content {i}", status=TaskStatus.todo, user_id=1)
            for i in range(3)
        ]
        mock_repo.get_tasks.return_value = mock_tasks
        
        service = TaskService(repository=mock_repo)
        pagination = TasksPagination(limit=3)
        tasks = await service.get_tasks_service(
            user_id=1,
            task_status=None,
            pagination=pagination
        )
        
        assert len(tasks) == 3
        mock_repo.get_tasks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_offset(self):
        """Test getting tasks with offset through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_tasks = [
            Task(id=i, title=f"Task {i}", content=f"Content {i}", status=TaskStatus.todo, user_id=1)
            for i in range(5)
        ]
        mock_repo.get_tasks.return_value = mock_tasks
        
        service = TaskService(repository=mock_repo)
        pagination = TasksPagination(offset=5)
        tasks = await service.get_tasks_service(
            user_id=1,
            task_status=None,
            pagination=pagination
        )
        
        assert len(tasks) == 5
        mock_repo.get_tasks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_from_newest(self):
        """Test getting tasks sorted by newest first through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        # Mock returns tasks in reverse order (newest first)
        mock_tasks = [
            Task(id=4, title="Task 4", content="Content 4", status=TaskStatus.todo, user_id=1),
            Task(id=3, title="Task 3", content="Content 3", status=TaskStatus.todo, user_id=1),
            Task(id=2, title="Task 2", content="Content 2", status=TaskStatus.todo, user_id=1),
            Task(id=1, title="Task 1", content="Content 1", status=TaskStatus.todo, user_id=1),
            Task(id=0, title="Task 0", content="Content 0", status=TaskStatus.todo, user_id=1),
        ]
        mock_repo.get_tasks.return_value = mock_tasks
        
        service = TaskService(repository=mock_repo)
        pagination = TasksPagination(from_newest=True)
        newest_tasks = await service.get_tasks_service(
            user_id=1,
            task_status=None,
            pagination=pagination
        )
        
        assert newest_tasks[0].id == 4
        assert newest_tasks[-1].id == 0
        mock_repo.get_tasks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_empty_result(self):
        """Test getting tasks when user has no tasks."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_tasks.return_value = []
        
        service = TaskService(repository=mock_repo)
        pagination = TasksPagination()
        tasks = await service.get_tasks_service(
            user_id=1,
            task_status=None,
            pagination=pagination
        )
        
        assert tasks == []
        mock_repo.get_tasks.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_task_service_success(self):
        """Test getting a specific task through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_task = Task(id=1, title="Task", content="Content", status=TaskStatus.todo, user_id=1)
        mock_repo.get_task.return_value = mock_task
        
        service = TaskService(repository=mock_repo)
        task_read = await service.get_task_service(1, 1)
        
        assert task_read.id == 1
        assert task_read.title == mock_task.title
        assert task_read.content == mock_task.content
        mock_repo.get_task.assert_called_once_with(task_id=1, user_id=1)
    
    @pytest.mark.asyncio
    async def test_get_task_service_not_found(self):
        """Test getting a non-existent task raises TaskNotFoundError."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_task.return_value = None
        
        service = TaskService(repository=mock_repo)
        
        with pytest.raises(TaskNotFoundError):
            await service.get_task_service(99999, 1)
    
    @pytest.mark.asyncio
    async def test_get_task_service_user_isolation(self):
        """Test that users cannot access other users' tasks through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_task.return_value = None
        
        service = TaskService(repository=mock_repo)
        
        with pytest.raises(TaskNotFoundError):
            await service.get_task_service(1, 2)
    
    @pytest.mark.asyncio
    async def test_update_task_service_success(self):
        """Test updating a task through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_task = Task(id=1, title="Task", content="Content", status=TaskStatus.todo, user_id=1)
        mock_repo.get_task.return_value = mock_task
        
        updated_task = Task(id=1, title="Updated Title", content="Updated Content", status=TaskStatus.done, user_id=1)
        mock_repo.update_task.return_value = updated_task
        
        service = TaskService(repository=mock_repo)
        update_data = TaskUpdate(
            title="Updated Title",
            content="Updated Content",
            status=TaskStatus.done
        )
        
        result = await service.update_task_service(1, 1, update_data)
        
        assert result.id == 1
        assert result.title == "Updated Title"
        assert result.content == "Updated Content"
        assert result.status == TaskStatus.done
        mock_repo.get_task.assert_called_once()
        mock_repo.update_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_task_service_partial_update(self):
        """Test partial task update through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_task = Task(id=1, title="Task", content="Content", status=TaskStatus.todo, user_id=1)
        mock_repo.get_task.return_value = mock_task
        
        updated_task = Task(id=1, title="Updated Title Only", content="Content", status=TaskStatus.todo, user_id=1)
        mock_repo.update_task.return_value = updated_task
        
        service = TaskService(repository=mock_repo)
        update_data = TaskUpdate(title="Updated Title Only")
        
        result = await service.update_task_service(task_id=1, user_id=1, task_update=update_data)
        
        assert result.title == "Updated Title Only"
        assert result.content == mock_task.content
        assert result.status == mock_task.status
        mock_repo.get_task.assert_called_once()
        mock_repo.update_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_task_service_not_found(self):
        """Test updating a non-existent task raises TaskNotFoundError."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_task.return_value = None
        
        service = TaskService(repository=mock_repo)
        update_data = TaskUpdate(title="Updated")
        
        with pytest.raises(TaskNotFoundError):
            await service.update_task_service(99999, 1, update_data)
    
    @pytest.mark.asyncio
    async def test_update_task_service_user_isolation(self):
        """Test that users cannot update other users' tasks through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_task.return_value = None
        
        service = TaskService(repository=mock_repo)
        update_data = TaskUpdate(title="Hacked Title")
        
        with pytest.raises(TaskNotFoundError):
            await service.update_task_service(1, 2, update_data)
    
    @pytest.mark.asyncio
    async def test_delete_task_service_success(self):
        """Test deleting a task through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_task = Task(id=1, title="Task", content="Content", status=TaskStatus.todo, user_id=1)
        mock_repo.get_task.return_value = mock_task
        mock_repo.delete_task.return_value = None
        
        service = TaskService(repository=mock_repo)
        await service.delete_task_service(1, 1)
        
        mock_repo.get_task.assert_called_once()
        mock_repo.delete_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_task_service_not_found(self):
        """Test deleting a non-existent task raises TaskNotFoundError."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_task.return_value = None
        
        service = TaskService(repository=mock_repo)
        
        with pytest.raises(TaskNotFoundError):
            await service.delete_task_service(99999, 1)
    
    @pytest.mark.asyncio
    async def test_delete_task_service_user_isolation(self):
        """Test that users cannot delete other users' tasks through service."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_repo.get_task.return_value = None
        
        service = TaskService(repository=mock_repo)
        
        with pytest.raises(TaskNotFoundError):
            await service.delete_task_service(1, 2)
    
    @pytest.mark.asyncio
    async def test_get_tasks_service_with_status_and_pagination(self):
        """Test getting tasks with status filter and pagination."""
        mock_repo = AsyncMock(spec=TaskRepository)
        mock_tasks = [
            Task(id=i, title=f"Task {i}", content=f"Content {i}", status=TaskStatus.in_progress, user_id=1)
            for i in range(2)
        ]
        mock_repo.get_tasks_by_status.return_value = mock_tasks
        
        service = TaskService(repository=mock_repo)
        pagination = TasksPagination(limit=2, offset=1)
        tasks = await service.get_tasks_service(
            user_id=1,
            task_status=TaskStatus.in_progress,
            pagination=pagination
        )
        
        assert len(tasks) == 2
        assert all(task.status == TaskStatus.in_progress for task in tasks)
        mock_repo.get_tasks_by_status.assert_called_once()
