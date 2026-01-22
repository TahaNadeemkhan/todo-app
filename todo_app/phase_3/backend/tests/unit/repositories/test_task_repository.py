import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from repositories.task_repository import TaskRepository
from models.task import Task
from models.tag import Tag
import uuid

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_find_or_create_tags_new(mock_session):
    repo = TaskRepository(mock_session)
    user_id = "user123"
    tag_names = ["work", "urgent"]
    
    # Mock result for execute (return nothing first)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    tags = await repo.find_or_create_tags(user_id, tag_names)
    
    assert len(tags) == 2
    assert tags[0].name == "work"
    assert tags[1].name == "urgent"
    assert mock_session.add.call_count == 2

@pytest.mark.asyncio
async def test_create_task_with_tags(mock_session):
    repo = TaskRepository(mock_session)
    user_id = "user123"
    title = "Test Task"
    tag_names = ["work"]
    
    # Mock find_or_create_tags to return a list with one tag
    mock_tag = Tag(name="work", user_id=user_id)
    
    with patch.object(TaskRepository, "find_or_create_tags", return_value=[mock_tag]) as mock_find:
        task = await repo.create(user_id=user_id, title=title, tags=tag_names)
        
        assert task.title == title
        assert task.tags == [mock_tag]
        mock_find.assert_called_once_with(user_id, tag_names)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
