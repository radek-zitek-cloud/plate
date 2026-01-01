# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added - 2026-01-01

#### Configuration Management
- **Split .env configuration**: Implemented two-tier environment variable structure
  - **Root `.env`**: Infrastructure variables (POSTGRES_*, REDIS_*) used by docker-compose services
  - **`backend/.env`**: Application-specific variables (DATABASE_URL, SECRET_KEY, CORS, etc.)
  - Docker Compose loads root `.env` automatically for all services
  - Backend service loads both files (root first, then backend) via `env_file` directive
  - Created `.env.example` and `backend/.env.example` template files
  - Added note in `backend/.env` that DATABASE_URL credentials must match root .env

- **Benefits of split configuration**:
  - Single source of truth for infrastructure credentials
  - PostgreSQL container now properly uses variables from root `.env`
  - Application config stays separate and can be environment-specific
  - Prevents duplication while maintaining flexibility

#### Bug Fixes
- **API documentation**: Fixed missing endpoints in Swagger/OpenAPI docs
  - Changed `app.mount()` to `app.include_router()` in `app/main.py`
  - `app.mount()` is for sub-applications, not for including routers
  - All endpoints now properly appear in http://localhost:8000/api/v1/docs
  - Fixed endpoints: auth/login, auth/test-token, users/*, etc.

- **Docker .venv issue**: Fixed "exec /app/.venv/bin/uvicorn: no such file or directory" error
  - Created `backend/.dockerignore` to prevent host's .venv from being copied into Docker container
  - The host's .venv had shebangs pointing to host Python paths which don't exist in containers
  - Now Docker builds create a clean .venv inside the container with correct paths

- **Missing dependencies**: Added required dependencies that were missing from pyproject.toml
  - `email-validator` - Required for Pydantic's EmailStr validation
  - `python-multipart` - Required for FastAPI's OAuth2PasswordRequestForm (form data parsing)

- **Schema exports**: Fixed `app.schemas` module to properly export User and other schemas
  - Updated `backend/app/schemas/__init__.py` to export all schema classes
  - Fixed AttributeError when importing schemas in API endpoints

#### Development Workflow
- **make rebuild**: Added rebuild target to Makefile
  - Performs full rebuild of all Docker images without cache
  - Stops services, rebuilds with `--no-cache`, and restarts
  - Recommended command for dependency changes and base image updates
  - Added to help menu and documented in CLAUDE.md

#### Database Migrations
- **Automatic migrations on startup**: Implemented automatic database migration execution
  - Added lifespan context manager to `app/main.py` that runs `alembic upgrade head` on startup
  - Uses modern FastAPI lifespan API (not deprecated `@app.on_event()`)
  - Migrations run automatically when backend container starts
  - Includes error handling with informative log messages
  - Application continues to start even if migration fails (with warning)
  - Eliminates need to manually run migrations in development

- **Alembic configuration**: Configured Alembic for database migrations
  - Updated `backend/alembic/env.py` to convert async DATABASE_URL to sync for Alembic
  - Alembic requires synchronous PostgreSQL driver, so URL is converted from `postgresql+asyncpg://` to `postgresql://`
  - Added `psycopg2-binary` dependency for Alembic's synchronous database operations
  - Created initial migration: `37d1ed0daae5_initial_migration_create_users_table.py`
  - Migration creates users table with all fields, indexes, and constraints

- **Database credentials**: Fixed DATABASE_URL and postgres credentials to be consistent
  - Updated `backend/.env` to use matching credentials for DATABASE_URL and POSTGRES_* variables
  - Both now use: backend_user / backend_password / backend_db

- **Migration command**: Run migrations inside Docker container
  - Command: `docker compose exec backend alembic revision --autogenerate -m "message"`
  - Must run in container to access postgres hostname in Docker network

#### Documentation
- **CLAUDE.md**: Created comprehensive documentation for Claude Code instances working in this repository
  - Project overview and architecture patterns
  - Essential development commands (make targets, docker compose, uv)
  - Detailed architecture explanation (dependency injection, CRUD patterns, async database, JWT auth)
  - Common development tasks (adding endpoints, models, CRUD operations)
  - Environment architecture summary (dev/test/prod)
  - Docker workflow and rebuilding instructions
  - VSCode integration guidance

- **Documentation Requirements**: Established strict documentation rules in CLAUDE.md
  - Required documentation for all significant changes
  - Guidelines on what, where, and when to document
  - Emphasis on architecture decisions, breaking changes, and gotchas
  - **docs/CHANGELOG.md** marked as REQUIRED location for recording all changes

- **CHANGELOG.md**: Created changelog file following Keep a Changelog format
  - Records all notable changes with dates
  - Tracks added features, changes, and important notes
  - Must be updated with every significant change (strict requirement)
  - Added "How to Update the Changelog" section to CLAUDE.md with clear instructions and example

- **backend/.dockerignore**: Created Docker ignore file to prevent build issues
  - Excludes .venv, __pycache__, .env, and other local files from Docker builds
  - Critical for preventing "no such file or directory" errors with Python virtual environments
  - Documented importance in CLAUDE.md Docker Development Workflow section

#### Standards Established
- **Docker Compose V2**: Project standardized on `docker compose` (with space) instead of legacy `docker-compose` (hyphen)
  - Updated all documentation to reflect this standard
  - Added prominent warnings in CLAUDE.md
  - Makefile already uses correct syntax

### Changed - 2026-01-01
- Updated Makefile documentation references in CLAUDE.md to match actual targets (removed non-existent `rebuild` target, added `test` and `test-watch`)
- Corrected docker-compose.yml reference to docker-compose.yaml (actual filename)

### Notes
- This is the initial documentation setup for the project
- Existing code was not modified, only documentation was added
- Frontend directory exists but is currently empty (not documented in detail)
- Alembic migrations not yet configured (noted in documentation)
- Test infrastructure exists but no tests written yet
