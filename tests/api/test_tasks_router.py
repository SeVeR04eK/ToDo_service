"""Tests for Tasks Router API endpoints."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import TaskFactory, UserFactory
from app.domain.enums import TaskStatus


@pytest.mark.integration
@pytest.mark.tasks
class TestTasksRouter:
    """Test suite for Tasks API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, authenticated_client: AsyncClient, task_create_data: dict):
        """Test successful task creation via API."""
        response = await authenticated_client.post("/tasks/me", json=task_create_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_create_data["title"]
        assert data["content"] == task_create_data["content"]
        assert data["status"] == task_create_data["status"]
        assert "id" in data
        assert "user_id" in data
    
    @pytest.mark.asyncio
    async def test_create_task_unauthorized(self, client: AsyncClient, task_create_data: dict):
        """Test task creation without authentication."""
        response = await client.post("/tasks/me", json=task_create_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, authenticated_client: AsyncClient):
        """Test task creation with invalid data."""
        invalid_data = {
            "title": "",  # Empty title should fail validation
            "content": "Test content"
        }
        
        response = await authenticated_client.post("/tasks/me", json=invalid_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_task_title_too_long(self, authenticated_client: AsyncClient):
        """Test task creation with title exceeding max length."""
        invalid_data = {
            "title": "a" * 81,  # Max is 80
            "content": "Test content"
        }
        
        response = await authenticated_client.post("/tasks/me", json=invalid_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_tasks_success(self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting all tasks via API."""
        await TaskFactory.create_many_in_db(db_session, count=5, user_id=test_user.id)
        
        response = await authenticated_client.get("/tasks/me")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5
    
    @pytest.mark.asyncio
    async def test_get_tasks_empty(self, authenticated_client: AsyncClient):
        """Test getting tasks when user has none."""
        response = await authenticated_client.get("/tasks/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    @pytest.mark.asyncio
    async def test_get_tasks_unauthorized(self, client: AsyncClient):
        """Test getting tasks without authentication."""
        response = await client.get("/tasks/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_status_filter(self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting tasks filtered by status."""
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.in_progress)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.done)
        
        response = await authenticated_client.get("/tasks/me?task_status=todo")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == TaskStatus.todo
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_limit(self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting tasks with limit parameter."""
        await TaskFactory.create_many_in_db(db_session, count=10, user_id=test_user.id)
        
        response = await authenticated_client.get("/tasks/me?limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_offset(self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting tasks with offset parameter."""
        await TaskFactory.create_many_in_db(db_session, count=10, user_id=test_user.id)
        
        response = await authenticated_client.get("/tasks/me?offset=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
    
    @pytest.mark.asyncio
    async def test_get_tasks_with_from_newest(self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting tasks sorted by newest first."""
        tasks = await TaskFactory.create_many_in_db(db_session, count=5, user_id=test_user.id)
        
        response = await authenticated_client.get("/tasks/me?from_newest=true")
        
        assert response.status_code == 200
        data = response.json()
        assert data[0]["id"] == tasks[-1].id
        assert data[-1]["id"] == tasks[0].id
    
    @pytest.mark.asyncio
    async def test_get_tasks_limit_validation(self, authenticated_client: AsyncClient):
        """Test that limit must be between 1 and 100."""
        response = await authenticated_client.get("/tasks/me?limit=0")
        assert response.status_code == 422
        
        response = await authenticated_client.get("/tasks/me?limit=101")
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_tasks_offset_validation(self, authenticated_client: AsyncClient):
        """Test that offset must be between 1 and 100."""
        response = await authenticated_client.get("/tasks/me?offset=0")
        assert response.status_code == 422
        
        response = await authenticated_client.get("/tasks/me?offset=101")
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_tasks_combined_filters(self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting tasks with multiple filters combined."""
        for _ in range(5):
            await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        for _ in range(3):
            await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.in_progress)
        
        response = await authenticated_client.get("/tasks/me?task_status=todo&limit=2&offset=1&from_newest=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(task["status"] == TaskStatus.todo for task in data)
    
    @pytest.mark.asyncio
    async def test_get_task_by_id_success(self, authenticated_client: AsyncClient, test_task):
        """Test getting a specific task by ID via API."""
        response = await authenticated_client.get(f"/tasks/me/{test_task.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == test_task.title
        assert data["content"] == test_task.content
    
    @pytest.mark.asyncio
    async def test_get_task_by_id_not_found(self, authenticated_client: AsyncClient):
        """Test getting a non-existent task."""
        response = await authenticated_client.get("/tasks/me/99999")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_task_by_id_unauthorized(self, client: AsyncClient, test_task):
        """Test getting a task without authentication."""
        response = await client.get(f"/tasks/me/{test_task.id}")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_task_user_isolation(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test that users cannot access other users' tasks."""
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        task = await TaskFactory.create_in_db(db_session, user_id=user1.id)
        
        # Create auth headers for user2
        from app.security import create_access_token
        from httpx import ASGITransport
        from app.main import app
        access_token = create_access_token(
            username=user2.username,
            user_id=user2.id,
            role=user2.role.name
        )
        
        client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        response = await client.get(f"/tasks/me/{task.id}")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_task_success(self, authenticated_client: AsyncClient, test_task, task_update_data: dict):
        """Test updating a task via API."""
        response = await authenticated_client.patch(f"/tasks/me/{test_task.id}", json=task_update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["title"] == task_update_data["title"]
        assert data["content"] == task_update_data["content"]
        assert data["status"] == task_update_data["status"]
    
    @pytest.mark.asyncio
    async def test_update_task_partial(self, authenticated_client: AsyncClient, test_task):
        """Test partial task update via API."""
        partial_update = {"title": "Updated Title Only"}
        
        response = await authenticated_client.patch(f"/tasks/me/{test_task.id}", json=partial_update)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title Only"
        assert data["content"] == test_task.content  # Unchanged
    
    @pytest.mark.asyncio
    async def test_update_task_not_found(self, authenticated_client: AsyncClient, task_update_data: dict):
        """Test updating a non-existent task."""
        response = await authenticated_client.patch("/tasks/me/99999", json=task_update_data)
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_task_unauthorized(self, client: AsyncClient, test_task, task_update_data: dict):
        """Test updating a task without authentication."""
        response = await client.patch(f"/tasks/me/{test_task.id}", json=task_update_data)
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_update_task_user_isolation(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test that users cannot update other users' tasks."""
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        task = await TaskFactory.create_in_db(db_session, user_id=user1.id)
        
        # Create auth headers for user2
        from app.security import create_access_token
        from httpx import ASGITransport
        from app.main import app
        access_token = create_access_token(
            username=user2.username,
            user_id=user2.id,
            role=user2.role.name
        )
        
        client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        response = await client.patch(f"/tasks/me/{task.id}", json={"title": "Hacked"})
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_task_validation_error(self, authenticated_client: AsyncClient, test_task):
        """Test task update with invalid data."""
        invalid_data = {"title": ""}  # Empty title should fail
        
        response = await authenticated_client.patch(f"/tasks/me/{test_task.id}", json=invalid_data)
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_delete_task_success(self, authenticated_client: AsyncClient, test_task):
        """Test deleting a task via API."""
        response = await authenticated_client.delete(f"/tasks/me/{test_task.id}")
        
        assert response.status_code == 204
        
        # Verify task is deleted
        get_response = await authenticated_client.get(f"/tasks/me/{test_task.id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, authenticated_client: AsyncClient):
        """Test deleting a non-existent task."""
        response = await authenticated_client.delete("/tasks/me/99999")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_task_unauthorized(self, client: AsyncClient, test_task):
        """Test deleting a task without authentication."""
        response = await client.delete(f"/tasks/me/{test_task.id}")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_delete_task_user_isolation(self, authenticated_client: AsyncClient, db_session: AsyncSession):
        """Test that users cannot delete other users' tasks."""
        user1 = await UserFactory.create_in_db(db_session, username="user1")
        user2 = await UserFactory.create_in_db(db_session, username="user2")
        
        task = await TaskFactory.create_in_db(db_session, user_id=user1.id)
        
        # Create auth headers for user2
        from app.security import create_access_token
        from httpx import ASGITransport
        from app.main import app
        access_token = create_access_token(
            username=user2.username,
            user_id=user2.id,
            role=user2.role.name
        )
        
        client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        response = await client.delete(f"/tasks/me/{task.id}")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_admin_can_access_tasks(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_admin_user):
        """Test that admin users can access task endpoints."""
        await TaskFactory.create_in_db(db_session, user_id=test_admin_user.id)
        
        response = await authenticated_admin_client.get("/tasks/me")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_task_response_model_structure(self, authenticated_client: AsyncClient, task_create_data: dict):
        """Test that task response has correct structure."""
        response = await authenticated_client.post("/tasks/me", json=task_create_data)
        
        assert response.status_code == 201
        data = response.json()
        
        required_fields = ["id", "title", "content", "status", "user_id"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
