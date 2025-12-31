import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock
from mcp_server.tools.add_task import add_task

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_add_task_success(mock_session):
    user_id = str(uuid4())
    title = "Buy Milk"
    description = "2 cartons"
    
    # Mock Repository and DB
    mock_task = MagicMock()
    mock_task.id = uuid4()
    mock_task.title = title
    mock_task.description = description
    
    # Mock async generator for get_async_session
    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.add_task.get_async_session", return_value=mock_async_gen()):
        
        with patch("mcp_server.tools.add_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.create = AsyncMock(return_value=mock_task)
            
            with patch("mcp_server.tools.add_task.email_service.send_notification") as mock_email:
                result = await add_task(user_id=user_id, title=title, description=description)
                
                assert result["status"] == "created"
                assert result["title"] == title
                assert result["task_id"] == str(mock_task.id)
                assert result["email_sent"] is True
                repo_instance.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_add_task_invalid_uuid():
    # Now that we accept strings, we should test empty string or non-string
    with pytest.raises(ValueError, match="Invalid user_id format"):
        await add_task(user_id="", title="Test Task")
    
    with pytest.raises(ValueError, match="Invalid user_id format"):
        await add_task(user_id=None, title="Test Task")
