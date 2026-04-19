# ToDo Service Backend API (FastAPI + PostgreSQL)

A production-oriented REST API for task management with authentication, authorization (RBAC), and scalable architecture.

---

## Overview

This project implements a fully-featured backend service for managing tasks and users. It follows clean architecture principles, separates concerns, and mimics real-world backend systems.

**Key goals:**

* Build a secure and scalable API
* Demonstrate backend engineering best practices

---

## Tech Stack

* **Python 3.9+**
* **FastAPI** — high-performance async web framework
* **Uvicorn** — ASGI server
* **PostgreSQL** — relational database
* **SQLAlchemy (ORM)** — database abstraction
* **Alembic** — database migrations
* **Pydantic** — data validation & serialization
* **Pydantic Settings** — environment configuration
* **asyncpg** — async PostgreSQL driver
* **psycopg2** — sync PostgreSQL driver for alembic
* **JWT (JSON Web Tokens)** — authentication
* **Passlib / bcrypt** — password hashing
* **python-multipart** — form/file uploads
* **Black** — code formatting

---

## Features

### Authentication & Authorization

* User registration & login
* Password hashing (bcrypt)
* JWT-based authentication (access tokens)
* Refresh token rotation
* Role-based access control (RBAC)
* Active/inactive user handling

---

### User Management

Features available to regular users:

* Create Account
* Get Account Information 
* Update Account Information 
* Delete Account  

---

### Admin Management

Functionality available only to administrators.

#### User Operations
* List Users (filtering & pagination)  
* Search Users (`username` or `id`)  
* Block / Unblock Users** — toggle `is_active` status  
* Change User Role (non-admin users only)  
* Delete User (non-admin users only)  

#### User Task Operations
* Get User Tasks — list tasks of a specific user (filtering & pagination)  
* Get User Task
* Update User Task
* Delete User Task  

#### Role Management
* Create Role  
* Get Roles 

---

### Task Management

Functionality for managing personal tasks:

* Create Task 
* Update Task 
* Delete Task 
* Change Task Status (`todo`, `in_progress`, `done`)  
* Get Tasks (filter by status / from newest)  
* Get Task

---

### Security

* Password hashing
* Protected endpoints via dependencies
* Ownership checks (users access only their data)
* Admin overrides
* Proper HTTP status codes (401 / 403)

---

### Architecture

```
ToDo_service/
├── app/                      # main application package
│   ├── api/                  # API layer (routing, dependencies)
│   │   └── routers/          # individual FastAPI routers
│   ├── authorization/        # Role based access control
│   ├── core/                 # configuration, settings, security
│   ├── db/                   # database connection, session, engine
│   ├── migrations/           # Alembic migrations
│   │   └── versions/         # generated migration files
│   ├── models/               # SQLAlchemy ORM models
│   ├── repository/           # data access layer (CRUD repositories)
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # business logic layer
│   ├── utils/                # helper utilities
│   └── main.py               # FastAPI application entry point
├── scripts/                  # helper scripts (seed)
├── screenshots/              # screenshots for README.md
├── alembic.ini               # Alembic configuration
├── LICENSE                   # project license
├── README.md                 # project documentation
├── .env                      # environment variables (not committed)
├── .gitignore                # Git ignore rules
└── requirements.txt          # project dependencies


```

**Principle:**
`route → service → repository → database`

---

## Database Design

### Users

* id
* username (unique)
* password (hashed)
* role_id 
* is_active

---

### Tasks

* id
* title
* content
* status (Enum)
* user_id (FK)

---

### Refresh Tokens

* id
* user_id (FK)
* token
* expires_at

---

### Roles

* id
* name


---

### User ↔ Role

* many-to-one relationship

---

## Authentication Flow

1. User logs in
2. Server validates credentials
3. JWT token is issued
4. Client sends token in headers
5. Protected endpoints validate token

---

## API Examples

### Auth

![Auth](screenshots/auth.png)

* #### POST /auth/authentication

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
    "token_type": "bearer"
}
```

* #### POST /auth/refresh

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
    "token_type": "bearer"
}
```

---

### User

![User](screenshots/user.png)

* #### GET    /user/me

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "username": "user",
    "id": 1,
    "is_active": true,
    "role": {
        "name": "user"
    }
}
```

* #### POST   /user/me

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
  "username": "user",
  "id": 1,
  "is_active": true,
  "role": {
    "name": "user"
  }
}
```

* #### PATCH  /user/me

Request:
```
Authorization: Bearer <access_token>

{
  "username": "new_user",
  "password": "user12345",
  "password_confirm": "user12345"
}
```

Response:
```
{
    "username": "new_user",
    "id": 1,
    "is_active": true,
    "role": {
        "name": "user"
    }
}
```

* #### DELETE /user/me

Request:
```
Authorization: Bearer <access_token>
```


### Tasks

![Tasks](screenshots/tasks.png)

* #### GET    /tasks/me

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
[
    {
        "id": 1,
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": 1
    }
]
```

* #### POST   /tasks/me

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
    "id": 1,
    "title": "example title",
    "content": "example content",
    "status": "todo",
    "user_id": 1
}
```

* #### GET    /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "id": {task_id},
    "title": "example title",
    "content": "example content",
    "status": "todo",
    "user_id": 1
}
```

* #### PATCH  /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example new title",
  "content": "example new content ",
  "status": "done"
}
```

Response:
```
{
    "id": {task_id},
    "title": "example new title",
    "content": "example new content ",
    "status": "done",
    "user_id": 1
}
```

* #### DELETE /tasks/me/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

---

### Admin

ONLY for users with admin role

![Admin](screenshots/admin.png)

* #### GET    /admin/users 

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
[
    {
        "username": "user",
        "id": 1,
        "is_active": true,
        "role": {
            "name": "user"
        }
    }
]
```

* #### GET    /admin/users/{user_id}   

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "username": "user",
    "id": {user_id},
    "is_active": true,
    "role": {
        "name": "user"
    }
}
```

* #### PATCH  /admin/users/{user_id}     

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
    "username": "user",
    "id": {user_id},
    "is_active": false,
    "role": {
        "name": "admin"
    }
}
```

* #### DELETE /admin/users/{user_id}     

Request:
```
Authorization: Bearer <access_token>
```

* #### GET    /admin/users/{user_id}/tasks  


Request:
```
Authorization: Bearer <access_token>
```

Response:
```
[
    {
        "id": 1,
        "title": "example title",
        "content": "example content",
        "status": "todo",
        "user_id": {user_id}
    }
]
```

* #### GET    /admin/users/{user_id}/tasks/{task_id}    

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
{
    "id": {task_id},
    "title": "example title",
    "content": "example content",
    "status": "todo",
    "user_id": {user_id}}
}
```

* #### PATCH  /admin/users/{user_id}/tasks/{task_id}  

Request:
```
Authorization: Bearer <access_token>

{
  "title": "example new title",
  "content": "example new content ",
  "status": "done"
}
```

Response:
```
{
    "id": {task_id},
    "title": "example new title",
    "content": "example new content ",
    "status": "done",
    "user_id": {user_id}
}
```

* #### DELETE /admin/users/{user_id}/tasks/{task_id}

Request:
```
Authorization: Bearer <access_token>
```

* #### GET    /admin/roles         

Request:
```
Authorization: Bearer <access_token>
```

Response:
```
[
    {
        "name": "user",
        "id": 1
    },
    {
        "name": "admin",
        "id": 2
    }
]
```

* #### POST   /admin/roles     

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
    "name": "moderator",
    "id": 7
}
```


---

### Filters

![Tasks_filters](screenshots/tasks_filters.png)
![Users_filters](screenshots/users_filters.png)
```
GET /tasks/me?task_status=todo
GET /tasks/me?from_newest=true
GET /tasks/me?limit=10&offset=0

GET /admin/users?username=string
GET /admin/users?limit=10&offset=0
```

---

## Running the Project

### 1. Clone repository

```
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd todo-backend
```

---

### 2. Create virtual environment

```
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Generate secret key

```
python app/core/secret.py
```

---

### 5. Create database

```
CREATE DATABASE todo_service;   #psql
```

---

### 6. Setup environment variables

Create `.env` file:

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todo_service
SECRET_KEY=your_secret_key           
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=admin123
```

---

### 7. Run migrations

```
alembic upgrade head
```

---

### 8. Run seeds

```
python scripts/seed_roles.py
python scripts/seed_admin.py
```

---

### 9. Start server

```
uvicorn app.main:app --reload
```

---

### 10. Open docs

```
http://127.0.0.1:8000/docs
```

---

## Key Engineering Decisions

* Separation of concerns (routes vs services vs repository)
* Dependency injection via FastAPI
* RBAC instead of hardcoded checks
* Alembic migrations instead of manual DB changes
* Explicit error handling (401 vs 403)

---

## Why This Project Matters

This project demonstrates:

* Real-world backend architecture
* Secure authentication practices
* Database design skills
* API design and filtering
* Understanding of authorization models

## License

MIT License
