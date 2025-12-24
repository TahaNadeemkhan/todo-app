import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_server.tools.update_task import update_task

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_update_task_success(mock_session):
    user_id = str(uuid4())
    task_id = "123"
    
    mock_task = MagicMock()
    mock_task.id = 123
    mock_task.title = "New Title"
    mock_task.description = "New Desc"

    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.update_task.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.update_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.update = AsyncMock(return_value=mock_task)

            result = await update_task(
                user_id=user_id,
                task_id=task_id,
                title="New Title",
                description="New Desc"
            )

    assert result["title"] == "New Title"
    assert result["task_id"] == "123"
    
    repo_instance.update.assert_called_once()
    assert repo_instance.update.call_args.kwargs["task_id"] == 123
    assert repo_instance.update.call_args.kwargs["title"] == "New Title"

@pytest.mark.asyncio
async def test_update_task_no_updates():
    user_id = str(uuid4())
    with pytest.raises(ValueError, match="At least one field"):
        await update_task(user_id=user_id, task_id="123")

@pytest.mark.asyncio
async def test_update_task_not_found(mock_session):
    user_id = str(uuid4())
    task_id = "123"

    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.update_task.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.update_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.update.side_effect = ValueError("Task not found")

            with pytest.raises(ValueError, match="Task not found"):
                await update_task(user_id=user_id, task_id=task_id, title="Update")
