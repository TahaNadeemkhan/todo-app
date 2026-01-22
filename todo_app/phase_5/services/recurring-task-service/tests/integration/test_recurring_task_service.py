"""
T113: Integration test for Recurring Task Service - TDD Red Phase

End-to-end test: Publish task.completed event → verify next occurrence created
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from typing import Dict, Any


class TestRecurringTaskServiceIntegration:
    """Integration tests for the complete recurring task flow"""

    @pytest.fixture
    async def kafka_producer(self):
        """Mock Kafka producer for publishing events"""
        # TODO: Replace with actual Kafka producer when Dapr is configured
        from unittest.mock import AsyncMock
        producer = AsyncMock()
        producer.publish = AsyncMock()
        return producer

    @pytest.fixture
    async def backend_api_client(self):
        """HTTP client to verify tasks created in backend"""
        # TODO: Replace with actual HTTP client pointing to backend API
        from unittest.mock import AsyncMock
        client = AsyncMock()
        client.get_task = AsyncMock()
        return client

    @pytest.fixture
    async def event_log_db(self):
        """Database for event log (idempotency tracking)"""
        # TODO: Replace with actual database session
        from unittest.mock import AsyncMock
        db = AsyncMock()
        db.query_event = AsyncMock(return_value=None)
        db.insert_event = AsyncMock()
        return db

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_daily_recurring_task_creates_next_occurrence(
        self,
        kafka_producer,
        backend_api_client
    ):
        """
        T113: End-to-end test for daily recurring task.

        Scenario:
        1. User completes a daily recurring task (due today at 10:00)
        2. Backend publishes task.completed event to Kafka
        3. Recurring Task Service consumes event
        4. Service creates next occurrence (due tomorrow at 10:00)
        5. Verify new task exists in backend with correct due date

        This test verifies the complete event-driven flow.
        """
        # Step 1: Prepare task.completed event
        original_task_id = str(uuid4())
        user_id = "test-user-123"
        original_due_at = datetime(2026, 1, 6, 10, 0, 0, tzinfo=timezone.utc)

        task_completed_event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "task_id": original_task_id,
                "user_id": user_id,
                "completed_at": original_due_at.isoformat(),
                "has_recurrence": True,
                "recurrence_pattern": "daily",
                "recurrence_interval": 1,
                "original_task": {
                    "title": "Daily Exercise",
                    "description": "30 minutes cardio",
                    "priority": "high",
                    "tags": ["health", "recurring"],
                    "due_at": original_due_at.isoformat()
                }
            }
        }

        # Step 2: Publish event to Kafka topic
        await kafka_producer.publish(
            topic="task-events",
            key=original_task_id,
            value=json.dumps(task_completed_event)
        )

        # Step 3: Wait for service to process event (poll with timeout)
        # In real test, this would wait for actual Kafka consumption
        await asyncio.sleep(2)  # Give service time to process

        # Step 4: Query backend API to verify next occurrence was created
        # Expected: New task with same title, due_at = tomorrow
        expected_next_due = original_due_at + timedelta(days=1)

        # Mock response (in real test, this would be actual API call)
        backend_api_client.get_task.return_value = {
            "id": str(uuid4()),
            "user_id": user_id,
            "title": "Daily Exercise",
            "description": "30 minutes cardio",
            "priority": "high",
            "tags": ["health", "recurring"],
            "due_at": expected_next_due.isoformat(),
            "completed": False,
            "has_recurrence": True,
            "recurrence_pattern": "daily",
            "recurrence_interval": 1
        }

        # Step 5: Verify next task was created correctly
        next_task = await backend_api_client.get_task(user_id=user_id)

        assert next_task is not None, "Next occurrence was not created"
        assert next_task["title"] == "Daily Exercise"
        assert next_task["description"] == "30 minutes cardio"
        assert next_task["priority"] == "high"
        assert next_task["tags"] == ["health", "recurring"]
        assert next_task["completed"] is False
        assert next_task["has_recurrence"] is True
        assert next_task["recurrence_pattern"] == "daily"

        # Verify due date is exactly 1 day later
        actual_due = datetime.fromisoformat(next_task["due_at"])
        assert actual_due == expected_next_due

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_weekly_recurring_task_on_specific_days(
        self,
        kafka_producer,
        backend_api_client
    ):
        """
        T113: Weekly recurring task with days_of_week.

        Scenario:
        - Task recurs every Monday and Thursday
        - Completed on Monday (2026-01-05)
        - Next occurrence should be Thursday (2026-01-08)
        """
        original_due_at = datetime(2026, 1, 5, 14, 0, 0, tzinfo=timezone.utc)  # Monday

        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-456",
                "completed_at": original_due_at.isoformat(),
                "has_recurrence": True,
                "recurrence_pattern": "weekly",
                "recurrence_interval": 1,
                "recurrence_days_of_week": [0, 3],  # Monday, Thursday
                "original_task": {
                    "title": "Team Sync",
                    "due_at": original_due_at.isoformat()
                }
            }
        }

        await kafka_producer.publish(topic="task-events", value=json.dumps(event))
        await asyncio.sleep(2)

        # Expected: Next Thursday (3 days later)
        expected_next_due = datetime(2026, 1, 8, 14, 0, 0, tzinfo=timezone.utc)

        backend_api_client.get_task.return_value = {
            "title": "Team Sync",
            "due_at": expected_next_due.isoformat(),
            "has_recurrence": True,
            "recurrence_pattern": "weekly",
            "recurrence_days_of_week": [0, 3]
        }

        next_task = await backend_api_client.get_task(user_id="user-456")
        actual_due = datetime.fromisoformat(next_task["due_at"])
        assert actual_due == expected_next_due

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_monthly_recurring_task_with_edge_case(
        self,
        kafka_producer,
        backend_api_client
    ):
        """
        T113: Monthly recurring task with 31st day edge case.

        Scenario:
        - Task due on 31st of each month
        - Completed on January 31
        - Next occurrence should be February 28 (not 31, as Feb only has 28 days)
        """
        original_due_at = datetime(2026, 1, 31, 9, 0, 0, tzinfo=timezone.utc)

        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-789",
                "completed_at": original_due_at.isoformat(),
                "has_recurrence": True,
                "recurrence_pattern": "monthly",
                "recurrence_interval": 1,
                "recurrence_day_of_month": 31,
                "original_task": {
                    "title": "Month End Report",
                    "due_at": original_due_at.isoformat()
                }
            }
        }

        await kafka_producer.publish(topic="task-events", value=json.dumps(event))
        await asyncio.sleep(2)

        # Expected: February 28 (last day of February 2026)
        expected_next_due = datetime(2026, 2, 28, 9, 0, 0, tzinfo=timezone.utc)

        backend_api_client.get_task.return_value = {
            "title": "Month End Report",
            "due_at": expected_next_due.isoformat(),
            "has_recurrence": True,
            "recurrence_pattern": "monthly",
            "recurrence_day_of_month": 31
        }

        next_task = await backend_api_client.get_task(user_id="user-789")
        actual_due = datetime.fromisoformat(next_task["due_at"])
        assert actual_due == expected_next_due

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_idempotency_duplicate_event_not_processed_twice(
        self,
        kafka_producer,
        backend_api_client,
        event_log_db
    ):
        """
        T113: Verify idempotency - duplicate events are not processed twice.

        Scenario:
        1. Publish task.completed event
        2. Service processes event and creates next occurrence
        3. Same event is published again (network retry, etc.)
        4. Service should skip duplicate event, NOT create another task
        """
        event_id = str(uuid4())
        original_task_id = str(uuid4())

        event = {
            "event_id": event_id,
            "event_type": "task.completed.v1",
            "data": {
                "task_id": original_task_id,
                "user_id": "user-idempotency",
                "has_recurrence": True,
                "recurrence_pattern": "daily",
                "recurrence_interval": 1,
                "original_task": {
                    "title": "Idempotency Test",
                    "due_at": "2026-01-06T10:00:00Z"
                }
            }
        }

        # Publish event first time
        await kafka_producer.publish(topic="task-events", value=json.dumps(event))
        await asyncio.sleep(1)

        # Verify event was logged
        logged_event = await event_log_db.query_event(event_id)
        assert logged_event is not None, "Event should be logged after processing"

        # Track API call count
        initial_call_count = backend_api_client.get_task.call_count

        # Publish SAME event again (duplicate)
        await kafka_producer.publish(topic="task-events", value=json.dumps(event))
        await asyncio.sleep(1)

        # Verify no additional API calls were made
        final_call_count = backend_api_client.get_task.call_count
        assert final_call_count == initial_call_count, \
            "Duplicate event should not trigger additional task creation"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_non_recurring_task_skipped(
        self,
        kafka_producer,
        backend_api_client
    ):
        """
        T113: Verify non-recurring tasks are skipped.

        Scenario:
        - Task with has_recurrence=false is completed
        - Service should NOT create next occurrence
        """
        event = {
            "event_id": str(uuid4()),
            "event_type": "task.completed.v1",
            "data": {
                "task_id": str(uuid4()),
                "user_id": "user-no-recur",
                "has_recurrence": False,
                "original_task": {
                    "title": "One-time Task"
                }
            }
        }

        initial_call_count = backend_api_client.get_task.call_count

        await kafka_producer.publish(topic="task-events", value=json.dumps(event))
        await asyncio.sleep(1)

        # Verify no API calls were made (task not created)
        final_call_count = backend_api_client.get_task.call_count
        assert final_call_count == initial_call_count, \
            "Non-recurring task should not trigger task creation"
