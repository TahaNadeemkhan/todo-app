import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from mcp_server.tools.list_tasks import list_tasks

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_list_tasks_success(mock_session):
    user_id_str = str(uuid4())
    
    # Mock Tasks
    task1 = MagicMock()
    task1.id = 1
    task1.title = "Task 1"
    task1.description = "Desc 1"
    task1.completed = False
    task1.created_at = datetime.now(timezone.utc)

    task2 = MagicMock()
    task2.id = 2
    task2.title = "Task 2"
    task2.description = "Desc 2"
    task2.completed = True
    task2.created_at = datetime.now(timezone.utc)

    # Mock async generator for get_async_session
    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.list_tasks.get_async_session", return_value=mock_async_gen()):

        with patch("mcp_server.tools.list_tasks.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            # We updated the tool to use get_by_user
            repo_instance.get_by_user = AsyncMock(return_value=[task1, task2])

            result = await list_tasks(user_id=user_id_str, status="all")

    assert result["count"] == 2
    assert len(result["tasks"]) == 2
    assert result["tasks"][0]["title"] == "Task 1"
    assert result["tasks"][1]["title"] == "Task 2"
    
    # Verify call args
    repo_instance.get_by_user.assert_called_once()
    call_kwargs = repo_instance.get_by_user.call_args.kwargs
    assert call_kwargs["user_id"] == user_id_str
    assert call_kwargs["completed"] is None

@pytest.mark.asyncio
async def test_list_tasks_filtered_pending(mock_session):
    user_id_str = str(uuid4())

    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.list_tasks.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.list_tasks.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.get_by_user = AsyncMock(return_value=[])

            await list_tasks(user_id=user_id_str, status="pending")
            
            repo_instance.get_by_user.assert_called_once()
            assert repo_instance.get_by_user.call_args.kwargs["completed"] is False

@pytest.mark.asyncio
async def test_list_tasks_invalid_user_id():
    with pytest.raises(ValueError, match="Invalid user_id format"):
        await list_tasks(user_id=None)

@pytest.mark.asyncio
async def test_list_tasks_invalid_status():
    user_id = str(uuid4())
    with pytest.raises(ValueError, match="Invalid status"):
        await list_tasks(user_id=user_id, status="invalid")
