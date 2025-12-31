import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_server.tools.delete_task import delete_task

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_delete_task_success(mock_session):
    user_id = str(uuid4())
    task_id = "123"

    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.delete_task.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.delete_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.delete = AsyncMock(return_value=True)

            result = await delete_task(user_id=user_id, task_id=task_id)

    assert result["status"] == "deleted"
    assert result["task_id"] == "123"
    
    repo_instance.delete.assert_called_once_with(
        task_id=123,
        user_id=user_id
    )

@pytest.mark.asyncio
async def test_delete_task_not_found(mock_session):
    user_id = str(uuid4())
    task_id = "123"

    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.delete_task.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.delete_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.delete = AsyncMock(return_value=False)

            with pytest.raises(ValueError, match="Task not found"):
                await delete_task(user_id=user_id, task_id=task_id)

@pytest.mark.asyncio
async def test_delete_task_invalid_uuid():
    with pytest.raises(ValueError, match="Invalid task_id format"):
        await delete_task(user_id="user1", task_id="invalid")
