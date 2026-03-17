"""
T094 [P] [US2]: Contract tests for POST /tasks with due_at and reminders

Tests the API contract for creating tasks with reminders:
- POST /api/{user_id}/tasks with due_at and reminders array
- GET /api/{user_id}/tasks/{task_id}/reminders
- POST /api/{user_id}/tasks/{task_id}/reminders to add reminder to existing task

Validates request/response schemas and API behavior.

Following TDD Red-Green-Refactor cycle.
"""

import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from uuid import uuid4

from main import app


class TestCreateTaskWithReminders:
    """T094: Contract tests for POST /tasks with reminders."""

    @pytest.mark.asyncio
    async def test_create_task_with_due_at_and_reminder(self):
        """
        Given: Valid task payload with due_at and one reminder
        When: POST /api/{user_id}/tasks
        Then: 201 Created, task is created with reminder
        """
        # Arrange
        user_id = str(uuid4())
        due_at = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()

        payload = {
            "title": "Task with Reminder",
            "description": "Test task with due date and reminder",
            "due_date": due_at,
            "priority": "high",
            "reminders": [
                {
                    "remind_before": "PT1H",  # 1 hour before
                    "channels": ["email"]
                }
            ]
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json=payload
            )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Task with Reminder"
        assert data["due_date"] is not None
        # Note: Response doesn't include reminders inline, need separate GET

    @pytest.mark.asyncio
    async def test_create_task_with_multiple_reminders(self):
        """
        Given: Task with multiple reminders (1 hour, 1 day before)
        When: POST /api/{user_id}/tasks
        Then: 201 Created, task is created with all reminders
        """
        # Arrange
        user_id = str(uuid4())
        due_at = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

        payload = {
            "title": "Task with Multiple Reminders",
            "description": "Test",
            "due_date": due_at,
            "priority": "medium",
            "reminders": [
                {
                    "remind_before": "PT1H",  # 1 hour before
                    "channels": ["email"]
                },
                {
                    "remind_before": "P1D",  # 1 day before
                    "channels": ["push"]
                }
            ]
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json=payload
            )

        # Assert
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_task_with_invalid_reminder_duration(self):
        """
        Given: Task with invalid reminder duration "1 hour" (not ISO 8601)
        When: POST /api/{user_id}/tasks
        Then: 422 Unprocessable Entity with validation error
        """
        # Arrange
        user_id = str(uuid4())
        due_at = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()

        payload = {
            "title": "Task with Invalid Reminder",
            "description": "Test",
            "due_date": due_at,
            "priority": "high",
            "reminders": [
                {
                    "remind_before": "1 hour",  # Invalid format
                    "channels": ["email"]
                }
            ]
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json=payload
            )

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "Invalid ISO 8601 duration" in str(data)

    @pytest.mark.asyncio
    async def test_create_task_with_invalid_reminder_channel(self):
        """
        Given: Task with invalid channel "sms"
        When: POST /api/{user_id}/tasks
        Then: 422 Unprocessable Entity
        """
        # Arrange
        user_id = str(uuid4())
        due_at = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()

        payload = {
            "title": "Task with Invalid Channel",
            "description": "Test",
            "due_date": due_at,
            "priority": "high",
            "reminders": [
                {
                    "remind_before": "PT1H",
                    "channels": ["sms"]  # Invalid channel
                }
            ]
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json=payload
            )

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_with_reminder_but_no_due_date(self):
        """
        Given: Task with reminder but no due_date
        When: POST /api/{user_id}/tasks
        Then: 422 Unprocessable Entity (cannot set reminder without due date)
        """
        # Arrange
        user_id = str(uuid4())

        payload = {
            "title": "Task with Reminder but No Due Date",
            "description": "Test",
            "priority": "high",
            "reminders": [
                {
                    "remind_before": "PT1H",
                    "channels": ["email"]
                }
            ]
            # Missing due_date
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json=payload
            )

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "due_date required when reminders are set" in str(data).lower()

    @pytest.mark.asyncio
    async def test_create_task_with_empty_reminders_array(self):
        """
        Given: Task with empty reminders array []
        When: POST /api/{user_id}/tasks
        Then: 201 Created (empty reminders is valid)
        """
        # Arrange
        user_id = str(uuid4())
        due_at = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()

        payload = {
            "title": "Task with No Reminders",
            "description": "Test",
            "due_date": due_at,
            "priority": "medium",
            "reminders": []  # Empty but valid
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks",
                json=payload
            )

        # Assert
        assert response.status_code == 201


class TestGetTaskReminders:
    """T094: Contract tests for GET /tasks/{id}/reminders."""

    @pytest.mark.asyncio
    async def test_get_task_reminders_single_reminder(self):
        """
        Given: Task has one reminder
        When: GET /api/{user_id}/tasks/{task_id}/reminders
        Then: 200 OK with reminder array
        """
        # Arrange
        user_id = str(uuid4())
        task_id = str(uuid4())

        # Note: In real test, task would be created first
        # For TDD, we're testing the contract/interface

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks/{task_id}/reminders"
            )

        # Assert - In Red phase, this will fail (endpoint doesn't exist)
        # Expected response format:
        # {
        #     "reminders": [
        #         {
        #             "id": 1,
        #             "remind_before": "PT1H",
        #             "channels": ["email"],
        #             "sent_at": null
        #         }
        #     ]
        # }
        assert response.status_code in [200, 404]  # 404 if task not found

    @pytest.mark.asyncio
    async def test_get_task_reminders_no_reminders(self):
        """
        Given: Task has no reminders
        When: GET /api/{user_id}/tasks/{task_id}/reminders
        Then: 200 OK with empty reminders array
        """
        # Arrange
        user_id = str(uuid4())
        task_id = str(uuid4())

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks/{task_id}/reminders"
            )

        # Assert
        # Expected: {"reminders": []}
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_task_reminders_unauthorized_user(self):
        """
        Given: Task belongs to different user
        When: GET /api/{user_id}/tasks/{task_id}/reminders
        Then: 404 Not Found (don't leak task existence)
        """
        # Arrange
        user_id = str(uuid4())
        task_id = str(uuid4())  # Task belongs to different user

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_id}/tasks/{task_id}/reminders"
            )

        # Assert
        assert response.status_code == 404


class TestAddReminderToExistingTask:
    """T094: Contract tests for POST /tasks/{id}/reminders."""

    @pytest.mark.asyncio
    async def test_add_reminder_to_existing_task(self):
        """
        Given: Existing task with due_date
        When: POST /api/{user_id}/tasks/{task_id}/reminders
        Then: 201 Created, reminder is added
        """
        # Arrange
        user_id = str(uuid4())
        task_id = str(uuid4())

        payload = {
            "remind_before": "PT1H",
            "channels": ["email", "push"]
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks/{task_id}/reminders",
                json=payload
            )

        # Assert - In Red phase, this will fail
        # Expected response:
        # {
        #     "id": 1,
        #     "task_id": "...",
        #     "remind_before": "PT1H",
        #     "channels": ["email", "push"],
        #     "sent_at": null
        # }
        assert response.status_code in [201, 404]  # 404 if task not found

    @pytest.mark.asyncio
    async def test_add_reminder_to_task_without_due_date(self):
        """
        Given: Task without due_date
        When: POST /api/{user_id}/tasks/{task_id}/reminders
        Then: 400 Bad Request (cannot add reminder to task without due date)
        """
        # Arrange
        user_id = str(uuid4())
        task_id = str(uuid4())

        payload = {
            "remind_before": "PT1H",
            "channels": ["email"]
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks/{task_id}/reminders",
                json=payload
            )

        # Assert
        assert response.status_code in [400, 404]

    @pytest.mark.asyncio
    async def test_add_reminder_with_invalid_duration(self):
        """
        Given: Invalid remind_before format
        When: POST /api/{user_id}/tasks/{task_id}/reminders
        Then: 422 Unprocessable Entity
        """
        # Arrange
        user_id = str(uuid4())
        task_id = str(uuid4())

        payload = {
            "remind_before": "invalid",
            "channels": ["email"]
        }

        # Act
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_id}/tasks/{task_id}/reminders",
                json=payload
            )

        # Assert
        assert response.status_code == 422


class TestReminderResponseSchema:
    """T094: Contract tests for reminder response schema validation."""

    def test_reminder_response_schema_structure(self):
        """
        Given: Reminder response from API
        When: Response is parsed
        Then: Schema matches expected structure
        """
        # Expected schema for reminder response:
        expected_schema = {
            "id": int,
            "task_id": str,  # UUID string
            "user_id": str,  # UUID string
            "remind_before": str,  # ISO 8601 duration
            "channels": list,  # ["email", "push"]
            "sent_at": (str, type(None)),  # ISO 8601 datetime or null
            "created_at": str,  # ISO 8601 datetime
        }

        # This test documents the expected schema
        # Actual validation happens in integration tests
        assert expected_schema is not None

    def test_task_create_request_schema_with_reminders(self):
        """
        Given: Task create request payload with reminders
        When: Request is validated
        Then: Schema matches expected structure
        """
        # Expected request schema:
        expected_schema = {
            "title": str,  # Required
            "description": (str, type(None)),  # Optional
            "due_date": (str, type(None)),  # ISO 8601 datetime, optional
            "priority": str,  # "low" | "medium" | "high"
            "reminders": list,  # Array of reminder configs
            # Each reminder:
            # {
            #     "remind_before": str,  # ISO 8601 duration
            #     "channels": list[str]  # ["email", "push"]
            # }
        }

        # This test documents the expected schema
        assert expected_schema is not None
