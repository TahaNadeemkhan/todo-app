"""TaskReminder model for Phase 5."""

from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from .enums import NotificationChannel


class TaskReminder(SQLModel, table=True):
    """Task reminder configuration."""

    __tablename__ = "task_reminders"

    id: int = Field(default=None, primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", nullable=False, max_length=36, index=True)
    user_id: str = Field(nullable=False, max_length=36, index=True)

    # Reminder configuration
    remind_before: str = Field(nullable=False, max_length=20)  # ISO 8601 duration (PT1H, P1D, P1W)
    channels: List[str] = Field(
        default=[],
        sa_column=Column(JSONB, nullable=False)
    )  # ["email", "push"]

    # Delivery tracking
    sent_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True)
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
