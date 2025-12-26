from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime
from typing import Optional


class Notification(SQLModel, table=True):
    """Notification entity for email send tracking."""

    __tablename__ = "notifications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    task_id: Optional[int] = Field(default=None, index=True)
    type: str = Field(nullable=False, max_length=50)  # task_created, task_updated, task_deleted, task_completed
    title: str = Field(nullable=False, max_length=255)
    message: str = Field(nullable=False, max_length=1000)
    email_sent_to: str = Field(nullable=False, max_length=255)
    is_read: bool = Field(default=False)
    sent_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
