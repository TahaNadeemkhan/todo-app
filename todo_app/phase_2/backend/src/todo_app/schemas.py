"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = None
    priority: Priority = Priority.MEDIUM
    # Notification settings
    notify_email: str | None = Field(default=None, max_length=255)
    notifications_enabled: bool = False


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = None
    priority: Priority | None = None
    # Notification settings
    notify_email: str | None = Field(default=None, max_length=255)
    notifications_enabled: bool | None = None


class TaskResponse(BaseModel):
    """Schema for task responses."""

    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool
    due_date: datetime | None
    priority: str
    # Notification settings
    notify_email: str | None
    notifications_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str