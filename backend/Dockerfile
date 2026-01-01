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

# Expose port
EXPOSE 8000

# Health check using Python from the virtual environment
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Production command
# Because .venv/bin is in PATH, this finds uvicorn from the virtual environment
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]