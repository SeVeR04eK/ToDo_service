# API Examples

## Health Check

![Health](../screenshots/health.png)

### GET /health

Request:
```
GET /health
```

Response:
```
{
    "status": "healthy",
    "timestamp": "2026-08-15T12:00:00.000000",
    "service": "ToDo Service API",
    "version": "0.3.0",
    "database": {
        "status": "healthy",
        "error": null
    }
}
```

**Note:** Use this endpoint for service monitoring and health checks in production environments.

---

## Auth

![Auth](../screenshots/auth.png)

### POST /auth/authentication

Request:
```
Content-Type: application/x-www-form-urlencoded

username=user
password=user12345
```

Response:
```
{
    "refresh_token": "example.refresh.token",
    "access_token": "example.access.token",
    "token_type": "bearer",
    "expires_in": 900
}
```

### POST /auth/refresh

Request
```
{
  "refresh_token": "example.refresh.token"
}
```

Response:
```
{
    "refresh_token": "example.new.refresh.token",
    "access_token": "example.new.access.token",
    "token_type": "bearer",
    "expires_in": 900
}
```

**Note:** Refresh token rotation is enabled - each refresh returns a new refresh token and invalidates the old one.

### POST /auth/logout

Request:
```
{
  "refresh_token": "example.refresh.token"
}
```

Response:
```
204 No Content
```

**Note:** Revokes the current refresh token session.

### POST /auth/logout-all

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
204 No Content
```

**Note:** Revokes all refresh token sessions for the authenticated user.

---

## User

![User](../screenshots/user.png)

### GET    /user/me

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": {
        "username": "user",
        "id": 1,
        "is_active": true,
        "role": {
            "name": "user"
        }
    }
}
```

### POST   /user/me

Request:
```
{
  "username": "user",
  "password": "user12345",
  "password_confirm": "user12345"
}
```

Response:
```
{
  "data": {
    "username": "user",
    "id": 1,
    "is_active": true,
    "role": {
      "name": "user"
    }
  }
}
```

### PATCH  /user/me

Request:
```
Authorization: Bearer <access_token>

{
  "username": "new_user",
  "password": "user12345",
  "password_confirm": "user12345",
  "previous_password": "oldpassword123"
}
```

Response:
```
{
    "data": {
        "username": "new_user",
        "id": 1,
        "is_active": true,
        "role": {
            "name": "user"
        }
    }
}
```

**Note:** The `previous_password` field is required only when updating the password. This ensures users must provide their current password before changing to a new one.

### DELETE /user/me

Request:
```
Authorization: Bearer <access_token>
```

---

## Tasks

![Tasks](../screenshots/tasks.png)

### GET    /tasks/me

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": [
        {
            "id": 1,
            "title": "example title",
            "content": "example content",
            "status": "todo",
            "user_id": 1
        }
    ],
    "meta": {
        "page": 1,
        "page_size": 10,
        "total_items": 1,
        "total_pages": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

### POST   /tasks/me

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example title",
  "content": "example content",
  "status": "todo"
}
```

Response:
```
{
    "data": {
        "id": 1,
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": 1
    }
}
```

### GET    /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": {
        "id": {task_id},
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": 1
    }
}
```

### PATCH  /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example new title",
  "content": "example new content",
  "status": "done"
}
```

Response:
```
{
    "data": {
        "id": {task_id},
        "title": "example new title",
        "content": "example new content",
        "status": "done",
        "user_id": 1
    }
}
```

### DELETE /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

---

## Admin

ONLY for users with admin role

![Admin](../screenshots/admin.png)

### GET    /admin/users 

Request:
```
Authorization: Bearer <access_token>
```

Response (paginated list):
```
{
    "data": [
        {
            "username": "user",
            "id": 1,
            "is_active": true,
            "role": {
                "name": "user"
            }
        }
    ],
    "meta": {
        "page": 1,
        "page_size": 10,
        "total_items": 1,
        "total_pages": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

Response (single user when filtered by username):
```
{
    "data": {
        "username": "user",
        "id": 1,
        "is_active": true,
        "role": {
            "name": "user"
        }
    }
}
```

**Important:** When filtering by `username`, pagination parameters (`limit` and `offset`) are **not allowed** and will result in an `InvalidPaginationParameters` exception. This is because username filtering returns a single user, making pagination meaningless.

### GET    /admin/users/{user_id}   

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": {
        "username": "user",
        "id": {user_id},
        "is_active": true,
        "role": {
            "name": "user"
        }
    }
}
```

### PATCH  /admin/users/{user_id}     

Request:
```
Authorization: Bearer <access_token>

{
  "is_active": false,
  "role": "admin"
}
```

Response:
```
{
    "data": {
        "username": "user",
        "id": {user_id},
        "is_active": false,
        "role": {
            "name": "admin"
        }
    }
}
```

### DELETE /admin/users/{user_id}     

Request:
```
Authorization: Bearer <access_token>
```

### GET    /admin/users/{user_id}/tasks  


Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": [
        {
            "id": 1,
            "title": "example title",
            "content": "example content",
            "status": "todo",
            "user_id": {user_id}
        }
    ],
    "meta": {
        "page": 1,
        "page_size": 10,
        "total_items": 1,
        "total_pages": 1,
        "has_next": false,
        "has_previous": false
    }
}
```

### GET    /admin/users/{user_id}/tasks/{task_id}    

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": {
        "id": {task_id},
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": {user_id}
    }
}
```

### PATCH  /admin/users/{user_id}/tasks/{task_id}  

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example new title",
  "content": "example new content",
  "status": "done"
}
```

Response:
```
{
    "data": {
        "id": {task_id},
        "title": "example new title",
        "content": "example new content",
        "status": "done",
        "user_id": {user_id}
    }
}
```

### DELETE /admin/users/{user_id}/tasks/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

### GET    /admin/roles         

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "data": [
        {
            "name": "user",
            "id": 1
        },
        {
            "name": "admin",
            "id": 2
        }
    ]
}
```

### POST   /admin/roles

Request:
```
Authorization: Bearer <access_token>

{
  "name": "moderator"
}
```

Response:
```
{
    "data": {
        "name": "moderator",
        "id": 7
    }
}
```

---

## Filters

![Tasks_filters](../screenshots/tasks_filters.png)
![Users_filters](../screenshots/users_filters.png)
```
GET /tasks/me?task_status=todo
GET /tasks/me?from_newest=true
GET /tasks/me?limit=10&offset=0

GET /admin/users?username=string
GET /admin/users?limit=10&offset=0
```

---

## Response Format

All successful API responses follow a consistent wrapped format for better API contract consistency and future extensibility.

**Single Item Response (DataResponse[T]):**
```
{
  "data": {
    "id": 1,
    "username": "john_doe",
    "is_active": true,
    "role": {
      "name": "user"
    }
  }
}
```

**List Response (ListResponse[T]):**
```
{
  "data": [
    {
      "id": 1,
      "name": "admin"
    },
    {
      "id": 2,
      "name": "user"
    }
  ]
}
```

**Paginated Response (PaginatedResponse[T]):**
```
{
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total_items": 157,
    "total_pages": 8,
    "has_next": true,
    "has_previous": false
  }
}
```

---

## Pagination

All list endpoints that support pagination return a consistent paginated response format with `data` and `meta` fields.

**Pagination Parameters:**
- `limit`: Number of items per page (default: 10, max: 100)
- `offset`: Number of items to skip (for pagination navigation)

**Pagination Response Fields:**
- `data`: Array of items for the current page
- `meta.page`: Current page number (1-indexed)
- `meta.page_size`: Number of items per page
- `meta.total_items`: Total number of items matching the query
- `meta.total_pages`: Total number of pages available
- `meta.has_next`: Whether there is a next page
- `meta.has_previous`: Whether there is a previous page

**Note:** Filtering affects only the `data` list and `total_items`/`total_pages` counts.