# Boilerplate Project

Full-stack application boilerplate with FastAPI backend and React TypeScript frontend.

## Features

### Backend (FastAPI)
- ✅ **FastAPI** with Python 3.12+
- ✅ **PostgreSQL** database with async SQLAlchemy
- ✅ **Redis** for caching
- ✅ **JWT Authentication** with secure token handling
- ✅ **Alembic** database migrations
- ✅ **Pytest** with 85 passing tests
- ✅ **Docker** development and production setup
- ✅ **API Documentation** with Swagger UI

### Frontend (React + TypeScript)
- ✅ **React 18** with TypeScript
- ✅ **Vite** for fast development and builds
- ✅ **React Router** for navigation
- ✅ **Axios** for API integration
- ✅ **JWT Token Management** with localStorage
- ✅ **Protected Routes** for authenticated users
- ✅ **Modern UI** with gradient styling
- ✅ **Hot Module Replacement** for fast development

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Make (optional, for convenient commands)

### Development

Start the entire development stack (frontend + backend + databases):

```bash
make dev
```

This will start:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Run Tests

```bash
make test
```

Runs the complete backend test suite (85 tests) in an isolated environment.

### Stop Services

```bash
make down
```

### Clean Everything

```bash
make clean
```

Removes all containers, volumes, and dangling images.

## Project Structure

```
.
├── backend/           # FastAPI backend
│   ├── app/           # Application code
│   │   ├── api/       # API routes and endpoints
│   │   ├── core/      # Core functionality (config, database, security)
│   │   ├── crud/      # Database operations
│   │   ├── models/    # SQLAlchemy models
│   │   └── schemas/   # Pydantic schemas
│   ├── alembic/       # Database migrations
│   └── tests/         # Test suite
├── frontend/          # React TypeScript frontend
│   ├── src/           # Source code
│   │   ├── api/       # API client
│   │   ├── components/# React components
│   │   ├── context/   # React Context
│   │   └── pages/     # Page components
│   └── public/        # Static assets
├── docs/              # Documentation
├── docker-compose.yaml # Docker orchestration
└── Makefile           # Convenient commands
```

## Available Make Commands

```bash
make help          # Show all available commands
make dev           # Start development environment
make down          # Stop all services
make test          # Run backend tests
make test-watch    # Run tests with file watching
make logs          # View development logs
make shell-backend # Open shell in backend container
make shell-db      # Open PostgreSQL shell
make clean         # Remove all containers and volumes
make rebuild       # Rebuild all images without cache
```

## Environment Variables

### Backend
Create `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://backend_user:backend_password@postgres:5432/backend_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-change-this
```

### Infrastructure
Create `.env` in root:
```env
POSTGRES_USER=backend_user
POSTGRES_PASSWORD=backend_password
POSTGRES_DB=backend_db
```

### Frontend
Configured in `frontend/.env.development` and `frontend/.env.production`:
```env
VITE_API_URL=http://localhost:8000
```

## Authentication Flow

1. **Signup**: User creates account at `/signup`
2. **Login**: User logs in at `/login` with username/email and password
3. **Token Storage**: JWT token stored in localStorage
4. **Protected Access**: Token automatically sent with API requests
5. **Dashboard**: Authenticated users can access `/dashboard`
6. **Logout**: Token removed from localStorage

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/test-token` - Validate token

### Users
- `POST /api/v1/users/signup` - User registration
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID (authenticated)
- `GET /api/v1/users/` - List users (superuser only)
- `DELETE /api/v1/users/{user_id}` - Delete user (superuser only)

## Development Workflow

### Backend Development
1. Code is in `backend/app/`
2. Hot reload is enabled - changes apply immediately
3. Access API docs at http://localhost:8000/api/v1/docs
4. Run tests with `make test`

### Frontend Development
1. Code is in `frontend/src/`
2. Hot Module Replacement enabled - instant updates
3. Access app at http://localhost:5173
4. API calls automatically proxied to backend

### Database Migrations
```bash
# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec backend alembic upgrade head

# Rollback migration
docker compose exec backend alembic downgrade -1
```

## Testing

### Backend Tests
- **85 tests** covering all functionality
- Tests use isolated test database (port 5433)
- Automatic cleanup after each test
- Coverage includes:
  - Authentication endpoints
  - User CRUD operations
  - Security functions
  - Dependencies
  - Database operations

Run tests:
```bash
make test           # Run all tests
make test-watch     # Run tests with file watching
```

## Production Deployment

### Build Production Images
```bash
docker compose -f docker-compose.prod.yml build
```

### Frontend Production
- Built with Vite
- Served by Nginx
- Gzip compression enabled
- Security headers configured
- SPA routing configured

### Backend Production
- Uses `Dockerfile` (not `Dockerfile.dev`)
- Optimized Python image
- Production-ready configuration

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Pydantic** - Data validation
- **PostgreSQL** - Relational database
- **Redis** - In-memory data store
- **JWT** - JSON Web Tokens for auth
- **Pytest** - Testing framework

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **CSS3** - Modern styling

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Make** - Task automation
- **Nginx** - Web server (production)

## Documentation

All project documentation is located in the [`docs/`](./docs) directory:

- **[docs/README.md](./docs/README.md)** - Documentation index and navigation guide
- **[docs/CLAUDE.md](./docs/CLAUDE.md)** - Comprehensive development guide and architecture
- **[docs/CHANGELOG.md](./docs/CHANGELOG.md)** - Complete project history and changes
- **[docs/FRONTEND_TESTING.md](./docs/FRONTEND_TESTING.md)** - Frontend testing guide
- **[docs/BACKEND_TESTING.md](./docs/BACKEND_TESTING.md)** - Backend testing guide
- **[docs/Environment-Architecture.md](./docs/Environment-Architecture.md)** - Infrastructure and deployment

See [docs/README.md](./docs/README.md) for the complete documentation index.

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.
