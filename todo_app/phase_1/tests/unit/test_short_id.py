import pytest
from unittest.mock import MagicMock
from todo_app.service.task_service import TaskService
from todo_app.repository.in_memory import InMemoryTaskRepository
from todo_app.domain.task import Task
from todo_app.domain.exceptions import TaskNotFoundError

def test_find_by_short_id():
    repo = InMemoryTaskRepository()
    service = TaskService(repo)
    
    # Create a task with a known ID
    task = Task(title="Test Task")
    repo.add(task)
    
    # Try to find/delete by first 8 chars
    short_id = task.id[:8]
    
    # This should succeed if short ID logic is implemented
    # Currently it will fail (RED)
    deleted_dto = service.delete_task(short_id)
    assert deleted_dto.id == task.id
    assert repo.get(task.id) is None
