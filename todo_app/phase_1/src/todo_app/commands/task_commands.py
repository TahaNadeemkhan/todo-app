from typing import Optional
from todo_app.repository.base import TaskRepository
from todo_app.domain.task import Task, TaskStatus, TaskPriority

class AddTaskCommand:
    def __init__(self, repository: TaskRepository, task: Task):
        self.repository = repository
        self.task = task

    @property
    def description(self) -> str:
        return f"Add task '{self.task.title}'"

    def execute(self) -> None:
        self.repository.add(self.task)

    def undo(self) -> None:
        self.repository.delete(self.task.id)

class DeleteTaskCommand:
    def __init__(self, repository: TaskRepository, task: Task):
        self.repository = repository
        self.task = task

    @property
    def description(self) -> str:
        return f"Delete task '{self.task.title}'"

    def execute(self) -> None:
        self.repository.delete(self.task.id)

    def undo(self) -> None:
        self.repository.add(self.task)

class UpdateTaskCommand:
    def __init__(
        self,
        repository: TaskRepository,
        task: Task,
        old_title: Optional[str],
        new_title: Optional[str],
        old_desc: Optional[str],
        new_desc: Optional[str],
        old_priority: Optional[TaskPriority],
        new_priority: Optional[TaskPriority]
    ):
        self.repository = repository
        self.task = task
        self.old_title = old_title
        self.new_title = new_title
        self.old_desc = old_desc
        self.new_desc = new_desc
        self.old_priority = old_priority
        self.new_priority = new_priority

    @property
    def description(self) -> str:
        return f"Update task '{self.old_title or self.task.title}'"

    def execute(self) -> None:
        if self.new_title is not None:
            self.task.title = self.new_title
        if self.new_desc is not None:
            self.task.description = self.new_desc
        if self.new_priority is not None:
            self.task.priority = self.new_priority
        self.repository.update(self.task)

    def undo(self) -> None:
        if self.old_title is not None:
            self.task.title = self.old_title
        if self.old_desc is not None:
            self.task.description = self.old_desc
        if self.old_priority is not None:
            self.task.priority = self.old_priority
        self.repository.update(self.task)

class CompleteTaskCommand:
    def __init__(self, repository: TaskRepository, task: Task):
        self.repository = repository
        self.task = task
        self.previous_status = task.status

    @property
    def description(self) -> str:
        return f"Complete task '{self.task.title}'"

    def execute(self) -> None:
        self.task.status = TaskStatus.COMPLETED
        self.repository.update(self.task)

    def undo(self) -> None:
        self.task.status = self.previous_status
        self.repository.update(self.task)