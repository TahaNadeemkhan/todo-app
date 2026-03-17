import pytest
from unittest.mock import AsyncMock, MagicMock
from repositories.task_repository import TaskRepository
from models.enums import Priority

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def repository(mock_session):
    return TaskRepository(mock_session)

@pytest.mark.asyncio
async def test_search_tasks(repository, mock_session):
    user_id = "user123"
    query_text = "urgent"
    
    # Mock result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    await repository.search(user_id, query_text)
    
    # Verify execute was called
    mock_session.execute.assert_called_once()
    # We could inspect the query text if needed, but it's complex sqlmodel object

@pytest.mark.asyncio
async def test_filter_by_priority(repository, mock_session):
    user_id = "user123"
    priority = Priority.HIGH
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    await repository.filter_by_priority(user_id, priority)
    
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_filter_by_tags(repository, mock_session):
    user_id = "user123"
    tags = ["work", "backend"]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    await repository.filter_by_tags(user_id, tags)
    
    mock_session.execute.assert_called_once()
