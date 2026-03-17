import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from main import app
from services.task_service import TaskService
from deps import get_task_service, get_current_user
from models.task import Task
from schemas.task_schemas import TaskCreate, Priority
from datetime import datetime, timezone

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_task_service():
    service = AsyncMock(spec=TaskService)
    return service

def test_create_task_with_priority_and_tags(client, mock_task_service):
    user_id = "test_user_id"
    
    # Mock authentication
    app.dependency_overrides[get_current_user] = lambda: user_id
    
    # Mock TaskService dependency
    app.dependency_overrides[get_task_service] = lambda: mock_task_service

    # Setup mock response
    mock_task = Task(
        id="task_123",
        user_id=user_id,
        title="Priority Task",
        priority=Priority.HIGH,
        tags=["urgent", "work"],
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        # Default values for other fields
        notifications_enabled=False,
        due_at=None
    )
    mock_task_service.create_task.return_value = mock_task

    # Define request payload
    payload = {
        "title": "Priority Task",
        "priority": "high",
        "tags": ["urgent", "work"]
    }

    # Make request
    response = client.post(f"/api/{user_id}/tasks", json=payload)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Priority Task"
    assert data["priority"] == "high"
    assert "urgent" in data["tags"]
    assert "work" in data["tags"]
    
    # Verify service was called with correct arguments
    mock_task_service.create_task.assert_called_once()
    call_kwargs = mock_task_service.create_task.call_args.kwargs
    assert call_kwargs["title"] == "Priority Task"
    assert call_kwargs["priority"] == "high"
    assert call_kwargs["tags"] == ["urgent", "work"]

    # Clean up overrides
    app.dependency_overrides = {}