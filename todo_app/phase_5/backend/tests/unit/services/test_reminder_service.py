"""
T093 [P] [US2]: Unit tests for ReminderService.create_reminder validation

Tests the ReminderService which:
- Creates reminders for tasks
- Validates reminder configurations
- Ensures remind_before is valid ISO 8601 duration
- Validates channels are valid (email, push)

Following TDD Red-Green-Refactor cycle.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from services.reminder_service import ReminderService
from models.task_reminder import TaskReminder


class TestReminderServiceCreateReminder:
    """T093: Unit tests for create_reminder method with validation."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def service(self, mock_db_session):
        """Create ReminderService instance with mocked dependencies."""
        return ReminderService(db_session=mock_db_session)

    @pytest.mark.asyncio
    async def test_create_reminder_valid_pt1h(
        self, service, mock_db_session
    ):
        """
        Given: Valid task_id, user_id, remind_before="PT1H", channels=["email"]
        When: create_reminder is called
        Then: Reminder is created successfully
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = "PT1H"  # 1 hour before
        channels = ["email"]

        # Act
        reminder = await service.create_reminder(
            task_id=task_id,
            user_id=user_id,
            remind_before=remind_before,
            channels=channels
        )

        # Assert
        assert reminder is not None
        assert reminder.task_id == task_id
        assert reminder.user_id == user_id
        assert reminder.remind_before == remind_before
        assert reminder.channels == channels
        assert reminder.sent_at is None
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_reminder_valid_p1d(
        self, service, mock_db_session
    ):
        """
        Given: Valid remind_before="P1D" (1 day before)
        When: create_reminder is called
        Then: Reminder is created successfully
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = "P1D"  # 1 day before
        channels = ["email", "push"]

        # Act
        reminder = await service.create_reminder(
            task_id=task_id,
            user_id=user_id,
            remind_before=remind_before,
            channels=channels
        )

        # Assert
        assert reminder.remind_before == "P1D"
        assert reminder.channels == ["email", "push"]

    @pytest.mark.asyncio
    async def test_create_reminder_valid_p1w(
        self, service, mock_db_session
    ):
        """
        Given: Valid remind_before="P1W" (1 week before)
        When: create_reminder is called
        Then: Reminder is created successfully
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = "P1W"  # 1 week before
        channels = ["push"]

        # Act
        reminder = await service.create_reminder(
            task_id=task_id,
            user_id=user_id,
            remind_before=remind_before,
            channels=channels
        )

        # Assert
        assert reminder.remind_before == "P1W"

    @pytest.mark.asyncio
    async def test_create_reminder_invalid_duration_format(
        self, service, mock_db_session
    ):
        """
        Given: Invalid remind_before="1 hour" (not ISO 8601)
        When: create_reminder is called
        Then: ValueError is raised
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = "1 hour"  # Invalid format
        channels = ["email"]

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.create_reminder(
                task_id=task_id,
                user_id=user_id,
                remind_before=remind_before,
                channels=channels
            )

        assert "Invalid ISO 8601 duration format" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_reminder_empty_duration(
        self, service, mock_db_session
    ):
        """
        Given: Empty remind_before=""
        When: create_reminder is called
        Then: ValueError is raised
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = ""  # Empty
        channels = ["email"]

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.create_reminder(
                task_id=task_id,
                user_id=user_id,
                remind_before=remind_before,
                channels=channels
            )

        assert "remind_before cannot be empty" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_reminder_invalid_channel(
        self, service, mock_db_session
    ):
        """
        Given: Invalid channel "sms" (only email/push allowed)
        When: create_reminder is called
        Then: ValueError is raised
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = "PT1H"
        channels = ["sms"]  # Invalid channel

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.create_reminder(
                task_id=task_id,
                user_id=user_id,
                remind_before=remind_before,
                channels=channels
            )

        assert "Invalid channel" in str(exc_info.value)
        assert "sms" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_reminder_empty_channels(
        self, service, mock_db_session
    ):
        """
        Given: Empty channels list
        When: create_reminder is called
        Then: ValueError is raised
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = "PT1H"
        channels = []  # Empty

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.create_reminder(
                task_id=task_id,
                user_id=user_id,
                remind_before=remind_before,
                channels=channels
            )

        assert "At least one channel required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_reminder_multiple_valid_channels(
        self, service, mock_db_session
    ):
        """
        Given: Multiple valid channels ["email", "push"]
        When: create_reminder is called
        Then: Reminder is created with both channels
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = "PT1H"
        channels = ["email", "push"]

        # Act
        reminder = await service.create_reminder(
            task_id=task_id,
            user_id=user_id,
            remind_before=remind_before,
            channels=channels
        )

        # Assert
        assert set(reminder.channels) == {"email", "push"}

    @pytest.mark.asyncio
    async def test_create_reminder_duplicate_channels_deduplicated(
        self, service, mock_db_session
    ):
        """
        Given: Duplicate channels ["email", "email", "push"]
        When: create_reminder is called
        Then: Channels are deduplicated to ["email", "push"]
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())
        remind_before = "PT1H"
        channels = ["email", "email", "push"]

        # Act
        reminder = await service.create_reminder(
            task_id=task_id,
            user_id=user_id,
            remind_before=remind_before,
            channels=channels
        )

        # Assert
        assert len(set(reminder.channels)) == 2  # Deduplicated
        assert "email" in reminder.channels
        assert "push" in reminder.channels


class TestReminderServiceGetReminders:
    """T093: Unit tests for get_reminders_for_task method."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_db_session):
        """Create ReminderService instance."""
        return ReminderService(db_session=mock_db_session)

    @pytest.mark.asyncio
    async def test_get_reminders_for_task_single_reminder(
        self, service, mock_db_session
    ):
        """
        Given: Task has one reminder
        When: get_reminders_for_task is called
        Then: Reminder is returned
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())

        reminder = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email"],
            sent_at=None,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [reminder]
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        reminders = await service.get_reminders_for_task(task_id)

        # Assert
        assert len(reminders) == 1
        assert reminders[0].id == 1

    @pytest.mark.asyncio
    async def test_get_reminders_for_task_no_reminders(
        self, service, mock_db_session
    ):
        """
        Given: Task has no reminders
        When: get_reminders_for_task is called
        Then: Empty list is returned
        """
        # Arrange
        task_id = str(uuid4())

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        reminders = await service.get_reminders_for_task(task_id)

        # Assert
        assert reminders == []

    @pytest.mark.asyncio
    async def test_get_reminders_for_task_multiple_reminders(
        self, service, mock_db_session
    ):
        """
        Given: Task has multiple reminders (1 hour, 1 day before)
        When: get_reminders_for_task is called
        Then: All reminders are returned
        """
        # Arrange
        task_id = str(uuid4())
        user_id = str(uuid4())

        reminder1 = TaskReminder(
            id=1,
            task_id=task_id,
            user_id=user_id,
            remind_before="PT1H",
            channels=["email"],
            sent_at=None,
        )

        reminder2 = TaskReminder(
            id=2,
            task_id=task_id,
            user_id=user_id,
            remind_before="P1D",
            channels=["push"],
            sent_at=None,
        )

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [reminder1, reminder2]
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Act
        reminders = await service.get_reminders_for_task(task_id)

        # Assert
        assert len(reminders) == 2
        assert reminders[0].remind_before == "PT1H"
        assert reminders[1].remind_before == "P1D"


class TestReminderServiceValidation:
    """T093: Unit tests for validation helper methods."""

    @pytest.fixture
    def service(self):
        """Create ReminderService instance (no DB needed for validation)."""
        return ReminderService(db_session=AsyncMock())

    def test_validate_iso8601_duration_valid_pt1h(self, service):
        """
        Given: Valid ISO 8601 duration "PT1H"
        When: validate_iso8601_duration is called
        Then: No exception is raised
        """
        # Act & Assert - Should not raise
        service.validate_iso8601_duration("PT1H")

    def test_validate_iso8601_duration_valid_p1d(self, service):
        """
        Given: Valid ISO 8601 duration "P1D"
        When: validate_iso8601_duration is called
        Then: No exception is raised
        """
        # Act & Assert - Should not raise
        service.validate_iso8601_duration("P1D")

    def test_validate_iso8601_duration_valid_p1w(self, service):
        """
        Given: Valid ISO 8601 duration "P1W"
        When: validate_iso8601_duration is called
        Then: No exception is raised
        """
        # Act & Assert - Should not raise
        service.validate_iso8601_duration("P1W")

    def test_validate_iso8601_duration_invalid_format(self, service):
        """
        Given: Invalid duration "1h" (not ISO 8601)
        When: validate_iso8601_duration is called
        Then: ValueError is raised
        """
        # Act & Assert
        with pytest.raises(ValueError):
            service.validate_iso8601_duration("1h")

    def test_validate_channels_valid_email(self, service):
        """
        Given: Valid channel ["email"]
        When: validate_channels is called
        Then: No exception is raised
        """
        # Act & Assert - Should not raise
        service.validate_channels(["email"])

    def test_validate_channels_valid_push(self, service):
        """
        Given: Valid channel ["push"]
        When: validate_channels is called
        Then: No exception is raised
        """
        # Act & Assert - Should not raise
        service.validate_channels(["push"])

    def test_validate_channels_valid_both(self, service):
        """
        Given: Valid channels ["email", "push"]
        When: validate_channels is called
        Then: No exception is raised
        """
        # Act & Assert - Should not raise
        service.validate_channels(["email", "push"])

    def test_validate_channels_invalid_sms(self, service):
        """
        Given: Invalid channel ["sms"]
        When: validate_channels is called
        Then: ValueError is raised
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            service.validate_channels(["sms"])

        assert "Invalid channel" in str(exc_info.value)

    def test_validate_channels_empty_list(self, service):
        """
        Given: Empty channels list []
        When: validate_channels is called
        Then: ValueError is raised
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            service.validate_channels([])

        assert "At least one channel required" in str(exc_info.value)
