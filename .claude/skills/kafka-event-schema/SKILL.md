---
name: kafka-event-schema
description: Generate type-safe Kafka event schemas with Python Pydantic models for event-driven architectures. Use for tasks, reminders, and notification event definitions.
---

# Kafka Event Schema Generator

## Overview

This skill generates production-ready Kafka event schemas using Python Pydantic models for event-driven microservices architecture. It provides type-safe event definitions, validation, and serialization for Phase 5 event streaming.

## When to Use This Skill

- Building event-driven microservices with Kafka/Redpanda
- Defining event schemas for task operations, reminders, or notifications
- Creating type-safe producer/consumer contracts
- Implementing event sourcing or CQRS patterns
- Validating event payloads across service boundaries

## Core Components Generated

### 1. Event Type Enums
- String-based enums for event types
- Consistent naming convention (e.g., `task.created`, `task.updated`)
- Type safety for event routing

### 2. Event Payload Models
- Pydantic models with field validation
- Support for optional fields and defaults
- Type hints for UUIDs, datetimes, and custom types
- Field constraints (min/max length, patterns)

### 3. Event Wrapper with Metadata
- Standard event envelope structure
- Correlation IDs for distributed tracing
- Timestamps in UTC timezone-aware format
- Versioning support for schema evolution

### 4. Helper Functions
- JSON serialization/deserialization
- Event validation
- Integration with Dapr Pub/Sub

## Usage

### Generate Event Schema for Task Operations

```bash
/kafka-event-schema \
  --domain=tasks \
  --events=created,updated,completed,deleted \
  --output=backend/src/events/task_events.py
```

### Generate Reminder Event Schema

```bash
/kafka-event-schema \
  --domain=reminders \
  --events=scheduled,sent,failed \
  --output=backend/src/events/reminder_events.py
```

### Generate Notification Event Schema

```bash
/kafka-event-schema \
  --domain=notifications \
  --events=delivered,failed,bounced \
  --output=backend/src/events/notification_events.py
```

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `--domain` | Business domain name | tasks, reminders, notifications |
| `--events` | Comma-separated event types | created,updated,deleted |
| `--output` | Output file path | src/events/task_events.py |
| `--metadata` | Include metadata fields | true (default) |
| `--validation` | Add strict validation | true (default) |
| `--versioning` | Add schema version | true (default) |

## Event Schema Best Practices

### 1. Immutability
- Events are immutable facts that have occurred
- Never modify published events
- Use new event types for schema changes

### 2. Versioning Strategy
- Include schema version in event type (`task.created.v1`)
- New fields must be optional for backward compatibility
- Use semantic versioning for major changes

### 3. Timestamp Standards
- Always use UTC timezone-aware datetimes
- Store as ISO 8601 strings in events
- Use `datetime.utcnow()` for consistency

### 4. ID Standards
- Use UUIDs for event_id and entity IDs
- Generate event_id with `uuid4()`
- Use deterministic UUIDs for idempotency

### 5. Metadata Standards
- Include correlation_id for distributed tracing
- Add causation_id to link related events
- Store user_id for audit trails

## Integration Patterns

### Publishing Events via Dapr

Events integrate with Dapr Pub/Sub to abstract Kafka complexity:

```python
import httpx

async def publish_task_event(event: TaskEvent):
    """Publish event via Dapr Pub/Sub"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
            json=event.model_dump(mode="json")
        )
```

### Consuming Events in Microservices

Microservices subscribe to topics and deserialize events:

```python
from events.task_events import TaskEvent

@app.post("/events/task-events")
async def handle_task_event(request: Request):
    data = await request.json()
    event = TaskEvent.model_validate(data)

    if event.event_type == TaskEventType.COMPLETED:
        # Handle recurring task spawning
        await spawn_next_occurrence(event)
```

## Phase 5 Event Schemas

### Task Events
- `task.created` - New task added by user
- `task.updated` - Task modified (title, description, priority, tags)
- `task.completed` - Task marked complete (triggers recurring logic)
- `task.deleted` - Task removed from system

### Reminder Events
- `reminder.scheduled` - Reminder scheduled for future time
- `reminder.due` - Reminder time reached, trigger notification
- `reminder.sent` - Notification delivered successfully
- `reminder.failed` - Notification delivery failed

### Recurring Task Events
- `recurring.triggered` - Recurring pattern matched on completion
- `recurring.spawned` - New task occurrence created from pattern

## Validation Examples

The generated schemas provide runtime validation:

```python
# ✅ Valid event
event = TaskEvent(
    event_type=TaskEventType.CREATED,
    payload=TaskCreatedPayload(
        task_id=uuid4(),
        user_id=uuid4(),
        title="Buy groceries",
        priority="high"
    )
)

# ❌ Invalid event (raises ValidationError)
event = TaskEvent(
    event_type=TaskEventType.CREATED,
    payload=TaskCreatedPayload(
        task_id="not-a-uuid",  # Type error
        title="",  # Min length violation
    )
)
```

## Testing Generated Schemas

```python
import pytest
from events.task_events import TaskEvent, TaskEventType

def test_event_serialization():
    event = TaskEvent(...)
    json_str = event.model_dump_json()
    deserialized = TaskEvent.model_validate_json(json_str)
    assert deserialized == event
```

For complete code examples, see [examples.md](examples.md).

## Related Skills

- **dapr-component-generator**: Generate Dapr Pub/Sub components for event streaming
- **microservice-scaffold**: Scaffold event consumer microservices
- **fastapi-design**: Create event webhook endpoints

## Tags

kafka, events, schema, pydantic, validation, event-driven, messaging, pub-sub, dapr, microservices
