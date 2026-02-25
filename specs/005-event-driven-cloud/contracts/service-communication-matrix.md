# Service Communication Matrix

**Feature**: 005-event-driven-cloud
**Created**: 2026-01-05

## Overview

This document provides a comprehensive matrix of all service-to-service communications in Phase 5, including HTTP/REST, Kafka events, and Dapr Service Invocation patterns.

---

## Communication Patterns

### Pattern 1: Frontend → Backend API (HTTP/REST)
- **Protocol**: HTTPS
- **Authentication**: JWT Bearer Token
- **See**: `backend-api.md` for complete REST API specification

### Pattern 2: Backend API → Kafka (Event Publishing)
- **Protocol**: Kafka via Dapr Pub/Sub
- **Topics**: `task-events`, `reminders`
- **See**: `kafka-events.md` for event schemas

### Pattern 3: Microservices → Kafka (Event Consumption)
- **Protocol**: Kafka via Dapr Pub/Sub
- **Services**: Notification Service, Recurring Task Service
- **See**: Service-specific contracts

### Pattern 4: Recurring Task Service → Backend API (Service Invocation)
- **Protocol**: Dapr Service Invocation (HTTP over mTLS)
- **Method**: POST `/api/v1/users/{user_id}/tasks`
- **See**: `recurring-task-service.md` section "Dapr Service Invocation"

---

## Service Communication Matrix

| Source Service | Target Service | Protocol | Purpose | Contract Reference |
|----------------|----------------|----------|---------|-------------------|
| **Frontend** | Backend API | HTTPS/REST | All user operations (CRUD tasks, notifications) | `backend-api.md` |
| **Backend API** | Kafka (`task-events`) | Dapr Pub/Sub | Publish task lifecycle events | `kafka-events.md` |
| **Backend API** | Kafka (`reminders`) | Dapr Pub/Sub | Publish reminder due events | `kafka-events.md` |
| **Backend API** | PostgreSQL | SQL | Persist tasks, users, reminders | `data-model.md` |
| **Notification Service** | Kafka (`reminders`) | Dapr Pub/Sub (consumer) | Consume reminder events | `notification-service.md` |
| **Notification Service** | SMTP Server | SMTP | Send email notifications | `notification-service.md` |
| **Notification Service** | Firebase FCM | HTTPS | Send push notifications | `notification-service.md` |
| **Notification Service** | Kafka (`notifications`) | Dapr Pub/Sub | Publish notification status events | `kafka-events.md` |
| **Notification Service** | PostgreSQL | SQL | Persist notification records | `data-model.md` |
| **Recurring Task Service** | Kafka (`task-events`) | Dapr Pub/Sub (consumer) | Consume task completion events | `recurring-task-service.md` |
| **Recurring Task Service** | Backend API | Dapr Service Invocation | Create next task occurrence | `recurring-task-service.md` |
| **Recurring Task Service** | PostgreSQL | SQL | Query task recurrence data | `data-model.md` |
| **All Services** | Dapr Sidecar | HTTP/gRPC | Access Dapr building blocks | `dapr-components.md` |
| **Prometheus** | All Services | HTTP | Scrape metrics from `/metrics` | Monitoring docs |

---

## Event Flow Diagrams

### Flow 1: User Creates Recurring Task

```
┌─────────┐     POST /tasks      ┌──────────────┐
│ Frontend├─────────────────────>│ Backend API  │
└─────────┘                      └──────┬───────┘
                                        │
                                        │ 1. Save to DB
                                        │ 2. Publish event
                                        ▼
                                 ┌──────────────────┐
                                 │ Kafka Topic:     │
                                 │ task-events      │
                                 │                  │
                                 │ task.created.v1  │
                                 └──────────────────┘
```

### Flow 2: Task Completion → Next Occurrence Creation

```
┌─────────┐  PATCH /complete   ┌──────────────┐
│ Frontend├───────────────────>│ Backend API  │
└─────────┘                    └──────┬───────┘
                                      │
                                      │ 1. Mark complete
                                      │ 2. Publish event
                                      ▼
                            ┌──────────────────────┐
                            │ Kafka Topic:         │
                            │ task-events          │
                            │                      │
                            │ task.completed.v1    │
                            └──────────┬───────────┘
                                       │
                                       │ consumes
                                       ▼
                            ┌───────────────────────────┐
                            │ Recurring Task Service    │
                            │                           │
                            │ 1. Check has_recurrence   │
                            │ 2. Calculate next due     │
                            │ 3. Call Backend API       │
                            └──────────┬────────────────┘
                                       │
                                       │ Dapr Service Invocation
                                       │ POST /tasks
                                       ▼
                            ┌──────────────────┐
                            │ Backend API      │
                            │                  │
                            │ Creates new task │
                            └──────────────────┘
```

### Flow 3: Reminder Due → Notification Sent

```
┌──────────────┐      Cron trigger      ┌──────────────────┐
│ Dapr Cron    ├───────────────────────>│ Backend API      │
│ Binding      │    every 5 minutes     │                  │
└──────────────┘                        │ Reminder         │
                                        │ Scheduler        │
                                        └────────┬─────────┘
                                                 │
                                                 │ Find due reminders
                                                 │ Publish events
                                                 ▼
                                        ┌──────────────────┐
                                        │ Kafka Topic:     │
                                        │ reminders        │
                                        │                  │
                                        │ reminder.due.v1  │
                                        └────────┬─────────┘
                                                 │
                                                 │ consumes
                                                 ▼
                                        ┌──────────────────────────┐
                                        │ Notification Service     │
                                        │                          │
                                        │ 1. Validate event        │
                                        │ 2. Send email (SMTP)     │
                                        │ 3. Send push (FCM)       │
                                        │ 4. Publish result        │
                                        └────────┬─────────────────┘
                                                 │
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │ Kafka Topic:     │
                                        │ notifications    │
                                        │                  │
                                        │ *.sent/failed.v1 │
                                        └──────────────────┘
```

---

## Synchronous vs Asynchronous Communication

### Synchronous Communication (Request-Response)

**Use Cases**:
- Frontend → Backend API (user operations require immediate response)
- Recurring Task Service → Backend API (task creation must succeed before acknowledging Kafka message)

**Characteristics**:
- Caller waits for response
- Immediate error handling
- Strong consistency
- Higher latency

**Error Handling**:
- HTTP status codes (4xx, 5xx)
- Retry with exponential backoff (Dapr Service Invocation)
- Circuit breaker pattern (Dapr Resiliency)

### Asynchronous Communication (Events)

**Use Cases**:
- Backend API → Notification Service (fire-and-forget reminders)
- Backend API → Recurring Task Service (eventual consistency for recurring tasks)

**Characteristics**:
- Caller doesn't wait for processing
- Deferred error handling
- Eventual consistency
- Lower latency for caller
- Higher throughput

**Error Handling**:
- Idempotency (event_id deduplication)
- Dead letter queues (failed events)
- Retry mechanisms (Kafka consumer retries)
- Monitoring and alerting

---

## Inter-Service Error Handling

### Backend API Errors

**Error Codes** (returned to Frontend):
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: User does not own resource
- `404 Not Found`: Resource does not exist
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Operation conflicts with current state
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Unexpected error
- `503 Service Unavailable`: Dependency unavailable (DB, Kafka)

**Error Response Format**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title must be between 1 and 500 characters",
    "details": {
      "field": "title",
      "value": ""
    },
    "timestamp": "2026-01-05T12:00:00Z",
    "trace_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Dapr Service Invocation Errors

**Recurring Task Service → Backend API**:

**Success** (201 Created):
- New task created successfully
- Response contains task ID and details

**Client Errors** (4xx):
- `400 Bad Request`: Invalid task data (malformed JSON, validation errors)
  - **Action**: Log error, acknowledge Kafka message, move to DLQ
- `401 Unauthorized`: Missing or invalid internal service token
  - **Action**: Log critical error, DO NOT acknowledge, retry
- `403 Forbidden`: Service not authorized to create tasks
  - **Action**: Log critical error, DO NOT acknowledge, alert operations

**Server Errors** (5xx):
- `500 Internal Server Error`: Backend API error
  - **Action**: DO NOT acknowledge Kafka message, retry with backoff
- `503 Service Unavailable`: Backend API unavailable (DB down, overloaded)
  - **Action**: DO NOT acknowledge, retry with exponential backoff (1s, 2s, 4s)
  - **Max Retries**: 3 attempts
  - **After Max Retries**: Acknowledge message, move to DLQ, alert operations

**Timeout Errors**:
- Dapr Service Invocation timeout (default: 60s)
  - **Action**: DO NOT acknowledge, retry
  - **Max Retries**: 3 attempts

### Kafka Consumer Errors

**Notification Service Errors**:

**SMTP Failures**:
- Connection timeout → Create notification record with `status=failed`, publish `notification.failed.v1`, acknowledge Kafka message
- Authentication failed → Log critical error, alert operations, acknowledge message
- Invalid recipient email → Log warning, create notification record with error, acknowledge message

**FCM Failures**:
- Token expired → Create notification with `status=failed` and `error="FCM token expired"`, acknowledge message
- Service unavailable → Retry 3 times with backoff, then acknowledge and move to DLQ

**Event Schema Validation Failures**:
- Invalid JSON → Log error, acknowledge message, move to DLQ
- Missing required fields → Log error, acknowledge message, move to DLQ

**Recurring Task Service Errors**:

**Database Query Failures**:
- Connection lost → DO NOT acknowledge, wait for reconnection, retry
- Query timeout → DO NOT acknowledge, retry with backoff

**Recurrence Calculation Errors**:
- Invalid recurrence pattern → Log error, acknowledge message (data corruption)
- Edge case errors (e.g., Feb 30) → Use fallback logic (last day of month), log warning

---

## Retry Policies

### Dapr Service Invocation (Default)

```yaml
policies:
  retries:
    backend-api-retry:
      policy: exponential
      maxRetries: 3
      maxInterval: 10s
      initialInterval: 1s
```

### Kafka Consumer Retry

**Notification Service**:
- **Max Retries**: 3 (via Kafka consumer configuration)
- **Backoff**: None (Kafka handles retry automatically)
- **Dead Letter Queue**: `reminders-dlq` topic

**Recurring Task Service**:
- **Max Retries**: 3
- **Backoff**: Exponential (1s, 2s, 4s)
- **Dead Letter Queue**: `task-events-dlq` topic

### SMTP/FCM Retry

**SMTP**:
- **Max Retries**: 2
- **Backoff**: Linear (5s, 10s)
- **Timeout**: 30s per attempt

**FCM**:
- **Max Retries**: 3
- **Backoff**: Exponential (1s, 2s, 4s)
- **Timeout**: 10s per attempt

---

## Circuit Breaker Configuration

### Backend API → PostgreSQL

```yaml
policies:
  circuitBreakers:
    postgresql-cb:
      maxRequests: 10
      interval: 10s
      timeout: 60s
      trip: consecutiveFailures > 5
```

**Behavior**:
- After 5 consecutive failures, circuit opens
- Requests fail fast for 60 seconds (circuit open)
- After 60s, allow 10 test requests (circuit half-open)
- If test requests succeed, circuit closes
- If test requests fail, circuit opens again

### Recurring Task Service → Backend API

```yaml
policies:
  circuitBreakers:
    backend-api-cb:
      maxRequests: 5
      interval: 5s
      timeout: 30s
      trip: consecutiveFailures > 3
```

---

## Timeout Configuration

| Source | Target | Operation | Timeout |
|--------|--------|-----------|---------|
| Frontend | Backend API | All HTTP requests | 30s (client-side) |
| Backend API | PostgreSQL | Database queries | 10s |
| Backend API | Kafka | Publish event | 5s |
| Notification Service | SMTP | Send email | 30s |
| Notification Service | FCM | Send push | 10s |
| Recurring Task Service | Backend API | Create task (Dapr) | 60s |
| Recurring Task Service | PostgreSQL | Query recurrence | 10s |
| Dapr Sidecar | Kafka | Consumer poll | 5s |

---

## Idempotency Guarantees

### Backend API → Kafka

**Guarantee**: At-least-once delivery
- Events may be published multiple times if Kafka acknowledgment fails
- Consumers MUST implement idempotency using `event_id`

### Kafka → Notification Service

**Guarantee**: Exactly-once processing
- Uses `event_id` in `EventLog` table
- Duplicate events are detected and skipped before processing

### Kafka → Recurring Task Service

**Guarantee**: Exactly-once processing
- Uses `event_id` in `EventLog` table
- Duplicate events do not create duplicate tasks

### Recurring Task Service → Backend API

**Guarantee**: At-most-once creation
- If Backend API call succeeds but Kafka acknowledgment fails:
  - Event will be reprocessed
  - Duplicate detection prevents creating duplicate task

---

## Authentication & Authorization

### Frontend → Backend API

**Authentication**: JWT Bearer Token
- Token issued by Better Auth during login
- Token includes user claims: `sub` (user_id), `email`, `name`
- Token expiration: 24 hours
- Refresh token expiration: 30 days

**Authorization**:
- All endpoints (except `/health`) require valid JWT
- Resource ownership verified: `user_id` in JWT claims must match URL parameter
- Example: `GET /api/v1/users/123/tasks` requires JWT with `sub=123`

### Recurring Task Service → Backend API

**Authentication**: Internal service token (Dapr mTLS)
- Dapr automatically provides mTLS between services
- No explicit token needed for Dapr Service Invocation
- Backend API trusts requests from Dapr sidecar

**Authorization**:
- Backend API verifies Dapr app-id header: `dapr-app-id: recurring-task-service`
- Only trusted service app-ids can bypass JWT authentication
- Configured in Backend API middleware

---

## Rate Limiting

### Frontend → Backend API

**Limits**:
- Unauthenticated: 100 requests/minute per IP
- Authenticated: 1000 requests/minute per user

**Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1704470400
```

**Response** (429 Too Many Requests):
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Retry after 30 seconds.",
    "retry_after": 30,
    "timestamp": "2026-01-05T12:00:00Z"
  }
}
```

### Internal Services

**No Rate Limiting**:
- Recurring Task Service → Backend API: Unlimited
- Notification Service → SMTP/FCM: Limited by external service provider

---

## Health Checks

All services expose `/health` endpoint:

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-05T12:00:00Z",
  "version": "5.0.0",
  "dependencies": {
    "database": "healthy",
    "kafka": "healthy",
    "dapr": "healthy"
  }
}
```

**Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "timestamp": "2026-01-05T12:00:00Z",
  "dependencies": {
    "database": "unhealthy: connection timeout",
    "kafka": "healthy",
    "dapr": "healthy"
  }
}
```

**Kubernetes Probes**:
- **Liveness**: `GET /health` (kill pod if failing)
- **Readiness**: `GET /health` (remove from load balancer if failing)
- **Startup**: `GET /health` (allow slow startup)

---

## Observability

### Distributed Tracing

**Tool**: Jaeger (OpenTelemetry)

**Trace Propagation**:
- Frontend → Backend API: `traceparent` HTTP header
- Backend API → Kafka: `traceparent` in event metadata
- Kafka → Microservices: `traceparent` extracted from event
- Recurring Task Service → Backend API: `traceparent` in Dapr headers

**Trace Example**:
```
Trace ID: 550e8400-e29b-41d4-a716-446655440000

Span 1: Frontend POST /tasks (200ms)
  └─ Span 2: Backend API validate_input (10ms)
  └─ Span 3: Backend API save_to_db (50ms)
  └─ Span 4: Backend API publish_to_kafka (20ms)
      └─ Span 5: Kafka publish (10ms)
```

### Logging

**Format**: Structured JSON logs

**Example**:
```json
{
  "timestamp": "2026-01-05T12:00:00Z",
  "level": "info",
  "service": "backend-api",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "span_id": "123e4567-e89b-12d3",
  "message": "Task created successfully",
  "user_id": "789e4567-e89b-12d3-a456-426614174000",
  "task_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Metrics

**Prometheus Metrics** (all services):
- `http_requests_total{service, method, status}`
- `http_request_duration_seconds{service, method}`
- `kafka_messages_published_total{service, topic, event_type}`
- `kafka_messages_consumed_total{service, topic, event_type}`
- `kafka_consumer_lag{service, topic, group}`
- `database_query_duration_seconds{service, operation}`
- `dapr_service_invocation_total{source, target, method, status}`

---

## Security Considerations

### Network Security

**mTLS** (Dapr):
- All service-to-service communication encrypted
- Certificates rotated every 24 hours by Dapr Sentry
- No manual certificate management needed

**Network Policies** (Kubernetes):
```yaml
# Allow Backend API → PostgreSQL
# Allow Backend API → Kafka
# Allow Notification Service → Kafka
# Allow Notification Service → SMTP (external)
# Allow Notification Service → FCM (external)
# Allow Recurring Task Service → Kafka
# Allow Recurring Task Service → Backend API (via Dapr)
# Deny all other traffic
```

### Secrets Management

**Dapr Secrets Store**:
- All secrets stored in Kubernetes Secrets
- Accessed via Dapr Secrets API
- Never hardcoded or logged

**Secret Rotation**:
- PostgreSQL password: Rotate every 90 days
- SMTP credentials: Rotate every 90 days
- FCM server key: Rotate every 90 days
- JWT secret: Rotate every 180 days

### Input Validation

**All services validate inputs**:
- JSON Schema validation for Kafka events
- Pydantic model validation for HTTP requests
- SQL parameterization for database queries (prevent SQL injection)
- HTML escaping for email templates (prevent XSS)

---

## Testing Contracts

### Contract Tests

**Purpose**: Validate request/response schemas between services

**Tools**: Pact, JSON Schema Validator

**Example** (Recurring Task Service → Backend API):
```python
def test_create_task_contract():
    """Test that Recurring Task Service sends valid request to Backend API."""
    request = {
        "title": "Buy groceries",
        "description": "Milk, bread, eggs",
        "priority": "high",
        "tags": ["shopping"],
        "due_at": "2026-01-08T18:00:00Z",
        "recurrence": {
            "pattern": "weekly",
            "interval": 1,
            "days_of_week": [0, 3, 5]
        }
    }

    # Validate request matches Backend API schema
    validate_schema(request, backend_api_create_task_schema)

    # Send request and validate response
    response = invoke_backend_api_create_task(request)
    validate_schema(response, backend_api_create_task_response_schema)
```

### Integration Tests

**Purpose**: Test actual communication between services

**Example** (End-to-End):
```python
@pytest.mark.integration
async def test_recurring_task_creation():
    """Test full flow: Complete task → Create next occurrence."""
    # 1. Create recurring task via Backend API
    task = await create_task(recurring=True, pattern="daily", interval=1)

    # 2. Complete the task
    await complete_task(task.id)

    # 3. Wait for Recurring Task Service to process event
    await asyncio.sleep(5)

    # 4. Verify new task created
    tasks = await list_tasks(user_id=task.user_id)
    next_task = [t for t in tasks if t.id != task.id and t.title == task.title][0]

    assert next_task.due_at > task.due_at
    assert next_task.status == "pending"
```

---

## Deployment Dependencies

**Deployment Order**:
1. PostgreSQL (database)
2. Kafka (event broker)
3. Dapr (runtime)
4. Backend API (core service)
5. Notification Service (consumer)
6. Recurring Task Service (consumer)
7. Frontend (user interface)

**Critical Path**:
- Backend API depends on: PostgreSQL, Kafka, Dapr
- Notification Service depends on: Kafka, Dapr, SMTP, FCM
- Recurring Task Service depends on: Kafka, Dapr, Backend API
- Frontend depends on: Backend API

---

## Change Management

### Adding New Events

1. Define event schema in `kafka-events.md`
2. Update producer service to publish event
3. Create/update consumer service to process event
4. Add contract tests for event schema
5. Deploy producer and consumer in sequence (producer first)

### Modifying Existing Events

**Backward Compatible Changes**:
- Add optional fields (consumers ignore unknown fields)
- Add new enum values (with fallback handling)

**Breaking Changes** (requires versioning):
- Remove fields → Create `event_type.v2`
- Change field types → Create `event_type.v2`
- Rename fields → Create `event_type.v2`

**Migration Strategy**:
1. Deploy consumers supporting both v1 and v2
2. Deploy producers publishing v2 events
3. Wait for all v1 events to be processed (check Kafka consumer lag)
4. Remove v1 support from consumers

### Adding New Services

1. Document service contract in `contracts/`
2. Define Kafka topics and event schemas
3. Create Dapr component configurations
4. Implement service with contract tests
5. Deploy to staging and verify
6. Deploy to production with monitoring

---

## Contact & Support

**Service Ownership**:
- Backend API: Backend Team (@backend-team)
- Notification Service: Notification Team (@notification-team)
- Recurring Task Service: Scheduling Team (@scheduling-team)
- Frontend: Frontend Team (@frontend-team)

**On-Call Escalation**:
- P1 (Critical): Page on-call engineer immediately
- P2 (High): Create incident ticket, notify team
- P3 (Medium): Create bug ticket
- P4 (Low): Create feature request

**Documentation Updates**:
- All contract changes require PR review
- Update contract docs before implementing changes
- Notify dependent teams of breaking changes 2 weeks in advance
