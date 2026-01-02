from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Backend API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    TESTING: bool = False  # Set to True to disable rate limiting during tests

    # Database
    DATABASE_URL: str
    SQL_ECHO: bool = False  # Set to True for SQL query debugging

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()