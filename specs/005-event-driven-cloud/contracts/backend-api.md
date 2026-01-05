# Backend API Contract

**Service**: Backend API (FastAPI)
**Base URL**: `/api/v1`
**Authentication**: JWT Bearer Token (required for all endpoints except health check)

## Health Check

### GET `/health`

**Purpose**: Kubernetes liveness/readiness probe

**Authentication**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T12:00:00Z",
  "version": "5.0.0",
  "dependencies": {
    "database": "healthy",
    "kafka": "healthy",
    "dapr": "healthy"
  }
}
```

---

## Task Management (Extended from Phase 2)

### GET `/api/v1/users/{user_id}/tasks`

**Purpose**: List user's tasks with filtering, sorting, and search

**Authentication**: Required (JWT)

**Authorization**: `user_id` must match JWT claims `sub` field

**Query Parameters**:
- `status` (optional): `pending` | `completed`
- `priority` (optional): `high` | `medium` | `low`
- `tags` (optional): Comma-separated tag list (e.g., `work,urgent`)
- `due_before` (optional): ISO 8601 datetime (e.g., `2026-01-10T00:00:00Z`)
- `due_after` (optional): ISO 8601 datetime
- `search` (optional): Full-text search query (searches title + description)
- `sort_by` (optional): `due_date` | `priority` | `created_at` | `title` (default: `created_at`)
- `sort_order` (optional): `asc` | `desc` (default: `desc`)
- `limit` (optional): Max results (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "789e4567-e89b-12d3-a456-426614174000",
      "title": "Buy groceries",
      "description": "Milk, bread, eggs",
      "status": "pending",
      "priority": "high",
      "tags": ["shopping", "urgent"],
      "due_at": "2026-01-05T18:00:00Z",
      "has_recurrence": true,
      "recurrence": {
        "pattern": "weekly",
        "interval": 1,
        "days_of_week": [0, 3, 5],
        "next_due_at": "2026-01-08T18:00:00Z"
      },
      "created_at": "2026-01-04T12:00:00Z",
      "updated_at": "2026-01-04T12:00:00Z",
      "completed_at": null
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: `user_id` does not match JWT claims
- `400 Bad Request`: Invalid query parameters

---

### POST `/api/v1/users/{user_id}/tasks`

**Purpose**: Create a new task (with optional recurrence and reminders)

**Authentication**: Required (JWT)

**Authorization**: `user_id` must match JWT claims `sub` field

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "priority": "high",
  "tags": ["shopping", "urgent"],
  "due_at": "2026-01-05T18:00:00Z",
  "recurrence": {
    "pattern": "weekly",
    "interval": 1,
    "days_of_week": [0, 3, 5]
  },
  "reminders": [
    {
      "remind_before": "PT1H",
      "channels": ["email", "push"]
    },
    {
      "remind_before": "P1D",
      "channels": ["email"]
    }
  ]
}
```

**Validation Rules**:
- `title`: Required, 1-500 characters
- `description`: Optional, max 2000 characters
- `priority`: Optional, one of `high` | `medium` | `low` (default: `medium`)
- `tags`: Optional, array of strings (max 10 tags, each max 50 chars)
- `due_at`: Optional, must be future datetime
- `recurrence`: Optional object (see recurrence validation below)
- `reminders`: Optional array (max 5 reminders, requires `due_at`)

**Recurrence Validation**:
- `pattern`: Required if `recurrence` present, one of `daily` | `weekly` | `monthly`
- `interval`: Optional, >= 1 (default: 1)
- `days_of_week`: Required if `pattern=weekly`, array of 0-6 (Mon=0, Sun=6)
- `day_of_month`: Required if `pattern=monthly`, 1-31

**Reminder Validation**:
- `remind_before`: Required, ISO 8601 duration (e.g., `PT1H`, `P1D`, `P1W`)
- `channels`: Required, array containing `email` and/or `push`

**Response** (201 Created):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "789e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "status": "pending",
  "priority": "high",
  "tags": ["shopping", "urgent"],
  "due_at": "2026-01-05T18:00:00Z",
  "has_recurrence": true,
  "recurrence": {
    "id": "rec-uuid",
    "pattern": "weekly",
    "interval": 1,
    "days_of_week": [0, 3, 5],
    "next_due_at": "2026-01-08T18:00:00Z",
    "active": true
  },
  "reminders": [
    {
      "id": 1,
      "remind_before": "PT1H",
      "channels": ["email", "push"],
      "sent_at": null
    },
    {
      "id": 2,
      "remind_before": "P1D",
      "channels": ["email"],
      "sent_at": null
    }
  ],
  "created_at": "2026-01-04T12:00:00Z",
  "updated_at": "2026-01-04T12:00:00Z",
  "completed_at": null
}
```

**Side Effects**:
- Publishes `task.created.v1` event to `task-events` Kafka topic

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: `user_id` does not match JWT claims
- `400 Bad Request`: Validation errors
- `422 Unprocessable Entity`: Invalid recurrence configuration

---

### PATCH `/api/v1/users/{user_id}/tasks/{task_id}`

**Purpose**: Update task fields (including priority, tags, due date, recurrence)

**Authentication**: Required (JWT)

**Authorization**: `user_id` must match JWT claims; task must belong to user

**Request Body** (partial update):
```json
{
  "title": "Buy groceries and fruits",
  "priority": "medium",
  "tags": ["shopping"],
  "due_at": "2026-01-06T18:00:00Z"
}
```

**Response** (200 OK): Updated task object (same structure as POST response)

**Side Effects**:
- Publishes `task.updated.v1` event to `task-events` Kafka topic

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Task does not belong to user
- `404 Not Found`: Task ID not found
- `400 Bad Request`: Validation errors

---

### PATCH `/api/v1/users/{user_id}/tasks/{task_id}/complete`

**Purpose**: Mark task as completed

**Authentication**: Required (JWT)

**Authorization**: `user_id` must match JWT claims; task must belong to user

**Request Body**: (empty)

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "completed_at": "2026-01-05T15:00:00Z"
}
```

**Side Effects**:
- Sets `status=completed` and `completed_at=now()`
- Publishes `task.completed.v1` event to `task-events` Kafka topic
- If task has active recurrence, Recurring Task Service will create next occurrence

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Task does not belong to user
- `404 Not Found`: Task ID not found
- `409 Conflict`: Task already completed

---

### DELETE `/api/v1/users/{user_id}/tasks/{task_id}`

**Purpose**: Delete a task (and all related data: recurrence, reminders)

**Authentication**: Required (JWT)

**Authorization**: `user_id` must match JWT claims; task must belong to user

**Response** (204 No Content): (empty body)

**Side Effects**:
- Deletes task and cascades to `task_recurrences`, `task_reminders`
- Publishes `task.deleted.v1` event to `task-events` Kafka topic

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Task does not belong to user
- `404 Not Found`: Task ID not found

---

### PATCH `/api/v1/users/{user_id}/tasks/{task_id}/recurrence/stop`

**Purpose**: Stop future recurrence (but keep existing task)

**Authentication**: Required (JWT)

**Authorization**: `user_id` must match JWT claims; task must belong to user

**Request Body**: (empty)

**Response** (200 OK):
```json
{
  "id": "rec-uuid",
  "active": false
}
```

**Side Effects**:
- Sets `active=false` on TaskRecurrence record
- No new tasks will be created on completion

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Task does not belong to user
- `404 Not Found`: Task ID not found or task has no recurrence

---

## Notification Management

### GET `/api/v1/users/{user_id}/notifications`

**Purpose**: List user's notification history

**Authentication**: Required (JWT)

**Authorization**: `user_id` must match JWT claims

**Query Parameters**:
- `status` (optional): `pending` | `sent` | `failed`
- `channel` (optional): `email` | `push`
- `limit` (optional): Max results (default: 50, max: 500)
- `offset` (optional): Pagination offset (default: 0)

**Response** (200 OK):
```json
{
  "notifications": [
    {
      "id": 101,
      "user_id": "789e4567-e89b-12d3-a456-426614174000",
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "channel": "email",
      "status": "sent",
      "message": "Reminder: Buy groceries is due in 1 hour",
      "sent_at": "2026-01-05T17:00:05Z",
      "error": null,
      "created_at": "2026-01-05T17:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: `user_id` does not match JWT claims

---

## Metrics Endpoint (Prometheus)

### GET `/metrics`

**Purpose**: Expose Prometheus metrics

**Authentication**: None (internal Kubernetes endpoint)

**Response** (200 OK, Content-Type: text/plain):
```
# HELP tasks_created_total Total number of tasks created
# TYPE tasks_created_total counter
tasks_created_total 42

# HELP tasks_completed_total Total number of tasks completed
# TYPE tasks_completed_total counter
tasks_completed_total 30

# HELP http_requests_total Total HTTP requests by method and status
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 1000
http_requests_total{method="POST",status="201"} 42

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 950
http_request_duration_seconds_bucket{le="0.5"} 990
http_request_duration_seconds_bucket{le="1.0"} 1000

# HELP kafka_messages_published_total Messages published to Kafka by topic
# TYPE kafka_messages_published_total counter
kafka_messages_published_total{topic="task-events",event_type="task.created.v1"} 42
kafka_messages_published_total{topic="task-events",event_type="task.completed.v1"} 30

# HELP database_query_duration_seconds Database query latency
# TYPE database_query_duration_seconds histogram
database_query_duration_seconds_bucket{operation="select",le="0.01"} 900
database_query_duration_seconds_bucket{operation="select",le="0.1"} 990
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title must be between 1 and 500 characters",
    "details": {
      "field": "title",
      "value": ""
    },
    "timestamp": "2026-01-04T12:00:00Z"
  }
}
```

**Error Codes**:
- `AUTHENTICATION_REQUIRED`: 401 - Missing JWT
- `INVALID_TOKEN`: 401 - JWT signature invalid or expired
- `FORBIDDEN`: 403 - User does not own resource
- `NOT_FOUND`: 404 - Resource does not exist
- `VALIDATION_ERROR`: 400 - Input validation failed
- `CONFLICT`: 409 - Operation conflicts with current state
- `INTERNAL_ERROR`: 500 - Unexpected server error

---

## Rate Limiting

- **Unauthenticated requests**: 100 requests/minute per IP
- **Authenticated requests**: 1000 requests/minute per user
- **Response Headers**:
  - `X-RateLimit-Limit`: Total allowed requests
  - `X-RateLimit-Remaining`: Remaining requests in window
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

**Error Response** (429 Too Many Requests):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 30 seconds.",
    "timestamp": "2026-01-04T12:00:00Z"
  }
}
```

---

## CORS Configuration

- **Allowed Origins**: Frontend domain (e.g., `https://todo-app.example.com`)
- **Allowed Methods**: `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS`
- **Allowed Headers**: `Content-Type`, `Authorization`
- **Exposed Headers**: `X-RateLimit-*`
- **Credentials**: Allowed (cookies, authorization headers)

---

## Backward Compatibility

Phase 5 extends Phase 2/3 APIs without breaking changes:

- Existing `/api/v1/users/{user_id}/tasks` endpoints remain compatible
- New fields (`priority`, `tags`, `due_at`, `recurrence`, `reminders`) are optional
- Clients not using Phase 5 features can ignore new fields in responses
- Old clients can continue using Phase 2/3 endpoints without modification
