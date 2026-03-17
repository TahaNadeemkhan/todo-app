"""
T047-TEST: Contract test for task.completed.v1 event schema
TDD Red Phase - This test will FAIL until event schema is implemented
"""

import pytest
from datetime import datetime
from pydantic import ValidationError


class TestTaskCompletedEventSchema:
    """Contract tests for task.completed.v1 event schema validation."""

    def test_task_completed_event_valid_schema(self):
        """Test that valid task.completed event passes schema validation."""
        # Import will fail until schema is created (TDD Red)
        from schemas.event_schemas import TaskCompletedEvent

        # Valid event data as per contract
        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440001",
            "event_type": "task.completed.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T15:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "completed_at": "2026-01-05T15:00:00Z",
                "has_recurrence": True,
                "recurrence_pattern": "weekly",
                "recurrence_interval": 1,
                "recurrence_days_of_week": [0, 3, 5]
            }
        }

        # Should validate successfully
        event = TaskCompletedEvent(**event_data)
        assert event.event_id == "550e8400-e29b-41d4-a716-446655440001"
        assert event.event_type == "task.completed.v1"
        assert event.data.task_id == "123e4567-e89b-12d3-a456-426614174000"
        assert event.data.has_recurrence is True
        assert event.data.recurrence_pattern == "weekly"

    def test_task_completed_event_without_recurrence(self):
        """Test that task.completed event without recurrence is valid."""
        from schemas.event_schemas import TaskCompletedEvent

        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440001",
            "event_type": "task.completed.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T15:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "completed_at": "2026-01-05T15:00:00Z",
                "has_recurrence": False
            }
        }

        # Should validate successfully
        event = TaskCompletedEvent(**event_data)
        assert event.data.has_recurrence is False
        assert not hasattr(event.data, 'recurrence_pattern') or event.data.recurrence_pattern is None

    def test_task_completed_event_missing_required_fields(self):
        """Test that event with missing required fields fails validation."""
        from schemas.event_schemas import TaskCompletedEvent

        # Missing 'user_id'
        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440001",
            "event_type": "task.completed.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T15:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                # "user_id" missing
                "completed_at": "2026-01-05T15:00:00Z",
                "has_recurrence": False
            }
        }

        # Should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            TaskCompletedEvent(**event_data)

        assert "user_id" in str(exc_info.value)

    def test_task_completed_event_recurrence_data_consistency(self):
        """Test that if has_recurrence=true, pattern is required."""
        from schemas.event_schemas import TaskCompletedEvent

        # has_recurrence=True but no pattern
        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440001",
            "event_type": "task.completed.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T15:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "completed_at": "2026-01-05T15:00:00Z",
                "has_recurrence": True
                # Missing recurrence_pattern when has_recurrence=True
            }
        }

        # Should either raise validation error or handle gracefully
        # Implementation will decide exact behavior
        try:
            event = TaskCompletedEvent(**event_data)
            # If validation passes, has_recurrence should be False or pattern should have default
            assert event.data.has_recurrence is False or event.data.recurrence_pattern is not None
        except ValidationError:
            # This is also acceptable - strict validation
            pass

    def test_task_completed_event_json_serialization(self):
        """Test that event can be serialized to JSON."""
        from schemas.event_schemas import TaskCompletedEvent

        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440001",
            "event_type": "task.completed.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T15:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "completed_at": "2026-01-05T15:00:00Z",
                "has_recurrence": True,
                "recurrence_pattern": "daily",
                "recurrence_interval": 1
            }
        }

        event = TaskCompletedEvent(**event_data)
        json_str = event.model_dump_json()

        # Should produce valid JSON string
        assert isinstance(json_str, str)
        assert "task.completed.v1" in json_str
        assert "daily" in json_str
