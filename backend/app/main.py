import logging
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    This runs when the application starts and cleans up when it shuts down.
    """
    # Startup: Run database migrations
    logger.info(f"Starting {settings.PROJECT_NAME}...")
    logger.info("Running database migrations...")

    try:
        # Get the project root directory (where alembic.ini is located)
        project_root = Path(__file__).resolve().parent.parent

        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )

        logger.info("✓ Database migrations completed successfully")
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                logger.info(f"  {line}")

    except subprocess.CalledProcessError as e:
        logger.error("✗ Database migration failed!")
        logger.error(f"Error: {e.stderr}")
        logger.warning("Application will continue to start, but database may be out of sync.")
        logger.warning("Please run migrations manually: docker compose exec backend alembic upgrade head")
    except Exception as e:
        logger.error(f"✗ Unexpected error during migration: {e}")
        logger.warning("Application will continue to start, but database may be out of sync.")

    yield  # Application runs

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI application instance with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",  # Swagger UI
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",  # ReDoc
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
# IMPORTANT: Use include_router() for APIRouter instances, not mount()
# mount() is for sub-applications (WSGI/ASGI apps), not for routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    This is useful for Docker health checks, Kubernetes liveness probes,
    and monitoring systems. It's a simple endpoint that returns 200 OK
    if the application is running.
    """
    return {"status": "healthy"}