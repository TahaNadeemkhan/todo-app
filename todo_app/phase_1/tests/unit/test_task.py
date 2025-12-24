import pytest
from pydantic import ValidationError
from todo_app.domain.task import Task, TaskStatus

def test_create_task_with_title():
    task = Task(title="Buy groceries")
    assert task.title == "Buy groceries"
    assert task.status == TaskStatus.PENDING
    assert task.id is not None
    assert task.created_at is not None
    assert task.updated_at is not None

def test_task_title_validation():
    # Empty title
    with pytest.raises(ValidationError):
        Task(title="")
    
    # Title too long
    with pytest.raises(ValidationError):
        Task(title="a" * 201)

def test_task_status_enum():
    assert TaskStatus.PENDING.value == "PENDING"
    assert TaskStatus.COMPLETED.value == "COMPLETED"
