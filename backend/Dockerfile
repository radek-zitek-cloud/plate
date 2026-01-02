# Stage 1: Build stage with all build dependencies
FROM python:3.12-trixie AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into virtual environment
# The virtual environment is created at /app/.venv
RUN uv sync --frozen --no-dev

# Stage 2: Runtime stage with minimal footprint
FROM python:3.12-slim-trixie

WORKDIR /app

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Copy only the virtual environment from builder stage
# We don't need the build tools or source files from the builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Add virtual environment to PATH
# This makes installed packages available without activation
ENV PATH="/app/.venv/bin:$PATH"

# Expose port (default 8000, Railway will override with PORT env var)
EXPOSE 8000

# Health check using Python from the virtual environment
# Uses httpx which is already in dependencies
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import httpx, os; httpx.get(f'http://localhost:{os.getenv(\"PORT\", \"8000\")}/health', timeout=5.0)"

# Production command
# Because .venv/bin is in PATH, this finds uvicorn from the virtual environment
# Railway sets PORT env var, default to 8000 for local testing
# Workers can be overridden with WORKERS env var (default 4)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-4}