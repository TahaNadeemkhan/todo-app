"""
T127: Unit tests for NotificationHandler
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from schemas import ReminderDueEvent, ReminderDueData, NotificationChannelEnum
from handlers.notification_handler import NotificationHandler


@pytest.fixture
def notification_handler():
    """Create NotificationHandler instance for testing."""
    handler = NotificationHandler()
    # Mock dependencies
    handler.event_log_repo = Mock()
    handler.notification_repo = Mock()
    handler.email_handler = Mock()
    handler.push_handler = Mock()
    return handler


@pytest.fixture
def sample_reminder_event():
    """Create sample ReminderDueEvent for testing."""
    return ReminderDueEvent(
        event_id="event-123",
        event_type="reminder.due.v1",
        schema_version="1.0",
        timestamp="2026-01-10T17:00:00Z",
        data=ReminderDueData(
            reminder_id=1,
            task_id="task-456",
            user_id="user-789",
            user_email="user@example.com",
            task_title="Buy groceries",
            task_description="Milk, bread, eggs",
            due_at="2026-01-10T18:00:00Z",
            remind_before="PT1H",
            channels=[NotificationChannelEnum.EMAIL],
        ),
    )


@pytest.mark.asyncio
async def test_handle_reminder_due_success(notification_handler, sample_reminder_event):
    """Test successful reminder processing."""
    # Mock idempotency check - not processed
    notification_handler.event_log_repo.is_event_processed = AsyncMock(return_value=False)
    notification_handler.event_log_repo.mark_event_processed = AsyncMock()

    # Mock email sending success
    notification_handler.email_handler.send_reminder_email = AsyncMock(return_value=True)

    # Mock logging
    notification_handler.notification_repo.log_sent = AsyncMock(return_value=101)

    # Mock Dapr publish
    with patch("handlers.notification_handler.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Execute
        await notification_handler.handle_reminder_due(sample_reminder_event)

        # Assert
        notification_handler.email_handler.send_reminder_email.assert_called_once()
        notification_handler.notification_repo.log_sent.assert_called_once()
        notification_handler.event_log_repo.mark_event_processed.assert_called_once_with(
            "event-123", "reminder.due.v1", "notification-service"
        )


@pytest.mark.asyncio
async def test_handle_reminder_due_already_processed(
    notification_handler, sample_reminder_event
):
    """Test skipping already processed events (idempotency)."""
    # Mock idempotency check - already processed
    notification_handler.event_log_repo.is_event_processed = AsyncMock(return_value=True)

    # Execute
    await notification_handler.handle_reminder_due(sample_reminder_event)

    # Assert - should not send notification
    notification_handler.email_handler.send_reminder_email.assert_not_called()


@pytest.mark.asyncio
async def test_handle_reminder_due_email_failure_with_retry(
    notification_handler, sample_reminder_event
):
    """Test retry logic when email sending fails."""
    # Mock idempotency check
    notification_handler.event_log_repo.is_event_processed = AsyncMock(return_value=False)
    notification_handler.event_log_repo.mark_event_processed = AsyncMock()

    # Mock email sending - fail twice, succeed on third attempt
    notification_handler.email_handler.send_reminder_email = AsyncMock(
        side_effect=[False, False, True]
    )

    # Mock logging
    notification_handler.notification_repo.log_sent = AsyncMock(return_value=101)

    # Mock Dapr publish
    with patch("handlers.notification_handler.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Execute
        await notification_handler.handle_reminder_due(sample_reminder_event)

        # Assert - should retry 3 times
        assert notification_handler.email_handler.send_reminder_email.call_count == 3
        notification_handler.notification_repo.log_sent.assert_called_once()


@pytest.mark.asyncio
async def test_handle_reminder_due_max_retries_exceeded(
    notification_handler, sample_reminder_event
):
    """Test failure after max retries exceeded."""
    # Mock idempotency check
    notification_handler.event_log_repo.is_event_processed = AsyncMock(return_value=False)
    notification_handler.event_log_repo.mark_event_processed = AsyncMock()

    # Mock email sending - always fails
    notification_handler.email_handler.send_reminder_email = AsyncMock(return_value=False)

    # Mock logging
    notification_handler.notification_repo.log_failed = AsyncMock(return_value=102)

    # Mock Dapr publish
    with patch("handlers.notification_handler.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Execute
        await notification_handler.handle_reminder_due(sample_reminder_event)

        # Assert - should retry max times and log failure
        assert notification_handler.email_handler.send_reminder_email.call_count == 3
        notification_handler.notification_repo.log_failed.assert_called_once()


@pytest.mark.asyncio
async def test_handle_reminder_due_multiple_channels(notification_handler):
    """Test sending notifications via multiple channels."""
    # Create event with both email and push channels
    event = ReminderDueEvent(
        event_id="event-multi",
        event_type="reminder.due.v1",
        schema_version="1.0",
        timestamp="2026-01-10T17:00:00Z",
        data=ReminderDueData(
            reminder_id=2,
            task_id="task-999",
            user_id="user-888",
            user_email="user@example.com",
            task_title="Team meeting",
            task_description=None,
            due_at="2026-01-10T18:00:00Z",
            remind_before="PT1H",
            channels=[NotificationChannelEnum.EMAIL, NotificationChannelEnum.PUSH],
        ),
    )

    # Mock
    notification_handler.event_log_repo.is_event_processed = AsyncMock(return_value=False)
    notification_handler.event_log_repo.mark_event_processed = AsyncMock()
    notification_handler.email_handler.send_reminder_email = AsyncMock(return_value=True)
    notification_handler.push_handler.send_reminder_push = AsyncMock(return_value=True)
    notification_handler.notification_repo.log_sent = AsyncMock(return_value=201)

    with patch("handlers.notification_handler.httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Execute
        await notification_handler.handle_reminder_due(event)

        # Assert - both channels called
        notification_handler.email_handler.send_reminder_email.assert_called_once()
        notification_handler.push_handler.send_reminder_push.assert_called_once()
        assert notification_handler.notification_repo.log_sent.call_count == 2
