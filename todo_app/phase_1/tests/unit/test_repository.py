import pytest
from todo_app.domain.task import Task
from todo_app.repository.in_memory import InMemoryTaskRepository

@pytest.fixture
def repo():
    return InMemoryTaskRepository()

def test_add_task_stores_task(repo):
    task = Task(title="Test Task")
    saved_task = repo.add(task)
    assert saved_task.id == task.id
    
    retrieved_task = repo.get(task.id)
    assert retrieved_task is not None
    assert retrieved_task.title == "Test Task"

def test_get_all_returns_list(repo):
    repo.add(Task(title="Task 1"))
    repo.add(Task(title="Task 2"))
    repo.add(Task(title="Task 3"))
    
    tasks = repo.get_all()
    assert len(tasks) == 3

def test_update_modifies_task(repo):
    task = Task(title="Original Title")
    repo.add(task)
    
    task.title = "Updated Title"
    updated_task = repo.update(task)
    
    assert updated_task.title == "Updated Title"
    assert repo.get(task.id).title == "Updated Title"
    # Ensure updated_at is recent (simple check that it's a datetime)
    assert updated_task.updated_at >= task.created_at

def test_delete_removes_task(repo):
    task = Task(title="To Delete")
    repo.add(task)
    
    repo.delete(task.id)
    assert repo.get(task.id) is None
