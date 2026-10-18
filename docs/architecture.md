# Architecture

The application follows **Clean Architecture** and is divided into four main layers:

* **Domain** — entities, value objects, domain exceptions, and interfaces
* **Application** — use cases, services, DTOs, and application interfaces
* **Infrastructure** — database, repositories, security, Redis, Celery, RabbitMQ, and Unit of Work implementations
* **Presentation** — FastAPI routers, schemas, dependencies, middleware, and exception handlers

Dependencies point inward toward the domain layer. Infrastructure-specific implementations are provided through interfaces and dependency injection, keeping business logic independent from external frameworks and services.

---

## Project Structure

```text
app/
├── application/       # use cases, services, DTOs, interfaces
├── core/              # configuration and logging
├── domain/            # entities, interfaces, value objects, exceptions and enums
├── infrastructure/    # database, repositories, security, Redis, Celery, RabbitMQ, services and UoW
├── migrations/        # Alembic migration versions
├── presentation/      # API, schemas, dependencies, middleware, routers and exception handlers
└── main.py            # application entry point

tests/
├── api/
├── infrastructure/
├── repositories/
├── services/
└── use_cases/
```

---

## Request Flow

Synchronous HTTP requests follow the application layer boundaries:

```text
                    ┌─────────────────┐
                    │   HTTP Request  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │  FastAPI Router │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │     Use Case    │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │     Service     │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │   Unit of Work  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │   Repository    │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    └─────────────────┘
```

The FastAPI application handles the HTTP lifecycle, while use cases and services contain application logic. Repositories provide persistence operations through interfaces defined outside the infrastructure layer.

---

## Reverse Proxy and Load Balancing

The application is accessed through **Nginx**, which acts as the public entry point for HTTP traffic.

Clients do not connect directly to the FastAPI containers.

```text
Client
   │
   │ HTTPS :443
   ▼
┌─────────────────┐
│      Nginx      │
│ Reverse Proxy   │
└────────┬────────┘
         │
         │ load balancing
         │
    ┌────┼────────────┐
    │    │            │
    ▼    ▼            ▼
┌──────┐ ┌──────┐ ┌──────┐
│backend│ │backend│ │backend│
│  -1  │ │  -2  │ │  -3  │
│:8000 │ │:8000 │ │:8000 │
└──────┘ └──────┘ └──────┘
```

Nginx is responsible for:

* accepting incoming HTTP and HTTPS connections
* redirecting HTTP traffic to HTTPS
* terminating TLS connections
* forwarding requests to FastAPI backend containers
* distributing requests between backend replicas
* forwarding client information through proxy headers

The backend containers listen on port `8000` internally.

They do **not** publish port `8000` to the host.

Each container has its own network namespace and IP address, therefore all backend containers can listen on the same container port:

```text
backend-1 → 172.x.x.2:8000
backend-2 → 172.x.x.3:8000
backend-3 → 172.x.x.4:8000
```

There is no port conflict because the containers have different IP addresses.

The backend services use Docker's internal network and are exposed to Nginx through Docker service names:

```nginx
upstream backend {
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}
```

Only Nginx publishes ports to the host:

```text
Host :80  → Nginx :80
Host :443 → Nginx :443
```

Backend services do not use:

```yaml
ports:
  - "8000:8000"
```

Instead, they use:

```yaml
expose:
  - "8000"
```

The application is therefore accessed through:

```text
https://localhost
```

rather than:

```text
http://localhost:8000
```

---

## HTTPS and TLS

Nginx terminates TLS connections.

The HTTP request flow is:

```text
Client
   │
   │ HTTP :80
   ▼
 Nginx
   │
   │ 301 redirect
   ▼
Client
   │
   │ HTTPS :443
   ▼
 Nginx
   │
   │ decrypted HTTP
   ▼
FastAPI backend
```

HTTP traffic is redirected to HTTPS:

```nginx
server {
    listen 80;
    server_name localhost;

    return 301 https://$host$request_uri;
}
```

The HTTPS server uses a TLS certificate:

```nginx
server {
    listen 443 ssl;
    server_name localhost;

    ssl_certificate /etc/nginx/certs/localhost+1.pem;
    ssl_certificate_key /etc/nginx/certs/localhost+1-key.pem;
}
```

For local development, certificates are generated with `mkcert`.

Certificates are not stored in the Docker image or committed to Git.

---

## Docker Architecture

The project uses Docker Compose to run the application and its infrastructure.

### Development Environment

The development environment contains:

```text
                    ┌─────────────────┐
                    │      Nginx      │
                    │     :80/:443    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Backend     │
                    │      :8000      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        PostgreSQL         Redis         RabbitMQ
                                            │
                                     ┌──────┴──────┐
                                     ▼             ▼
                               Celery Worker   Celery Beat
```

The development environment runs a single backend replica.

Database initialization is performed by a dedicated one-shot `init-db` service.

---

### Production Environment

The production environment supports horizontal scaling:

```text
                         Client
                           │
                           │ HTTPS
                           ▼
                    ┌─────────────┐
                    │    Nginx    │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │backend-1 │  │backend-2 │  │backend-3 │
       │  :8000   │  │  :8000   │  │  :8000   │
       └─────┬────┘  └─────┬────┘  └─────┬────┘
             │             │             │
             └─────────────┼─────────────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
       PostgreSQL        Redis        RabbitMQ
                                          │
                                  ┌───────┴───────┐
                                  ▼               ▼
                            Celery Worker    Celery Beat
```

All backend replicas run the same application code.

Each replica listens on port `8000` inside its own container.

Nginx distributes incoming requests between the replicas.

---

## Docker Network

Application services communicate through a dedicated Docker network:

```text
                app_network
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
     Nginx        Backend       PostgreSQL
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
        Redis   RabbitMQ   Celery
```

Docker service names are used for internal communication.

Examples:

```text
PostgreSQL → db:5432
Redis      → redis:6379
RabbitMQ   → rabbitmq:5672
Backend    → backend-1:8000
```

The services communicate using the internal Docker network instead of `localhost`.

For example, from inside a backend container:

```text
localhost
```

refers to the backend container itself.

It does not refer to PostgreSQL, Redis, RabbitMQ, or the host machine.

Therefore the application uses Docker service names in its environment configuration.

---

## Database Initialization

Database initialization is handled by a dedicated one-shot Docker Compose service called `init-db`.

The initialization flow is:

```text
PostgreSQL
    │
    │ healthcheck passes
    ▼
 init-db
    │
    ├── alembic upgrade head
    │
    └── development only:
          ├── seed_roles
          └── seed_admin
    │
    ▼
Container exits successfully
    │
    ▼
Backend / Celery services start
```

The `init-db` service waits until PostgreSQL is healthy before running migrations.

Alembic migrations are executed only by this initialization service.

This prevents multiple backend replicas, Celery workers, or Celery Beat instances from attempting to run migrations simultaneously.

### Development

In the development environment:

```text
alembic upgrade head
        ↓
seed_roles
        ↓
seed_admin
```

Development seed scripts create the initial roles and administrator.

### Production

In production:

```text
alembic upgrade head
```

is executed by `init-db`.

Production does not automatically run development seed scripts.

This keeps database schema initialization separate from application startup.

---

## Background Processing

Background processing is implemented with **Celery** and **RabbitMQ**.

The FastAPI application does not execute long-running background work inside the request lifecycle. Instead, the application publishes a Celery task to RabbitMQ and returns control to the HTTP request flow.

```text
                         ┌─────────────────┐
                         │    FastAPI      │
                         └────────┬────────┘
                                  │
                                  │ publish task
                                  ▼
                         ┌─────────────────┐
                         │ Celery Publisher│
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │    RabbitMQ     │
                         │     Broker      │
                         └────────┬────────┘
                                  │
                                  │ deliver task
                                  ▼
                         ┌─────────────────┐
                         │ Celery Worker   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Celery Task   │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ External Service│
                         │ / Database      │
                         └─────────────────┘
```

---

## Celery Integration

Celery is isolated inside the infrastructure layer.

Application services depend on the `MessagePublisher` interface rather than directly depending on Celery:

```text
                    Application Layer
                           │
                           │ MessagePublisher
                           ▼
              ┌─────────────────────────┐
              │ CeleryMessagePublisher  │
              └────────────┬────────────┘
                           │
                           ▼
                    Celery Task
                           │
                           ▼
                        RabbitMQ
                           │
                           ▼
                    Celery Worker
```

This keeps the application layer independent from the Celery framework. The concrete `CeleryMessagePublisher` is an infrastructure implementation injected through the application interfaces.

---

## Welcome Email Flow

Welcome emails are processed asynchronously after user registration:

```text
User Registration
       │
       ▼
   UserService
       │
       ▼
 MessagePublisher
       │
       ▼
CeleryMessagePublisher
       │
       ▼
   RabbitMQ
       │
       ▼
 Celery Worker
       │
       ▼
send_welcome_email_task
       │
       ▼
   EmailService
       │
       ▼
    SMTP Server
```

The API request does not wait for the email to be delivered.

The email task supports automatic retries with exponential backoff and jitter for failures that propagate as exceptions.

---

## Periodic Tasks

Periodic maintenance tasks are scheduled by **Celery Beat**.

```text
                    ┌─────────────────┐
                    │   Celery Beat   │
                    └────────┬────────┘
                             │
                             │ schedule task
                             ▼
                    ┌─────────────────┐
                    │    RabbitMQ     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Celery Worker   │
                    └────────┬────────┘
                             │
                             ▼
                clean_expired_tokens_task
                             │
                             ▼
                       PostgreSQL
```

Celery Beat is responsible only for scheduling. Task execution is performed by Celery workers.

The expired refresh-token cleanup task periodically removes expired tokens from PostgreSQL.

---

## Task Reliability

Celery tasks use retry and acknowledgement mechanisms to improve reliability:

* Failed email tasks can be retried automatically
* Retry backoff increases the delay between attempts
* Retry jitter prevents synchronized retry attempts
* Late acknowledgements allow tasks to be acknowledged after execution
* Worker failures can result in task redelivery

The system therefore follows an **at-least-once task delivery model**.

Tasks should not be assumed to execute exactly once.

---

## System Architecture

The complete application architecture can be represented as:

```text
                                      ┌─────────────────┐
                                      │      Client     │
                                      └────────┬────────┘
                                               │
                                               │ HTTPS :443
                                               ▼
                                      ┌─────────────────┐
                                      │      Nginx      │
                                      │ Reverse Proxy   │
                                      │ Load Balancer   │
                                      └────────┬────────┘
                                               │
                         ┌─────────────────────┼─────────────────────┐
                         │                     │                     │
                         ▼                     ▼                     ▼
                  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
                  │  Backend-1  │       │  Backend-2  │       │  Backend-3  │
                  │    :8000    │       │    :8000    │       │    :8000    │
                  └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
                         │                     │                     │
                         └─────────────────────┼─────────────────────┘
                                               │
                       ┌───────────────────────┼───────────────────────┐
                       │                       │                       │
                       ▼                       ▼                       ▼
                ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
                │ PostgreSQL  │        │    Redis    │        │  RabbitMQ   │
                │             │        │             │        │   Broker    │
                └─────────────┘        └─────────────┘        └──────┬──────┘
                                                                      │
                                                        ┌─────────────┴─────────────┐
                                                        │                           │
                                                        ▼                           ▼
                                                 ┌─────────────┐             ┌─────────────┐
                                                 │Celery Worker│             │ Celery Beat │
                                                 └──────┬──────┘             └──────┬──────┘
                                                        │                           │
                                                        │                           │
                                                        ▼                           ▼
                                                 Background Tasks              RabbitMQ
```

---

## Infrastructure Responsibilities

| Component | Responsibility |
| --- | --- |
| Nginx | HTTPS termination, HTTP→HTTPS redirect, reverse proxy and load balancing |
| Backend replicas | FastAPI HTTP API and request lifecycle |
| PostgreSQL | Persistent application data |
| Redis | Caching and rate limiting |
| RabbitMQ | Celery message broker |
| Celery Worker | Executes background tasks |
| Celery Beat | Schedules periodic tasks |
| `init-db` | Runs database migrations and development seed scripts |
| Docker Network | Provides internal service-to-service communication |

---

## Horizontal Scaling

The production architecture uses multiple backend replicas:

```text
Nginx
  │
  ├── backend-1:8000
  ├── backend-2:8000
  └── backend-3:8000
```

The replicas are independent application containers running the same code.

Nginx distributes incoming HTTP requests between them.

Because the application state is stored in shared infrastructure services, backend replicas do not need to share a filesystem or local process state.

Shared infrastructure includes:

```text
PostgreSQL → persistent application data
Redis      → shared cache and rate limiting
RabbitMQ   → shared task queue
```

Adding more backend replicas does not require changing the internal backend port.

For example:

```text
backend-1:8000
backend-2:8000
backend-3:8000
backend-4:8000
```

Nginx can simply include the additional service in its upstream configuration.

---

## Unit of Work & Transactions

The application uses the **Unit of Work pattern** to define transaction boundaries across repository operations.

Key characteristics:

* Services operate through a shared Unit of Work
* Repositories do not commit transactions independently
* `flush()` and `refresh()` are used for persistence within the transaction
* The Unit of Work controls commit and rollback
* Exceptions trigger automatic rollback
* Refresh token rotation is performed atomically

This centralizes transaction management and prevents individual repositories from controlling application-level transactions.

## Middleware

The API uses middleware for cross-cutting HTTP concerns:

* **Correlation ID** — assigns a unique identifier to each request
* **Request Logging** — records HTTP requests and response duration
* **Security Headers** — adds security-related HTTP headers
* **CORS** — controls allowed cross-origin requests

Middleware is configured in:

```text
app/presentation/api/middleware/setup.py
```