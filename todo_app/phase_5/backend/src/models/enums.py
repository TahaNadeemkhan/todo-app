"""Enums for Phase 5 domain models."""

from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecurrencePattern(str, Enum):
    """Task recurrence patterns."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    PUSH = "push"


class NotificationStatus(str, Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
