import pytest
from unittest.mock import AsyncMock, MagicMock
from repositories.task_repository import TaskRepository

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def repository(mock_session):
    return TaskRepository(mock_session)

@pytest.mark.asyncio
async def test_sort_by_due_date(repository, mock_session):
    user_id = "user123"
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    # We expect the repository method to accept sort_by and order
    # But currently TaskRepository.get_by_user doesn't support it.
    # T174 says "Add sort_by parameter support in TaskRepository".
    
    # Let's assume we update get_by_user to accept sort params
    # OR we add specific methods like sort_by_due_date. 
    # T175-T178 imply specific methods? Or implementing logic.
    
    # Better approach: Update get_by_user to accept sort_by and order.
    
    await repository.get_by_user(user_id, sort_by="due_at", sort_order="asc")
    
    mock_session.execute.assert_called_once()
    # We could inspect the call to see if ORDER BY is in the query

@pytest.mark.asyncio
async def test_sort_by_priority(repository, mock_session):
    user_id = "user123"
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_result

    await repository.get_by_user(user_id, sort_by="priority", sort_order="desc")
    
    mock_session.execute.assert_called_once()
