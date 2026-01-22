"""
Database connection and session management using SQLModel and AsyncSession.
"""

from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config.settings import get_settings

# Import all models to ensure they are registered with SQLModel.metadata
from models.task import Task
from models.conversation import Conversation
from models.message import Message

settings = get_settings()

# We need an async engine for the repositories
# Ensure DATABASE_URL is an async one (e.g. postgresql+asyncpg://)
# If it's standard postgresql://, we might need to swap it.
db_url = settings.database_url
connect_args = {}

if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

# Fix for asyncpg: it doesn't support 'sslmode' in the query string
# We need to remove it and pass ssl configuration via connect_args
if "sslmode" in db_url:
    # Remove sslmode param (handle both ?sslmode=... and &sslmode=...)
    import re
    db_url = re.sub(r"[?&]sslmode=[^&]+", "", db_url)
    
    # If the URL ends with ? or &, clean it up (optional but good practice)
    if db_url.endswith("?") or db_url.endswith("&"):
        db_url = db_url[:-1]
        
    # Pass ssl="require" to asyncpg
    connect_args["ssl"] = "require"

async_engine = create_async_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,
    connect_args=connect_args,
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
