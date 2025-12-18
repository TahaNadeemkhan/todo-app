from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class TaskPriority(str, Enum):
    """Priority levels inspired by Todoist/TaskWarrior."""
    HIGH = "HIGH"      # P1 - Urgent/Important
    MEDIUM = "MEDIUM"  # P2 - Normal
    LOW = "LOW"        # P3 - Can wait


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def short_id(self) -> str:
        """Return first 8 characters of ID for display (like git commit hashes)."""
        return self.id[:8]
