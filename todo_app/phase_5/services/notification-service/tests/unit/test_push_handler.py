"""
T126: Unit tests for PushHandler
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from handlers.push_handler import PushHandler


@pytest.fixture
def push_handler():
    """Create PushHandler instance for testing."""
    with patch("handlers.push_handler.firebase_admin.initialize_app"):
        handler = PushHandler()
        handler._initialized = True  # Mock initialization
        return handler


@pytest.mark.asyncio
async def test_send_reminder_push_success(push_handler):
    """Test successful push notification sending."""
    # Mock Firebase messaging
    with patch("handlers.push_handler.messaging.send") as mock_send:
        mock_send.return_value = "message-id-123"

        # Test data
        user_id = "user-123"
        task_title = "Buy groceries"
        task_description = "Milk, bread, eggs"
        due_at = datetime(2026, 1, 10, 18, 0, 0)
        remind_before = "PT1H"
        fcm_token = "fcm-token-abc"

        # Execute
        result = await push_handler.send_reminder_push(
            user_id, task_title, task_description, due_at, remind_before, fcm_token
        )

        # Assert
        assert result is True
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_send_reminder_push_not_initialized(push_handler):
    """Test push notification when FCM not initialized."""
    push_handler._initialized = False

    result = await push_handler.send_reminder_push(
        "user-123", "Test Task", None, datetime.now(), "PT1H", "token"
    )

    assert result is False


@pytest.mark.asyncio
async def test_send_reminder_push_no_token(push_handler):
    """Test push notification when user has no FCM token."""
    result = await push_handler.send_reminder_push(
        "user-123", "Test Task", None, datetime.now(), "PT1H", None
    )

    assert result is False


@pytest.mark.asyncio
async def test_send_reminder_push_invalid_token(push_handler):
    """Test push notification with invalid/expired FCM token."""
    with patch("handlers.push_handler.messaging.send") as mock_send:
        from firebase_admin import messaging

        mock_send.side_effect = messaging.UnregisteredError("Token invalid")

        result = await push_handler.send_reminder_push(
            "user-123", "Test Task", None, datetime.now(), "PT1H", "invalid-token"
        )

        assert result is False


@pytest.mark.asyncio
async def test_send_test_notification(push_handler):
    """Test sending test notification."""
    with patch("handlers.push_handler.messaging.send") as mock_send:
        mock_send.return_value = "test-message-id"

        result = await push_handler.send_test_notification("test-token")

        assert result is True
        mock_send.assert_called_once()
