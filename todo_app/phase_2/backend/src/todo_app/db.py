"""
Database connection and session management using SQLModel.
"""

from collections.abc import Generator
from sqlmodel import Session, SQLModel, create_engine

from todo_app.config import get_settings

settings = get_settings()

# Create engine with connection pooling for production
engine = create_engine(
    settings.database_url,
    echo=False,  # Set True for SQL debugging
    pool_pre_ping=True,  # Verify connections before use
)


def create_db_and_tables() -> None:
    """Create all tables defined by SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for dependency injection."""
    with Session(engine) as session:
        yield session
