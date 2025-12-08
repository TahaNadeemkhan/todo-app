import pytest
from unittest.mock import MagicMock
from todo_app.service.task_service import TaskService
from todo_app.service.dto import TaskDTO
from todo_app.repository.base import TaskRepository
from todo_app.domain.task import Task, TaskStatus
from todo_app.domain.exceptions import TaskNotFoundError

@pytest.fixture
def mock_repo():
    return MagicMock(spec=TaskRepository)

@pytest.fixture
def service(mock_repo):
    return TaskService(repository=mock_repo)

def test_create_task_returns_task(service, mock_repo):
    # Setup
    mock_repo.add.side_effect = lambda t: t
    
    # Execute
    dto = service.create_task("Buy milk")
    
    # Assert
    assert dto.title == "Buy milk"
    assert dto.id is not None
    mock_repo.add.assert_called_once()

def test_create_task_empty_title_raises(service):
    with pytest.raises(ValueError, match="Title cannot be empty"):
        service.create_task("")

def test_list_tasks_returns_all(service, mock_repo):
    # Setup
    task1 = Task(title="Task 1")
    task2 = Task(title="Task 2")
    mock_repo.get_all.return_value = [task1, task2]
    
    # Execute
    tasks = service.list_tasks()
    
    # Assert
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert isinstance(tasks[0], TaskDTO)

def test_complete_task_changes_status(service, mock_repo):
    # Setup
    task = Task(title="Task 1", status=TaskStatus.PENDING)
    mock_repo.get.return_value = task
    mock_repo.update.return_value = task 
    
    # Execute
    dto = service.complete_task(task.id)
    
    # Assert
    assert dto.status == TaskStatus.COMPLETED
    mock_repo.update.assert_called_once()
    assert task.status == TaskStatus.COMPLETED

def test_complete_nonexistent_raises(service, mock_repo):
    mock_repo.get.return_value = None
    
    with pytest.raises(TaskNotFoundError):
        service.complete_task("fake-id")

def test_update_task_changes_title(service, mock_repo):
    task = Task(title="Old Title")
    mock_repo.get.return_value = task
    mock_repo.update.return_value = task
    
    dto = service.update_task(task.id, title="New Title")
    
    assert task.title == "New Title"
    mock_repo.update.assert_called_once()
    assert dto.title == "New Title"

def test_update_nonexistent_raises(service, mock_repo):
    mock_repo.get.return_value = None
    with pytest.raises(TaskNotFoundError):
        service.update_task("fake", title="new")

def test_delete_task_removes_and_returns_dto(service, mock_repo):
    task = Task(title="To Delete")
    mock_repo.get.return_value = task
    
    dto = service.delete_task(task.id)
    
    mock_repo.delete.assert_called_with(task.id)
    assert dto.title == "To Delete"

def test_delete_nonexistent_raises(service, mock_repo):
    mock_repo.get.return_value = None
    
    with pytest.raises(TaskNotFoundError):
        service.delete_task("fake")

def test_undo_last_action(service, mock_repo):
    # Setup
    mock_repo.add.side_effect = lambda t: t
    
    # Action
    service.create_task("Task 1")
    
    # Undo
    desc = service.undo()
    
    assert desc == "Add task 'Task 1'"
    mock_repo.delete.assert_called()

def test_clear_all_tasks(service, mock_repo):
    service.clear_all_tasks()
    mock_repo.delete_all.assert_called_once()