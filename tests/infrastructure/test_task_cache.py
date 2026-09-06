"""Tests for RedisTaskCache."""
import pytest
from unittest.mock import AsyncMock, patch
from app.infrastructure.redis.cache import RedisTaskCache
from app.domain.entities import Task
from app.domain.enums import TaskStatus
from app.domain.value_objects import Page


@pytest.mark.unit
class TestRedisTaskCache:
    """Test suite for RedisTaskCache."""

    @pytest.fixture
    def mock_redis_client(self):
        """Create a mock Redis client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def cache(self, mock_redis_client):
        """Create a RedisTaskCache instance with mocked client."""
        with patch('app.infrastructure.redis.cache.base_cache.get_redis_client', return_value=mock_redis_client):
            return RedisTaskCache()

    @pytest.fixture
    def test_task(self):
        """Create a test task."""
        return Task(
            id=1,
            title="Test Task",
            content="Test content",
            status=TaskStatus.todo,
            user_id=1
        )

    def test_get_task_key(self, cache):
        """Test task key generation."""
        key = cache._get_task_key(123, 456)
        assert key == "task:123:456"

    def test_get_task_list_key_with_status(self, cache):
        """Test task list key generation with status."""
        key = cache._get_task_list_key(123, "todo", 10, 0, True)
        assert key == "tasks:user:123:status:todo:limit:10:offset:0:newest:True"

    def test_get_task_list_key_without_status(self, cache):
        """Test task list key generation without status."""
        key = cache._get_task_list_key(123, None, 10, 0, False)
        assert key == "tasks:user:123:status:all:limit:10:offset:0:newest:False"

    async def test_get_task_success(self, cache, mock_redis_client, test_task):
        """Test successful task retrieval."""
        mock_redis_client.get.return_value = '{"id": 1, "title": "Test Task", "content": "Test content", "status": "todo", "user_id": 1}'
        
        result = await cache.get_task(1, 1)
        
        assert result is not None
        assert result.id == 1
        assert result.title == "Test Task"
        assert result.status == TaskStatus.todo
        mock_redis_client.get.assert_called_once()

    async def test_get_task_not_found(self, cache, mock_redis_client):
        """Test task retrieval when not found."""
        mock_redis_client.get.return_value = None
        
        result = await cache.get_task(1, 999)
        
        assert result is None
        mock_redis_client.get.assert_called_once()

    async def test_get_task_deserialize_error(self, cache, mock_redis_client):
        """Test task retrieval with deserialization error."""
        mock_redis_client.get.return_value = "invalid json"
        
        result = await cache.get_task(1, 1)
        
        assert result is None

    async def test_set_task(self, cache, mock_redis_client, test_task):
        """Test setting task in cache."""
        mock_redis_client.set.return_value = True
        
        await cache.set_task(1, 1, test_task, 300)
        
        mock_redis_client.set.assert_called_once()

    async def test_delete_task(self, cache, mock_redis_client):
        """Test deleting task from cache."""
        mock_redis_client.delete.return_value = 1
        
        await cache.delete_task(1, 1)
        
        mock_redis_client.delete.assert_called_once_with("task:1:1")

    async def test_get_task_list_success(self, cache, mock_redis_client):
        """Test successful task list retrieval."""
        mock_redis_client.get.return_value = '{"items": [{"id": 1, "title": "Task 1", "content": "Content 1", "status": "todo", "user_id": 1}, {"id": 2, "title": "Task 2", "content": "Content 2", "status": "done", "user_id": 1}], "page": 1, "page_size": 10, "total_items": 2, "total_pages": 1, "has_next": false, "has_previous": false}'
        
        result = await cache.get_task_list(1, "todo", 10, 0, True)
        
        assert result is not None
        assert isinstance(result, Page)
        assert len(result.items) == 2
        assert result.page == 1
        assert result.total_items == 2
        mock_redis_client.get.assert_called_once()

    async def test_get_task_list_not_found(self, cache, mock_redis_client):
        """Test task list retrieval when not found."""
        mock_redis_client.get.return_value = None
        
        result = await cache.get_task_list(1, "todo", 10, 0, True)
        
        assert result is None
        mock_redis_client.get.assert_called_once()

    async def test_get_task_list_deserialize_error(self, cache, mock_redis_client):
        """Test task list retrieval with deserialization error."""
        mock_redis_client.get.return_value = "invalid json"
        
        result = await cache.get_task_list(1, "todo", 10, 0, True)
        
        assert result is None

    async def test_set_task_list(self, cache, mock_redis_client):
        """Test setting task list in cache."""
        tasks = [
            Task(id=1, title="Task 1", content="Content 1", status=TaskStatus.todo, user_id=1),
            Task(id=2, title="Task 2", content="Content 2", status=TaskStatus.done, user_id=1)
        ]
        page = Page.create(tasks, page=1, page_size=10, total_items=2)
        
        mock_redis_client.set.return_value = True
        
        await cache.set_task_list(1, "todo", 10, 0, True, page, 300)
        
        mock_redis_client.set.assert_called_once()

    async def test_delete_task_list(self, cache, mock_redis_client):
        """Test deleting all task lists for a user."""
        mock_redis_client.keys.return_value = ["tasks:user:1:status:todo:limit:10:offset:0:newest:True", "tasks:user:1:status:all:limit:10:offset:0:newest:False"]
        mock_redis_client.delete.return_value = 2
        
        await cache.delete_task_list(1)
        
        mock_redis_client.keys.assert_called_once_with("tasks:user:1:*")
        mock_redis_client.delete.assert_called_once_with("tasks:user:1:status:todo:limit:10:offset:0:newest:True", "tasks:user:1:status:all:limit:10:offset:0:newest:False")

    async def test_delete_task_list_no_keys(self, cache, mock_redis_client):
        """Test deleting task lists when no keys exist."""
        mock_redis_client.keys.return_value = []
        
        await cache.delete_task_list(1)
        
        mock_redis_client.keys.assert_called_once_with("tasks:user:1:*")
        mock_redis_client.delete.assert_not_called()

    async def test_delete_task_list_with_error(self, cache, mock_redis_client):
        """Test deleting task lists with error."""
        mock_redis_client.keys.side_effect = Exception("Redis error")
        
        await cache.delete_task_list(1)
        
        mock_redis_client.keys.assert_called_once_with("tasks:user:1:*")

    async def test_get_task_list_with_different_statuses(self, cache, mock_redis_client):
        """Test task list retrieval with different status values."""
        statuses = [None, "todo", "in_progress", "done"]
        
        for status in statuses:
            mock_redis_client.get.return_value = '{"items": [], "page": 1, "page_size": 10, "total_items": 0, "total_pages": 0, "has_next": false, "has_previous": false}'
            
            result = await cache.get_task_list(1, status, 10, 0, True)
            
            assert result is not None
            mock_redis_client.reset_mock()

    async def test_get_task_list_with_different_pagination(self, cache, mock_redis_client):
        """Test task list retrieval with different pagination parameters."""
        mock_redis_client.get.return_value = '{"items": [], "page": 2, "page_size": 20, "total_items": 50, "total_pages": 3, "has_next": true, "has_previous": true}'
        
        result = await cache.get_task_list(1, "todo", 20, 20, False)
        
        assert result is not None
        assert result.page == 2
        assert result.page_size == 20
        assert result.has_next is True
        assert result.has_previous is True
