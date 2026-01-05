from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from todo_app.domain.task import TaskStatus, TaskPriority


class TaskDTO(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: datetime

    @property
    def short_id(self) -> str:
        """Return first 8 characters of ID for display."""
        return self.id[:8]
