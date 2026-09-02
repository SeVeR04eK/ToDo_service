"""Tests for Redis serializers."""
import pytest
from app.domain.entities import User, Role, Task
from app.domain.enums import TaskStatus
from app.domain.exceptions import SerializationError
from app.infrastructure.redis.serializers import (
    serialize_user,
    deserialize_user,
    serialize_role,
    deserialize_role,
    serialize_task,
    deserialize_task,
    serialize_task_list,
    deserialize_task_list,
    serialize_roles,
    deserialize_roles,
    to_json,
    from_json
)


@pytest.mark.unit
class TestUserSerializer:
    """Test suite for User serialization/deserialization."""

    def test_serialize_user(self):
        """Test User serialization."""
        role = Role(id=1, name="user")
        user = User(
            id=1,
            username="testuser",
            hashed_password="hashed123",
            is_active=True,
            role_id=1,
            role=role
        )
        result = serialize_user(user)
        
        assert result["id"] == 1
        assert result["username"] == "testuser"
        assert result["hashed_password"] == "hashed123"
        assert result["is_active"] is True
        assert result["role_id"] == 1
        assert result["role"]["id"] == 1
        assert result["role"]["name"] == "user"

    def test_serialize_user_without_role(self):
        """Test User serialization without role."""
        user = User(
            id=1,
            username="testuser",
            hashed_password="hashed123",
            is_active=True,
            role_id=1,
            role=None
        )
        result = serialize_user(user)
        
        assert result["role"] is None

    def test_deserialize_user(self):
        """Test User deserialization."""
        data = {
            "id": 1,
            "username": "testuser",
            "hashed_password": "hashed123",
            "is_active": True,
            "role_id": 1,
            "role": {"id": 1, "name": "user"}
        }
        result = deserialize_user(data)
        
        assert isinstance(result, User)
        assert result.id == 1
        assert result.username == "testuser"
        assert result.hashed_password == "hashed123"
        assert result.is_active is True
        assert result.role_id == 1
        assert result.role.id == 1
        assert result.role.name == "user"

    def test_deserialize_user_without_role(self):
        """Test User deserialization without role."""
        data = {
            "id": 1,
            "username": "testuser",
            "hashed_password": "hashed123",
            "is_active": True,
            "role_id": 1,
            "role": None
        }
        result = deserialize_user(data)
        
        assert isinstance(result, User)
        assert result.role is None


@pytest.mark.unit
class TestRoleSerializer:
    """Test suite for Role serialization/deserialization."""

    def test_serialize_role(self):
        """Test Role serialization."""
        role = Role(id=1, name="admin")
        result = serialize_role(role)
        
        assert result["id"] == 1
        assert result["name"] == "admin"

    def test_deserialize_role(self):
        """Test Role deserialization."""
        data = {"id": 1, "name": "admin"}
        result = deserialize_role(data)
        
        assert isinstance(result, Role)
        assert result.id == 1
        assert result.name == "admin"


@pytest.mark.unit
class TestTaskSerializer:
    """Test suite for Task serialization/deserialization."""

    def test_serialize_task(self):
        """Test Task serialization."""
        task = Task(
            id=1,
            title="Test Task",
            content="Test content",
            status=TaskStatus.todo,
            user_id=1
        )
        result = serialize_task(task)
        
        assert result["id"] == 1
        assert result["title"] == "Test Task"
        assert result["content"] == "Test content"
        assert result["status"] == "todo"
        assert result["user_id"] == 1

    def test_deserialize_task(self):
        """Test Task deserialization."""
        data = {
            "id": 1,
            "title": "Test Task",
            "content": "Test content",
            "status": "todo",
            "user_id": 1
        }
        result = deserialize_task(data)
        
        assert isinstance(result, Task)
        assert result.id == 1
        assert result.title == "Test Task"
        assert result.content == "Test content"
        assert result.status == TaskStatus.todo
        assert result.user_id == 1

    def test_deserialize_task_with_different_status(self):
        """Test Task deserialization with different status values."""
        statuses = [TaskStatus.todo, TaskStatus.in_progress, TaskStatus.done]
        for status in statuses:
            data = {
                "id": 1,
                "title": "Test Task",
                "content": "Test content",
                "status": status.value,
                "user_id": 1
            }
            result = deserialize_task(data)
            assert result.status == status


@pytest.mark.unit
class TestTaskListSerializer:
    """Test suite for Task list serialization/deserialization."""

    def test_serialize_task_list(self):
        """Test Task list serialization."""
        tasks = [
            Task(id=1, title="Task 1", content="Content 1", status=TaskStatus.todo, user_id=1),
            Task(id=2, title="Task 2", content="Content 2", status=TaskStatus.done, user_id=1)
        ]
        page_metadata = {
            "page": 1,
            "page_size": 10,
            "total_items": 2,
            "total_pages": 1,
            "has_next": False,
            "has_previous": False
        }
        result = serialize_task_list(tasks, page_metadata)
        
        assert len(result["items"]) == 2
        assert result["page"] == 1
        assert result["page_size"] == 10
        assert result["total_items"] == 2
        assert result["total_pages"] == 1

    def test_deserialize_task_list(self):
        """Test Task list deserialization."""
        data = {
            "items": [
                {"id": 1, "title": "Task 1", "content": "Content 1", "status": "todo", "user_id": 1},
                {"id": 2, "title": "Task 2", "content": "Content 2", "status": "done", "user_id": 1}
            ],
            "page": 1,
            "page_size": 10,
            "total_items": 2,
            "total_pages": 1,
            "has_next": False,
            "has_previous": False
        }
        tasks, metadata = deserialize_task_list(data)
        
        assert len(tasks) == 2
        assert all(isinstance(task, Task) for task in tasks)
        assert metadata["page"] == 1
        assert metadata["total_items"] == 2


@pytest.mark.unit
class TestRolesSerializer:
    """Test suite for Roles list serialization/deserialization."""

    def test_serialize_roles(self):
        """Test Roles list serialization."""
        roles = [
            Role(id=1, name="user"),
            Role(id=2, name="admin")
        ]
        result = serialize_roles(roles)
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "user"
        assert result[1]["id"] == 2
        assert result[1]["name"] == "admin"

    def test_deserialize_roles(self):
        """Test Roles list deserialization."""
        data = [
            {"id": 1, "name": "user"},
            {"id": 2, "name": "admin"}
        ]
        result = deserialize_roles(data)
        
        assert len(result) == 2
        assert all(isinstance(role, Role) for role in result)
        assert result[0].id == 1
        assert result[0].name == "user"
        assert result[1].id == 2
        assert result[1].name == "admin"


@pytest.mark.unit
class TestJsonSerializers:
    """Test suite for JSON serialization/deserialization."""

    def test_to_json_success(self):
        """Test successful JSON serialization."""
        data = {"key": "value", "number": 123}
        result = to_json(data)
        
        assert isinstance(result, str)
        assert "key" in result
        assert "value" in result

    def test_to_json_with_list(self):
        """Test JSON serialization with list."""
        data = [1, 2, 3, "test"]
        result = to_json(data)
        
        assert isinstance(result, str)

    def test_to_json_failure(self):
        """Test JSON serialization failure with unserializable object."""
        class Unserializable:
            pass
        
        with pytest.raises(SerializationError):
            to_json(Unserializable())

    def test_from_json_success(self):
        """Test successful JSON deserialization."""
        json_str = '{"key": "value", "number": 123}'
        result = from_json(json_str)
        
        assert result["key"] == "value"
        assert result["number"] == 123

    def test_from_json_with_list(self):
        """Test JSON deserialization with list."""
        json_str = '[1, 2, 3, "test"]'
        result = from_json(json_str)
        
        assert result == [1, 2, 3, "test"]

    def test_from_json_failure(self):
        """Test JSON deserialization failure with invalid JSON."""
        with pytest.raises(SerializationError):
            from_json("invalid json")

    def test_from_json_failure_with_type_error(self):
        """Test JSON deserialization failure with type error."""
        with pytest.raises(SerializationError):
            from_json(None)
