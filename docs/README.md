# Documentation Index

This directory contains all project documentation. All documentation has been consolidated here for easy access and maintenance.

## Quick Links

### For Developers
- **[CLAUDE.md](./CLAUDE.md)** - Comprehensive guide for Claude Code (AI assistant) working with this codebase
  - Project overview and architecture
  - Development workflows and commands
  - Common tasks and patterns
  - Security best practices
  - Testing guidelines

### For Understanding the Project
- **[../README.md](../README.md)** - Main project README (in root)
  - Quick start guide
  - Features overview
  - Basic usage

- **[Environment-Architecture.md](./Environment-Architecture.md)** - Infrastructure and deployment
  - Development, test, and production environments
  - Docker setup and configuration
  - Environment variable management

- **[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)** - Railway.app deployment guide
  - Step-by-step deployment instructions
  - Environment variable configuration
  - Troubleshooting and monitoring
  - Cost optimization tips

### Testing
- **[FRONTEND_TESTING.md](./FRONTEND_TESTING.md)** - Frontend testing guide
  - Vitest and React Testing Library setup
  - Test patterns and best practices
  - Running tests and coverage

- **[BACKEND_TESTING.md](./BACKEND_TESTING.md)** - Backend test suite summary
  - Pytest test organization
  - Test coverage details
  - Security and CRUD testing

### Frontend Development
- **[FRONTEND.md](./FRONTEND.md)** - Frontend architecture and development
  - React + TypeScript setup
  - Project structure
  - Development workflow
  - Authentication implementation

### Change History
- **[CHANGELOG.md](./CHANGELOG.md)** - Complete project history
  - All changes with dates
  - Migration notes
  - Breaking changes
  - Security updates

## Documentation Standards

All significant changes to the codebase **MUST** be documented in [CHANGELOG.md](./CHANGELOG.md). This is not optional.

See [CLAUDE.md - Documentation Requirements](./CLAUDE.md#documentation-requirements) for detailed guidelines on:
- What to document
- Where to document it
- When to update documentation
- How to write changelog entries

## Document Organization

```
docs/
├── README.md                    # This file - documentation index
├── CLAUDE.md                    # AI assistant guide and project overview
├── CHANGELOG.md                 # Complete change history (REQUIRED to update)
├── Environment-Architecture.md  # Infrastructure and deployment guide
├── RAILWAY_DEPLOYMENT.md        # Railway.app deployment guide
├── FRONTEND.md                  # Frontend architecture and development
├── FRONTEND_TESTING.md          # Frontend testing guide
└── BACKEND_TESTING.md           # Backend testing guide
```

## Contributing to Documentation

When adding or modifying documentation:

1. **Update CHANGELOG.md** - Always document your changes
2. **Update this index** - If adding new documentation files
3. **Link between docs** - Add cross-references where helpful
4. **Keep it current** - Update docs when code changes
5. **Be specific** - Include examples and code snippets

## Finding What You Need

| I want to... | Read this... |
|-------------|-------------|
| Understand the project | [../README.md](../README.md), [CLAUDE.md](./CLAUDE.md) |
| Set up development environment | [../README.md](../README.md), [Environment-Architecture.md](./Environment-Architecture.md) |
| Learn the architecture | [CLAUDE.md](./CLAUDE.md) |
| Write tests | [FRONTEND_TESTING.md](./FRONTEND_TESTING.md), [BACKEND_TESTING.md](./BACKEND_TESTING.md) |
| See what changed | [CHANGELOG.md](./CHANGELOG.md) |
| Understand security | [CLAUDE.md - Security section](./CLAUDE.md#security) |
| Deploy to Railway | [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) |
| Understand environments | [Environment-Architecture.md](./Environment-Architecture.md) |
| Work on frontend | [FRONTEND.md](./FRONTEND.md) |

## Questions?

- Check [CLAUDE.md](./CLAUDE.md) for comprehensive information
- Review [CHANGELOG.md](./CHANGELOG.md) for recent changes
- Read [Environment-Architecture.md](./Environment-Architecture.md) for infrastructure questions
