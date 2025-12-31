import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from services.chat_service import ChatService
from models.conversation import Conversation
from models.message import Message, MessageRole

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_openai_client():
    with patch("services.chat_service.AsyncOpenAI") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance

@pytest.fixture
def mock_mcp():
    with patch("services.chat_service.mcp") as mock:
        yield mock

@pytest.fixture
def chat_service(mock_session, mock_openai_client, mock_mcp):
    # We need to patch the repositories inside ChatService or Mock them before init
    # Since they are instantiated in __init__, we can patch the class imports
    with patch("services.chat_service.ConversationRepository") as MockConvRepo, \
         patch("services.chat_service.MessageRepository") as MockMsgRepo:
        
        service = ChatService(mock_session)
        service.conversation_repo = MockConvRepo.return_value
        service.message_repo = MockMsgRepo.return_value
        
        # Setup async mocks for repo methods
        service.conversation_repo.get_by_id = AsyncMock()
        service.conversation_repo.create = AsyncMock()
        service.message_repo.create = AsyncMock()
        service.message_repo.get_history = AsyncMock()
        
        yield service

@pytest.mark.asyncio
async def test_process_message_new_conversation(chat_service, mock_openai_client):
    user_id = uuid4()
    message_content = "Hello AI"
    
    # Mock Repo Responses
    new_conv = Conversation(id=uuid4(), user_id=user_id)
    chat_service.conversation_repo.create.return_value = new_conv
    chat_service.message_repo.get_history.return_value = []
    
    # Mock OpenAI Response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello User"
    mock_response.choices[0].message.tool_calls = None
    
    chat_service.client.chat.completions.create.return_value = mock_response

    # Execute
    result = await chat_service.process_message(user_id, message_content)

    # Verify
    assert result["response"] == "Hello User"
    assert result["conversation_id"] == new_conv.id
    
    # Verify Repos Called
    chat_service.conversation_repo.create.assert_called_once_with(user_id)
    chat_service.message_repo.create.assert_any_call(
        conversation_id=new_conv.id,
        user_id=user_id,
        role=MessageRole.user,
        content=message_content
    )
    chat_service.message_repo.create.assert_any_call(
        conversation_id=new_conv.id,
        user_id=user_id,
        role=MessageRole.assistant,
        content="Hello User"
    )

@pytest.mark.asyncio
async def test_process_message_existing_conversation(chat_service, mock_openai_client):
    user_id = uuid4()
    conv_id = uuid4()
    message_content = "Continue chat"
    
    # Mock Repo Responses
    existing_conv = Conversation(id=conv_id, user_id=user_id)
    chat_service.conversation_repo.get_by_id.return_value = existing_conv
    
    # Mock History
    history = [
        Message(id=uuid4(), conversation_id=conv_id, user_id=user_id, role=MessageRole.user, content="Hi"),
        Message(id=uuid4(), conversation_id=conv_id, user_id=user_id, role=MessageRole.assistant, content="Hello")
    ]
    chat_service.message_repo.get_history.return_value = history
    
    # Mock OpenAI Response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Sure"
    mock_response.choices[0].message.tool_calls = None
    
    chat_service.client.chat.completions.create.return_value = mock_response

    # Execute
    result = await chat_service.process_message(user_id, message_content, conversation_id=conv_id)

    # Verify
    assert result["conversation_id"] == conv_id
    chat_service.conversation_repo.get_by_id.assert_called_with(conv_id)
    chat_service.conversation_repo.create.assert_not_called()

@pytest.mark.asyncio
async def test_process_message_with_tool_call(chat_service, mock_openai_client, mock_mcp):
    user_id = uuid4()
    message_content = "Add task Buy Milk"
    conv_id = uuid4()
    
    # Mock Repo
    chat_service.conversation_repo.create.return_value = Conversation(id=conv_id, user_id=user_id)
    chat_service.message_repo.get_history.return_value = []
    
    # Mock OpenAI Responses (2 turns: 1. Tool Call, 2. Final Response)
    
    # Turn 1: Tool Call
    msg_turn1 = MagicMock()
    msg_turn1.content = None
    msg_turn1.tool_calls = [MagicMock()]
    msg_turn1.tool_calls[0].id = "call_123"
    msg_turn1.tool_calls[0].function.name = "add_task"
    msg_turn1.tool_calls[0].function.arguments = '{"title": "Buy Milk"}'
    
    resp_turn1 = MagicMock()
    resp_turn1.choices = [MagicMock(message=msg_turn1)]
    
    # Turn 2: Final Response
    msg_turn2 = MagicMock()
    msg_turn2.content = "Task added"
    msg_turn2.tool_calls = None
    
    resp_turn2 = MagicMock()
    resp_turn2.choices = [MagicMock(message=msg_turn2)]
    
    chat_service.client.chat.completions.create.side_effect = [resp_turn1, resp_turn2]
    
    # Mock MCP Tool Execution
    mock_mcp.call_tool.return_value = {"task_id": "task_123", "status": "created"}
    
    # Mock MCP Tool Listing
    tool_mock = MagicMock()
    tool_mock.name = "add_task"
    tool_mock.description = "Add task"
    tool_mock.model_dump.return_value = {
        "name": "add_task",
        "description": "Add task",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "title": {"type": "string"}
            },
            "required": ["user_id", "title"]
        }
    }
    mock_mcp._tool_manager.list_tools.return_value = [tool_mock]

    # Execute
    result = await chat_service.process_message(user_id, message_content)

    # Verify
    assert result["response"] == "Task added"
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["tool"] == "add_task"
    
    # Verify user_id was injected
    call_args = mock_mcp.call_tool.call_args
    assert call_args[0][0] == "add_task"
    assert call_args[0][1]["title"] == "Buy Milk"
    assert call_args[0][1]["user_id"] == str(user_id)
