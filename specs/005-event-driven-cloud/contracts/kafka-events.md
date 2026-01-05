# Kafka Event Schemas and Topic Specifications

**Feature**: 005-event-driven-cloud
**Created**: 2026-01-04

## Overview

This document defines Kafka topic configurations and event schemas for Phase 5 event-driven architecture.

## Topic Configuration

### Topic: `task-events`

**Purpose**: All task lifecycle events (create, update, complete, delete)

**Configuration**:
- **Partitions**: 3 (allows parallel processing by up to 3 consumers)
- **Replication Factor**: 3 (for durability in production)
- **Retention**: 7 days (604800000 ms)
- **Cleanup Policy**: Delete (time-based retention)
- **Compression**: `snappy` (good balance of compression ratio and CPU)
- **Min In-Sync Replicas**: 2 (ensures durability)

**Partition Key**: `user_id` (ensures all events for a user go to same partition → ordering guaranteed per user)

**Producers**:
- Backend API (all CRUD operations)
- Recurring Task Service (task.created for next occurrence)

**Consumers**:
- Recurring Task Service (consumer group: `recurring-task-service`)
- Analytics Service (future - consumer group: `analytics-service`)

---

### Topic: `reminders`

**Purpose**: Reminder due events (trigger notifications)

**Configuration**:
- **Partitions**: 2
- **Replication Factor**: 3
- **Retention**: 3 days (259200000 ms)
- **Cleanup Policy**: Delete
- **Compression**: `snappy`
- **Min In-Sync Replicas**: 2

**Partition Key**: `user_id`

**Producers**:
- Backend API (Reminder Scheduler cron job)

**Consumers**:
- Notification Service (consumer group: `notification-service`)

---

### Topic: `notifications`

**Purpose**: Notification delivery status events (sent/failed)

**Configuration**:
- **Partitions**: 2
- **Replication Factor**: 3
- **Retention**: 7 days (604800000 ms)
- **Cleanup Policy**: Delete
- **Compression**: `snappy`
- **Min In-Sync Replicas**: 2

**Partition Key**: `user_id`

**Producers**:
- Notification Service (after sending email/push)

**Consumers**:
- Backend API (updates notification status - future)
- Analytics Service (future - consumer group: `analytics-service`)

---

## Event Schema Specifications

All events follow this envelope format:

```json
{
  "event_id": "uuid",               // Unique event identifier (for idempotency)
  "event_type": "string.v1",        // Event type with version
  "schema_version": "string",       // Schema version (e.g., "1.0")
  "timestamp": "ISO8601",           // Event creation time (UTC)
  "data": { ... }                   // Event-specific payload
}
```

---

## Event Type: `task.created.v1`

**Topic**: `task-events`

**Produced By**: Backend API, Recurring Task Service

**Consumed By**: Analytics Service (future)

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "schema_version", "timestamp", "data"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "task.created.v1"},
    "schema_version": {"type": "string", "const": "1.0"},
    "timestamp": {"type": "string", "format": "date-time"},
    "data": {
      "type": "object",
      "required": ["task_id", "user_id", "title", "priority", "tags", "created_at"],
      "properties": {
        "task_id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string", "format": "uuid"},
        "title": {"type": "string", "minLength": 1, "maxLength": 500},
        "description": {"type": "string", "maxLength": 2000},
        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
        "tags": {"type": "array", "items": {"type": "string"}},
        "due_at": {"type": "string", "format": "date-time"},
        "has_recurrence": {"type": "boolean"},
        "recurrence_pattern": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
        "recurrence_interval": {"type": "integer", "minimum": 1},
        "recurrence_days_of_week": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 6}},
        "recurrence_day_of_month": {"type": "integer", "minimum": 1, "maximum": 31},
        "created_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task.created.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-04T12:00:00Z",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": "high",
    "tags": ["shopping", "urgent"],
    "due_at": "2026-01-05T18:00:00Z",
    "has_recurrence": true,
    "recurrence_pattern": "weekly",
    "recurrence_interval": 1,
    "recurrence_days_of_week": [0, 3, 5],
    "created_at": "2026-01-04T12:00:00Z"
  }
}
```

---

## Event Type: `task.completed.v1`

**Topic**: `task-events`

**Produced By**: Backend API

**Consumed By**: Recurring Task Service

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "schema_version", "timestamp", "data"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "task.completed.v1"},
    "schema_version": {"type": "string", "const": "1.0"},
    "timestamp": {"type": "string", "format": "date-time"},
    "data": {
      "type": "object",
      "required": ["task_id", "user_id", "completed_at", "has_recurrence"],
      "properties": {
        "task_id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string", "format": "uuid"},
        "completed_at": {"type": "string", "format": "date-time"},
        "has_recurrence": {"type": "boolean"},
        "recurrence_pattern": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
        "recurrence_interval": {"type": "integer", "minimum": 1},
        "recurrence_days_of_week": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 6}},
        "recurrence_day_of_month": {"type": "integer", "minimum": 1, "maximum": 31}
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440001",
  "event_type": "task.completed.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-04T15:00:00Z",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "completed_at": "2026-01-04T15:00:00Z",
    "has_recurrence": true,
    "recurrence_pattern": "weekly",
    "recurrence_interval": 1,
    "recurrence_days_of_week": [0, 3, 5]
  }
}
```

---

## Event Type: `task.updated.v1`

**Topic**: `task-events`

**Produced By**: Backend API

**Consumed By**: Analytics Service (future)

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "schema_version", "timestamp", "data"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "task.updated.v1"},
    "schema_version": {"type": "string", "const": "1.0"},
    "timestamp": {"type": "string", "format": "date-time"},
    "data": {
      "type": "object",
      "required": ["task_id", "user_id", "changes", "updated_at"],
      "properties": {
        "task_id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string", "format": "uuid"},
        "changes": {
          "type": "object",
          "description": "Map of field_name -> {old: value, new: value}"
        },
        "updated_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440002",
  "event_type": "task.updated.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-04T14:00:00Z",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "changes": {
      "priority": {"old": "medium", "new": "high"},
      "tags": {"old": ["shopping"], "new": ["shopping", "urgent"]}
    },
    "updated_at": "2026-01-04T14:00:00Z"
  }
}
```

---

## Event Type: `task.deleted.v1`

**Topic**: `task-events`

**Produced By**: Backend API

**Consumed By**: Analytics Service (future)

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "schema_version", "timestamp", "data"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "task.deleted.v1"},
    "schema_version": {"type": "string", "const": "1.0"},
    "timestamp": {"type": "string", "format": "date-time"},
    "data": {
      "type": "object",
      "required": ["task_id", "user_id", "deleted_at"],
      "properties": {
        "task_id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string", "format": "uuid"},
        "deleted_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440003",
  "event_type": "task.deleted.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-04T16:00:00Z",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "deleted_at": "2026-01-04T16:00:00Z"
  }
}
```

---

## Event Type: `reminder.due.v1`

**Topic**: `reminders`

**Produced By**: Backend API (Reminder Scheduler)

**Consumed By**: Notification Service

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "schema_version", "timestamp", "data"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "reminder.due.v1"},
    "schema_version": {"type": "string", "const": "1.0"},
    "timestamp": {"type": "string", "format": "date-time"},
    "data": {
      "type": "object",
      "required": ["reminder_id", "task_id", "user_id", "task_title", "due_at", "remind_before", "channels"],
      "properties": {
        "reminder_id": {"type": "integer"},
        "task_id": {"type": "string", "format": "uuid"},
        "user_id": {"type": "string", "format": "uuid"},
        "task_title": {"type": "string"},
        "due_at": {"type": "string", "format": "date-time"},
        "remind_before": {"type": "string", "pattern": "^P.*"},
        "channels": {"type": "array", "items": {"type": "string", "enum": ["email", "push"]}}
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440004",
  "event_type": "reminder.due.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-05T17:00:00Z",
  "data": {
    "reminder_id": 42,
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "task_title": "Buy groceries",
    "due_at": "2026-01-05T18:00:00Z",
    "remind_before": "PT1H",
    "channels": ["email", "push"]
  }
}
```

---

## Event Type: `notification.sent.v1`

**Topic**: `notifications`

**Produced By**: Notification Service

**Consumed By**: Backend API (future), Analytics Service (future)

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "schema_version", "timestamp", "data"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "notification.sent.v1"},
    "schema_version": {"type": "string", "const": "1.0"},
    "timestamp": {"type": "string", "format": "date-time"},
    "data": {
      "type": "object",
      "required": ["notification_id", "user_id", "channel", "message", "sent_at"],
      "properties": {
        "notification_id": {"type": "integer"},
        "user_id": {"type": "string", "format": "uuid"},
        "task_id": {"type": "string", "format": "uuid"},
        "channel": {"type": "string", "enum": ["email", "push"]},
        "message": {"type": "string"},
        "sent_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440005",
  "event_type": "notification.sent.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-05T17:00:05Z",
  "data": {
    "notification_id": 101,
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "channel": "email",
    "message": "Reminder: Buy groceries is due in 1 hour",
    "sent_at": "2026-01-05T17:00:05Z"
  }
}
```

---

## Event Type: `notification.failed.v1`

**Topic**: `notifications`

**Produced By**: Notification Service

**Consumed By**: Backend API (future), Analytics Service (future)

**Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["event_id", "event_type", "schema_version", "timestamp", "data"],
  "properties": {
    "event_id": {"type": "string", "format": "uuid"},
    "event_type": {"type": "string", "const": "notification.failed.v1"},
    "schema_version": {"type": "string", "const": "1.0"},
    "timestamp": {"type": "string", "format": "date-time"},
    "data": {
      "type": "object",
      "required": ["notification_id", "user_id", "channel", "message", "error", "failed_at"],
      "properties": {
        "notification_id": {"type": "integer"},
        "user_id": {"type": "string", "format": "uuid"},
        "task_id": {"type": "string", "format": "uuid"},
        "channel": {"type": "string", "enum": ["email", "push"]},
        "message": {"type": "string"},
        "error": {"type": "string"},
        "failed_at": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

**Example**:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440006",
  "event_type": "notification.failed.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-05T17:00:10Z",
  "data": {
    "notification_id": 102,
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "channel": "push",
    "message": "Reminder: Buy groceries is due in 1 hour",
    "error": "FCM token expired",
    "failed_at": "2026-01-05T17:00:10Z"
  }
}
```

---

## Event Ordering Guarantees

- **Per-User Ordering**: All events for the same user_id go to the same partition → guaranteed ordering
- **Cross-User Ordering**: Not guaranteed (and not required)
- **Within-Service Ordering**: Recurring Task Service processes events for a user sequentially

---

## Idempotency Strategy

All consumers MUST implement idempotency to handle duplicate events:

1. **Event Log Table**: Store processed `event_id` values
   ```sql
   CREATE TABLE event_log (
     event_id UUID PRIMARY KEY,
     event_type VARCHAR(50) NOT NULL,
     processed_at TIMESTAMP NOT NULL
   );
   ```

2. **Before Processing**: Check if `event_id` exists in `event_log`
3. **After Processing**: Insert `event_id` into `event_log`
4. **Cleanup**: Periodically delete old entries (older than retention period)

---

## Schema Evolution

When updating event schemas:

1. **Backward Compatible Changes** (no version bump):
   - Adding optional fields
   - Adding new enum values (if consumers handle unknown values gracefully)

2. **Breaking Changes** (requires new version):
   - Removing fields
   - Changing field types
   - Renaming fields
   - Making optional fields required

**Example**: If we need to add `assignee_id` to `task.created`, we can add it as optional without bumping version. If we need to change `priority` from string to integer, we create `task.created.v2`.

---

## Testing Event Schemas

All services MUST validate event schemas using JSON Schema:

```python
import jsonschema

schema = {...}  # Load from file
event = {...}   # Received from Kafka

try:
    jsonschema.validate(instance=event, schema=schema)
except jsonschema.ValidationError as e:
    # Log error and reject event
    logger.error(f"Invalid event schema: {e}")
```
