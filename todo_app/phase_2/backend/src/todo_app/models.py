"""
SQLModel database models.
"""

from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String, DateTime, Boolean


class Task(SQLModel, table=True):
    """Task entity for todo items."""

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(nullable=False, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    
    # New Fields for US9
    due_date: datetime | None = Field(default=None)
    priority: str = Field(default="medium", max_length=20)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class Jwks(SQLModel, table=True):
    """JWKS table for Better Auth keys."""

    __tablename__ = "jwks"

    id: str = Field(primary_key=True)
    public_key: str = Field(sa_column=Column("publicKey", String, nullable=False))
    private_key: str = Field(sa_column=Column("privateKey", String, nullable=False))
    created_at: datetime = Field(sa_column=Column("createdAt", DateTime, nullable=False))
