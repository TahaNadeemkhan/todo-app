"""TaskRecurrence model for Phase 5."""

from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from .enums import RecurrencePattern


class TaskRecurrence(SQLModel, table=True):
    """Task recurrence configuration."""

    __tablename__ = "task_recurrences"

    id: str = Field(primary_key=True, max_length=36)  # UUID
    task_id: str = Field(foreign_key="tasks.id", nullable=False, max_length=36, index=True)

    # Recurrence pattern configuration
    pattern: str = Field(nullable=False, max_length=20)  # daily, weekly, monthly
    interval: int = Field(default=1, nullable=False)  # Every N days/weeks/months

    # Pattern-specific fields
    days_of_week: Optional[List[int]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True)
    )  # [0-6] for weekly (0=Monday, 6=Sunday)
    day_of_month: Optional[int] = Field(default=None)  # 1-31 for monthly

    # State tracking
    next_due_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True)
    )
    active: bool = Field(default=True, nullable=False, index=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
