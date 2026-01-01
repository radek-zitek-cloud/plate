.PHONY: help dev down test test-watch logs shell-backend shell-db clean rebuild

help:
	@echo "Available commands:"
	@echo "  make dev          - Start development environment"
	@echo "  make down         - Stop all services"
	@echo "  make rebuild      - Rebuild all images without cache and restart"
	@echo "  make test         - Run tests in test environment"
	@echo "  make test-watch   - Run tests with file watching"
	@echo "  make logs         - View development logs"
	@echo "  make shell-backend - Open shell in dev backend container"
	@echo "  make shell-db     - Open PostgreSQL shell (dev)"
	@echo "  make clean        - Remove all containers and volumes"

dev:
	docker compose up -d
	@echo ""
	@echo "Development environment started!"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/api/v1/docs"

down:
	docker compose down
	docker compose --profile test down

test:
	@echo "Running tests in isolated test environment..."
	docker compose --profile test up --abort-on-container-exit --exit-code-from backend_test
	docker compose --profile test down

test-watch:
	@echo "Running tests with file watching..."
	docker compose --profile test run --rm backend_test uv run pytest-watch

logs:
	docker compose logs -f

shell-backend:
	docker compose exec backend bash

shell-db:
	docker compose exec postgres psql -U backend_user -d backend_db

clean:
	docker compose down -v
	docker compose --profile test down -v
	docker system prune -f

rebuild:
	@echo "Rebuilding all services without cache..."
	docker compose down
	docker compose build --no-cache
	docker compose up -d
	@echo ""
	@echo "Rebuild complete!"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/api/v1/docs"