import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_server.tools.complete_task import complete_task

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_complete_task_success(mock_session):
    user_id = str(uuid4())
    task_id = "123"  # Integer as string
    
    mock_task = MagicMock()
    mock_task.id = 123
    mock_task.title = "Task 1"
    mock_task.completed = True

    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.complete_task.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.complete_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.update = AsyncMock(return_value=mock_task)

            result = await complete_task(user_id=user_id, task_id=task_id)

    assert result["status"] == "completed"
    assert result["task_id"] == "123"
    
    repo_instance.update.assert_called_once_with(
        task_id=123,
        user_id=user_id,
        completed=True
    )

@pytest.mark.asyncio
async def test_complete_task_not_found(mock_session):
    user_id = str(uuid4())
    task_id = "123"

    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.complete_task.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.complete_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            # ValueError raised by repository when task not found/not owned
            repo_instance.update.side_effect = ValueError("Task not found")

            with pytest.raises(ValueError, match="Task not found"):
                await complete_task(user_id=user_id, task_id=task_id)

@pytest.mark.asyncio
async def test_complete_task_invalid_uuid():
    # It now checks for integer format
    with pytest.raises(ValueError, match="Invalid task_id format"):
        await complete_task(user_id="user1", task_id="invalid-int")
