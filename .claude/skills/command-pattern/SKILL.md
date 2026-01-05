---
name: command-pattern
description: Command Pattern implementation for undo/redo functionality in Todo app
version: 1.0.0
author: TahaNadeemkhan
tags: [phase1, python, design-pattern, undo, redo]
---

# Command Pattern Skill

## Purpose
Implement undo/redo functionality using the Command Pattern. This is the "delighter" feature (US-006) that differentiates the Phase 1 app.

## When to Use
- Implementing undo for Add/Update/Delete/Complete operations
- Any reversible state-changing action

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COMMAND PATTERN                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    executes    ┌──────────────────────┐  │
│  │   Invoker    │───────────────▶│     Command          │  │
│  │ (CLI/Service)│                │   (Abstract)         │  │
│  └──────────────┘                ├──────────────────────┤  │
│         │                        │ + execute()          │  │
│         │ undo_stack             │ + undo()             │  │
│         ▼                        └──────────┬───────────┘  │
│  ┌──────────────┐                           │              │
│  │ [Command1,   │                ┌──────────┴───────────┐  │
│  │  Command2,   │                │                      │  │
│  │  Command3]   │       ┌────────┴────────┬─────────────┤  │
│  └──────────────┘       ▼                 ▼             ▼  │
│                   AddCommand      DeleteCommand    UpdateCommand
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation

### 1. Command Protocol (Interface)

```python
# src/todo_app/commands/base.py
from typing import Protocol, runtime_checkable


@runtime_checkable
class Command(Protocol):
    """Command interface for undo/redo operations."""

    def execute(self) -> None:
        """Execute the command."""
        ...

    def undo(self) -> None:
        """Reverse the command."""
        ...

    @property
    def description(self) -> str:
        """Human-readable description for audit log."""
        ...
```

---

### 2. Concrete Commands

```python
# src/todo_app/commands/task_commands.py
from dataclasses import dataclass
from typing import Optional

from todo_app.domain.task import Task
from todo_app.repository.base import TaskRepository


@dataclass
class AddTaskCommand:
    """Command to add a new task."""

    repository: TaskRepository
    task: Task
    _added_task_id: Optional[str] = None

    def execute(self) -> None:
        """Add task to repository."""
        result = self.repository.add(self.task)
        self._added_task_id = result.id

    def undo(self) -> None:
        """Remove the added task."""
        if self._added_task_id:
            self.repository.delete(self._added_task_id)

    @property
    def description(self) -> str:
        return f"ADD: {self.task.title}"


@dataclass
class DeleteTaskCommand:
    """Command to delete a task."""

    repository: TaskRepository
    task_id: str
    _deleted_task: Optional[Task] = None

    def execute(self) -> None:
        """Delete task, storing it for potential undo."""
        self._deleted_task = self.repository.get(self.task_id)
        if self._deleted_task:
            self.repository.delete(self.task_id)

    def undo(self) -> None:
        """Restore the deleted task."""
        if self._deleted_task:
            self.repository.add(self._deleted_task)

    @property
    def description(self) -> str:
        title = self._deleted_task.title if self._deleted_task else self.task_id
        return f"DELETE: {title}"


@dataclass
class UpdateTaskCommand:
    """Command to update a task."""

    repository: TaskRepository
    task_id: str
    new_title: Optional[str] = None
    new_description: Optional[str] = None
    _previous_state: Optional[Task] = None

    def execute(self) -> None:
        """Update task, storing previous state for undo."""
        task = self.repository.get(self.task_id)
        if task:
            # Store previous state
            self._previous_state = task.model_copy()

            # Apply updates
            if self.new_title is not None:
                task.title = self.new_title
            if self.new_description is not None:
                task.description = self.new_description

            self.repository.update(task)

    def undo(self) -> None:
        """Restore previous state."""
        if self._previous_state:
            self.repository.update(self._previous_state)

    @property
    def description(self) -> str:
        return f"UPDATE: {self.task_id[:8]}..."


@dataclass
class CompleteTaskCommand:
    """Command to toggle task completion status."""

    repository: TaskRepository
    task_id: str
    _previous_status: Optional[str] = None

    def execute(self) -> None:
        """Toggle task completion."""
        task = self.repository.get(self.task_id)
        if task:
            from todo_app.domain.task import TaskStatus

            self._previous_status = task.status
            task.status = (
                TaskStatus.COMPLETED
                if task.status == TaskStatus.PENDING
                else TaskStatus.PENDING
            )
            self.repository.update(task)

    def undo(self) -> None:
        """Restore previous status."""
        if self._previous_status:
            task = self.repository.get(self.task_id)
            if task:
                task.status = self._previous_status
                self.repository.update(task)

    @property
    def description(self) -> str:
        return f"COMPLETE: {self.task_id[:8]}..."
```

---

### 3. Command Invoker (with Undo Stack)

```python
# src/todo_app/commands/invoker.py
from typing import List, Optional

from todo_app.commands.base import Command


class CommandInvoker:
    """Executes commands and maintains undo history."""

    def __init__(self, max_history: int = 50):
        self._undo_stack: List[Command] = []
        self._max_history = max_history

    def execute(self, command: Command) -> None:
        """Execute a command and add to history."""
        command.execute()
        self._undo_stack.append(command)

        # Limit history size
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def undo(self) -> Optional[str]:
        """Undo the last command. Returns description or None if nothing to undo."""
        if not self._undo_stack:
            return None

        command = self._undo_stack.pop()
        command.undo()
        return command.description

    def can_undo(self) -> bool:
        """Check if there are commands to undo."""
        return len(self._undo_stack) > 0

    def history(self) -> List[str]:
        """Get descriptions of all commands in history."""
        return [cmd.description for cmd in self._undo_stack]

    def clear_history(self) -> None:
        """Clear undo history."""
        self._undo_stack.clear()
```

---

### 4. Integration with Service Layer

```python
# src/todo_app/service/task_service.py
from typing import List, Optional

from todo_app.domain.task import Task
from todo_app.repository.base import TaskRepository
from todo_app.commands.invoker import CommandInvoker
from todo_app.commands.task_commands import (
    AddTaskCommand,
    DeleteTaskCommand,
    UpdateTaskCommand,
    CompleteTaskCommand,
)


class TaskService:
    """Service layer with command pattern integration."""

    def __init__(self, repository: TaskRepository):
        self._repository = repository
        self._invoker = CommandInvoker()

    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        """Add a new task (undoable)."""
        task = Task(title=title, description=description)
        command = AddTaskCommand(repository=self._repository, task=task)
        self._invoker.execute(command)
        return task

    def delete_task(self, task_id: str) -> None:
        """Delete a task (undoable)."""
        command = DeleteTaskCommand(repository=self._repository, task_id=task_id)
        self._invoker.execute(command)

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update a task (undoable)."""
        command = UpdateTaskCommand(
            repository=self._repository,
            task_id=task_id,
            new_title=title,
            new_description=description,
        )
        self._invoker.execute(command)

    def complete_task(self, task_id: str) -> None:
        """Toggle task completion (undoable)."""
        command = CompleteTaskCommand(repository=self._repository, task_id=task_id)
        self._invoker.execute(command)

    def undo(self) -> Optional[str]:
        """Undo last action. Returns description or None."""
        return self._invoker.undo()

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._invoker.can_undo()

    # Non-undoable operations (queries)
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._repository.get(task_id)

    def list_tasks(self) -> List[Task]:
        """List all tasks."""
        return self._repository.get_all()
```

---

## File Structure

```
src/todo_app/commands/
├── __init__.py
├── base.py              # Command Protocol
├── task_commands.py     # AddTask, DeleteTask, UpdateTask, CompleteTask
└── invoker.py           # CommandInvoker with undo stack
```

---

## Testing Commands

```python
# tests/unit/test_commands.py
import pytest
from todo_app.domain.task import Task, TaskStatus
from todo_app.repository.in_memory import InMemoryTaskRepository
from todo_app.commands.task_commands import AddTaskCommand, DeleteTaskCommand
from todo_app.commands.invoker import CommandInvoker


class TestAddTaskCommand:
    def test_execute_adds_task(self):
        repo = InMemoryTaskRepository()
        task = Task(title="Test")
        cmd = AddTaskCommand(repository=repo, task=task)

        cmd.execute()

        assert repo.get(task.id) is not None

    def test_undo_removes_task(self):
        repo = InMemoryTaskRepository()
        task = Task(title="Test")
        cmd = AddTaskCommand(repository=repo, task=task)
        cmd.execute()

        cmd.undo()

        assert repo.get(task.id) is None


class TestCommandInvoker:
    def test_undo_returns_description(self):
        repo = InMemoryTaskRepository()
        invoker = CommandInvoker()
        task = Task(title="Test Task")
        cmd = AddTaskCommand(repository=repo, task=task)

        invoker.execute(cmd)
        result = invoker.undo()

        assert result == "ADD: Test Task"

    def test_undo_empty_stack_returns_none(self):
        invoker = CommandInvoker()

        result = invoker.undo()

        assert result is None
```

---

## Usage Example

```python
# CLI usage
service = TaskService(repository=InMemoryTaskRepository())

# Add task (undoable)
task = service.add_task("Buy groceries")
print(f"Added: {task.title}")

# Undo the add
if service.can_undo():
    undone = service.undo()
    print(f"Undone: {undone}")  # "Undone: ADD: Buy groceries"
```
