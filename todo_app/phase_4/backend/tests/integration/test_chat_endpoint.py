import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from main import app

@pytest.fixture
def mock_chat_service():
    with patch("api.routes.chat.ChatService") as MockService:
        instance = MockService.return_value
        instance.process_message = AsyncMock()
        yield instance

@pytest.mark.asyncio
async def test_chat_endpoint_success(mock_chat_service):
    user_id = uuid4()
    conv_id = uuid4()
    
    mock_chat_service.process_message.return_value = {
        "conversation_id": conv_id,
        "response": "Hello!",
        "tool_calls": [],
        "created_at": "2023-01-01T12:00:00"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/chat",
            json={"message": "Hi"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Hello!"
    assert data["conversation_id"] == str(conv_id)
    
    mock_chat_service.process_message.assert_called_once()
    args = mock_chat_service.process_message.call_args
    assert args.kwargs["user_id"] == user_id
    assert args.kwargs["message_content"] == "Hi"

@pytest.mark.asyncio
async def test_chat_endpoint_with_conversation_id(mock_chat_service):
    user_id = uuid4()
    conv_id = uuid4()
    
    mock_chat_service.process_message.return_value = {
        "conversation_id": conv_id,
        "response": "Continued",
        "tool_calls": [],
        "created_at": "2023-01-01T12:00:00"
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/chat",
            json={"message": "Next", "conversation_id": str(conv_id)}
        )

    assert response.status_code == 200
    mock_chat_service.process_message.assert_called_once()
    assert str(mock_chat_service.process_message.call_args.kwargs["conversation_id"]) == str(conv_id)

@pytest.mark.asyncio
async def test_chat_endpoint_validation_error(mock_chat_service):
    user_id = uuid4()
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Missing message field
        response = await client.post(
            f"/api/{user_id}/chat",
            json={}
        )

    assert response.status_code == 422
