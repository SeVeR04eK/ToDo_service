# Changelog

All notable changes to this project will be documented in this file.

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
