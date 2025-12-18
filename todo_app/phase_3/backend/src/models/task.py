from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from typing import Optional
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    """Task entity for todo items."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)
    title: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)

    # New Fields for US9
    due_date: Optional[datetime] = Field(default=None)
    priority: str = Field(default="medium", max_length=20)

    # Notification settings
    notify_email: Optional[str] = Field(default=None, max_length=255)
    notifications_enabled: bool = Field(default=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
