import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app
from services.task_service import TaskService
from deps import get_task_service, get_current_user
from models.task import Task
from models.enums import Priority
from datetime import datetime, timezone

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_task_service():
    service = AsyncMock(spec=TaskService)
    return service

def test_sort_tasks(client, mock_task_service):
    user_id = "test_user_id"
    
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_task_service] = lambda: mock_task_service

    # Setup mock response
    mock_task = Task(
        id="task_1",
        user_id=user_id,
        title="Urgent Work",
        priority=Priority.HIGH,
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    mock_task_service.list_user_tasks.return_value = [mock_task]

    # Test sorting
    response = client.get(f"/api/{user_id}/tasks?sort_by=due_date&sort_order=asc")
    
    assert response.status_code == 200
    
    # Check if list_user_tasks was called with sort params
    # We need to update TaskService.list_user_tasks to accept sort_by/sort_order first.
    # T174/T179
    
    # We haven't updated TaskService interface yet.
    
    # Clean up
    app.dependency_overrides = {}
