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
    notify_email = "test@example.com"
    
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
                result = await add_task(
                    user_id=user_id, 
                    title=title, 
                    description=description,
                    notify_email=notify_email
                )
                
                assert result["status"] == "created"
                assert result["title"] == title
                assert result["task_id"] == str(mock_task.id)
                assert result["email_sent"] is True
                
                # Verify create was called with explicit email
                repo_instance.create.assert_awaited_with(
                    user_id=user_id,
                    title=title,
                    description=description,
                    notify_email=notify_email
                )

@pytest.mark.asyncio
async def test_add_task_with_email_lookup(mock_session):
    """Test that tool looks up user email if not provided."""
    user_id = str(uuid4())
    title = "Buy Eggs"
    user_email = "user@lookup.com"
    
    # Mock Task
    mock_task = MagicMock()
    mock_task.id = uuid4()
    mock_task.title = title
    mock_task.description = None

    # Mock User lookup result
    mock_user = MagicMock()
    mock_user.email = user_email
    
    # Mock session.execute result for User lookup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    # Mock async generator
    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.add_task.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.add_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.create = AsyncMock(return_value=mock_task)
            
            with patch("mcp_server.tools.add_task.email_service.send_notification") as mock_email:
                # Call WITHOUT notify_email
                result = await add_task(user_id=user_id, title=title)
                
                assert result["status"] == "created"
                assert result["email_sent"] is True
                
                # Verify DB lookup for user
                mock_session.execute.assert_called() 
                
                # Verify create was called with FOUND email
                repo_instance.create.assert_awaited_with(
                    user_id=user_id,
                    title=title,
                    description=None,
                    notify_email=user_email
                )

@pytest.mark.asyncio
async def test_add_task_with_tags(mock_session):
    """Test adding a task with tags."""
    user_id = str(uuid4())
    title = "Task with tags"
    tags = ["work", "important"]
    
    mock_task = MagicMock()
    mock_task.id = uuid4()
    mock_task.title = title
    mock_task.tags = [MagicMock(name=t) for t in tags]
    for i, t in enumerate(tags):
        mock_task.tags[i].name = t

    async def mock_async_gen():
        yield mock_session

    with patch("mcp_server.tools.add_task.get_async_session", return_value=mock_async_gen()):
        with patch("mcp_server.tools.add_task.TaskRepository") as MockRepo:
            repo_instance = MockRepo.return_value
            repo_instance.create = AsyncMock(return_value=mock_task)
            
            with patch("mcp_server.tools.add_task.email_service.send_notification"):
                result = await add_task(user_id=user_id, title=title, tags=tags)
                
                assert result["status"] == "created"
                assert "work" in result["tags"]
                assert "important" in result["tags"]
                repo_instance.create.assert_awaited_with(
                    user_id=user_id,
                    title=title,
                    description=None,
                    notify_email=None,
                    tags=tags
                )

@pytest.mark.asyncio
async def test_add_task_invalid_uuid():
    # Now that we accept strings, we should test empty string or non-string
    with pytest.raises(ValueError, match="Invalid user_id format"):
        await add_task(user_id="", title="Test Task")
    
    with pytest.raises(ValueError, match="Invalid user_id format"):
        await add_task(user_id=None, title="Test Task")
