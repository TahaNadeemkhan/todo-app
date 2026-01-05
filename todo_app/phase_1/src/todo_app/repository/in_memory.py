from typing import Dict, List, Optional
from datetime import datetime, timezone
from todo_app.domain.task import Task
from .base import TaskRepository

class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: Dict[str, Task] = {}

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_all(self) -> List[Task]:
        return list(self._tasks.values())

    def update(self, task: Task) -> Task:
        task.updated_at = datetime.now(timezone.utc)
        self._tasks[task.id] = task
        return task

    def delete(self, task_id: str) -> None:
        if task_id in self._tasks:
            del self._tasks[task_id]

    def delete_all(self) -> None:
        self._tasks.clear()