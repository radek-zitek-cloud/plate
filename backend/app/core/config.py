from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path


def _read_version() -> str:
    """Read version from VERSION file at project root."""
    version_file = Path(__file__).resolve().parent.parent.parent / "VERSION"
    try:
        return version_file.read_text().strip()
    except Exception:
        # Fallback version if VERSION file doesn't exist
        return "0.0.0"


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Backend API"
    VERSION: str = _read_version()
    API_V1_PREFIX: str = "/api/v1"
    TESTING: bool = False  # Set to True to disable rate limiting during tests

    # Database
    DATABASE_URL: str
    SQL_ECHO: bool = False  # Set to True for SQL query debugging

    @property
    def async_database_url(self) -> str:
        """
        Convert DATABASE_URL to use asyncpg driver for async SQLAlchemy.

        Railway and other platforms provide postgres:// or postgresql:// URLs,
        but we need postgresql+asyncpg:// for async SQLAlchemy to work.
        """
        url = self.DATABASE_URL

        # Replace postgres:// with postgresql+asyncpg://
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)

        # Replace postgresql:// with postgresql+asyncpg://
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Already has a driver specified (e.g., postgresql+asyncpg://)
        return url

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
