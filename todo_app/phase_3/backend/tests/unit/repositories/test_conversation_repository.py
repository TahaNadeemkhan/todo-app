import pytest
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock
from repositories.conversation_repository import ConversationRepository
from models.conversation import Conversation

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.mark.asyncio
async def test_create_conversation(mock_session):
    repo = ConversationRepository(mock_session)
    user_id = uuid4()
    
    conversation = await repo.create(user_id)
    
    assert conversation.user_id == user_id
    assert isinstance(conversation.id, UUID)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_by_id_found(mock_session):
    repo = ConversationRepository(mock_session)
    conversation_id = uuid4()
    expected_conversation = Conversation(id=conversation_id, user_id=uuid4())
    
    # Mock the execute result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_conversation
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_by_id(conversation_id)
    
    assert result == expected_conversation
    mock_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_by_id_not_found(mock_session):
    repo = ConversationRepository(mock_session)
    conversation_id = uuid4()
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_by_id(conversation_id)
    
    assert result is None

@pytest.mark.asyncio
async def test_get_by_user(mock_session):
    repo = ConversationRepository(mock_session)
    user_id = uuid4()
    conversations = [Conversation(user_id=user_id) for _ in range(2)]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = conversations
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_by_user(user_id)
    
    assert len(result) == 2
    assert result == conversations
    mock_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_conversation_success(mock_session):
    repo = ConversationRepository(mock_session)
    conversation_id = uuid4()
    conversation = Conversation(id=conversation_id, user_id=uuid4())
    
    # Mock get_by_id to return conversation
    repo.get_by_id = AsyncMock(return_value=conversation)
    
    result = await repo.delete(conversation_id)
    
    assert result is True
    mock_session.delete.assert_awaited_once_with(conversation)
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_conversation_not_found(mock_session):
    repo = ConversationRepository(mock_session)
    conversation_id = uuid4()
    
    # Mock get_by_id to return None
    repo.get_by_id = AsyncMock(return_value=None)
    
    result = await repo.delete(conversation_id)
    
    assert result is False
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()
