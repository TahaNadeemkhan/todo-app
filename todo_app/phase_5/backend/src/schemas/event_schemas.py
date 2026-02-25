"""
T029-T036: Kafka Event Schema Definitions
All events follow CloudEvents-inspired envelope format with Pydantic validation

Event Types:
- task.created.v1 (T030)
- task.updated.v1 (T031)
- task.completed.v1 (T032)
- task.deleted.v1 (T033)
- reminder.due.v1 (T034)
- notification.sent.v1 (T035)
- notification.failed.v1 (T036)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ============================================================================
# Enums for Validation
# ============================================================================

class PriorityEnum(str, Enum):
    """Priority levels for tasks."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrencePatternEnum(str, Enum):
    """Recurrence patterns for recurring tasks."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class NotificationChannelEnum(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    PUSH = "push"


# ============================================================================
# Base Event Envelope
# ============================================================================

class BaseEventData(BaseModel):
    """Base class for all event data payloads."""
    pass


class BaseEvent(BaseModel):
    """
    Base event envelope following CloudEvents-inspired format.
    All events must have: event_id, event_type, schema_version, timestamp, data
    """
    event_id: str = Field(..., description="Unique event identifier (UUID) for idempotency")
    event_type: str = Field(..., description="Event type with version (e.g., task.created.v1)")
    schema_version: str = Field(default="1.0", description="Schema version")
    timestamp: str = Field(..., description="Event creation time (ISO 8601 UTC)")
    data: BaseEventData = Field(..., description="Event-specific payload")

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_type": "task.created.v1",
                "schema_version": "1.0",
                "timestamp": "2026-01-04T12:00:00Z",
                "data": {}
            }
        }
    }


# ============================================================================
# T030: task.created.v1 - Task Creation Event
# ============================================================================

class TaskCreatedData(BaseEventData):
    """Data payload for task.created.v1 event."""
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="User UUID who created the task")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    priority: PriorityEnum = Field(..., description="Task priority (high/medium/low)")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    due_at: Optional[str] = Field(None, description="Task due date/time (ISO 8601)")

    # Recurrence fields (optional)
    has_recurrence: Optional[bool] = Field(False, description="Whether task has recurrence")
    recurrence_pattern: Optional[RecurrencePatternEnum] = Field(None, description="Recurrence pattern")
    recurrence_interval: Optional[int] = Field(None, ge=1, description="Recurrence interval")
    recurrence_days_of_week: Optional[List[int]] = Field(None, description="Days of week (0=Monday, 6=Sunday)")
    recurrence_day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month")

    created_at: str = Field(..., description="Task creation timestamp (ISO 8601)")

    @field_validator('recurrence_days_of_week')
    @classmethod
    def validate_days_of_week(cls, v):
        """Validate days of week are 0-6."""
        if v is not None:
            for day in v:
                if not (0 <= day <= 6):
                    raise ValueError('Days of week must be 0-6')
        return v


class TaskCreatedEvent(BaseEvent):
    """
    T030: Event published when a new task is created.

    Topic: task-events
    Partition Key: user_id
    Produced By: Backend API, Recurring Task Service
    Consumed By: Analytics Service (future)
    """
    event_type: str = Field(default="task.created.v1", const=True)
    data: TaskCreatedData

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440000",
                "event_type": "task.created.v1",
                "schema_version": "1.0",
                "timestamp": "2026-01-04T12:00:00Z",
                "data": {
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "789e4567-e89b-12d3-a456-426614174000",
                    "title": "Buy groceries",
                    "description": "Milk, bread, eggs",
                    "priority": "high",
                    "tags": ["shopping", "urgent"],
                    "due_at": "2026-01-05T18:00:00Z",
                    "has_recurrence": True,
                    "recurrence_pattern": "weekly",
                    "recurrence_interval": 1,
                    "recurrence_days_of_week": [0, 3, 5],
                    "created_at": "2026-01-04T12:00:00Z"
                }
            }
        }
    }


# ============================================================================
# T031: task.updated.v1 - Task Update Event
# ============================================================================

class TaskUpdatedData(BaseEventData):
    """Data payload for task.updated.v1 event."""
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="User UUID who updated the task")
    changes: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Map of field_name -> {old: value, new: value}"
    )
    updated_at: str = Field(..., description="Update timestamp (ISO 8601)")


class TaskUpdatedEvent(BaseEvent):
    """
    T031: Event published when a task is updated.

    Topic: task-events
    Partition Key: user_id
    Produced By: Backend API
    Consumed By: Analytics Service (future)
    """
    event_type: str = Field(default="task.updated.v1", const=True)
    data: TaskUpdatedData

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440002",
                "event_type": "task.updated.v1",
                "schema_version": "1.0",
                "timestamp": "2026-01-04T14:00:00Z",
                "data": {
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "789e4567-e89b-12d3-a456-426614174000",
                    "changes": {
                        "priority": {"old": "medium", "new": "high"},
                        "tags": {"old": ["shopping"], "new": ["shopping", "urgent"]}
                    },
                    "updated_at": "2026-01-04T14:00:00Z"
                }
            }
        }
    }


# ============================================================================
# T032: task.completed.v1 - Task Completion Event
# ============================================================================

class TaskCompletedData(BaseEventData):
    """Data payload for task.completed.v1 event."""
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="User UUID who completed the task")
    completed_at: str = Field(..., description="Completion timestamp (ISO 8601)")

    # Recurrence fields (for Recurring Task Service to create next occurrence)
    has_recurrence: bool = Field(..., description="Whether task has recurrence")
    recurrence_pattern: Optional[RecurrencePatternEnum] = Field(None, description="Recurrence pattern")
    recurrence_interval: Optional[int] = Field(None, ge=1, description="Recurrence interval")
    recurrence_days_of_week: Optional[List[int]] = Field(None, description="Days of week (0=Monday, 6=Sunday)")
    recurrence_day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month")


class TaskCompletedEvent(BaseEvent):
    """
    T032: Event published when a task is marked as completed.

    Topic: task-events
    Partition Key: user_id
    Produced By: Backend API
    Consumed By: Recurring Task Service (if has_recurrence=true)

    Critical: This event triggers the Recurring Task Service to create the next
    occurrence if has_recurrence=true.
    """
    event_type: str = Field(default="task.completed.v1", const=True)
    data: TaskCompletedData

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440001",
                "event_type": "task.completed.v1",
                "schema_version": "1.0",
                "timestamp": "2026-01-04T15:00:00Z",
                "data": {
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "789e4567-e89b-12d3-a456-426614174000",
                    "completed_at": "2026-01-04T15:00:00Z",
                    "has_recurrence": True,
                    "recurrence_pattern": "weekly",
                    "recurrence_interval": 1,
                    "recurrence_days_of_week": [0, 3, 5]
                }
            }
        }
    }


# ============================================================================
# T033: task.deleted.v1 - Task Deletion Event
# ============================================================================

class TaskDeletedData(BaseEventData):
    """Data payload for task.deleted.v1 event."""
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="User UUID who deleted the task")
    deleted_at: str = Field(..., description="Deletion timestamp (ISO 8601)")


class TaskDeletedEvent(BaseEvent):
    """
    T033: Event published when a task is deleted.

    Topic: task-events
    Partition Key: user_id
    Produced By: Backend API
    Consumed By: Analytics Service (future)
    """
    event_type: str = Field(default="task.deleted.v1", const=True)
    data: TaskDeletedData

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440003",
                "event_type": "task.deleted.v1",
                "schema_version": "1.0",
                "timestamp": "2026-01-04T16:00:00Z",
                "data": {
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "789e4567-e89b-12d3-a456-426614174000",
                    "deleted_at": "2026-01-04T16:00:00Z"
                }
            }
        }
    }


# ============================================================================
# T034: reminder.due.v1 - Reminder Due Event
# ============================================================================

class ReminderDueData(BaseEventData):
    """Data payload for reminder.due.v1 event."""
    reminder_id: int = Field(..., description="Reminder database ID")
    task_id: str = Field(..., description="Task UUID")
    user_id: str = Field(..., description="User UUID")
    task_title: str = Field(..., description="Task title (for notification message)")
    due_at: str = Field(..., description="Task due date/time (ISO 8601)")
    remind_before: str = Field(..., description="ISO 8601 duration (PT1H, P1D, P1W)")
    channels: List[NotificationChannelEnum] = Field(..., description="Notification channels")


class ReminderDueEvent(BaseEvent):
    """
    T034: Event published when a reminder is due.

    Topic: reminders
    Partition Key: user_id
    Produced By: Backend API (Reminder Scheduler cron job)
    Consumed By: Notification Service

    Critical: This event triggers the Notification Service to send email/push notifications.
    """
    event_type: str = Field(default="reminder.due.v1", const=True)
    data: ReminderDueData

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440004",
                "event_type": "reminder.due.v1",
                "schema_version": "1.0",
                "timestamp": "2026-01-05T17:00:00Z",
                "data": {
                    "reminder_id": 42,
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "789e4567-e89b-12d3-a456-426614174000",
                    "task_title": "Buy groceries",
                    "due_at": "2026-01-05T18:00:00Z",
                    "remind_before": "PT1H",
                    "channels": ["email", "push"]
                }
            }
        }
    }


# ============================================================================
# T035: notification.sent.v1 - Notification Sent Event
# ============================================================================

class NotificationSentData(BaseEventData):
    """Data payload for notification.sent.v1 event."""
    notification_id: int = Field(..., description="Notification database ID")
    user_id: str = Field(..., description="User UUID")
    task_id: Optional[str] = Field(None, description="Task UUID (if related to a task)")
    channel: NotificationChannelEnum = Field(..., description="Delivery channel")
    message: str = Field(..., description="Notification message content")
    sent_at: str = Field(..., description="Sent timestamp (ISO 8601)")


class NotificationSentEvent(BaseEvent):
    """
    T035: Event published when a notification is successfully sent.

    Topic: notifications
    Partition Key: user_id
    Produced By: Notification Service
    Consumed By: Backend API (future - update status), Analytics Service (future)
    """
    event_type: str = Field(default="notification.sent.v1", const=True)
    data: NotificationSentData

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440005",
                "event_type": "notification.sent.v1",
                "schema_version": "1.0",
                "timestamp": "2026-01-05T17:00:05Z",
                "data": {
                    "notification_id": 101,
                    "user_id": "789e4567-e89b-12d3-a456-426614174000",
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "channel": "email",
                    "message": "Reminder: Buy groceries is due in 1 hour",
                    "sent_at": "2026-01-05T17:00:05Z"
                }
            }
        }
    }


# ============================================================================
# T036: notification.failed.v1 - Notification Failed Event
# ============================================================================

class NotificationFailedData(BaseEventData):
    """Data payload for notification.failed.v1 event."""
    notification_id: int = Field(..., description="Notification database ID")
    user_id: str = Field(..., description="User UUID")
    task_id: Optional[str] = Field(None, description="Task UUID (if related to a task)")
    channel: NotificationChannelEnum = Field(..., description="Delivery channel")
    message: str = Field(..., description="Notification message content")
    error: str = Field(..., description="Error message explaining failure")
    failed_at: str = Field(..., description="Failure timestamp (ISO 8601)")


class NotificationFailedEvent(BaseEvent):
    """
    T036: Event published when a notification fails to send.

    Topic: notifications
    Partition Key: user_id
    Produced By: Notification Service
    Consumed By: Backend API (future - update status, retry), Analytics Service (future)
    """
    event_type: str = Field(default="notification.failed.v1", const=True)
    data: NotificationFailedData

    model_config = {
        "json_schema_extra": {
            "example": {
                "event_id": "550e8400-e29b-41d4-a716-446655440006",
                "event_type": "notification.failed.v1",
                "schema_version": "1.0",
                "timestamp": "2026-01-05T17:00:10Z",
                "data": {
                    "notification_id": 102,
                    "user_id": "789e4567-e89b-12d3-a456-426614174000",
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "channel": "push",
                    "message": "Reminder: Buy groceries is due in 1 hour",
                    "error": "FCM token expired",
                    "failed_at": "2026-01-05T17:00:10Z"
                }
            }
        }
    }


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    # Event classes
    "TaskCreatedEvent",
    "TaskUpdatedEvent",
    "TaskCompletedEvent",
    "TaskDeletedEvent",
    "ReminderDueEvent",
    "NotificationSentEvent",
    "NotificationFailedEvent",

    # Data classes (for type hints)
    "TaskCreatedData",
    "TaskUpdatedData",
    "TaskCompletedData",
    "TaskDeletedData",
    "ReminderDueData",
    "NotificationSentData",
    "NotificationFailedData",

    # Enums
    "PriorityEnum",
    "RecurrencePatternEnum",
    "NotificationChannelEnum",
]
