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

Production Docker images are tagged with the version:
- Backend: `registry/backend:0.1.0` and `registry/backend:latest`
- Frontend: `registry/frontend:0.1.0` and `registry/frontend:latest`

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
# Create a git tag (local only)
make release

# Create and push git tag to remote
make release-push
```

### Using Scripts Directly

```bash
# Create git tag locally
./scripts/release.sh

# Create and push git tag
./scripts/release.sh --push
```

The release script:
- Creates an annotated git tag (e.g., `v0.1.0`)
- Optionally pushes the tag to the remote repository
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
```

### Using Docker Compose

```bash
# Build production images
VERSION=0.1.0 docker compose -f docker-compose.prod.yaml build

# Run production stack
VERSION=0.1.0 docker compose -f docker-compose.prod.yaml up -d
```

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

# 4. Create and push release tag
make release-push

# 5. Build and push Docker images (optional)
./scripts/build-images.sh --push --registry your-registry.com

# 6. Push commits to remote
git push origin main
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
