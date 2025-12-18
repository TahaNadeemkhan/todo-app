"""
Database connection and session management using SQLModel and AsyncSession.
"""

from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config.settings import get_settings

settings = get_settings()

# We need an async engine for the repositories
# Ensure DATABASE_URL is an async one (e.g. postgresql+asyncpg://)
# If it's standard postgresql://, we might need to swap it.
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,
)

# For sync operations (Alembic or non-async tools if any)
sync_engine = create_engine(
    settings.database_url, # Original URL
    echo=False,
    pool_pre_ping=True,
)

async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_async_session() -> AsyncSession:
    """Provide an async database session."""
    async with async_session_maker() as session:
        yield session
