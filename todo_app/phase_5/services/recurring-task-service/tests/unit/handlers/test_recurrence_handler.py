"""
T111-T112: Unit tests for RecurrenceHandler - TDD Red Phase

Tests the core business logic for handling task.completed events
and creating next occurrences for recurring tasks.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


class TestRecurrenceHandler:
    """Unit tests for RecurrenceHandler.handle_task_completed"""

    @pytest.fixture
    def mock_task_api_client(self):
        """Mock HTTP client for calling backend API"""
        client = AsyncMock()
        client.create_task = AsyncMock(return_value={
            "id": str(uuid4()),
            "title": "Next Occurrence",
            "user_id": "user-123",
            "due_at": "2026-01-07T10:00:00Z"
        })
        return client

    @pytest.fixture
    def mock_event_log_repo(self):
        """Mock EventLogRepository for idempotency tracking"""
        repo = AsyncMock()
        repo.has_processed = AsyncMock(return_value=False)
        repo.mark_as_processed = AsyncMock()
        return repo

    @pytest.fixture
    def recurrence_handler(self, mock_task_api_client, mock_event_log_repo):
        """Create RecurrenceHandler instance with mocked dependencies"""
        from handlers.recurrence_handler import RecurrenceHandler
        handler = RecurrenceHandler(
            task_api_client=mock_task_api_client,
            event_log_repo=mock_event_log_repo
        )
        return handler

    @pytest.mark.asyncio
    async def test_handle_daily_recurrence(self, recurrence_handler, mock_task_api_client):
        """
        T111: Handle task.completed event for daily recurring task.

        Given: A task.completed event with has_recurrence=true, pattern=daily, interval=1
        When: handle_task_completed is called
        Then: Next occurrence is created with due_at = current due_at + 1 day
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-123",
                "completed_at": "2026-01-06T10:00:00Z",
                "has_recurrence": True,
                "recurrence_pattern": "daily",
                "recurrence_interval": 1,
                "original_task": {
                    "title": "Daily Task",
                    "description": "Recurring task",
                    "priority": "medium",
                    "tags": ["recurring"],
                    "due_at": "2026-01-06T10:00:00Z"
                }
            }
        }

        await recurrence_handler.handle_task_completed(event)

        # Verify next task was created via API
        mock_task_api_client.create_task.assert_called_once()
        call_args = mock_task_api_client.create_task.call_args[1]

        assert call_args["user_id"] == "user-123"
        assert call_args["title"] == "Daily Task"
        assert call_args["description"] == "Recurring task"
        assert call_args["priority"] == "medium"
        assert call_args["tags"] == ["recurring"]
        assert call_args["has_recurrence"] is True
        assert call_args["recurrence_pattern"] == "daily"
        assert call_args["recurrence_interval"] == 1

        # Verify next due_at is 1 day later
        original_due = datetime.fromisoformat("2026-01-06T10:00:00+00:00")
        expected_due = original_due + timedelta(days=1)
        actual_due = datetime.fromisoformat(call_args["due_at"].replace("Z", "+00:00"))
        assert actual_due == expected_due

    @pytest.mark.asyncio
    async def test_handle_weekly_recurrence(self, recurrence_handler, mock_task_api_client):
        """
        T111: Handle task.completed event for weekly recurring task.

        Given: Task with pattern=weekly, interval=1, days_of_week=[0,3] (Mon,Thu)
        When: Completed on Monday
        Then: Next occurrence due on Thursday (3 days later)
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-456",
                "completed_at": "2026-01-05T14:00:00Z",  # Monday
                "has_recurrence": True,
                "recurrence_pattern": "weekly",
                "recurrence_interval": 1,
                "recurrence_days_of_week": [0, 3],  # Monday, Thursday
                "original_task": {
                    "title": "Weekly Meeting",
                    "due_at": "2026-01-05T14:00:00Z"
                }
            }
        }

        await recurrence_handler.handle_task_completed(event)

        mock_task_api_client.create_task.assert_called_once()
        call_args = mock_task_api_client.create_task.call_args[1]

        # Next occurrence should be Thursday (2026-01-08)
        expected_due = datetime(2026, 1, 8, 14, 0, 0, tzinfo=timezone.utc)
        actual_due = datetime.fromisoformat(call_args["due_at"].replace("Z", "+00:00"))
        assert actual_due == expected_due

    @pytest.mark.asyncio
    async def test_handle_monthly_recurrence(self, recurrence_handler, mock_task_api_client):
        """
        T111: Handle task.completed event for monthly recurring task.

        Given: Task with pattern=monthly, interval=1, day_of_month=15
        When: Completed in January
        Then: Next occurrence due on February 15
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-789",
                "completed_at": "2026-01-15T09:00:00Z",
                "has_recurrence": True,
                "recurrence_pattern": "monthly",
                "recurrence_interval": 1,
                "recurrence_day_of_month": 15,
                "original_task": {
                    "title": "Monthly Report",
                    "due_at": "2026-01-15T09:00:00Z"
                }
            }
        }

        await recurrence_handler.handle_task_completed(event)

        mock_task_api_client.create_task.assert_called_once()
        call_args = mock_task_api_client.create_task.call_args[1]

        # Next occurrence should be February 15
        expected_due = datetime(2026, 2, 15, 9, 0, 0, tzinfo=timezone.utc)
        actual_due = datetime.fromisoformat(call_args["due_at"].replace("Z", "+00:00"))
        assert actual_due == expected_due

    @pytest.mark.asyncio
    async def test_handle_monthly_edge_case_31st(self, recurrence_handler, mock_task_api_client):
        """
        T111: Handle monthly recurrence edge case (31st → February).

        Given: Task with day_of_month=31, completed on Jan 31
        When: Next month is February (only 28 days)
        Then: Next occurrence due on February 28
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-999",
                "completed_at": "2026-01-31T12:00:00Z",
                "has_recurrence": True,
                "recurrence_pattern": "monthly",
                "recurrence_interval": 1,
                "recurrence_day_of_month": 31,
                "original_task": {
                    "title": "Month End Task",
                    "due_at": "2026-01-31T12:00:00Z"
                }
            }
        }

        await recurrence_handler.handle_task_completed(event)

        call_args = mock_task_api_client.create_task.call_args[1]

        # February 2026 has 28 days, so expect February 28
        expected_due = datetime(2026, 2, 28, 12, 0, 0, tzinfo=timezone.utc)
        actual_due = datetime.fromisoformat(call_args["due_at"].replace("Z", "+00:00"))
        assert actual_due == expected_due

    @pytest.mark.asyncio
    async def test_skip_non_recurring_task(self, recurrence_handler, mock_task_api_client):
        """
        T111: Skip event if task has no recurrence.

        Given: A task.completed event with has_recurrence=false
        When: handle_task_completed is called
        Then: No API call is made, handler returns early
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-123",
                "completed_at": "2026-01-06T10:00:00Z",
                "has_recurrence": False,
                "original_task": {
                    "title": "One-time Task"
                }
            }
        }

        await recurrence_handler.handle_task_completed(event)

        # No API call should be made
        mock_task_api_client.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_idempotency_duplicate_event(self, recurrence_handler, mock_event_log_repo, mock_task_api_client):
        """
        T112: Reject duplicate events (idempotency).

        Given: An event with event_id that has already been processed
        When: handle_task_completed is called
        Then: Event is skipped, no task is created
        """
        # Mark event as already processed
        mock_event_log_repo.has_processed.return_value = True

        event = {
            "event_id": "duplicate-event-123",
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-123",
                "has_recurrence": True,
                "recurrence_pattern": "daily",
                "original_task": {"title": "Task", "due_at": "2026-01-06T10:00:00Z"}
            }
        }

        await recurrence_handler.handle_task_completed(event)

        # Verify event was checked
        mock_event_log_repo.has_processed.assert_called_once_with("duplicate-event-123")

        # No task should be created
        mock_task_api_client.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_idempotency_marks_new_event(self, recurrence_handler, mock_event_log_repo, mock_task_api_client):
        """
        T112: Mark new events as processed for idempotency.

        Given: A new event (not yet processed)
        When: handle_task_completed is called successfully
        Then: Event is marked as processed in event log
        """
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-123",
                "has_recurrence": True,
                "recurrence_pattern": "daily",
                "recurrence_interval": 1,
                "original_task": {"title": "Task", "due_at": "2026-01-06T10:00:00Z"}
            }
        }

        await recurrence_handler.handle_task_completed(event)

        # Verify event was marked as processed
        mock_event_log_repo.mark_as_processed.assert_called_once()
        call_kwargs = mock_event_log_repo.mark_as_processed.call_args.kwargs
        assert call_kwargs["event_id"] == event_id

    @pytest.mark.asyncio
    async def test_error_handling_api_failure(self, recurrence_handler, mock_task_api_client, mock_event_log_repo):
        """
        T111: Handle API failure when creating next occurrence.

        Given: API call fails (network error, 500, etc.)
        When: handle_task_completed is called
        Then: Exception is raised, event is NOT marked as processed (for retry)
        """
        # Simulate API failure
        mock_task_api_client.create_task.side_effect = Exception("API connection failed")

        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-123",
                "has_recurrence": True,
                "recurrence_pattern": "daily",
                "recurrence_interval": 1,
                "original_task": {"title": "Task", "due_at": "2026-01-06T10:00:00Z"}
            }
        }

        # Expect exception to propagate
        with pytest.raises(Exception, match="API connection failed"):
            await recurrence_handler.handle_task_completed(event)

        # Event should NOT be marked as processed (allow retry)
        mock_event_log_repo.mark_as_processed.assert_not_called()

    @pytest.mark.asyncio
    async def test_preserve_task_metadata(self, recurrence_handler, mock_task_api_client):
        """
        T111: Preserve task metadata when creating next occurrence.

        Given: Task with tags, description, priority
        When: Next occurrence is created
        Then: All metadata is copied to new task
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-123",
                "has_recurrence": True,
                "recurrence_pattern": "daily",
                "recurrence_interval": 2,
                "original_task": {
                    "title": "Team Standup",
                    "description": "Daily sync with engineering team",
                    "priority": "high",
                    "tags": ["meeting", "recurring", "team"],
                    "due_at": "2026-01-06T09:00:00Z"
                }
            }
        }

        await recurrence_handler.handle_task_completed(event)

        call_args = mock_task_api_client.create_task.call_args[1]

        # Verify all metadata preserved
        assert call_args["title"] == "Team Standup"
        assert call_args["description"] == "Daily sync with engineering team"
        assert call_args["priority"] == "high"
        assert call_args["tags"] == ["meeting", "recurring", "team"]
        assert call_args["has_recurrence"] is True
        assert call_args["recurrence_pattern"] == "daily"
        assert call_args["recurrence_interval"] == 2
