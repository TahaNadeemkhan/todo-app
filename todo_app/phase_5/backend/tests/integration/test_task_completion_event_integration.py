"""
T051-TEST: Integration test - Complete task → verify event published to Kafka
TDD Red Phase - This test will FAIL until event publishing is implemented
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from uuid import uuid4

from testcontainers.kafka import KafkaContainer
from kafka import KafkaConsumer


@pytest.fixture(scope="module")
def kafka_container():
    """Spin up Kafka container for integration testing."""
    kafka = KafkaContainer(image="bitnami/kafka:3.6")
    kafka.start()

    bootstrap_servers = kafka.get_bootstrap_server()
    print(f"Kafka started at: {bootstrap_servers}")

    yield bootstrap_servers

    kafka.stop()


@pytest.fixture
async def test_db_session():
    """Create test database session."""
    from unittest.mock import AsyncMock
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture
def kafka_consumer(kafka_container):
    """Create Kafka consumer for reading test events."""
    consumer = KafkaConsumer(
        "task-events",
        bootstrap_servers=kafka_container,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="test-consumer-group-completion",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=5000
    )

    yield consumer

    consumer.close()


class TestTaskCompletionEventIntegration:
    """Integration tests for task completion event publishing to Kafka."""

    @pytest.mark.asyncio
    async def test_complete_task_publishes_event_to_kafka(
        self, kafka_container, kafka_consumer, test_db_session
    ):
        """
        T051-TEST: Test that completing a task publishes task.completed.v1 event to Kafka.

        Flow:
        1. Create task
        2. Complete task via TaskService
        3. Verify task.completed.v1 event published to task-events topic
        4. Verify event structure matches contract
        5. Verify completed_at timestamp is present
        """
        from services.task_service import TaskService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        dapr_client = DaprClient()
        kafka_service = KafkaService(
            dapr_client=dapr_client,
            bootstrap_servers=kafka_container
        )
        task_service = TaskService(
            db_session=test_db_session,
            kafka_service=kafka_service
        )

        # Create a task first
        user_id = str(uuid4())
        task_data = {
            "title": "Task to complete",
            "priority": "medium",
            "tags": ["test"],
            "user_id": user_id
        }
        created_task = await task_service.create_task(**task_data)

        # Clear kafka_consumer to skip task.created event
        for _ in kafka_consumer:
            break

        # Complete the task
        completed_task = await task_service.complete_task(
            task_id=created_task.id,
            user_id=user_id
        )

        await asyncio.sleep(1)

        # Consume task.completed event
        events = []
        for message in kafka_consumer:
            event = message.value
            if event["event_type"] == "task.completed.v1":
                events.append(event)
                break

        # Assertions
        assert len(events) == 1, "Expected one task.completed event"

        event = events[0]

        # Verify event structure
        assert event["event_type"] == "task.completed.v1"
        assert event["schema_version"] == "1.0"
        assert "event_id" in event
        assert "timestamp" in event
        assert "data" in event

        # Verify event data
        event_data = event["data"]
        assert event_data["task_id"] == created_task.id
        assert event_data["user_id"] == user_id
        assert "completed_at" in event_data
        assert event_data["has_recurrence"] is False

    @pytest.mark.asyncio
    async def test_complete_recurring_task_includes_recurrence_in_event(
        self, kafka_container, kafka_consumer, test_db_session
    ):
        """
        T051-TEST: Test that completing a recurring task includes recurrence data in event.

        This is critical for the Recurring Task Service to know whether to create
        the next instance of the task.
        """
        from services.task_service import TaskService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        dapr_client = DaprClient()
        kafka_service = KafkaService(
            dapr_client=dapr_client,
            bootstrap_servers=kafka_container
        )
        task_service = TaskService(
            db_session=test_db_session,
            kafka_service=kafka_service
        )

        # Create recurring task
        user_id = str(uuid4())
        task_data = {
            "title": "Daily standup",
            "priority": "high",
            "tags": ["meetings"],
            "user_id": user_id,
            "has_recurrence": True,
            "recurrence_pattern": "daily",
            "recurrence_interval": 1
        }
        created_task = await task_service.create_task(**task_data)

        # Clear task.created event
        for _ in kafka_consumer:
            break

        # Complete the recurring task
        await task_service.complete_task(
            task_id=created_task.id,
            user_id=user_id
        )

        await asyncio.sleep(1)

        # Consume task.completed event
        events = []
        for message in kafka_consumer:
            event = message.value
            if event["event_type"] == "task.completed.v1":
                events.append(event)
                break

        assert len(events) == 1
        event = events[0]

        # Verify recurrence data is present
        event_data = event["data"]
        assert event_data["has_recurrence"] is True
        assert event_data["recurrence_pattern"] == "daily"
        assert event_data["recurrence_interval"] == 1

        # Recurring Task Service will use this to create next task instance

    @pytest.mark.asyncio
    async def test_complete_task_event_ordering(
        self, kafka_container, kafka_consumer, test_db_session
    ):
        """
        T051-TEST: Test that task.created and task.completed events are published in order.
        """
        from services.task_service import TaskService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        dapr_client = DaprClient()
        kafka_service = KafkaService(
            dapr_client=dapr_client,
            bootstrap_servers=kafka_container
        )
        task_service = TaskService(
            db_session=test_db_session,
            kafka_service=kafka_service
        )

        user_id = str(uuid4())

        # Create and immediately complete task
        task_data = {
            "title": "Quick task",
            "priority": "high",
            "tags": [],
            "user_id": user_id
        }
        created_task = await task_service.create_task(**task_data)
        await task_service.complete_task(
            task_id=created_task.id,
            user_id=user_id
        )

        await asyncio.sleep(2)

        # Consume both events
        events = []
        for message in kafka_consumer:
            events.append(message.value)
            if len(events) == 2:
                break

        assert len(events) == 2

        # Verify event ordering
        assert events[0]["event_type"] == "task.created.v1"
        assert events[1]["event_type"] == "task.completed.v1"

        # Verify both reference same task
        assert events[0]["data"]["task_id"] == created_task.id
        assert events[1]["data"]["task_id"] == created_task.id

        # Verify completed_at comes after created_at
        created_at = datetime.fromisoformat(events[0]["data"]["created_at"].replace("Z", "+00:00"))
        completed_at = datetime.fromisoformat(events[1]["data"]["completed_at"].replace("Z", "+00:00"))
        assert completed_at >= created_at

    @pytest.mark.asyncio
    async def test_multiple_task_completions_publish_separate_events(
        self, kafka_container, kafka_consumer, test_db_session
    ):
        """
        T051-TEST: Test that completing multiple tasks publishes separate events.
        """
        from services.task_service import TaskService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        dapr_client = DaprClient()
        kafka_service = KafkaService(
            dapr_client=dapr_client,
            bootstrap_servers=kafka_container
        )
        task_service = TaskService(
            db_session=test_db_session,
            kafka_service=kafka_service
        )

        user_id = str(uuid4())

        # Create 3 tasks
        tasks = []
        for i in range(3):
            task_data = {
                "title": f"Task {i+1}",
                "priority": "medium",
                "tags": [],
                "user_id": user_id
            }
            task = await task_service.create_task(**task_data)
            tasks.append(task)

        # Clear task.created events
        for _ in range(3):
            for _ in kafka_consumer:
                break

        # Complete all 3 tasks
        for task in tasks:
            await task_service.complete_task(
                task_id=task.id,
                user_id=user_id
            )

        await asyncio.sleep(2)

        # Consume task.completed events
        completed_events = []
        for message in kafka_consumer:
            event = message.value
            if event["event_type"] == "task.completed.v1":
                completed_events.append(event)
            if len(completed_events) == 3:
                break

        assert len(completed_events) == 3

        # Verify each event references different task
        task_ids = [event["data"]["task_id"] for event in completed_events]
        assert len(set(task_ids)) == 3, "Each event should reference a different task"

        # Verify all have unique event_ids
        event_ids = [event["event_id"] for event in completed_events]
        assert len(set(event_ids)) == 3, "Each event should have a unique event_id"
