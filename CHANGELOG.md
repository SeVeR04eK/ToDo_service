# Changelog

All notable changes to this project will be documented in this file.


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
