"""
T092 [P] [US2]: Unit tests for ReminderScheduler.find_due_reminders

Tests the ReminderScheduler service which:
- Finds tasks with unsent reminders that are due
- Publishes reminder.due events to Kafka
- Marks reminders as sent after publishing

Following TDD Red-Green-Refactor cycle.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from services.reminder_scheduler import ReminderScheduler
from models.task import Task
from models.task_reminder import TaskReminder
from schemas.event_schemas import ReminderDueEvent


class TestReminderSchedulerFindDueReminders:
    """T092: Unit tests for find_due_reminders method."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_kafka_service(self):
        """Mock Kafka service."""
        kafka = AsyncMock()
        kafka.publish_event = AsyncMock()
        return kafka

    @pytest.fixture
    def scheduler(self, mock_db_session, mock_kafka_service):
        """Create ReminderScheduler instance with mocked dependencies."""
        return ReminderScheduler(
            db_session=mock_db_session,
            kafka_service=mock_kafka_service
        )

    @pytest.mark.asyncio
    async def test_find_due_reminders_no_tasks(
        self, scheduler, mock_db_session
    ):
        """
        Given: No tasks with reminders exist
        When: find_due_reminders is called
        Then: Empty list is returned
        """
        # Arrange
        mock_db_session.execute = AsyncMock(return_value=MagicMock(scalars=lambda: []))

        # Act
        due_reminders = await scheduler.find_due_reminders()

        # Assert
        assert due_reminders == []

    @pytest.mark.asyncio
    async def test_find_due_reminders_with_one_hour_before(
        self, scheduler, mock_db_session
    ):
        """
        Given: Task with due_at=2026-01-06 15:00 and reminder "PT1H" (1 hour before)
        When: Current time is 2026-01-06 14:00 (1 hour before due)
        Then: Reminder is found and returned
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        due_at = datetime(2026, 1, 6, 15, 0, 0, tzinfo=timezone.utc)  # 3 PM
        current_time = datetime(2026, 1, 6, 14, 0, 0, tzinfo=timezone.utc)  # 2 PM

        task = Task(
            id=task_id,
            user_id=user_id,
            title="Test Task",
            description="Test Description",
            due_at=due_at,
            priority="medium",
            completed=False,
        )

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",  # ISO 8601 duration: 1 hour
            channels=["email"],
            sent_at=None,
        )

        # Mock database query to return task with reminder
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [(task, reminder)]
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        with patch('services.reminder_scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = current_time
            due_reminders = await scheduler.find_due_reminders()

        # Assert
        assert len(due_reminders) == 1
        assert due_reminders[0][0].id == task_id
        assert due_reminders[0][1].id == 1

    @pytest.mark.asyncio
    async def test_find_due_reminders_excludes_already_sent(
        self, scheduler, mock_db_session
    ):
        """
        Given: Task with reminder that has already been sent (sent_at is not None)
        When: find_due_reminders is called
        Then: Reminder is excluded from results
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())

        task = Task(
            id=task_id,
            user_id=user_id,
            title="Test Task",
            description="Test Description",
            due_at=datetime.now(timezone.utc) + timedelta(hours=1),
            priority="medium",
            completed=False,
        )

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email"],
            sent_at=datetime.now(timezone.utc),  # Already sent
        )

        # Mock: Query should filter out sent reminders
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # No unsent reminders
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        due_reminders = await scheduler.find_due_reminders()

        # Assert
        assert due_reminders == []

    @pytest.mark.asyncio
    async def test_find_due_reminders_excludes_completed_tasks(
        self, scheduler, mock_db_session
    ):
        """
        Given: Task with reminder but task is completed
        When: find_due_reminders is called
        Then: Reminder is excluded from results (no need to remind for completed tasks)
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())

        task = Task(
            id=task_id,
            user_id=user_id,
            title="Test Task",
            description="Test Description",
            due_at=datetime.now(timezone.utc) + timedelta(hours=1),
            priority="medium",
            completed=True,  # Task is completed
        )

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email"],
            sent_at=None,
        )

        # Mock: Query should filter out completed tasks
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        due_reminders = await scheduler.find_due_reminders()

        # Assert
        assert due_reminders == []

    @pytest.mark.asyncio
    async def test_find_due_reminders_with_multiple_channels(
        self, scheduler, mock_db_session
    ):
        """
        Given: Task with reminder configured for multiple channels (email, push)
        When: find_due_reminders is called
        Then: Reminder is returned with all channels
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        due_at = datetime.now(timezone.utc) + timedelta(hours=1)

        task = Task(
            id=task_id,
            user_id=user_id,
            title="Multi-channel Task",
            description="Test",
            due_at=due_at,
            priority="high",
            completed=False,
        )

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email", "push"],  # Multiple channels
            sent_at=None,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [(task, reminder)]
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        due_reminders = await scheduler.find_due_reminders()

        # Assert
        assert len(due_reminders) == 1
        assert due_reminders[0][1].channels == ["email", "push"]

    @pytest.mark.asyncio
    async def test_find_due_reminders_with_one_day_before(
        self, scheduler, mock_db_session
    ):
        """
        Given: Task with due_at=2026-01-07 10:00 and reminder "P1D" (1 day before)
        When: Current time is 2026-01-06 10:00 (exactly 1 day before)
        Then: Reminder is found and returned
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        due_at = datetime(2026, 1, 7, 10, 0, 0, tzinfo=timezone.utc)
        current_time = datetime(2026, 1, 6, 10, 0, 0, tzinfo=timezone.utc)

        task = Task(
            id=task_id,
            user_id=user_id,
            title="Daily Reminder Task",
            description="Test",
            due_at=due_at,
            priority="medium",
            completed=False,
        )

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="P1D",  # ISO 8601 duration: 1 day
            channels=["email"],
            sent_at=None,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [(task, reminder)]
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        with patch('services.reminder_scheduler.datetime') as mock_datetime:
            mock_datetime.now.return_value = current_time
            due_reminders = await scheduler.find_due_reminders()

        # Assert
        assert len(due_reminders) == 1


class TestReminderSchedulerPublishReminderEvents:
    """T092: Unit tests for publish_reminder_events method."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_kafka_service(self):
        """Mock Kafka service."""
        kafka = AsyncMock()
        kafka.publish_event = AsyncMock()
        return kafka

    @pytest.fixture
    def scheduler(self, mock_db_session, mock_kafka_service):
        """Create ReminderScheduler instance with mocked dependencies."""
        return ReminderScheduler(
            db_session=mock_db_session,
            kafka_service=mock_kafka_service
        )

    @pytest.mark.asyncio
    async def test_publish_reminder_events_single_reminder(
        self, scheduler, mock_kafka_service, mock_db_session
    ):
        """
        Given: One due reminder (task + reminder)
        When: publish_reminder_events is called
        Then: reminder.due.v1 event is published to Kafka
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        due_at = datetime.now(timezone.utc) + timedelta(hours=1)

        task = Task(
            id=task_id,
            user_id=user_id,
            title="Test Task",
            description="Test",
            due_at=due_at,
            priority="medium",
            completed=False,
        )

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email"],
            sent_at=None,
        )

        due_reminders = [(task, reminder)]

        # Act
        await scheduler.publish_reminder_events(due_reminders)

        # Assert
        mock_kafka_service.publish_event.assert_called_once()
        call_args = mock_kafka_service.publish_event.call_args
        assert call_args[1]['topic'] == 'reminders'
        assert call_args[1]['event_type'] == 'reminder.due.v1'
        assert call_args[1]['data']['reminder_id'] == 1
        assert call_args[1]['data']['task_id'] == task_id
        assert call_args[1]['data']['user_id'] == user_id

    @pytest.mark.asyncio
    async def test_publish_reminder_events_marks_as_sent(
        self, scheduler, mock_kafka_service, mock_db_session
    ):
        """
        Given: One due reminder
        When: publish_reminder_events is called successfully
        Then: Reminder.sent_at is updated in database
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())

        task = Task(
            id=task_id,
            user_id=user_id,
            title="Test Task",
            description="Test",
            due_at=datetime.now(timezone.utc) + timedelta(hours=1),
            priority="medium",
            completed=False,
        )

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email"],
            sent_at=None,
        )

        due_reminders = [(task, reminder)]

        # Act
        await scheduler.publish_reminder_events(due_reminders)

        # Assert
        mock_db_session.commit.assert_called()
        assert reminder.sent_at is not None

    @pytest.mark.asyncio
    async def test_publish_reminder_events_multiple_reminders(
        self, scheduler, mock_kafka_service, mock_db_session
    ):
        """
        Given: Multiple due reminders
        When: publish_reminder_events is called
        Then: reminder.due.v1 event is published for each reminder
        """
        # Arrange
        task1_id = str(uuid4())
        task2_id = str(uuid4())
        user_id = str(uuid4())

        task1 = Task(
            id=task1_id,
            user_id=user_id,
            title="Task 1",
            description="Test 1",
            due_at=datetime.now(timezone.utc) + timedelta(hours=1),
            priority="high",
            completed=False,
        )

        reminder1 = TaskReminder(
            id=1,
            task_id=task1_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email"],
            sent_at=None,
        )

        task2 = Task(
            id=task2_id,
            user_id=user_id,
            title="Task 2",
            description="Test 2",
            due_at=datetime.now(timezone.utc) + timedelta(days=1),
            priority="medium",
            completed=False,
        )

        reminder2 = TaskReminder(
            id=2,
            task_id=task2_id,
            user_id=user_id,
            remind_before="P1D",
            channels=["push"],
            sent_at=None,
        )

        due_reminders = [(task1, reminder1), (task2, reminder2)]

        # Act
        await scheduler.publish_reminder_events(due_reminders)

        # Assert
        assert mock_kafka_service.publish_event.call_count == 2

    @pytest.mark.asyncio
    async def test_publish_reminder_events_kafka_failure(
        self, scheduler, mock_kafka_service, mock_db_session
    ):
        """
        Given: Kafka service fails to publish event
        When: publish_reminder_events is called
        Then: Error is logged but does not crash
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())

        task = Task(
            id=task_id,
            user_id=user_id,
            title="Test Task",
            description="Test",
            due_at=datetime.now(timezone.utc) + timedelta(hours=1),
            priority="medium",
            completed=False,
        )

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email"],
            sent_at=None,
        )

        due_reminders = [(task, reminder)]

        # Mock Kafka failure
        mock_kafka_service.publish_event.side_effect = Exception("Kafka connection failed")

        # Act & Assert - Should not raise exception
        await scheduler.publish_reminder_events(due_reminders)

        # Reminder should NOT be marked as sent if Kafka fails
        assert reminder.sent_at is None
