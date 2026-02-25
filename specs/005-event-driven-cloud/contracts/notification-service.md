# Notification Service Contract

**Service**: Notification Service (Python FastAPI + Dapr)
**App ID**: `notification-service` (Dapr)
**Purpose**: Consume reminder events and send email/push notifications

## Architecture

```
┌──────────────────┐
│ Reminder         │
│ Scheduler        │
│ (Backend API)    │
└────────┬─────────┘
         │
         │ publishes
         │
┌────────▼─────────────────┐
│ Kafka Topic: reminders   │
│                          │
│ Event: reminder.due.v1   │
└────────┬─────────────────┘
         │
         │ consumes (Dapr Pub/Sub)
         │
┌────────▼──────────────────────┐
│ Notification Service          │
│                               │
│ 1. Validate event schema      │
│ 2. Send email (SMTP)          │
│ 3. Send push (FCM)            │
│ 4. Create Notification record │
│ 5. Publish result event       │
└────────┬──────────────────────┘
         │
         │ publishes
         │
┌────────▼─────────────────────────┐
│ Kafka Topic: notifications       │
│                                  │
│ Events: notification.sent.v1,    │
│         notification.failed.v1   │
└──────────────────────────────────┘
```

## Kafka Consumer

### Subscribed Topic: `reminders`

**Consumer Group ID**: `notification-service`

**Event Consumed**: `reminder.due.v1`

**Event Schema** (see data-model.md):
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

**Processing Logic**:
1. Validate event schema (JSON Schema validation)
2. Check idempotency: Query `notifications` table for existing record with `event_id`
3. If duplicate event (already processed), acknowledge and skip
4. For each channel in `data.channels`:
   - If `email`: Send via SMTP
   - If `push`: Send via Firebase Cloud Messaging (FCM)
5. Create `Notification` record in database with status
6. Publish result event to `notifications` topic
7. Acknowledge Kafka message

**Idempotency Strategy**:
- Store `event_id` in `Notification.metadata` JSON field (or separate `event_log` table)
- Before processing, check: `SELECT COUNT(*) FROM notifications WHERE metadata->>'event_id' = ?`
- If count > 0, skip processing (already handled)

**Error Handling**:
- If SMTP/FCM fails, create `Notification` with `status=failed` and `error` field
- Publish `notification.failed.v1` event
- Do NOT retry automatically (avoid infinite loops)
- Separate cron job can retry failed notifications with exponential backoff

**Metrics**:
- `notifications_sent_total{channel="email|push", status="sent|failed"}`
- `notification_processing_duration_seconds{channel="email|push"}`
- `kafka_consumer_lag{topic="reminders", group="notification-service"}`

---

## Kafka Producer

### Published Topic: `notifications`

**Events Produced**: `notification.sent.v1`, `notification.failed.v1`

**Event Schema** (see data-model.md):

#### `notification.sent.v1`
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

#### `notification.failed.v1`
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

## External Service Dependencies

### SMTP Email Service

**Configuration** (via Dapr Secrets):
- `SMTP_HOST`: SMTP server hostname (e.g., `smtp.gmail.com`)
- `SMTP_PORT`: SMTP server port (e.g., `587` for TLS)
- `SMTP_USERNAME`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password (stored in Kubernetes Secret)
- `SMTP_FROM_EMAIL`: Sender email address (e.g., `noreply@todo-app.example.com`)

**Email Template**:
```
Subject: Reminder: {task_title}

Hi,

This is a reminder that your task "{task_title}" is due at {due_at}.

Task details:
- Title: {task_title}
- Due: {due_at} ({human_readable_time})

View your tasks: https://todo-app.example.com/tasks

Best,
Todo App Team
```

**Error Scenarios**:
- SMTP connection timeout → `error="SMTP connection failed"`
- Invalid recipient email → `error="Invalid email address"`
- Authentication failed → `error="SMTP authentication failed"`

---

### Firebase Cloud Messaging (FCM) Push Service

**Configuration** (via Dapr Secrets):
- `FCM_SERVER_KEY`: Firebase Cloud Messaging server key (stored in Kubernetes Secret)
- `FCM_PROJECT_ID`: Firebase project ID

**Push Notification Payload**:
```json
{
  "to": "{fcm_device_token}",
  "notification": {
    "title": "Reminder: {task_title}",
    "body": "Due at {due_at}",
    "click_action": "OPEN_TASK",
    "icon": "ic_notification"
  },
  "data": {
    "task_id": "{task_id}",
    "due_at": "{due_at}"
  }
}
```

**Device Token Storage**:
- Users register FCM device tokens via `/api/v1/users/{user_id}/devices` endpoint (not part of Phase 5 scope, use placeholder/mock)
- Tokens stored in `user_devices` table (future enhancement)

**Error Scenarios**:
- FCM token expired → `error="FCM token expired"` (user needs to re-register device)
- FCM service unavailable → `error="FCM service unavailable"` (retry later)
- Invalid token format → `error="Invalid FCM token"`

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
    "smtp": "healthy",
    "fcm": "healthy",
    "database": "healthy"
  }
}
```

**Health Checks**:
- **Kafka**: Check Kafka connection, consumer lag < 1000 messages
- **SMTP**: Attempt connection to SMTP server (timeout: 5s)
- **FCM**: Validate FCM credentials (cached, refresh every 5 minutes)
- **Database**: Execute `SELECT 1` query

**Unhealthy Response** (503 Service Unavailable):
```json
{
  "status": "unhealthy",
  "timestamp": "2026-01-04T12:00:00Z",
  "dependencies": {
    "kafka": "unhealthy: consumer lag 5000 messages",
    "smtp": "healthy",
    "fcm": "unhealthy: credentials invalid",
    "database": "healthy"
  }
}
```

---

## Metrics Endpoint (Prometheus)

### GET `/metrics`

**Metrics Exposed**:
```
# Email notifications
notifications_sent_total{channel="email", status="sent"} 100
notifications_sent_total{channel="email", status="failed"} 5

# Push notifications
notifications_sent_total{channel="push", status="sent"} 80
notifications_sent_total{channel="push", status="failed"} 20

# Processing duration
notification_processing_duration_seconds{channel="email", quantile="0.5"} 0.5
notification_processing_duration_seconds{channel="email", quantile="0.95"} 1.2
notification_processing_duration_seconds{channel="push", quantile="0.5"} 0.3
notification_processing_duration_seconds{channel="push", quantile="0.95"} 0.8

# Kafka consumer lag
kafka_consumer_lag{topic="reminders", group="notification-service"} 10

# Error rates
smtp_errors_total{error_type="connection_timeout"} 3
smtp_errors_total{error_type="auth_failed"} 1
fcm_errors_total{error_type="token_expired"} 15
fcm_errors_total{error_type="service_unavailable"} 2
```

---

## Dapr Configuration

### Pub/Sub Component

**Component Name**: `kafka-pubsub`

**Component YAML** (`dapr-components/pubsub.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"
    - name: consumerGroup
      value: "notification-service"
    - name: clientId
      value: "notification-service"
```

**Subscription** (`notification-service.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: reminders-subscription
spec:
  topic: reminders
  route: /events/reminders
  pubsubname: kafka-pubsub
```

---

### Secrets Component

**Component Name**: `kubernetes-secrets`

**Secrets Required**:
- `smtp-credentials`: `SMTP_USERNAME`, `SMTP_PASSWORD`
- `fcm-credentials`: `FCM_SERVER_KEY`

**Access Pattern**:
```python
from dapr.clients import DaprClient

with DaprClient() as client:
    smtp_password = client.get_secret(
        store_name="kubernetes-secrets",
        key="smtp-credentials",
        metadata={"namespace": "default"}
    ).secret["SMTP_PASSWORD"]
```

---

## Deployment

### Container Image
- **Base Image**: `python:3.13-slim`
- **Build**: Multi-stage Dockerfile
- **Registry**: `ghcr.io/your-org/notification-service:latest`

### Kubernetes Deployment

**Resource Limits**:
- CPU: Request 100m, Limit 500m
- Memory: Request 128Mi, Limit 512Mi

**Replicas**: 2 (for high availability)

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
- Mock SMTP/FCM clients
- Test event schema validation
- Test idempotency logic

### Integration Tests
- Use `testcontainers-python` for Kafka
- Send test `reminder.due.v1` event → assert notification created
- Test duplicate event handling (idempotency)

### Contract Tests
- Validate `reminder.due.v1` event schema with JSON Schema
- Validate `notification.sent.v1` and `notification.failed.v1` schemas

### E2E Tests
- Create task with reminder → wait for due time → assert notification sent
