import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from repositories.message_repository import MessageRepository
from models.message import Message, MessageRole

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    return session

@pytest.mark.asyncio
async def test_create_message(mock_session):
    repo = MessageRepository(mock_session)
    conversation_id = uuid4()
    user_id = uuid4()
    
    message = await repo.create(conversation_id, user_id, MessageRole.USER, "Hello")
    
    assert message.conversation_id == conversation_id
    assert message.user_id == user_id
    assert message.role == MessageRole.USER
    assert message.content == "Hello"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_by_conversation(mock_session):
    repo = MessageRepository(mock_session)
    conversation_id = uuid4()
    messages = [Message(conversation_id=conversation_id, user_id=uuid4(), role=MessageRole.USER, content="Msg") for _ in range(2)]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = messages
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_by_conversation(conversation_id)
    
    assert len(result) == 2
    assert result == messages
    mock_session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_history(mock_session):
    repo = MessageRepository(mock_session)
    conversation_id = uuid4()
    # Create messages
    msg1 = Message(conversation_id=conversation_id, user_id=uuid4(), role=MessageRole.USER, content="First")
    msg2 = Message(conversation_id=conversation_id, user_id=uuid4(), role=MessageRole.ASSISTANT, content="Second")
    
    # DB query returns DESC (newest first)
    # So if msg2 is newer, it comes first
    db_result = [msg2, msg1]
    
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = db_result
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_history(conversation_id)
    
    # Repo should reverse them (oldest first)
    assert len(result) == 2
    assert result[0] == msg1 # Oldest
    assert result[1] == msg2 # Newest
    mock_session.execute.assert_awaited_once()
