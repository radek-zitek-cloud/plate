# Semantic Versioning Guide

This project uses semantic versioning (SemVer) with a centralized version management system.

## Current Version

The current version is stored in the `VERSION` file at the project root: **0.1.0**

## Version Format

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backwards compatible)
- **PATCH** version: Bug fixes (backwards compatible)

Format: `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)

## How Versioning Works

### Central Version Source

The `VERSION` file at the project root is the single source of truth for the application version.

### Version in Code

**Backend (Python/FastAPI)**:
- The version is read from `VERSION` file at runtime by `backend/app/core/config.py`
- Available via `settings.VERSION`
- Exposed at API endpoint: `GET /api/v1/version`
- Also set in `backend/pyproject.toml` for Python packaging

**Frontend (React/Vite)**:
- The version is injected at build time via `vite.config.ts`
- Available as `__APP_VERSION__` global constant
- Exported from `src/version.ts` for easy import

### Docker Images

The project uses separate Dockerfiles for development and production:

**Production Dockerfiles** (`Dockerfile`):
- Multi-stage builds for optimized image size
- Accept `VERSION` build argument
- Tagged with semantic version and `latest`
- Include OCI image labels with version metadata
- Backend: `registry/backend:0.1.0` and `registry/backend:latest`
- Frontend: `registry/frontend:0.1.0` and `registry/frontend:latest`

**Development Dockerfiles** (`Dockerfile.dev`):
- Single-stage builds for faster rebuilds
- Accept `VERSION` build argument (for consistency)
- Enable hot-reload for local development
- Include version labels for tracking

**docker-compose Files**:
- `docker-compose.yaml` - Uses `Dockerfile.dev` for development/testing
- `docker-compose.prod.yaml` - Uses `Dockerfile` for production builds

## Bumping Versions

### Using Make Commands (Recommended)

```bash
# Show current version
make version

# Bump patch version (0.1.0 -> 0.1.1)
make version-bump-patch

# Bump minor version (0.1.0 -> 0.2.0)
make version-bump-minor

# Bump major version (0.1.0 -> 1.0.0)
make version-bump-major
```

### Using Scripts Directly

```bash
# Bump version
./scripts/version-bump.sh [patch|minor|major]
```

The version bump script automatically updates:
- `VERSION` file
- `backend/pyproject.toml`
- `frontend/package.json`

### After Bumping

1. Review the changes:
   ```bash
   git diff
   ```

2. Commit the version bump:
   ```bash
   git add -A
   git commit -m "chore: bump version to X.Y.Z"
   ```

3. Create a release (see below)

## Creating Releases

### Using Make Commands (Recommended)

```bash
# Option 1: Create and push git tag in one step
make release-push

# Option 2: Create tag locally first, then push separately
make release        # Create tag locally
make release-push   # Push existing tag to remote
```

### Using Scripts Directly

```bash
# Create git tag locally
./scripts/release.sh

# Push existing tag (or create and push if tag doesn't exist)
./scripts/release.sh --push
```

The release script:
- Creates an annotated git tag (e.g., `v0.1.0`)
- Optionally pushes the tag to the remote repository
- If tag exists and --push flag is used, just pushes the existing tag
- Requires no uncommitted changes

## Building Production Images

### Using Make Commands (Recommended)

```bash
# Build production images with version tags
make build-prod
```

### Using Scripts Directly

```bash
# Build images locally
./scripts/build-images.sh

# Build and push to registry
./scripts/build-images.sh --push --registry your-registry.com

# Build with custom API URL for frontend
./scripts/build-images.sh --api-url https://api.yourdomain.com

# Full example with all options
./scripts/build-images.sh --push --registry ghcr.io/yourorg --api-url https://api.yourdomain.com
```

### Using Docker Compose

```bash
# Build production images with version
VERSION=0.1.0 docker compose -f docker-compose.prod.yaml build

# Build with custom frontend API URL
VERSION=0.1.0 VITE_API_URL=https://api.yourdomain.com docker compose -f docker-compose.prod.yaml build

# Run production stack
VERSION=0.1.0 docker compose -f docker-compose.prod.yaml up -d
```

## Docker Configuration Details

### Dockerfile Structure

**Backend Production (`backend/Dockerfile`)**:
- Multi-stage build for minimal image size
- Accepts `VERSION` build arg in both stages
- Adds OCI labels with version metadata
- Uses slim Python image for production
- Includes health check
- Non-root user for security

**Frontend Production (`frontend/Dockerfile`)**:
- Multi-stage build (Node.js builder + nginx)
- Accepts `VERSION` build arg and passes to vite via ENV
- Frontend reads `VERSION` env var during build (vite.config.ts)
- Final image is nginx-alpine with built static assets
- Includes OCI labels with version metadata

**Development Dockerfiles** (`Dockerfile.dev`):
- Single-stage for fast rebuilds
- Accept `VERSION` build arg for consistency
- Include volume mounts for hot-reload
- Backend uses uvicorn with `--reload`
- Frontend runs vite dev server

### Version Injection

**Backend**:
- Runtime: Reads `VERSION` file via `backend/app/core/config.py`
- Build: Receives VERSION as build arg for OCI labels only
- File must be present in Docker context

**Frontend**:
- Build time: VERSION injected via environment variable in Dockerfile
- Vite reads from `process.env.VERSION` or falls back to VERSION file
- Build arg → ENV → vite.config.ts → `__APP_VERSION__` global constant
- **VITE_API_URL**: Also requires build argument for production deployments
  - Defaults to `http://localhost:8000` if not provided
  - Railway/Production: Pass as build argument with backend URL
  - Build arg → ENV → Vite bakes into compiled JavaScript

### docker-compose Configuration

**Development (`docker-compose.yaml`)**:
```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
      args:
        VERSION: ${VERSION:-0.0.0}  # Optional in dev
```

**Production (`docker-compose.prod.yaml`)**:
```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        VERSION: ${VERSION:-0.0.0}
    image: ${DOCKER_REGISTRY:-localhost}/backend:${VERSION:-latest}

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VERSION: ${VERSION:-0.0.0}
        VITE_API_URL: ${VITE_API_URL:-http://localhost:8000}
    image: ${DOCKER_REGISTRY:-localhost}/frontend:${VERSION:-latest}
```

### .dockerignore Files

Both backend and frontend have `.dockerignore` files to exclude:
- `node_modules/` (frontend)
- `.venv/` (backend)
- `.git/`, `.env` files
- Build artifacts, test coverage
- IDE files

This ensures clean Docker builds and prevents host-specific paths from breaking container builds.

## Version Workflow Example

Here's a complete workflow for releasing a new version:

```bash
# 1. Make your changes and commit them
git add .
git commit -m "feat: add new feature"

# 2. Bump the version (choose appropriate level)
make version-bump-minor  # 0.1.0 -> 0.2.0

# 3. Review and commit version changes
git add -A
git commit -m "chore: bump version to 0.2.0"

# 4a. Create and push release tag in one step
make release-push

# OR

# 4b. Create tag locally first (to review), then push
make release          # Creates local tag
git push origin main  # Push commits first (optional)
make release-push     # Push the tag

# 5. Build and push Docker images (optional)
./scripts/build-images.sh --push --registry your-registry.com
```

## Version Information in Running Application

### Backend API

Check the version via the API endpoint:
```bash
curl http://localhost:8000/api/v1/version
```

Response:
```json
{
  "version": "0.1.0",
  "project_name": "Backend API"
}
```

### Frontend Application

Import and use the version in your React components:
```typescript
import { APP_VERSION, getVersion } from './version';

function Footer() {
  return <div>Version: {APP_VERSION}</div>;
}
```

### Docker Images

Check the version label on Docker images:
```bash
docker inspect backend:0.1.0 | grep org.opencontainers.image.version
```

## Files Modified by Version Management

- `VERSION` - Single source of truth
- `backend/pyproject.toml` - Python package version
- `frontend/package.json` - NPM package version

## Automation

The version management system is designed to be automation-friendly:

1. **CI/CD Integration**: Use `make version-bump-*` in your CI pipeline
2. **Git Hooks**: Add pre-commit hooks to validate version consistency
3. **Automated Releases**: Trigger builds when version tags are pushed

## Best Practices

1. **Always bump version before release**: Don't release without updating the version
2. **Follow SemVer**: Be consistent with version number meanings
3. **Tag releases**: Always create git tags for releases
4. **Document changes**: Update CHANGELOG.md when bumping versions
5. **Test before release**: Ensure all tests pass before bumping version

## Troubleshooting

### Version mismatch between files

If `VERSION`, `pyproject.toml`, or `package.json` are out of sync:
```bash
# Re-run the version bump script
make version-bump-patch  # or minor/major
```

### Docker images not tagged correctly

Ensure you're using the build script:
```bash
./scripts/build-images.sh
```

### Version not updating in running application

- **Backend**: Restart the service (version is read at startup)
- **Frontend**: Rebuild the application (version is injected at build time)
