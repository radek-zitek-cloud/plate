.PHONY: help dev down test test-backend test-frontend test-watch test-frontend-watch test-frontend-ui test-frontend-coverage lint lint-backend lint-frontend format format-backend format-frontend logs shell-backend shell-db clean rebuild

help:
	@echo "Available commands:"
	@echo "  make dev                    - Start development environment (backend + frontend)"
	@echo "  make down                   - Stop all services"
	@echo "  make rebuild                - Rebuild all images without cache and restart"
	@echo "  make test                   - Run all tests (backend + frontend)"
	@echo "  make test-backend           - Run backend tests in test environment"
	@echo "  make test-frontend          - Run frontend tests"
	@echo "  make test-watch             - Run backend tests with file watching"
	@echo "  make test-frontend-watch    - Run frontend tests in watch mode"
	@echo "  make test-frontend-ui       - Run frontend tests with interactive UI"
	@echo "  make test-frontend-coverage - Run frontend tests with coverage report"
	@echo "  make lint                   - Run all linters (backend + frontend)"
	@echo "  make lint-backend           - Run ruff linter on backend code"
	@echo "  make lint-frontend          - Run eslint on frontend code"
	@echo "  make format                 - Format all code (backend + frontend)"
	@echo "  make format-backend         - Format backend code with ruff"
	@echo "  make format-frontend        - Format frontend code with eslint"
	@echo "  make logs                   - View development logs"
	@echo "  make shell-backend          - Open shell in dev backend container"
	@echo "  make shell-db               - Open PostgreSQL shell (dev)"
	@echo "  make clean                  - Remove all containers and volumes"

dev:
	docker compose up -d
	@echo ""
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/api/v1/docs"

down:
	docker compose down
	docker compose --profile test down

test:
	@echo "Running all tests..."
	@echo ""
	@echo "=== Backend Tests ==="
	@$(MAKE) test-backend
	@echo ""
	@echo "=== Frontend Tests ==="
	@$(MAKE) test-frontend
	@echo ""
	@echo "All tests complete!"

test-backend:
	@echo "Running backend tests in isolated test environment..."
	docker compose --profile test up backend_test postgres_test redis_test --abort-on-container-exit --exit-code-from backend_test
	docker compose --profile test down

test-frontend:
	@echo "Running frontend tests in isolated test environment..."
	docker compose --profile test run --rm frontend_test

test-frontend-watch:
	@echo "Running frontend tests in watch mode..."
	@echo "Note: Requires 'make dev' to be running"
	docker compose exec frontend npm run test:watch

test-frontend-ui:
	@echo "Starting interactive frontend test UI..."
	@echo "Note: Requires 'make dev' to be running"
	@echo "Open http://localhost:51204 in your browser"
	docker compose exec frontend npm run test:ui

test-frontend-coverage:
	@echo "Running frontend tests with coverage..."
	@echo "Note: Requires 'make dev' to be running"
	docker compose exec frontend npm run test:coverage

test-watch:
	@echo "Running backend tests in watch mode..."
	@echo "Note: Requires 'make dev' to be running"
	@echo "Tests will re-run every 3 seconds. Press Ctrl+C to stop."
	@docker compose exec backend bash -c "while true; do clear; echo '=== Running Backend Tests ==='; echo ''; uv run pytest -v; echo ''; echo 'Waiting 3 seconds before next run... (Press Ctrl+C to stop)'; sleep 3; done"

lint:
	@echo "Running all linters..."
	@echo ""
	@echo "=== Backend Linting (ruff) ==="
	@$(MAKE) lint-backend
	@echo ""
	@echo "=== Frontend Linting (eslint) ==="
	@$(MAKE) lint-frontend
	@echo ""
	@echo "All linting complete!"

lint-backend:
	@echo "Running ruff linter on backend..."
	docker compose exec backend uv run ruff check app tests

lint-frontend:
	@echo "Running eslint on frontend..."
	@echo "Note: Requires 'make dev' to be running"
	docker compose exec frontend npm run lint

format:
	@echo "Formatting all code..."
	@echo ""
	@echo "=== Backend Formatting (ruff) ==="
	@$(MAKE) format-backend
	@echo ""
	@echo "=== Frontend Formatting (eslint --fix) ==="
	@$(MAKE) format-frontend
	@echo ""
	@echo "All formatting complete!"

format-backend:
	@echo "Formatting backend code with ruff..."
	docker compose exec backend uv run ruff check --fix app tests
	docker compose exec backend uv run ruff format app tests

format-frontend:
	@echo "Formatting frontend code with eslint --fix..."
	@echo "Note: Requires 'make dev' to be running"
	docker compose exec frontend npm run lint -- --fix

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
	@echo "Frontend: http://localhost:5173"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/api/v1/docs"