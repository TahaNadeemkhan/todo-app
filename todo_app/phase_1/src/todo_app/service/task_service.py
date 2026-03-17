from typing import Optional, List
from todo_app.repository.base import TaskRepository
from todo_app.domain.task import Task, TaskStatus, TaskPriority
from todo_app.domain.exceptions import TaskNotFoundError
from todo_app.domain.audit import AuditLogEntry
from .dto import TaskDTO
from todo_app.commands.invoker import CommandInvoker
from todo_app.service.audit_service import AuditLog
from todo_app.commands.task_commands import (
    AddTaskCommand,
    UpdateTaskCommand,
    DeleteTaskCommand,
    CompleteTaskCommand
)


class TaskService:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository
        self.invoker = CommandInvoker()
        self.audit_log = AuditLog()

    def _task_to_dto(self, task: Task) -> TaskDTO:
        """Convert Task domain model to DTO."""
        return TaskDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
    
    def _resolve_task(self, task_id: str) -> Task:
        """Resolve task by full ID or short ID."""
        task_id = task_id.strip()
        # 1. Try exact match
        task = self.repository.get(task_id)
        if task:
            return task
        
        # 2. Try short ID match
        if len(task_id) >= 4:
            all_tasks = self.repository.get_all()
            matches = [t for t in all_tasks if t.id.startswith(task_id)]
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                raise TaskNotFoundError(f"Ambiguous ID '{task_id}'. Multiple tasks found.")
        
        raise TaskNotFoundError(f"Task with ID '{task_id}' not found")

    def get_task(self, task_id: str) -> Optional[TaskDTO]:
        """Public method to get a single task DTO by full or short ID."""
        try:
            task = self._resolve_task(task_id)
            return self._task_to_dto(task)
        except TaskNotFoundError:
            return None

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM
    ) -> TaskDTO:
        if not title:
            raise ValueError("Title cannot be empty")

        task = Task(title=title, description=description, priority=priority)

        command = AddTaskCommand(self.repository, task)
        self.invoker.execute(command)
        self.audit_log.log("EXECUTE", command.description)

        return self._task_to_dto(task)

    def list_tasks(self) -> List[TaskDTO]:
        tasks = self.repository.get_all()
        return [self._task_to_dto(t) for t in tasks]

    def complete_task(self, task_id: str) -> TaskDTO:
        task = self._resolve_task(task_id)
        
        command = CompleteTaskCommand(self.repository, task)
        self.invoker.execute(command)
        self.audit_log.log("EXECUTE", command.description)

        return self._task_to_dto(task)

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[TaskPriority] = None
    ) -> TaskDTO:
        task = self._resolve_task(task_id)

        if title is not None and not title:
            raise ValueError("Title cannot be empty")

        command = UpdateTaskCommand(
            repository=self.repository,
            task=task,
            old_title=task.title if title is not None else None,
            new_title=title,
            old_desc=task.description if description is not None else None,
            new_desc=description,
            old_priority=task.priority if priority is not None else None,
            new_priority=priority
        )
        self.invoker.execute(command)
        self.audit_log.log("EXECUTE", command.description)

        return self._task_to_dto(task)

    def delete_task(self, task_id: str) -> TaskDTO:
        task = self._resolve_task(task_id)

        command = DeleteTaskCommand(self.repository, task)
        self.invoker.execute(command)
        self.audit_log.log("EXECUTE", command.description)

        return self._task_to_dto(task)
    
    def clear_all_tasks(self) -> None:
        self.repository.delete_all()
        self.invoker.clear_history() 
        self.audit_log.log("EXECUTE", "Cleared all tasks")

    def undo(self) -> Optional[str]:
        command = self.invoker.undo()
        if command:
            self.audit_log.log("UNDO", command.description)
            return command.description
        return None

    def get_history(self) -> List[AuditLogEntry]:
        return self.audit_log.get_history()