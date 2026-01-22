"""
T050-TEST: Integration test - Create task → verify event published to Kafka
TDD Red Phase - This test will FAIL until event publishing is implemented
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from uuid import uuid4
from typing import AsyncGenerator

# Testcontainers imports
from testcontainers.kafka import KafkaContainer
from kafka import KafkaConsumer
from kafka.errors import KafkaError


@pytest.fixture(scope="module")
def kafka_container():
    """
    Spin up Kafka container for integration testing.
    Uses Bitnami Kafka image (KRaft mode, no Zookeeper).
    """
    kafka = KafkaContainer(image="bitnami/kafka:3.6")
    kafka.start()

    # Wait for Kafka to be ready
    bootstrap_servers = kafka.get_bootstrap_server()
    print(f"Kafka started at: {bootstrap_servers}")

    yield bootstrap_servers

    kafka.stop()


@pytest.fixture
async def test_db_session():
    """
    Create test database session for integration tests.
    TODO: Implement after database setup is complete.
    """
    # Placeholder - will be implemented with actual DB connection
    from unittest.mock import AsyncMock
    mock_session = AsyncMock()
    yield mock_session


@pytest.fixture
def kafka_consumer(kafka_container):
    """
    Create Kafka consumer for reading test events.
    """
    consumer = KafkaConsumer(
        "task-events",
        bootstrap_servers=kafka_container,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="test-consumer-group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=5000  # 5 second timeout
    )

    yield consumer

    consumer.close()


class TestTaskCreationEventIntegration:
    """Integration tests for task creation event publishing to Kafka."""

    @pytest.mark.asyncio
    async def test_create_task_publishes_event_to_kafka(
        self, kafka_container, kafka_consumer, test_db_session
    ):
        """
        T050-TEST: Test that creating a task publishes task.created.v1 event to Kafka.

        Flow:
        1. Create task via TaskService
        2. Verify event published to task-events topic
        3. Verify event structure matches contract
        4. Verify event data matches created task
        """
        # Import will fail until implementation is complete (TDD Red)
        from services.task_service import TaskService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        # Setup Dapr client for Kafka
        dapr_client = DaprClient()
        kafka_service = KafkaService(
            dapr_client=dapr_client,
            bootstrap_servers=kafka_container
        )

        # Create TaskService with Kafka publishing
        task_service = TaskService(
            db_session=test_db_session,
            kafka_service=kafka_service
        )

        # Create a task
        task_data = {
            "title": "Buy groceries",
            "description": "Milk, bread, eggs",
            "priority": "high",
            "tags": ["shopping", "urgent"],
            "due_at": (datetime.utcnow() + timedelta(hours=6)).isoformat(),
            "user_id": str(uuid4())
        }

        created_task = await task_service.create_task(**task_data)

        # Wait for event to be published
        await asyncio.sleep(1)

        # Consume event from Kafka
        events = []
        for message in kafka_consumer:
            events.append(message.value)
            break  # Get first message

        # Assertions
        assert len(events) == 1, "Expected one event to be published"

        event = events[0]

        # Verify event structure
        assert "event_id" in event
        assert "event_type" in event
        assert "schema_version" in event
        assert "timestamp" in event
        assert "data" in event

        # Verify event type
        assert event["event_type"] == "task.created.v1"
        assert event["schema_version"] == "1.0"

        # Verify event data matches created task
        event_data = event["data"]
        assert event_data["task_id"] == created_task.id
        assert event_data["user_id"] == task_data["user_id"]
        assert event_data["title"] == task_data["title"]
        assert event_data["description"] == task_data["description"]
        assert event_data["priority"] == task_data["priority"]
        assert event_data["tags"] == task_data["tags"]

        # Verify timestamps
        assert "created_at" in event_data
        assert "timestamp" in event

    @pytest.mark.asyncio
    async def test_create_task_with_recurrence_publishes_correct_event(
        self, kafka_container, kafka_consumer, test_db_session
    ):
        """
        T050-TEST: Test that creating a recurring task includes recurrence data in event.
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
        task_data = {
            "title": "Weekly team meeting",
            "priority": "medium",
            "tags": ["meetings"],
            "user_id": str(uuid4()),
            "has_recurrence": True,
            "recurrence_pattern": "weekly",
            "recurrence_interval": 1,
            "recurrence_days_of_week": [0, 3, 5]  # Monday, Thursday, Saturday
        }

        created_task = await task_service.create_task(**task_data)

        await asyncio.sleep(1)

        # Consume event
        events = []
        for message in kafka_consumer:
            events.append(message.value)
            break

        assert len(events) == 1
        event = events[0]

        # Verify recurrence data in event
        event_data = event["data"]
        assert event_data["has_recurrence"] is True
        assert event_data["recurrence_pattern"] == "weekly"
        assert event_data["recurrence_interval"] == 1
        assert event_data["recurrence_days_of_week"] == [0, 3, 5]

    @pytest.mark.asyncio
    async def test_create_task_event_has_unique_event_id(
        self, kafka_container, kafka_consumer, test_db_session
    ):
        """
        T050-TEST: Test that each task.created event has a unique event_id for idempotency.
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

        # Create two tasks
        task1_data = {
            "title": "Task 1",
            "priority": "high",
            "tags": [],
            "user_id": str(uuid4())
        }
        task2_data = {
            "title": "Task 2",
            "priority": "low",
            "tags": [],
            "user_id": str(uuid4())
        }

        await task_service.create_task(**task1_data)
        await task_service.create_task(**task2_data)

        await asyncio.sleep(2)

        # Consume events
        events = []
        for message in kafka_consumer:
            events.append(message.value)
            if len(events) == 2:
                break

        assert len(events) == 2

        # Verify unique event IDs
        event_id_1 = events[0]["event_id"]
        event_id_2 = events[1]["event_id"]

        assert event_id_1 != event_id_2, "Event IDs must be unique"

        # Verify both are valid UUIDs
        from uuid import UUID
        UUID(event_id_1)  # Will raise ValueError if invalid
        UUID(event_id_2)
