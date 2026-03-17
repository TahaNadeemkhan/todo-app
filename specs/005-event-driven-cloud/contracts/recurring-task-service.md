# Recurring Task Service Contract

**Service**: Recurring Task Service (Python FastAPI + Dapr)
**App ID**: `recurring-task-service` (Dapr)
**Purpose**: Consume task completion events and create next task occurrence for recurring tasks

## Architecture

```
┌──────────────────┐
│ Backend API      │
│                  │
│ User completes   │
│ recurring task   │
└────────┬─────────┘
         │
         │ publishes
         │
┌────────▼──────────────────┐
│ Kafka Topic: task-events  │
│                           │
│ Event: task.completed.v1  │
└────────┬──────────────────┘
         │
         │ consumes (Dapr Pub/Sub)
         │
┌────────▼───────────────────────────┐
│ Recurring Task Service             │
│                                    │
│ 1. Validate event schema           │
│ 2. Check has_recurrence=true       │
│ 3. Load recurrence pattern         │
│ 4. Calculate next due date         │
│ 5. Create new task (API call)      │
│ 6. Update next_due_at              │
└────────┬───────────────────────────┘
         │
         │ publishes
         │
┌────────▼──────────────────┐
│ Kafka Topic: task-events  │
│                           │
│ Event: task.created.v1    │
└───────────────────────────┘
```

## Kafka Consumer

### Subscribed Topic: `task-events`

**Consumer Group ID**: `recurring-task-service`

**Event Consumed**: `task.completed.v1`

**Event Schema** (see data-model.md):
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

**Filtering Logic**:
- Only process events where `data.has_recurrence === true`
- If `data.has_recurrence === false`, acknowledge and skip

**Processing Logic**:
1. Validate event schema (JSON Schema validation)
2. Check idempotency: Query event log table for `event_id`
3. If duplicate event (already processed), acknowledge and skip
4. Load full task details from database:
   - Query: `SELECT * FROM tasks WHERE id = data.task_id`
   - Load recurrence: `SELECT * FROM task_recurrences WHERE task_id = data.task_id`
5. Verify recurrence is still active:
   - If `recurrence.active === false`, acknowledge and skip (user stopped recurrence)
6. Calculate next due date based on pattern:
   - **DAILY**: `next_due = completed_at + (interval * 1 day)`
   - **WEEKLY**: `next_due = next occurrence of days_of_week after completed_at`
   - **MONTHLY**: `next_due = day_of_month in next month after completed_at`
7. Create new task via Backend API:
   - Invoke `POST /api/v1/users/{user_id}/tasks` via Dapr Service Invocation
   - Copy title, description, priority, tags, recurrence from original task
   - Set `due_at = next_due`
   - Copy reminders (remind_before relative to new due_at)
8. Update recurrence record:
   - `UPDATE task_recurrences SET next_due_at = next_due WHERE id = recurrence.id`
9. Acknowledge Kafka message

**Idempotency Strategy**:
- Maintain `event_log` table with columns: `event_id`, `event_type`, `processed_at`
- Before processing: `SELECT COUNT(*) FROM event_log WHERE event_id = ?`
- If count > 0, skip processing
- After successful processing: `INSERT INTO event_log (event_id, event_type, processed_at) VALUES (?, ?, NOW())`

**Error Handling**:
- If Backend API call fails (500, 503), DO NOT acknowledge Kafka message → retry
- If API returns 400 (validation error), log error and acknowledge (dead letter queue)
- If database query fails, DO NOT acknowledge → retry
- Max retries: 3 with exponential backoff (1s, 2s, 4s)

**Metrics**:
- `recurring_tasks_created_total{pattern="daily|weekly|monthly"}`
- `recurring_tasks_processing_duration_seconds{pattern="daily|weekly|monthly"}`
- `kafka_consumer_lag{topic="task-events", group="recurring-task-service"}`
- `backend_api_calls_total{method="POST", endpoint="/tasks", status="2xx|4xx|5xx"}`

---

## Recurrence Calculation Logic

### Daily Recurrence

**Algorithm**:
```python
from datetime import datetime, timedelta

def calculate_next_daily(completed_at: datetime, interval: int) -> datetime:
    """Calculate next due date for daily recurrence."""
    return completed_at + timedelta(days=interval)
```

**Examples**:
- Task completed: `2026-01-04T15:00:00Z`, interval: 1 → Next: `2026-01-05T15:00:00Z`
- Task completed: `2026-01-04T15:00:00Z`, interval: 3 → Next: `2026-01-07T15:00:00Z`

---

### Weekly Recurrence

**Algorithm**:
```python
from datetime import datetime, timedelta

def calculate_next_weekly(
    completed_at: datetime,
    interval: int,
    days_of_week: list[int]  # 0=Mon, 6=Sun
) -> datetime:
    """Calculate next due date for weekly recurrence."""
    # Sort days_of_week ascending
    days_sorted = sorted(days_of_week)

    # Current day of week (0=Mon, 6=Sun)
    current_weekday = completed_at.weekday()

    # Find next occurrence in this week
    for day in days_sorted:
        if day > current_weekday:
            days_ahead = day - current_weekday
            return completed_at + timedelta(days=days_ahead)

    # No occurrence left in this week, go to first day of next week(s)
    first_day = days_sorted[0]
    days_ahead = (7 - current_weekday + first_day) + (interval - 1) * 7
    return completed_at + timedelta(days=days_ahead)
```

**Examples**:
- Task completed: `2026-01-04T15:00:00Z` (Saturday), days_of_week: `[0, 3]` (Mon, Thu), interval: 1
  - Current weekday: 5 (Sat)
  - Next occurrence: Monday (0) → 2 days ahead
  - Result: `2026-01-06T15:00:00Z`

- Task completed: `2026-01-04T15:00:00Z` (Saturday), days_of_week: `[2, 4]` (Wed, Fri), interval: 1
  - Current weekday: 5 (Sat)
  - Next occurrence: Wednesday (2) → 4 days ahead
  - Result: `2026-01-08T15:00:00Z`

---

### Monthly Recurrence

**Algorithm**:
```python
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_next_monthly(
    completed_at: datetime,
    interval: int,
    day_of_month: int  # 1-31
) -> datetime:
    """Calculate next due date for monthly recurrence."""
    # Move to next month(s)
    next_month = completed_at + relativedelta(months=interval)

    # Set day of month (handle edge case: Feb 30 → Feb 28/29)
    try:
        next_due = next_month.replace(day=day_of_month)
    except ValueError:
        # Day doesn't exist in that month (e.g., Feb 30)
        # Use last day of month instead
        next_due = (next_month + relativedelta(months=1)).replace(day=1) - timedelta(days=1)

    # If next_due is before completed_at (edge case), add another month
    if next_due <= completed_at:
        next_due = next_due + relativedelta(months=1)

    # Preserve time from completed_at
    return next_due.replace(hour=completed_at.hour, minute=completed_at.minute, second=completed_at.second)
```

**Examples**:
- Task completed: `2026-01-04T15:00:00Z`, day_of_month: 15, interval: 1
  - Next: `2026-02-15T15:00:00Z`

- Task completed: `2026-01-31T15:00:00Z`, day_of_month: 31, interval: 1
  - Next month: February (28 days in 2026)
  - day_of_month: 31 doesn't exist in Feb → use Feb 28
  - Result: `2026-02-28T15:00:00Z`

---

## Dapr Service Invocation (Backend API)

### Invoke Task Creation

**Method**: `POST`
**App ID**: `backend-api`
**Endpoint**: `/api/v1/users/{user_id}/tasks`

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "priority": "high",
  "tags": ["shopping", "urgent"],
  "due_at": "2026-01-08T18:00:00Z",
  "recurrence": {
    "pattern": "weekly",
    "interval": 1,
    "days_of_week": [0, 3, 5]
  },
  "reminders": [
    {
      "remind_before": "PT1H",
      "channels": ["email", "push"]
    }
  ]
}
```

**Python Code Example**:
```python
from dapr.clients import DaprClient

with DaprClient() as client:
    response = client.invoke_method(
        app_id="backend-api",
        method_name=f"/api/v1/users/{user_id}/tasks",
        http_verb="POST",
        data=json.dumps(task_data),
        headers={"Content-Type": "application/json"}
    )
```

**Success Response** (201 Created):
- New task created with same recurrence pattern
- Response body contains new task ID

**Error Responses**:
- `400 Bad Request`: Validation error (log and skip event)
- `500 Internal Server Error`: Backend API error (retry)
- `503 Service Unavailable`: Backend API down (retry)

---

## Health Check

### GET `/health`

**Purpose**: Kubernetes liveness/readiness probe

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T12:00:00Z",
  "version": "1.0.0",
  "dependencies": {
    "kafka": "healthy",
    "database": "healthy",
    "backend_api": "healthy"
  }
}
```

**Health Checks**:
- **Kafka**: Check Kafka connection, consumer lag < 1000 messages
- **Database**: Execute `SELECT 1` query
- **Backend API**: Invoke `GET /health` via Dapr Service Invocation

---

## Metrics Endpoint (Prometheus)

### GET `/metrics`

**Metrics Exposed**:
```
# Recurring task creation
recurring_tasks_created_total{pattern="daily"} 10
recurring_tasks_created_total{pattern="weekly"} 20
recurring_tasks_created_total{pattern="monthly"} 5

# Processing duration
recurring_tasks_processing_duration_seconds{pattern="daily", quantile="0.5"} 0.1
recurring_tasks_processing_duration_seconds{pattern="daily", quantile="0.95"} 0.3

# Kafka consumer lag
kafka_consumer_lag{topic="task-events", group="recurring-task-service"} 5

# Backend API calls
backend_api_calls_total{method="POST", endpoint="/tasks", status="201"} 35
backend_api_calls_total{method="POST", endpoint="/tasks", status="500"} 2

# Errors
recurrence_calculation_errors_total{pattern="daily"} 0
recurrence_calculation_errors_total{pattern="monthly"} 1
```

---

## Dapr Configuration

### Pub/Sub Component

**Component Name**: `kafka-pubsub`

**Subscription** (`recurring-task-service.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  topic: task-events
  route: /events/task-completed
  pubsubname: kafka-pubsub
```

---

## Deployment

### Container Image
- **Base Image**: `python:3.13-slim`
- **Build**: Multi-stage Dockerfile
- **Registry**: `ghcr.io/your-org/recurring-task-service:latest`

### Kubernetes Deployment

**Resource Limits**:
- CPU: Request 50m, Limit 200m
- Memory: Request 64Mi, Limit 256Mi

**Replicas**: 1 (single consumer group, no need for multiple replicas initially)

**Environment Variables**:
- `DAPR_ENABLED`: `true`
- `DAPR_HTTP_PORT`: `3500`
- `DAPR_GRPC_PORT`: `50001`
- `LOG_LEVEL`: `info`

**Probes**:
- Liveness: `GET /health` (initialDelaySeconds: 30, periodSeconds: 10)
- Readiness: `GET /health` (initialDelaySeconds: 10, periodSeconds: 5)

---

## Testing

### Unit Tests
- Mock Kafka consumer/producer
- Mock Dapr Service Invocation client
- Test recurrence calculation algorithms:
  - `test_calculate_next_daily()`
  - `test_calculate_next_weekly()`
  - `test_calculate_next_monthly()`
  - `test_monthly_edge_case_feb_30()`
- Test idempotency logic

### Integration Tests
- Use `testcontainers-python` for Kafka and PostgreSQL
- Send test `task.completed.v1` event → assert new task created
- Test duplicate event handling (idempotency)

### Contract Tests
- Validate `task.completed.v1` event schema with JSON Schema
- Validate Backend API request/response schemas

### E2E Tests
- Create recurring task → complete it → assert next occurrence created
- Verify next_due_at is correctly calculated
