# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI backend boilerplate with PostgreSQL, Redis, and Docker-based development environment. The project uses modern Python tooling (uv, SQLAlchemy 2.0 with async, Pydantic v2) and follows a modular architecture pattern.

**Critical**: This project uses Docker Compose V2. Always use `docker compose` (with a space), never `docker-compose` (with a hyphen).

## Documentation Requirements

**⚠️ STRICT RULE: THIS IS NON-NEGOTIABLE ⚠️**

**ALL SIGNIFICANT CHANGES, DECISIONS, AND ADDITIONS TO THE CODEBASE MUST BE DOCUMENTED.**

**Failure to maintain documentation, especially the CHANGELOG, is a violation of project standards.**

Every developer, AI assistant (including Claude), and contributor working on this project is **REQUIRED** to document their work. This is not a suggestion—it is a mandatory part of completing any task.

### What to Document

1. **Architecture decisions**: Why a particular pattern or technology was chosen
2. **Breaking changes**: Any changes that affect existing functionality or workflows
3. **New features**: What was added and how it works
4. **Configuration changes**: New environment variables, settings, or deployment requirements
5. **Database schema changes**: New models, migrations, or structural changes
6. **API changes**: New endpoints, modified responses, or authentication changes
7. **Gotchas and workarounds**: Non-obvious solutions to problems
8. **Bug fixes**: What was broken, root cause, and how it was fixed
9. **Dependency updates**: New or updated packages and why
10. **Infrastructure changes**: Docker, deployment, or environment modifications

### Where to Document

- **docs/CHANGELOG.md**: ⚠️ **MANDATORY** - ALL changes MUST be recorded here with date and clear description
- **This file (CLAUDE.md)**: For changes to development workflow, architecture patterns, or critical information future developers need
- **docs/ directory**: For detailed technical documentation, architecture decisions, guides
- **Code comments**: For complex logic that isn't self-evident
- **Commit messages**: Clear explanation of what and why (not just what)

### When to Update Documentation

- **Before considering work complete**: Documentation is PART of the work, not optional
- **Before committing**: Update relevant docs in the same commit as code changes
- **After architectural decisions**: Document why you chose an approach
- **When adding complexity**: If it needs explanation, document it immediately
- **When fixing bugs**: Document what was wrong and how it was fixed

### How to Update the Changelog

The changelog (docs/CHANGELOG.md) follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

1. Add entries under `## [Unreleased]` section
2. Use subsections: `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, `### Security`
3. Include date in format: `### Added - YYYY-MM-DD`
4. Be specific: What changed, why it matters, what developers need to know
5. Group related changes together
6. Update the "Recent Changes" section in this file for major changes

Example entry:
```markdown
### Added - 2026-01-01
- **User authentication**: Implemented JWT-based authentication with refresh tokens
  - New endpoint: POST /api/v1/auth/refresh
  - New environment variable: REFRESH_TOKEN_EXPIRE_DAYS (default: 7)
  - Breaking: Old session-based auth removed
```

## Environment Configuration

This project uses a **split .env configuration** for separation of concerns:

### File Structure

1. **Root `.env`** (infrastructure configuration)
   - Used by docker-compose services (PostgreSQL, Redis)
   - Contains: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
   - Template: `.env.example`
   - Gitignored: Yes

2. **`backend/.env`** (application configuration)
   - Used by the FastAPI backend application
   - Contains: `DATABASE_URL`, `SECRET_KEY`, `REDIS_URL`, `CORS`, etc.
   - Template: `backend/.env.example`
   - Gitignored: Yes

### Important Rules

- **Credentials must match**: The username/password in `DATABASE_URL` (in `backend/.env`) must match the `POSTGRES_*` variables in root `.env`
- **Load order**: Backend service loads root `.env` first, then `backend/.env` (allows overrides)
- **Never commit**: Both `.env` files are gitignored - always use `.env.example` files as templates

### Setup for New Developers

```bash
# 1. Copy example files
cp .env.example .env
cp backend/.env.example backend/.env

# 2. Generate a new SECRET_KEY
openssl rand -hex 32

# 3. Update backend/.env with the generated SECRET_KEY

# 4. Ensure DATABASE_URL credentials match root .env
# (Already matching in examples, but verify if you change them)
```

## Essential Commands

### Development Environment
```bash
# Start all services (PostgreSQL, Redis, FastAPI backend)
make dev

# Stop all services
make down

# Run tests
make test            # Run all tests in isolated environment
make test-watch      # Run tests with file watching

# View logs
make logs            # View development logs

# Access containers
make shell-backend   # Bash shell in backend container
make shell-db        # PostgreSQL shell (psql)

# Clean and rebuild
make clean           # Remove all containers and volumes
make rebuild         # Rebuild all images without cache and restart
```

### Working with Dependencies
```bash
# Install/sync dependencies (in backend/ directory)
uv sync              # Installs all dependencies including dev

# Add a new dependency
uv add <package>                    # Production dependency
uv add --dev <package>              # Development dependency
```

### Rebuilding Docker Images

**IMPORTANT**: Always use `docker compose` (with a space), not `docker-compose` (with a hyphen). This project uses Docker Compose V2.

```bash
# Full rebuild of all services without cache (RECOMMENDED)
make rebuild

# Rebuild only the backend service without cache
docker compose build --no-cache backend
docker compose up -d backend

# Quick rebuild with cache (faster, after code changes only)
docker compose build backend
docker compose up -d backend
```

Use `make rebuild` or `--no-cache` when:
- You've changed dependencies in `pyproject.toml`
- You've updated the base image
- You want to ensure a completely fresh build

### Running the Application

The backend runs at `http://localhost:8000` with auto-reload enabled in development.

- API Documentation (Swagger): `http://localhost:8000/api/v1/docs`
- Alternative Docs (ReDoc): `http://localhost:8000/api/v1/redoc`
- Health Check: `http://localhost:8000/health`

The application automatically reloads when Python files change due to uvicorn's `--reload` flag.

## Architecture

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization, CORS, health endpoint
│   ├── api/
│   │   ├── deps.py          # Dependency injection (get_db, get_current_user, auth deps)
│   │   └── v1/
│   │       ├── api.py       # Router aggregation
│   │       └── endpoints/   # Individual endpoint modules (auth, users)
│   ├── core/
│   │   ├── config.py        # Settings using pydantic-settings, loads from .env
│   │   ├── database.py      # Async SQLAlchemy engine, session factory, Base
│   │   └── security.py      # JWT token creation, password hashing (bcrypt)
│   ├── crud/
│   │   ├── base.py          # Generic CRUD base class with async methods
│   │   └── user.py          # User-specific CRUD operations
│   ├── models/              # SQLAlchemy models (User)
│   ├── schemas/             # Pydantic schemas for request/response validation
│   ├── services/            # Business logic layer
│   └── utils/               # Utility functions
├── alembic/                 # Database migrations (not yet configured)
├── tests/                   # Test directory
├── pyproject.toml           # uv project configuration
└── Dockerfile               # Development Dockerfile
```

### Key Architectural Patterns

**Dependency Injection**: FastAPI's dependency system is used extensively. Database sessions are injected via `get_db()`, user authentication via `get_current_user()`, and permissions via `get_current_active_user()` and `get_current_superuser()`.

**Generic CRUD Layer**: `crud/base.py` provides a type-safe generic base class `CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]` that implements standard database operations. Model-specific CRUD classes inherit from this and add specialized methods.

**Async Database Pattern**: All database operations use SQLAlchemy's async API. Sessions are created per-request via `AsyncSessionLocal`, automatically committed on success and rolled back on exceptions.

**Authentication Flow**: JWT-based authentication using OAuth2 password bearer tokens. Passwords are hashed with bcrypt. The `oauth2_scheme` in `deps.py` extracts tokens from Authorization headers, and `get_current_user()` validates them.

**Router Composition**: API endpoints are organized by domain (auth, users) in separate router modules, then aggregated in `api/v1/api.py` and mounted at the `/api/v1` prefix in `main.py`.

### Database

- **Engine**: Async SQLAlchemy with asyncpg driver
- **Models**: Use SQLAlchemy 2.0 `Mapped[]` type annotations and `mapped_column()`
- **Sessions**: Managed via `AsyncSessionLocal` session factory, yielded through dependency injection
- **Base Model**: All models inherit from `Base` defined in `core/database.py`

### Configuration Management

Settings are managed through `core/config.py` using `pydantic-settings`. Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql+asyncpg://user:pass@postgres:5432/db`)
  - **Railway/Production**: Railway provides `postgres://...` or `postgresql://...` URLs
  - **Automatic Conversion**: The `async_database_url` property automatically converts these to `postgresql+asyncpg://...` for async SQLAlchemy
  - **Local Development**: Use `postgresql+asyncpg://...` format in `.env` files
- `SECRET_KEY`: JWT signing key (use `openssl rand -hex 32` to generate)
- `REDIS_URL`: Redis connection string (default: `redis://redis:6379`)

Optional settings have defaults defined in the `Settings` class. Configuration is loaded from `backend/.env` which is gitignored.

**Important**: All database access uses the `async_database_url` property which ensures compatibility with both Railway-provided URLs (sync format) and local development URLs (async format). The property automatically converts `postgres://` or `postgresql://` to `postgresql+asyncpg://` for async SQLAlchemy.

## Environment Architecture

The project uses a three-environment strategy detailed in `docs/Environment-Architecture.md`:

**Development**: Docker Compose on localhost with volume mounts for hot reload. Data persists in named Docker volumes. Uses `backend/.env` for configuration.

**Test**: Docker Compose with `--profile test` flag. Ephemeral databases (no volume mounts). Tests run in isolated containers and clean up automatically. Configuration is hardcoded in docker-compose.yaml.

**Production**: Railway managed infrastructure. Uses managed PostgreSQL and Redis. Secrets managed through Railway's dashboard. Deployments triggered by git pushes to main branch.

Key principle: Development prioritizes fast iteration, test prioritizes reproducibility, production prioritizes reliability and security. Each environment has different infrastructure appropriate to its purpose.

## Docker Development Workflow

The Docker setup uses selective volume mounts to enable hot reload while preserving the container's .venv:
- `./backend/app:/app/app` mounts application code
- `./backend/alembic:/app/alembic` mounts migration files
- `./backend/tests:/app/tests` mounts test files
- The container's `/app/.venv` is NOT mounted, keeping the Docker-built virtual environment intact

When you modify Python files on your host, changes are immediately reflected in the running container and uvicorn automatically reloads.

### Critical: .dockerignore File

The `backend/.dockerignore` file is **REQUIRED** for proper Docker builds. It prevents the host's `.venv` directory (and other local files) from being copied into the container during `COPY . .` in the Dockerfile.

**Why this matters**: Without `.dockerignore`, the host's `.venv` gets copied with shebangs pointing to host Python paths (like `/home/yourname/code/backend/.venv/bin/python`). When the container tries to execute these, it fails with "no such file or directory" because those paths don't exist in the container.

The `.dockerignore` ensures Docker builds create a clean virtual environment inside the container with correct container paths.

## Common Development Tasks

### Adding a New Endpoint

1. Create endpoint function in `app/api/v1/endpoints/<domain>.py`
   ```python
   from fastapi import APIRouter

   router = APIRouter()

   @router.get("/example")
   async def example_endpoint():
       return {"message": "Hello"}
   ```

2. Use Depends() to inject dependencies:
   - Database session: `db: Annotated[AsyncSession, Depends(get_db)]`
   - Current user: `current_user: Annotated[User, Depends(get_current_user)]`
   - Active user: `current_user: Annotated[User, Depends(get_current_active_user)]`
   - Superuser: `current_user: Annotated[User, Depends(get_current_superuser)]`

3. Register router in `app/api/v1/api.py`:
   ```python
   from app.api.v1.endpoints import your_module

   api_router.include_router(your_module.router, prefix="/your-prefix", tags=["your-tag"])
   ```

4. The endpoint will automatically appear in API docs at http://localhost:8000/api/v1/docs

**IMPORTANT**: Always use `app.include_router()` for APIRouter instances, never `app.mount()`. The `mount()` method is for mounting sub-applications (WSGI/ASGI apps), not for including routers.

### Adding a New Model

1. Create model class in `app/models/<model>.py` inheriting from `Base`
2. Use `Mapped[]` type annotations with `mapped_column()` for columns
3. Import model in `app/models/__init__.py`
4. Create corresponding Pydantic schemas in `app/schemas/<model>.py`
5. Generate Alembic migration (when migrations are set up)

### Creating CRUD Operations

1. Create schema classes in `app/schemas/`: `<Model>Create`, `<Model>Update`, `<Model>`
2. Create CRUD class in `app/crud/<model>.py` inheriting from `CRUDBase[Model, ModelCreate, ModelUpdate]`
3. Add model-specific methods as needed
4. Instantiate CRUD object and import in `app/crud/__init__.py`

## Database Migrations

Alembic is configured for database migrations with **automatic migration execution on startup**.

### Automatic Migrations

**Migrations run automatically when the backend starts.** The `app/main.py` lifespan context manager executes `alembic upgrade head` on every startup, ensuring your database schema is always up to date.

- ✅ **Development**: Migrations apply automatically when you start/restart the backend
- ✅ **Production**: Migrations apply before the application accepts traffic
- ✅ **Error handling**: Application continues to start even if migration fails (with warnings)
- ✅ **No manual steps**: Just create migrations and restart - they apply automatically

### Creating Migrations

**IMPORTANT**: Always run Alembic commands inside the Docker container.

```bash
# Create a new migration (autogenerate from model changes)
docker compose exec backend alembic revision --autogenerate -m "description of changes"

# Create an empty migration (for manual SQL)
docker compose exec backend alembic revision -m "description"
```

### Applying Migrations

```bash
# Apply all pending migrations
docker compose exec backend alembic upgrade head

# Apply one migration at a time
docker compose exec backend alembic upgrade +1

# Rollback one migration
docker compose exec backend alembic downgrade -1
```

### Important Notes

- **Automatic on startup**: Migrations run automatically when backend starts - no manual intervention needed
- **Always run inside container**: Alembic commands need access to the `postgres` hostname which only exists in Docker network
- **Async to Sync conversion**: The `alembic/env.py` automatically converts `postgresql+asyncpg://` to `postgresql://` because Alembic requires synchronous drivers
- **Dependencies**: Both `asyncpg` (for FastAPI) and `psycopg2-binary` (for Alembic) are installed
- **Migration files**: Located in `backend/alembic/versions/`
- **Production**: Migrations run automatically via the lifespan context manager before application starts accepting requests

## Security

This application implements multiple layers of security for authentication, data protection, and abuse prevention.

### Password Security

**Password Validation**: All passwords must meet the following requirements (enforced in `app/core/password_validator.py`):
- Minimum 8 characters in length
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)

The `validate_password_or_raise()` function is called in:
- User creation (`crud.user.create()`)
- User updates when password is changed (`crud.user.update()`)
- Signup endpoint (`POST /api/v1/users/signup`)

Invalid passwords return a 400 error with specific validation messages.

**Password Hashing**: Passwords are hashed using bcrypt via passlib with the following settings:
- Algorithm: bcrypt
- Automatic salt generation
- One-way hashing (passwords cannot be decrypted)

Never store or log plaintext passwords.

### Authentication & JWT Tokens

**JWT Token Structure**: Access tokens include the following claims:
- `exp`: Expiration timestamp (default: 30 minutes from issuance)
- `iat`: Issued at timestamp (when token was created)
- `sub`: Subject (user ID)
- `jti`: JWT ID (unique identifier for token tracking/revocation)

The `iat` and `jti` claims enable future features like token revocation and refresh token rotation.

**Token Configuration**:
- Algorithm: HS256
- Secret key: Configured via `SECRET_KEY` environment variable (use `openssl rand -hex 32`)
- Expiration: Configured via `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 30)

**Authentication Flow**:
1. User submits credentials via `POST /api/v1/auth/login`
2. Password verified against bcrypt hash
3. JWT token generated and returned
4. Client includes token in `Authorization: Bearer <token>` header
5. Protected endpoints verify token via `get_current_user()` dependency

### Rate Limiting

Rate limiting is implemented using slowapi to prevent brute force attacks and abuse.

**Configuration** (`app/core/rate_limit.py`):
- Library: slowapi
- Key function: Remote IP address (`get_remote_address`)
- Disabled during testing: `enabled=not settings.TESTING`

**Current Limits**:
- Login endpoint: 5 requests per minute per IP (`POST /api/v1/auth/login`)
- Signup endpoint: 3 requests per hour per IP (`POST /api/v1/users/signup`)

**Testing Note**: Rate limiting is automatically disabled when `TESTING=True` in environment variables to prevent test failures.

To modify rate limits, update the `@limiter.limit()` decorators in endpoint files:
```python
@router.post("/login")
@limiter.limit("5/minute")  # Adjust as needed
async def login(request: Request, ...):
    ...
```

### Logging

Comprehensive logging is implemented for security-relevant events:

**Logged Events** (in `app/api/v1/endpoints/auth.py` and `app/api/v1/endpoints/users.py`):
- Login attempts (username/email)
- Successful logins (user ID)
- Failed login attempts
- User creation (email, user ID)
- Profile updates (user ID)
- Password changes (user ID)

All logs use Python's standard `logging` module. Configure log level via environment or update logging config in `app/main.py`.

**Security Best Practices for Logging**:
- Never log passwords (plaintext or hashed)
- Log user IDs, not sensitive PII when possible
- Include timestamps (automatic with logging module)
- Monitor failed login attempts for suspicious patterns

### Error Handling

**Backend**: API errors return appropriate HTTP status codes with error details in the response body:
- 400: Bad Request (validation errors, weak passwords)
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (user/resource doesn't exist)
- 409: Conflict (duplicate email/username)
- 500: Internal Server Error (unhandled exceptions)

**Frontend**: Centralized error handling via `src/utils/errorHandler.ts`:
```typescript
import { getErrorMessage } from '../utils/errorHandler';

try {
  await apiCall();
} catch (err: any) {
  setError(getErrorMessage(err, 'Operation failed'));
}
```

This utility extracts error messages from FastAPI responses (handles both string and array detail formats) and provides user-friendly fallback messages.

### Database Security

**SQL Injection Prevention**: SQLAlchemy ORM and parameterized queries prevent SQL injection. Never concatenate user input into raw SQL queries.

**Timezone-Aware Timestamps**: All datetime columns use `DateTime(timezone=True)` with UTC timestamps to prevent timezone-related security issues and ensure consistent time comparisons.

**Connection Security**: Database connections use environment variables (`DATABASE_URL`) and should use SSL in production.

### Frontend Security Considerations

**XSS Protection**: React escapes values by default. Never use `dangerouslySetInnerHTML` unless absolutely necessary and input is sanitized.

**Token Storage**: Currently tokens are stored in localStorage (see `src/context/AuthContext.tsx`). Be aware:
- localStorage is vulnerable to XSS attacks
- Consider httpOnly cookies for production
- Implement token refresh for long-lived sessions

**CORS Configuration**: CORS origins are configured in `app/main.py`. In production, restrict to specific domains (never use `allow_origins=["*"]` in production).

### Testing Security Features

When writing tests for security features:
- Set `TESTING=True` to disable rate limiting
- Use strong passwords in test fixtures (min 8 chars, uppercase, lowercase, number)
- Test both successful and failed authentication flows
- Verify error messages don't leak sensitive information

Example test password: `TestPassword123`

## VSCode Integration

After running `uv sync`, configure VSCode to use the Python interpreter at `backend/.venv/bin/python`. This enables autocomplete and type checking even though the application runs in Docker.

## Recent Changes & Important Notes

**ALWAYS check docs/CHANGELOG.md for the complete change history.**

### Current State (2026-01-01)
- **Backend is fully functional** - API running at http://localhost:8000
- **Alembic configured and working** - Initial migration created for users table
- Frontend directory exists but is currently empty
- Test infrastructure exists but no tests written yet
- Redis configured but caching not implemented yet
- User model exists with JWT authentication
- Required dependencies: email-validator, python-multipart, psycopg2-binary added today

### Standards & Decisions
- **Docker Compose V2**: Always use `docker compose` (space), never `docker-compose` (hyphen)
- **Documentation**: All changes MUST be recorded in docs/CHANGELOG.md
- **Split .env configuration**: Infrastructure vars in root `.env`, application vars in `backend/.env`
- **Automatic migrations**: Database migrations run automatically on backend startup
- **Python tooling**: Using uv for dependency management (not pip/poetry)
- **Async all the way**: SQLAlchemy async, FastAPI async endpoints
- **Generic CRUD**: Use CRUDBase inheritance pattern for database operations
- **Alembic commands**: Always run inside Docker container to access postgres hostname
