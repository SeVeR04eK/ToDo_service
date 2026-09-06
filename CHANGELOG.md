# Changelog

All notable changes to this project will be documented in this file.


## [0.4.0] - 2026-09-06

### Added

#### Cache

* Redis-backed cache-aside layer for users, roles, tasks, and paginated task lists to reduce database load
* Cache interfaces and Redis implementations for user, role, and task data
* JSON serialization for cached domain models and paginated responses
* Read-through cache lookups and background invalidation integrated into UserService, TaskService, and AdminService
* Fail-fast Redis configuration and cache dependency providers

#### Rate Limiting

* Redis-based API rate limiting with configurable limits for authentication, user, task, and admin endpoints
* Sliding window log and sliding window counter algorithms for request limiting
* Login-specific rate limiting with identifier-based request tracking
* Fail-closed behavior for authentication rate limiting when Redis is unavailable
* `RateLimiter` abstraction and domain-level rate limit exceeded exception
* `Retry-After` headers for rate-limited responses

### Changed

* Added Redis configuration and environment variables for application and test environments
* Applied rate limiting dependencies to protected API routes
* Restructured Redis infrastructure to support caching and rate limiting

### Tests

* Added cache, serializer, and Redis integration tests
* Added rate limiting tests covering both algorithms, endpoint limits, login protection, and failure behavior
* Updated fixtures and CI to provide Redis for automated tests


---

## [0.3.0] - 2026-08-22

### Added

- Refresh token rotation, reuse detection, token families, and revocation.
- JWT iss, aud, iat, and jti claims.
- Logout and logout-all endpoints.
- Password strength validation.
- Current password validation for password updates.
- 30-day absolute refresh token family lifetime.

### Changed
- Allow multiple active refresh token sessions.
- Require previous_password for password updates.
- Increased default pagination limit to 100.
- Increased maximum offset to 10,000.
- Updated migrations, repositories, services, DI, and tests.

### Fixed
- Removed unnecessary default value from RoleRead ID.

### Documentation
- Improved README and split documentation into separate files.

---

## [0.2.0] - 2026-08-15

### Added

- Unit of Work architecture with centralized transaction management
- Atomic refresh-token consumption to prevent concurrent token reuse
- Database indexes for frequently queried task and refresh-token columns
- Database connection pooling and health check endpoint
- `InvalidPaginationParameters` exception for invalid pagination usage

### Changed

- Migrated services and repositories to the Unit of Work pattern
- Optimized pagination count queries for better database performance
- Added pagination validation when filtering users by username
- Added null-safe role checks for authentication and authorization
- Updated API documentation and README with Unit of Work, token rotation, and pagination changes

### Fixed

- Updated authentication to return OAuth2-compatible token responses

### Tests

- Updated authentication and pagination tests
- Added Unit of Work integration tests for commit, rollback, and transaction atomicity
- Updated repository and service tests for transactional behavior

---

## [0.1.1] - 2026-08-05

### Added
- Structured application logging with `structlog`
- Request logging and correlation ID middleware for request tracing
- Configurable log levels through environment variables
- Standardized API response models:
  - `DataResponse`
  - `ListResponse`
  - `PaginatedResponse`
- Domain-level pagination support with pagination metadata
- Security headers middleware with optional HSTS support
- Configurable CORS settings

### Changed
- Standardized API responses using a consistent `data` wrapper format
- Updated paginated responses:
  - renamed `items` to `data`
  - renamed `pagination` to `meta`
- Updated repositories, services, and endpoints to support pagination
- Centralized middleware registration and configuration
- Improved structured logging across services, authentication, exceptions, and background tasks
- Updated API documentation and OpenAPI schemas
- Updated environment configuration for logging, CORS, and security settings

### Tests
- Updated API tests for standardized response formats
- Added validation for pagination metadata and response structures
- Updated authentication, user, task, and admin endpoint tests


## [0.1.0] - 2026-08-02

### Added
- Clean Architecture structure
- Repository pattern
- Secure configuration management
- Production-ready Docker setup
- Multi-stage Docker build
- Separate development and production environments
- Centralized domain exception handling
- Enhanced OpenAPI documentation with detailed schemas, examples, and response documentation

### Changed
- Moved exceptions from the core layer to the domain layer
- Moved mappers to the infrastructure layer
- Removed HTTPException handling from routers
- Improved dependency injection structure

### Tests
- Updated tests to match the new project architecture
- Added use case tests
- Improved API test coverage
- Added edge case tests
