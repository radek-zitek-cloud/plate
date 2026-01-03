from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Create async engine
# Use async_database_url property which converts postgres:// to postgresql+asyncpg://
# This is necessary for Railway and other platforms that provide standard postgres URLs
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.SQL_ECHO,
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Base class for models
class Base(DeclarativeBase):
    pass
