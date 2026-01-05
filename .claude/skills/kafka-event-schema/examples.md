# Kafka Event Schema - Code Examples

Complete, reusable code examples for generating and using Kafka event schemas with Pydantic.

## Example 1: Task Event Schema

### Generated Event Type Enum

```python
from enum import Enum

class TaskEventType(str, Enum):
    CREATED = "task.created"
    UPDATED = "task.updated"
    COMPLETED = "task.completed"
    DELETED = "task.deleted"
```

### Generated Event Payload Models

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class TaskCreatedPayload(BaseModel):
    task_id: UUID
    user_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: str = Field(default="medium")
    due_date: datetime | None = None
    tags: list[str] = Field(default_factory=list)

class TaskUpdatedPayload(BaseModel):
    task_id: UUID
    user_id: UUID
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
    tags: list[str] | None = None
    updated_fields: list[str]  # List of fields that changed

class TaskCompletedPayload(BaseModel):
    task_id: UUID
    user_id: UUID
    completed_at: datetime
    has_recurrence: bool = False
    recurrence_pattern: str | None = None

class TaskDeletedPayload(BaseModel):
    task_id: UUID
    user_id: UUID
    deleted_at: datetime
    reason: str | None = None
```

### Generated Event Wrapper with Metadata

```python
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4, UUID
from datetime import datetime, timezone

class TaskEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: TaskEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: UUID | None = None
    causation_id: UUID | None = None
    payload: TaskCreatedPayload | TaskUpdatedPayload | TaskCompletedPayload | TaskDeletedPayload

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_id": "123e4567-e89b-12d3-a456-426614174000",
                "event_type": "task.created",
                "timestamp": "2026-01-15T10:30:00Z",
                "correlation_id": "abc-def-ghi",
                "causation_id": "xyz-123-456",
                "payload": {
                    "task_id": "task-uuid",
                    "user_id": "user-uuid",
                    "title": "Buy groceries",
                    "priority": "high"
                }
            }
        }
    )
```

### Helper Functions

```python
def serialize_event(event: TaskEvent) -> str:
    """Serialize event to JSON for Kafka publishing"""
    return event.model_dump_json()

def deserialize_event(json_str: str) -> TaskEvent:
    """Deserialize Kafka message to TaskEvent"""
    return TaskEvent.model_validate_json(json_str)

def create_task_created_event(
    task_id: UUID,
    user_id: UUID,
    title: str,
    priority: str = "medium",
    due_date: datetime | None = None,
    tags: list[str] = None
) -> TaskEvent:
    """Helper to create task.created event"""
    return TaskEvent(
        event_type=TaskEventType.CREATED,
        payload=TaskCreatedPayload(
            task_id=task_id,
            user_id=user_id,
            title=title,
            priority=priority,
            due_date=due_date,
            tags=tags or []
        )
    )
```

## Example 2: Reminder Event Schema

```python
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class ReminderEventType(str, Enum):
    SCHEDULED = "reminder.scheduled"
    DUE = "reminder.due"
    SENT = "reminder.sent"
    FAILED = "reminder.failed"

class ReminderScheduledPayload(BaseModel):
    reminder_id: UUID
    task_id: UUID
    user_id: UUID
    scheduled_for: datetime
    notification_channel: str = Field(default="email")  # email, push, sms
    message: str

class ReminderDuePayload(BaseModel):
    reminder_id: UUID
    task_id: UUID
    user_id: UUID
    title: str
    due_at: datetime
    notification_channel: str

class ReminderSentPayload(BaseModel):
    reminder_id: UUID
    task_id: UUID
    user_id: UUID
    sent_at: datetime
    notification_channel: str
    delivery_status: str

class ReminderFailedPayload(BaseModel):
    reminder_id: UUID
    task_id: UUID
    user_id: UUID
    failed_at: datetime
    notification_channel: str
    error_message: str
    retry_count: int

class ReminderEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: ReminderEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: (
        ReminderScheduledPayload |
        ReminderDuePayload |
        ReminderSentPayload |
        ReminderFailedPayload
    )
```

## Example 3: Publishing Events via Dapr

```python
import httpx
from events.task_events import TaskEvent, create_task_created_event
from uuid import uuid4

async def publish_task_created(
    task_id: UUID,
    user_id: UUID,
    title: str,
    priority: str = "medium"
):
    """Publish task.created event via Dapr Pub/Sub"""
    event = create_task_created_event(
        task_id=task_id,
        user_id=user_id,
        title=title,
        priority=priority
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
            json=event.model_dump(mode="json")
        )
        response.raise_for_status()

# Usage
await publish_task_created(
    task_id=uuid4(),
    user_id=uuid4(),
    title="Buy groceries",
    priority="high"
)
```

## Example 4: Consuming Events in Microservice

```python
from fastapi import FastAPI, Request
from events.task_events import TaskEvent, TaskEventType

app = FastAPI()

@app.post("/dapr/subscribe")
async def subscribe():
    """Tell Dapr which topics to subscribe to"""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        }
    ]

@app.post("/events/task-events")
async def handle_task_event(request: Request):
    """Dapr calls this endpoint when task event arrives"""
    data = await request.json()
    event_data = data.get("data", {})

    # Deserialize and validate event
    event = TaskEvent.model_validate(event_data)

    # Route based on event type
    if event.event_type == TaskEventType.CREATED:
        await handle_task_created(event)
    elif event.event_type == TaskEventType.COMPLETED:
        await handle_task_completed(event)
    elif event.event_type == TaskEventType.DELETED:
        await handle_task_deleted(event)

    return {"success": True}

async def handle_task_created(event: TaskEvent):
    """Process task.created event"""
    payload = event.payload
    print(f"New task created: {payload.title} (Priority: {payload.priority})")

async def handle_task_completed(event: TaskEvent):
    """Process task.completed event - spawn recurring if needed"""
    payload = event.payload
    if payload.has_recurrence:
        # Spawn next occurrence
        await spawn_recurring_task(payload.task_id, payload.recurrence_pattern)

async def handle_task_deleted(event: TaskEvent):
    """Process task.deleted event"""
    payload = event.payload
    print(f"Task deleted: {payload.task_id}")
```

## Example 5: Testing Event Schemas

```python
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from events.task_events import (
    TaskEvent,
    TaskEventType,
    TaskCreatedPayload,
    create_task_created_event
)

def test_task_created_event_valid():
    """Test valid task.created event"""
    event = TaskEvent(
        event_type=TaskEventType.CREATED,
        payload=TaskCreatedPayload(
            task_id=uuid4(),
            user_id=uuid4(),
            title="Test task",
            priority="high",
            tags=["urgent", "important"]
        )
    )
    assert event.event_type == TaskEventType.CREATED
    assert event.payload.title == "Test task"
    assert event.payload.priority == "high"
    assert len(event.payload.tags) == 2

def test_task_event_serialization():
    """Test event serialization and deserialization"""
    original_event = create_task_created_event(
        task_id=uuid4(),
        user_id=uuid4(),
        title="Buy groceries",
        priority="medium"
    )

    # Serialize to JSON
    json_str = original_event.model_dump_json()

    # Deserialize back
    deserialized = TaskEvent.model_validate_json(json_str)

    # Verify fields match
    assert deserialized.event_type == original_event.event_type
    assert deserialized.payload.title == original_event.payload.title
    assert deserialized.payload.task_id == original_event.payload.task_id

def test_invalid_event_raises_validation_error():
    """Test that invalid events raise ValidationError"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        TaskEvent(
            event_type=TaskEventType.CREATED,
            payload=TaskCreatedPayload(
                task_id="not-a-uuid",  # Invalid: should be UUID
                user_id=uuid4(),
                title="",  # Invalid: min_length=1
            )
        )

def test_event_metadata_generation():
    """Test that event metadata is auto-generated"""
    event = create_task_created_event(
        task_id=uuid4(),
        user_id=uuid4(),
        title="Test"
    )

    # event_id should be auto-generated UUID
    assert event.event_id is not None

    # timestamp should be recent UTC time
    assert event.timestamp is not None
    now = datetime.now(timezone.utc)
    time_diff = (now - event.timestamp).total_seconds()
    assert time_diff < 5  # Generated within last 5 seconds
```

## Example 6: Event Schema with Versioning

```python
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID

class TaskEventTypeV2(str, Enum):
    """Version 2 of task events with schema evolution"""
    CREATED = "task.created.v2"
    UPDATED = "task.updated.v2"
    COMPLETED = "task.completed.v2"
    DELETED = "task.deleted.v2"

class TaskCreatedPayloadV2(BaseModel):
    """V2 adds optional attachments and subtasks"""
    task_id: UUID
    user_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: str = Field(default="medium")
    due_date: datetime | None = None
    tags: list[str] = Field(default_factory=list)

    # New fields in V2 (must be optional for compatibility)
    attachments: list[str] = Field(default_factory=list)
    subtasks: list[UUID] = Field(default_factory=list)
    estimated_duration_minutes: int | None = None

class TaskEventV2(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: TaskEventTypeV2
    schema_version: str = Field(default="2.0.0")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: TaskCreatedPayloadV2 | TaskUpdatedPayloadV2 | ...
```

## Example 7: Recurring Task Event Schema

```python
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class RecurringEventType(str, Enum):
    TRIGGERED = "recurring.triggered"
    SPAWNED = "recurring.spawned"

class RecurringTriggeredPayload(BaseModel):
    """Event when recurring task pattern is matched"""
    task_id: UUID  # The completed task
    user_id: UUID
    recurrence_pattern: str  # e.g., "daily", "weekly", "monthly"
    next_due_date: datetime
    original_task_data: dict  # Original task fields to copy

class RecurringSpawnedPayload(BaseModel):
    """Event when new occurrence is created"""
    new_task_id: UUID  # The newly created task
    original_task_id: UUID  # The completed task that triggered this
    user_id: UUID
    recurrence_pattern: str
    due_date: datetime
    occurrence_number: int  # 1st, 2nd, 3rd occurrence

class RecurringEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: RecurringEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: RecurringTriggeredPayload | RecurringSpawnedPayload
```

## Example 8: Integration with FastAPI Endpoint

```python
from fastapi import FastAPI, HTTPException
from events.task_events import TaskEvent, TaskEventType, create_task_created_event
import httpx

app = FastAPI()

@app.post("/api/v1/tasks")
async def create_task_api(task_data: dict):
    """Create task and publish event"""
    try:
        # 1. Save to database
        task = await save_task_to_database(task_data)

        # 2. Publish event
        event = create_task_created_event(
            task_id=task.id,
            user_id=task.user_id,
            title=task.title,
            priority=task.priority,
            due_date=task.due_date,
            tags=task.tags
        )

        # Publish via Dapr
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
                json=event.model_dump(mode="json")
            )

        return {"id": str(task.id), "title": task.title}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Example 9: Error Handling and Retries

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def publish_event_with_retry(event: TaskEvent):
    """Publish event with automatic retries"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(
            "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
            json=event.model_dump(mode="json")
        )
        response.raise_for_status()
        return response.json()

# Usage
try:
    await publish_event_with_retry(event)
except Exception as e:
    # Log failure and store in dead letter queue
    await log_publish_failure(event, str(e))
```

## Example 10: Batch Event Publishing

```python
async def publish_events_batch(events: list[TaskEvent]):
    """Publish multiple events efficiently"""
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post(
                "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
                json=event.model_dump(mode="json")
            )
            for event in events
        ]
        # Execute all publishes concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for failures
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Failed to publish event {i}: {response}")
```
