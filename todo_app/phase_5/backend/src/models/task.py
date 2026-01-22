from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from .enums import Priority

class Task(SQLModel, table=True):
    """Task entity for todo items - Phase 5 Extended."""

    __tablename__ = "tasks"

    id: str = Field(primary_key=True, max_length=36)  # UUID
    user_id: str = Field(index=True, nullable=False, max_length=36)
    title: str = Field(nullable=False, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)

    # Phase 5 New Fields
    priority: str = Field(default=Priority.MEDIUM.value, max_length=10)
    tags: List[str] = Field(default=[], sa_column=Column(JSONB, nullable=False, server_default='[]'))
    due_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    recurrence_id: Optional[str] = Field(default=None, max_length=36, foreign_key="task_recurrences.id")

    # Legacy notification fields (kept for backward compatibility)
    notify_email: Optional[str] = Field(default=None, max_length=255)
    notifications_enabled: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=lambda: datetime.now(timezone.utc)),
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
