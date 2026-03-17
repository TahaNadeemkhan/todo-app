"""Notification model for Phase 5."""

from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime
from typing import Optional
from .enums import NotificationChannel, NotificationStatus


class Notification(SQLModel, table=True):
    """Notification delivery record - Phase 5 Extended."""

    __tablename__ = "notifications"

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(nullable=False, max_length=36, index=True)
    task_id: Optional[str] = Field(default=None, max_length=36, index=True)

    # Phase 5: Notification details
    channel: str = Field(nullable=False, max_length=10, index=True)  # email, push
    status: str = Field(default=NotificationStatus.PENDING.value, max_length=10, index=True)
    message: str = Field(nullable=False)

    # Delivery tracking
    sent_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    error: Optional[str] = Field(default=None, max_length=500)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
    )
