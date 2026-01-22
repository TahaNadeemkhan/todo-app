"""
Event schemas for notification-service.
Imports from backend event_schemas to maintain consistency.
"""

# Copy minimal event schemas needed for notification service
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional


class NotificationChannelEnum(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    PUSH = "push"


class ReminderDueData(BaseModel):
    """Data payload for reminder.due.v1 event."""
    reminder_id: int = Field(..., description="Reminder database ID")
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="User UUID")
    user_email: str = Field(..., description="User email address")
    task_title: str = Field(..., description="Task title (for notification message)")
    task_description: Optional[str] = Field(None, description="Task description")
    due_at: str = Field(..., description="Task due date/time (ISO 8601)")
    remind_before: str = Field(..., description="ISO 8601 duration (PT1H, P1D, P1W)")
    channels: List[NotificationChannelEnum] = Field(..., description="Notification channels")


class ReminderDueEvent(BaseModel):
    """Event published when a reminder is due."""
    event_id: str
    event_type: str = "reminder.due.v1"
    schema_version: str = "1.0"
    timestamp: str
    data: ReminderDueData


class NotificationSentData(BaseModel):
    """Data payload for notification.sent.v1 event."""
    notification_id: int
    user_id: str
    task_id: Optional[str] = None
    channel: NotificationChannelEnum
    message: str
    sent_at: str


class NotificationFailedData(BaseModel):
    """Data payload for notification.failed.v1 event."""
    notification_id: int
    user_id: str
    task_id: Optional[str] = None
    channel: NotificationChannelEnum
    message: str
    error: str
    failed_at: str


__all__ = [
    "NotificationChannelEnum",
    "ReminderDueData",
    "ReminderDueEvent",
    "NotificationSentData",
    "NotificationFailedData",
]
