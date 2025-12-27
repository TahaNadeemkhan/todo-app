"""
Contract definition for the Todo App Service Layer.
This serves as the 'API' for the CLI integration.
"""

from typing import Protocol, List, Optional
from datetime import datetime
from enum import Enum

# --- Data Structures (Mirroring Pydantic Models) ---

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class TaskDTO:
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

# --- Service Interface ---

class TaskService(Protocol):
    """
    Core business logic interface.
    The CLI (and later API) will interact strictly via this contract.
    """
    
    def create_task(self, title: str, description: Optional[str] = None) -> TaskDTO:
        """Creates a new task and returns the created object."""
        ...

    def get_task(self, task_id: str) -> Optional[TaskDTO]:
        """Retrieves a single task by ID."""
        ...

    def list_tasks(self) -> List[TaskDTO]:
        """Retrieves all tasks."""
        ...

    def complete_task(self, task_id: str) -> TaskDTO:
        """Marks a task as COMPLETED."""
        ...

    def update_task(self, task_id: str, title: Optional[str] = None, description: Optional[str] = None) -> TaskDTO:
        """Updates task details."""
        ...

    def delete_task(self, task_id: str) -> None:
        """Permanently removes a task."""
        ...
