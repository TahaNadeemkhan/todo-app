# Microservice Scaffold Generator

**Purpose**: Scaffold complete Python FastAPI microservice with Dapr, Kafka consumers, and repository pattern

**Trigger Keywords**: microservice, service, scaffold, fastapi, consumer, worker, dapr-enabled

## Overview

This skill generates a production-ready microservice structure with:
- FastAPI application setup
- Kafka event consumer (via Dapr)
- Repository pattern for data access
- Service layer for business logic
- Pydantic schemas for validation
- Dockerfile and Kubernetes manifests
- Unit and integration tests

Perfect for Phase 5 microservices: Notification Service, Recurring Task Service.

## Usage

### Generate Notification Microservice

```bash
/microservice-scaffold \
  --name=notification-service \
  --consumes=reminders \
  --database=neon \
  --output=todo_app/phase_5/services/
```

### Generate Recurring Task Microservice

```bash
/microservice-scaffold \
  --name=recurring-task-service \
  --consumes=task-events \
  --database=neon \
  --output=todo_app/phase_5/services/
```

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| --name | Service name | notification-service |
| --consumes | Kafka topics (comma-separated) | reminders,task-events |
| --database | Database type | neon, postgres, none |
| --output | Output directory | services/ |
| --dapr | Enable Dapr integration | true (default) |

## Generated Directory Structure

```
notification-service/
├── src/
│   ├── main.py                    # FastAPI app + Dapr subscriber
│   ├── config.py                  # Settings with env vars
│   ├── db.py                      # Database connection
│   ├── models/
│   │   └── notification.py        # SQLModel tables
│   ├── repositories/
│   │   └── notification_repository.py  # Data access layer
│   ├── services/
│   │   └── notification_service.py     # Business logic
│   ├── events/
│   │   ├── handlers.py            # Event handler functions
│   │   └── schemas.py             # Event Pydantic models
│   └── utils/
│       ├── email.py               # Email sender
│       └── push.py                # Push notification sender
├── tests/
│   ├── unit/
│   │   └── test_notification_service.py
│   └── integration/
│       └── test_event_handlers.py
├── Dockerfile                     # Multi-stage build
├── pyproject.toml                 # UV dependencies
├── requirements.txt               # For Docker
├── k8s/
│   ├── deployment.yaml            # K8s Deployment
│   ├── service.yaml               # K8s Service (ClusterIP)
│   └── dapr-subscription.yaml     # Dapr topic subscription
└── README.md                      # Service documentation
```

## Generated Artifacts

### 1. Main FastAPI App with Dapr

```python
# src/main.py
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Notification Service starting...")
    yield
    # Shutdown
    print("🛑 Notification Service stopping...")

app = FastAPI(lifespan=lifespan)

@app.post("/dapr/subscribe")
async def subscribe():
    """Tell Dapr which topics to subscribe to"""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminders"
        }
    ]

@app.post("/events/reminders")
async def handle_reminder_event(request: Request):
    """Dapr calls this endpoint when event arrives"""
    from events.handlers import handle_reminder_due

    data = await request.json()
    event_data = data.get("data", {})

    await handle_reminder_due(event_data)

    return {"success": True}

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 2. Event Handler

```python
# src/events/handlers.py
from services.notification_service import NotificationService
from events.schemas import ReminderDueEvent
import logging

logger = logging.getLogger(__name__)

async def handle_reminder_due(event_data: dict):
    """Process reminder.due event and send notification"""
    try:
        event = ReminderDueEvent.model_validate(event_data)

        service = NotificationService()
        await service.send_reminder(
            user_id=event.user_id,
            task_title=event.title,
            due_at=event.due_at
        )

        logger.info(f"Reminder sent for task {event.task_id}")

    except Exception as e:
        logger.error(f"Failed to process reminder: {e}")
        raise  # Dapr will retry
```

### 3. Service Layer

```python
# src/services/notification_service.py
from repositories.notification_repository import NotificationRepository
from utils.email import send_email
from utils.push import send_push_notification
from datetime import datetime

class NotificationService:
    def __init__(self):
        self.repo = NotificationRepository()

    async def send_reminder(self, user_id: str, task_title: str, due_at: datetime):
        """Send reminder notification via email and push"""
        # Create notification record
        notification = await self.repo.create(
            user_id=user_id,
            title="Task Reminder",
            message=f"Task '{task_title}' is due at {due_at}",
            type="reminder"
        )

        # Send email
        await send_email(
            to=user_id,  # Assuming user_id is email
            subject=notification.title,
            body=notification.message
        )

        # Send push notification
        await send_push_notification(
            user_id=user_id,
            title=notification.title,
            body=notification.message
        )

        # Mark as sent
        await self.repo.mark_sent(notification.id)

        return notification
```

### 4. Repository Pattern

```python
# src/repositories/notification_repository.py
from sqlmodel import Session, select
from models.notification import Notification
from db import get_session

class NotificationRepository:
    async def create(self, user_id: str, title: str, message: str, type: str):
        """Create notification record"""
        async with get_session() as session:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type
            )
            session.add(notification)
            await session.commit()
            await session.refresh(notification)
            return notification

    async def mark_sent(self, notification_id: int):
        """Mark notification as sent"""
        async with get_session() as session:
            notification = await session.get(Notification, notification_id)
            notification.sent_at = datetime.utcnow()
            await session.commit()
```

### 5. Dockerfile

```dockerfile
# Multi-stage build
FROM python:3.13-slim AS builder

WORKDIR /app

# Install UV
RUN pip install uv

# Copy dependencies
COPY pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# Copy source code
COPY src/ ./src/

# Non-root user
RUN useradd -m -u 1001 appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### 6. Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  labels:
    app: notification-service
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "notification-service"
    dapr.io/app-port: "8001"
    dapr.io/log-level: "info"
spec:
  replicas: 2
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
    spec:
      containers:
      - name: notification-service
        image: notification-service:v1.0.0
        ports:
        - containerPort: 8001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: neon-db-secret
              key: connection-string
        - name: SMTP_HOST
          valueFrom:
            secretKeyRef:
              name: email-secret
              key: smtp-host
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 250m
            memory: 256Mi
```

### 7. Dapr Subscription

```yaml
# k8s/dapr-subscription.yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: notification-reminders-sub
spec:
  pubsubname: kafka-pubsub
  topic: reminders
  routes:
    default: /events/reminders
scopes:
- notification-service
```

## Microservice Best Practices

1. **Single Responsibility**: Each service handles one domain
2. **Event-Driven**: Consume events, don't poll databases
3. **Stateless**: All state in database, not in memory
4. **Idempotent**: Handle duplicate events gracefully
5. **Observability**: Log all events, errors, and metrics
6. **Health Checks**: Always expose /health endpoint

## Phase 5 Microservices

### 1. Notification Service
- **Consumes**: `reminders` topic
- **Sends**: Email + Push notifications
- **Database**: Notification log table
- **External**: SMTP server, Push notification provider

### 2. Recurring Task Service
- **Consumes**: `task-events` topic (filter: task.completed)
- **Produces**: `task-events` topic (event: task.created)
- **Logic**: If task has recurrence_pattern, create next occurrence
- **Database**: Reads/writes Task table

### 3. Audit Log Service (Optional)
- **Consumes**: All topics
- **Stores**: Immutable event log
- **Database**: Audit log table

## Testing Generated Microservice

```python
# tests/unit/test_notification_service.py
import pytest
from services.notification_service import NotificationService

@pytest.mark.asyncio
async def test_send_reminder():
    service = NotificationService()

    notification = await service.send_reminder(
        user_id="test@example.com",
        task_title="Buy groceries",
        due_at=datetime(2026, 1, 20, 14, 0)
    )

    assert notification.title == "Task Reminder"
    assert "Buy groceries" in notification.message
```

## Related Skills

- **kafka-event-schema**: Generate event schemas for consumers
- **dapr-component-generator**: Generate Dapr components
- **fastapi-design**: FastAPI best practices
- **sqlmodel-db**: Database model design

## Tags

microservice, scaffold, fastapi, dapr, kafka, consumer, event-driven, repository-pattern
