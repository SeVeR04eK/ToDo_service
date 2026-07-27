import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas import TaskStatus
from tests.factories import UserFactory, TaskFactory, RoleFactory


@pytest.mark.integration
class TestAdminRouter:
    """Test admin router endpoints."""

    @pytest.mark.asyncio
    async def test_get_users_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession):
        """Test getting all users as admin."""
        await UserFactory.create_in_db(db_session, username="user1")
        await UserFactory.create_in_db(db_session, username="user2")
        
        response = await authenticated_admin_client.get("/admin/users")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # admin + 2 new users

    @pytest.mark.asyncio
    async def test_get_users_with_username_filter(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession):
        """Test filtering users by username."""
        await UserFactory.create_in_db(db_session, username="specific_user")
        await UserFactory.create_in_db(db_session, username="other_user")
        
        response = await authenticated_admin_client.get("/admin/users?username=specific_user")
        
        assert response.status_code == 200
        data = response.json()
        # When filtering by username, service returns single UserRead object, not list
        assert data["username"] == "specific_user"

    @pytest.mark.asyncio
    async def test_get_users_with_limit(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession):
        """Test getting users with limit."""
        for i in range(5):
            await UserFactory.create_in_db(db_session, username=f"user{i}")
        
        response = await authenticated_admin_client.get("/admin/users?limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_get_users_unauthorized(self, client: AsyncClient):
        """Test getting users without admin role."""
        response = await client.get("/admin/users")
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting a specific user by ID."""
        response = await authenticated_admin_client.get(f"/admin/users/{test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, authenticated_admin_client: AsyncClient):
        """Test getting a non-existent user."""
        response = await authenticated_admin_client.get("/admin/users/99999")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_permission_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test updating user permissions."""
        response = await authenticated_admin_client.patch(
            f"/admin/users/{test_user.id}",
            json={"is_active": False, "role": "admin"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["role"]["name"] == "admin"

    @pytest.mark.asyncio
    async def test_update_user_permission_partial(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test updating only is_active field."""
        response = await authenticated_admin_client.patch(
            f"/admin/users/{test_user.id}",
            json={"is_active": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    @pytest.mark.asyncio
    async def test_delete_user_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession):
        """Test deleting a user."""
        user_role = await RoleFactory.create_in_db(db_session, name="user")
        user = await UserFactory.create_in_db(db_session, username="to_delete", role_id=user_role.id)
        
        response = await authenticated_admin_client.delete(f"/admin/users/{user.id}")
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_admin_user(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_admin_user):
        """Test that admin cannot delete another admin."""
        from app.security import create_access_token
        from httpx import ASGITransport
        from app.main import app
        
        admin2_role = await RoleFactory.create_in_db(db_session, name="admin2")
        admin2 = await UserFactory.create_in_db(db_session, username="admin2", role_id=admin2_role.id)
        
        access_token = create_access_token(
            username=admin2.username,
            user_id=admin2.id,
            role=admin2_role.name
        )
        
        client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        response = await client.delete(f"/admin/users/{test_admin_user.id}")
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_user_tasks_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting tasks of a specific user."""
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.in_progress)
        
        response = await authenticated_admin_client.get(f"/admin/users/{test_user.id}/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_get_user_tasks_with_status_filter(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test filtering user tasks by status."""
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.todo)
        await TaskFactory.create_in_db(db_session, user_id=test_user.id, status=TaskStatus.in_progress)
        
        response = await authenticated_admin_client.get(f"/admin/users/{test_user.id}/tasks?task_status=todo")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == TaskStatus.todo

    @pytest.mark.asyncio
    async def test_get_user_task_by_id_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test getting a specific task of a user."""
        task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        response = await authenticated_admin_client.get(f"/admin/users/{test_user.id}/tasks/{task.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id

    @pytest.mark.asyncio
    async def test_update_user_task_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test updating a user's task."""
        task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        response = await authenticated_admin_client.patch(
            f"/admin/users/{test_user.id}/tasks/{task.id}",
            json={"title": "Admin Updated", "status": TaskStatus.done}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Admin Updated"
        assert data["status"] == TaskStatus.done

    @pytest.mark.asyncio
    async def test_delete_user_task_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test deleting a user's task."""
        task = await TaskFactory.create_in_db(db_session, user_id=test_user.id)
        
        response = await authenticated_admin_client.delete(f"/admin/users/{test_user.id}/tasks/{task.id}")
        
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_create_role_success(self, authenticated_admin_client: AsyncClient):
        """Test creating a new role."""
        response = await authenticated_admin_client.post(
            "/admin/roles",
            json={"name": "moderator"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "moderator"

    @pytest.mark.asyncio
    async def test_admin_endpoint_requires_admin_role(self, authenticated_client: AsyncClient):
        """Test that admin endpoints require admin role."""
        response = await authenticated_client.get("/admin/users")
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_user_permission_role_not_found(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_user):
        """Test updating user with non-existent role."""
        response = await authenticated_admin_client.patch(
            f"/admin/users/{test_user.id}",
            json={"is_active": True, "role": "nonexistent"}
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_permission_permission_denied(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_admin_user):
        """Test updating admin permissions is denied."""
        response = await authenticated_admin_client.patch(
            f"/admin/users/{test_admin_user.id}",
            json={"is_active": False, "role": "user"}
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_user_permission_denied(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_admin_user):
        """Test deleting admin user is denied."""
        response = await authenticated_admin_client.delete(f"/admin/users/{test_admin_user.id}")
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_user_tasks_user_not_found(self, authenticated_admin_client: AsyncClient):
        """Test getting tasks for non-existent user."""
        response = await authenticated_admin_client.get("/admin/users/99999/tasks")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_tasks_permission_denied(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_admin_user):
        """Test getting tasks for admin user is denied."""
        response = await authenticated_admin_client.get(f"/admin/users/{test_admin_user.id}/tasks")
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_user_task_user_not_found(self, authenticated_admin_client: AsyncClient):
        """Test getting task for non-existent user."""
        response = await authenticated_admin_client.get("/admin/users/99999/tasks/1")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_user_task_permission_denied(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_admin_user):
        """Test getting task for admin user is denied."""
        response = await authenticated_admin_client.get(f"/admin/users/{test_admin_user.id}/tasks/1")
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_user_task_user_not_found(self, authenticated_admin_client: AsyncClient):
        """Test updating task for non-existent user."""
        response = await authenticated_admin_client.patch(
            "/admin/users/99999/tasks/1",
            json={"title": "Updated"}
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_task_permission_denied(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_admin_user):
        """Test updating task for admin user is denied."""
        response = await authenticated_admin_client.patch(
            f"/admin/users/{test_admin_user.id}/tasks/1",
            json={"title": "Updated"}
        )
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_user_task_user_not_found(self, authenticated_admin_client: AsyncClient):
        """Test deleting task for non-existent user."""
        response = await authenticated_admin_client.delete("/admin/users/99999/tasks/1")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_task_permission_denied(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession, test_admin_user):
        """Test deleting task for admin user is denied."""
        response = await authenticated_admin_client.delete(f"/admin/users/{test_admin_user.id}/tasks/1")
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_roles_success(self, authenticated_admin_client: AsyncClient, db_session: AsyncSession):
        """Test getting all roles."""
        await RoleFactory.create_in_db(db_session, name="moderator")
        
        response = await authenticated_admin_client.get("/admin/roles")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
