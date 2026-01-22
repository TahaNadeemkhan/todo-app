"""
T048-TEST & T049-TEST: Unit tests for KafkaService
TDD Red Phase - These tests will FAIL until KafkaService is implemented
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json


class TestKafkaService:
    """Unit tests for Kafka event publishing service."""

    @pytest.fixture
    def mock_dapr_client(self):
        """Mock Dapr client for testing."""
        mock = Mock()
        mock.publish_event = AsyncMock()
        return mock

    @pytest.mark.asyncio
    async def test_publish_event_success(self, mock_dapr_client):
        """T048-TEST: Test successful event publishing."""
        # Import will fail until KafkaService is created (TDD Red)
        from services.kafka_service import KafkaService

        kafka_service = KafkaService(dapr_client=mock_dapr_client)

        event_data = {
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": "789e4567-e89b-12d3-a456-426614174000",
            "title": "Buy groceries",
            "priority": "high",
            "tags": ["shopping"],
            "created_at": "2026-01-05T12:00:00Z"
        }

        # Publish event
        event_id = await kafka_service.publish_event(
            topic="task-events",
            event_type="task.created.v1",
            data=event_data
        )

        # Assertions
        assert event_id is not None
        assert isinstance(event_id, str)
        mock_dapr_client.publish_event.assert_called_once()

        # Verify event structure
        call_args = mock_dapr_client.publish_event.call_args
        assert call_args.kwargs['pubsub_name'] == 'kafka-pubsub'
        assert call_args.kwargs['topic_name'] == 'task-events'

    @pytest.mark.asyncio
    async def test_publish_event_generates_unique_event_id(self, mock_dapr_client):
        """T039-TEST: Test that event_id is generated (UUID) for idempotency."""
        from services.kafka_service import KafkaService

        kafka_service = KafkaService(dapr_client=mock_dapr_client)

        event_data = {"task_id": "123", "user_id": "789"}

        # Publish two events
        event_id_1 = await kafka_service.publish_event(
            topic="task-events",
            event_type="task.created.v1",
            data=event_data
        )
        event_id_2 = await kafka_service.publish_event(
            topic="task-events",
            event_type="task.created.v1",
            data=event_data
        )

        # Event IDs should be unique
        assert event_id_1 != event_id_2

    @pytest.mark.asyncio
    async def test_publish_event_with_retry_on_failure(self, mock_dapr_client):
        """T040-TEST: Test retry logic with exponential backoff for Kafka failures."""
        from services.kafka_service import KafkaService

        # Mock failure then success
        mock_dapr_client.publish_event = AsyncMock(
            side_effect=[Exception("Kafka unavailable"), None]
        )

        kafka_service = KafkaService(dapr_client=mock_dapr_client, max_retries=3)

        event_data = {"task_id": "123", "user_id": "789"}

        # Should retry and eventually succeed
        event_id = await kafka_service.publish_event(
            topic="task-events",
            event_type="task.created.v1",
            data=event_data
        )

        # Should have retried once
        assert mock_dapr_client.publish_event.call_count == 2
        assert event_id is not None

    @pytest.mark.asyncio
    async def test_publish_event_max_retries_exceeded(self, mock_dapr_client):
        """T040-TEST: Test that max retries are respected."""
        from services.kafka_service import KafkaService

        # Mock persistent failure
        mock_dapr_client.publish_event = AsyncMock(
            side_effect=Exception("Kafka unavailable")
        )

        kafka_service = KafkaService(dapr_client=mock_dapr_client, max_retries=3)

        event_data = {"task_id": "123", "user_id": "789"}

        # Should raise exception after max retries
        with pytest.raises(Exception) as exc_info:
            await kafka_service.publish_event(
                topic="task-events",
                event_type="task.created.v1",
                data=event_data
            )

        assert "Kafka unavailable" in str(exc_info.value)
        # Should have tried 1 initial + 3 retries = 4 times
        assert mock_dapr_client.publish_event.call_count == 4

    @pytest.mark.asyncio
    async def test_in_memory_buffer_when_kafka_unavailable(self, mock_dapr_client):
        """T041-TEST: Test in-memory buffer for events when Kafka is unavailable."""
        from services.kafka_service import KafkaService

        # Mock Kafka unavailable
        mock_dapr_client.publish_event = AsyncMock(
            side_effect=Exception("Kafka unavailable")
        )

        kafka_service = KafkaService(
            dapr_client=mock_dapr_client,
            max_retries=1,
            enable_buffer=True,
            max_buffer_size=1000
        )

        event_data = {"task_id": "123", "user_id": "789"}

        # Should buffer the event instead of raising exception
        event_id = await kafka_service.publish_event(
            topic="task-events",
            event_type="task.created.v1",
            data=event_data,
            use_buffer_on_failure=True
        )

        # Event should be in buffer
        assert event_id is not None
        assert kafka_service.get_buffer_size() == 1

    @pytest.mark.asyncio
    async def test_buffer_max_size_limit(self, mock_dapr_client):
        """T041-TEST: Test that buffer respects max size (1000 events)."""
        from services.kafka_service import KafkaService

        mock_dapr_client.publish_event = AsyncMock(
            side_effect=Exception("Kafka unavailable")
        )

        kafka_service = KafkaService(
            dapr_client=mock_dapr_client,
            max_retries=0,
            enable_buffer=True,
            max_buffer_size=5
        )

        event_data = {"task_id": "123", "user_id": "789"}

        # Fill buffer to max
        for i in range(5):
            await kafka_service.publish_event(
                topic="task-events",
                event_type="task.created.v1",
                data=event_data,
                use_buffer_on_failure=True
            )

        assert kafka_service.get_buffer_size() == 5

        # Next event should raise exception (buffer full)
        with pytest.raises(Exception) as exc_info:
            await kafka_service.publish_event(
                topic="task-events",
                event_type="task.created.v1",
                data=event_data,
                use_buffer_on_failure=True
            )

        assert "buffer full" in str(exc_info.value).lower() or "max" in str(exc_info.value).lower()


class TestEventSerialization:
    """T049-TEST: Tests for event serialization and deserialization."""

    def test_event_serialization_to_json(self):
        """Test that events are properly serialized to JSON."""
        from schemas.event_schemas import TaskCreatedEvent

        event = TaskCreatedEvent(
            event_id="550e8400-e29b-41d4-a716-446655440000",
            event_type="task.created.v1",
            schema_version="1.0",
            timestamp="2026-01-05T12:00:00Z",
            data={
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "priority": "high",
                "tags": ["shopping"],
                "created_at": "2026-01-05T12:00:00Z"
            }
        )

        json_str = event.model_dump_json()
        assert isinstance(json_str, str)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["event_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert parsed["event_type"] == "task.created.v1"
        assert parsed["data"]["title"] == "Buy groceries"

    def test_event_deserialization_from_json(self):
        """Test that events can be deserialized from JSON."""
        from schemas.event_schemas import TaskCreatedEvent

        json_str = '''
        {
            "event_id": "550e8400-e29b-41d4-a716-446655440000",
            "event_type": "task.created.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T12:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "priority": "high",
                "tags": ["shopping"],
                "created_at": "2026-01-05T12:00:00Z"
            }
        }
        '''

        event = TaskCreatedEvent.model_validate_json(json_str)
        assert event.event_id == "550e8400-e29b-41d4-a716-446655440000"
        assert event.data.title == "Buy groceries"
        assert event.data.priority == "high"

    def test_event_roundtrip_serialization(self):
        """Test that event can be serialized and deserialized without data loss."""
        from schemas.event_schemas import TaskCreatedEvent

        original_event = TaskCreatedEvent(
            event_id="550e8400-e29b-41d4-a716-446655440000",
            event_type="task.created.v1",
            schema_version="1.0",
            timestamp="2026-01-05T12:00:00Z",
            data={
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "priority": "high",
                "tags": ["shopping", "urgent"],
                "has_recurrence": True,
                "recurrence_pattern": "weekly",
                "recurrence_interval": 1,
                "recurrence_days_of_week": [0, 3, 5],
                "created_at": "2026-01-05T12:00:00Z"
            }
        )

        # Serialize
        json_str = original_event.model_dump_json()

        # Deserialize
        reconstructed_event = TaskCreatedEvent.model_validate_json(json_str)

        # Should be identical
        assert reconstructed_event.event_id == original_event.event_id
        assert reconstructed_event.data.title == original_event.data.title
        assert reconstructed_event.data.tags == original_event.data.tags
        assert reconstructed_event.data.recurrence_days_of_week == original_event.data.recurrence_days_of_week
