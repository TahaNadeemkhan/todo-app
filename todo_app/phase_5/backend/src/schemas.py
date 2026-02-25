"""
Pydantic schemas for API request/response validation - Phase 5 with Recurrence and Reminders.
T082: Updated to include recurrence fields.
T102: Updated to include reminder fields.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecurrencePattern(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ReminderCreate(BaseModel):
    """Schema for creating a reminder (nested in TaskCreate or standalone)."""

    remind_before: str = Field(..., description="ISO 8601 duration (PT1H, P1D, P1W)")
    channels: List[str] = Field(..., min_length=1, description="Notification channels (email, push)")

    @field_validator('channels')
    @classmethod
    def validate_channels(cls, v):
        """Validate channels are valid (email, push)."""
        valid_channels = {"email", "push"}
        for channel in v:
            if channel not in valid_channels:
                raise ValueError(f"Invalid channel: {channel}. Valid: {', '.join(valid_channels)}")
        return v


class ReminderResponse(BaseModel):
    """Schema for reminder responses."""

    id: int
    task_id: str
    user_id: str
    remind_before: str
    channels: List[str]
    sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    """Schema for creating a new task with optional recurrence and reminders."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = None
    priority: Priority = Priority.MEDIUM
    tags: List[str] = Field(default_factory=list)

    # Notification settings
    notify_email: str | None = Field(default=None, max_length=255)
    notifications_enabled: bool = False

    # T082: Recurrence fields
    has_recurrence: bool = False
    recurrence_pattern: Optional[RecurrencePattern] = None
    recurrence_interval: Optional[int] = Field(default=1, ge=1)
    recurrence_days_of_week: Optional[List[int]] = None
    recurrence_day_of_month: Optional[int] = Field(default=None, ge=1, le=31)

    # T102: Reminder fields
    reminders: List[ReminderCreate] = Field(default_factory=list)

    @field_validator('recurrence_days_of_week')
    @classmethod
    def validate_days_of_week(cls, v):
        """Validate days of week are 0-6 (Monday-Sunday)."""
        if v is not None:
            for day in v:
                if not (0 <= day <= 6):
                    raise ValueError('Days of week must be 0-6 (0=Monday, 6=Sunday)')
        return v

    @model_validator(mode='after')
    def validate_reminders_require_due_date(self):
        """Validate that reminders require a due_date."""
        if self.reminders and not self.due_date:
            raise ValueError('due_date required when reminders are set')
        return self


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
    """Schema for task responses with recurrence info."""

    id: str
    user_id: str
    title: str
    description: str | None
    completed: bool
    due_date: datetime | None
    priority: str
    tags: List[str] = Field(default_factory=list)

    # Notification settings
    notify_email: str | None
    notifications_enabled: bool

    # T082: Recurrence fields
    has_recurrence: bool = False
    recurrence_pattern: Optional[str] = None
    recurrence_interval: Optional[int] = None

    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RecurrenceResponse(BaseModel):
    """T083: Schema for GET /tasks/{id}/recurrence response."""

    id: str
    task_id: str
    pattern: str
    interval: int
    days_of_week: Optional[List[int]] = None
    day_of_month: Optional[int] = None
    next_due_at: Optional[datetime] = None
    active: bool

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str
