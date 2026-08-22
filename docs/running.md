# Running the Project

The project supports three execution modes:

**Docker DEV** — local development with hot‑reload and bind‑mount

**Docker PROD** — production-oriented container configuration

**Manual Setup** — run without Docker using your own environment

**⚠️ Important**: In `app/core/config.py`, the line `ENVIRONMENT = os.getenv("ENVIRONMENT", "local")` controls which `.env` file is loaded. Change this to:
- `"dev"` to load `.env.dev`
- `"prod"` to load `.env.prod`
- `"local"` to load `.env` (or keep as default)
---

## Docker Development Mode (DEV)

### Overview

The development environment uses a multi-stage Docker build with:
- Hot reload enabled for fast development
- Source code mounted as volume
- Development dependencies included
- Automatic database migrations on startup
- Seed scripts for initial data setup

### 1. Clone repository

```
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd ToDo_service
```

---

### 2. Generate secret key

```
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 3. Setup environment variables

The `.env.dev` file is already provided with default values. Update the `SECRET_KEY` with your generated key:

```bash
# .env.dev
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/todo_service
SECRET_KEY=your_generated_secret_key_here
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=admin123
DEBUG=true
```

**⚠️ Important**: When running with Docker DEV mode, ensure the `DATABASE_URL` uses `db` as the hostname (not `localhost`), as the database runs in a separate Docker container within the same network.

---

### 4. Run development environment

```bash
docker compose -f docker-compose.dev.yml up --build
```

This will:
- Build the Docker image using the `dev` stage
- Start PostgreSQL database
- Start the FastAPI backend with hot reload
- Run database migrations automatically
- Run seed scripts (roles and admin user)

---

### 5. Access the application

- **API Documentation**: http://127.0.0.1:8000/docs
- **Database**: localhost:5432

---

### 6. Stop the environment

```bash
docker compose -f docker-compose.dev.yml down
```

To remove volumes (including database data):

```bash
docker compose -f docker-compose.dev.yml down -v
```

### **For other execution mode look into [running.md](docs/running.md).**

---

## Docker Production-like Mode (PROD)

### Overview

The production-oriented Docker configuration uses:
- Multi-stage Docker build
- Production ASGI server (Gunicorn with Uvicorn workers)
- No source code volumes
- Only production dependencies
- Health checks and restart policies
- Network isolation

### 1. Clone repository

```
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd ToDo_service
```

---

### 2. Setup environment variables

Create `.env.prod` with production values:

```bash
# .env.prod
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/todo_service
SECRET_KEY=your_production_secret_key_minimum_32_characters
FIRST_ADMIN_USERNAME=admin
FIRST_ADMIN_PASSWORD=your_secure_admin_password
DEBUG=false
```

**⚠️ Security Notice**: In production, use proper secrets management (HashiCorp Vault, AWS Secrets Manager, etc.) instead of environment files.

---

### 3. Run production environment

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

This will:
- Build the Docker image using the `prod` stage
- Start PostgreSQL with health checks
- Start FastAPI with Gunicorn (4 workers)
- Run database migrations automatically
- Configure restart policies

**Note**: Seed scripts are NOT run in production. Run them manually if needed:

```bash
docker compose -f docker-compose.prod.yml exec backend python -m scripts.seed_roles
docker compose -f docker-compose.prod.yml exec backend python -m scripts.seed_admin
```

---

### 4. Access the application

- **API Documentation**: http://127.0.0.1:8000/docs
- **Database**: localhost:5432

---

### 5. Stop the environment

```bash
docker compose -f docker-compose.prod.yml down
```

To remove volumes:

```bash
docker compose -f docker-compose.prod.yml down -v
```

---

## Manual Setup

### 1. Clone repository

```
git clone https://github.com/SeVeR04eK/ToDo_service.git
cd ToDo_service
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
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 5. Create database

```
CREATE DATABASE todo_service;   #psql
```

---

### 6. Setup environment variables

Use `.env.dev` as a template for local development:

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
python -m scripts.seed_roles
python -m scripts.seed_admin
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