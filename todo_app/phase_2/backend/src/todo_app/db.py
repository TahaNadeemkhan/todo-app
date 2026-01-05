"""
Database connection and session management using SQLModel.
"""

from collections.abc import Generator
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import QueuePool

from todo_app.config import get_settings

settings = get_settings()

# Create engine with robust connection pooling for Neon serverless
engine = create_engine(
    settings.database_url,
    echo=False,  # Set True for SQL debugging
    pool_pre_ping=True,  # Verify connections before use (handles stale connections)
    poolclass=QueuePool,
    pool_size=5,  # Number of persistent connections
    max_overflow=10,  # Extra connections when pool is full
    pool_timeout=30,  # Seconds to wait for connection
    pool_recycle=300,  # Recycle connections after 5 minutes (Neon timeout)
    connect_args={
        "connect_timeout": 30,  # Connection timeout in seconds
        "keepalives": 1,  # Enable TCP keepalive
        "keepalives_idle": 30,  # Seconds before sending keepalive
        "keepalives_interval": 10,  # Seconds between keepalives
        "keepalives_count": 5,  # Number of keepalives before giving up
    },
)


def create_db_and_tables() -> None:
    """Create all tables defined by SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for dependency injection."""
    with Session(engine) as session:
        yield session
