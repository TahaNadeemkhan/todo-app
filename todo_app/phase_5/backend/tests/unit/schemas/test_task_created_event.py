"""
T046-TEST: Contract test for task.created.v1 event schema
TDD Red Phase - This test will FAIL until event schema is implemented
"""

import pytest
from datetime import datetime
from pydantic import ValidationError


class TestTaskCreatedEventSchema:
    """Contract tests for task.created.v1 event schema validation."""

    def test_task_created_event_valid_schema(self):
        """Test that valid task.created event passes schema validation."""
        # Import will fail until schema is created (TDD Red)
        from schemas.event_schemas import TaskCreatedEvent

        # Valid event data as per contract
        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440000",
            "event_type": "task.created.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T12:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "description": "Milk, bread, eggs",
                "priority": "high",
                "tags": ["shopping", "urgent"],
                "due_at": "2026-01-05T18:00:00Z",
                "has_recurrence": True,
                "recurrence_pattern": "weekly",
                "recurrence_interval": 1,
                "recurrence_days_of_week": [0, 3, 5],
                "created_at": "2026-01-05T12:00:00Z"
            }
        }

        # Should validate successfully
        event = TaskCreatedEvent(**event_data)
        assert event.event_id == "550e8400-e29b-41d4-a716-446655440000"
        assert event.event_type == "task.created.v1"
        assert event.data.task_id == "123e4567-e89b-12d3-a456-426614174000"
        assert event.data.priority == "high"
        assert event.data.has_recurrence is True

    def test_task_created_event_missing_required_fields(self):
        """Test that event with missing required fields fails validation."""
        from schemas.event_schemas import TaskCreatedEvent

        # Missing 'title' in data
        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440000",
            "event_type": "task.created.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T12:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                # "title" missing
                "priority": "high",
                "tags": [],
                "created_at": "2026-01-05T12:00:00Z"
            }
        }

        # Should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            TaskCreatedEvent(**event_data)

        assert "title" in str(exc_info.value)

    def test_task_created_event_invalid_priority(self):
        """Test that event with invalid priority enum fails validation."""
        from schemas.event_schemas import TaskCreatedEvent

        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440000",
            "event_type": "task.created.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T12:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "title": "Test task",
                "priority": "invalid_priority",  # Invalid enum value
                "tags": [],
                "created_at": "2026-01-05T12:00:00Z"
            }
        }

        # Should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            TaskCreatedEvent(**event_data)

        assert "priority" in str(exc_info.value)

    def test_task_created_event_invalid_recurrence_pattern(self):
        """Test that event with invalid recurrence pattern fails validation."""
        from schemas.event_schemas import TaskCreatedEvent

        event_data = {
            "event_id": "550e8400-e29b-41d4-a716-446655440000",
            "event_type": "task.created.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-05T12:00:00Z",
            "data": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "789e4567-e89b-12d3-a456-426614174000",
                "title": "Test task",
                "priority": "high",
                "tags": [],
                "has_recurrence": True,
                "recurrence_pattern": "yearly",  # Invalid pattern (not daily/weekly/monthly)
                "created_at": "2026-01-05T12:00:00Z"
            }
        }

        # Should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            TaskCreatedEvent(**event_data)

        assert "recurrence_pattern" in str(exc_info.value)

    def test_task_created_event_json_serialization(self):
        """Test that event can be serialized to JSON."""
        from schemas.event_schemas import TaskCreatedEvent

        event_data = {
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

        event = TaskCreatedEvent(**event_data)
        json_str = event.model_dump_json()

        # Should produce valid JSON string
        assert isinstance(json_str, str)
        assert "task.created.v1" in json_str
        assert "Buy groceries" in json_str
