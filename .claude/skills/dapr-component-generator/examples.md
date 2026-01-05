# Dapr Component Generator - Code Examples

Complete, reusable Dapr component YAML configurations and integration code examples.

## Example 1: Kafka Pub/Sub Component

### Generated YAML: `kafka-pubsub.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: clientId
      value: "todo-app"
    - name: authType
      value: "none"  # Use 'sasl' for Redpanda Cloud
    - name: maxMessageBytes
      value: "1024000"
scopes:
  - backend-api
  - notification-service
  - recurring-task-service
```

### Publishing Events via Dapr

```python
import httpx

async def publish_task_created(task_id: UUID, user_id: UUID):
    """Publish via Dapr Pub/Sub - abstracts Kafka"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
            json={
                "event_type": "task.created",
                "task_id": str(task_id),
                "user_id": str(user_id)
            }
        )
```

### Subscribing to Events

```python
from fastapi import FastAPI, Request

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
    """Dapr calls this endpoint when event arrives"""
    data = await request.json()
    event_data = data.get("data", {})
    # Process event
    return {"success": True}
```

## Example 2: PostgreSQL State Store Component

### Generated YAML: `statestore.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: neon-db-secret
        key: connection-string
    - name: tableName
      value: "dapr_state"
    - name: metadataTableName
      value: "dapr_metadata"
    - name: keyPrefix
      value: "todo"
scopes:
  - backend-api
  - notification-service
```

### Saving State via Dapr

```python
async def save_conversation(conv_id: str, messages: list):
    """Save state via Dapr - abstracts PostgreSQL"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/state/statestore",
            json=[{
                "key": f"conversation-{conv_id}",
                "value": {"messages": messages}
            }]
        )
```

### Retrieving State via Dapr

```python
async def get_conversation(conv_id: str) -> dict:
    """Get state via Dapr"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:3500/v1.0/state/statestore/conversation-{conv_id}"
        )
        if response.status_code == 204:
            return None
        return response.json()
```

### Deleting State via Dapr

```python
async def delete_conversation(conv_id: str):
    """Delete state via Dapr"""
    async with httpx.AsyncClient() as client:
        await client.delete(
            f"http://localhost:3500/v1.0/state/statestore/conversation-{conv_id}"
        )
```

## Example 3: Kubernetes Secret Store Component

### Generated YAML: `kubernetes-secrets.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
    - name: vaultName
      value: "default"
scopes:
  - backend-api
  - notification-service
  - frontend
```

### Retrieving Secrets via Dapr

```python
async def get_api_key() -> str:
    """Get secret via Dapr - abstracts Kubernetes Secret"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:3500/v1.0/secrets/kubernetes-secrets/openai-api-key"
        )
        return response.json()["openai-api-key"]

async def get_database_url() -> str:
    """Get database connection string"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:3500/v1.0/secrets/kubernetes-secrets/database-url"
        )
        return response.json()["database-url"]
```

### Creating Kubernetes Secrets

```bash
# Create secret for API keys
kubectl create secret generic api-keys \
  --from-literal=openai-api-key=sk-xxx \
  --from-literal=gemini-api-key=AIza-xxx \
  -n default

# Create secret for database
kubectl create secret generic neon-db-secret \
  --from-literal=connection-string="postgresql://user:pass@host/db" \
  -n default

# Create secret for SMTP
kubectl create secret generic email-secret \
  --from-literal=smtp-host=smtp.gmail.com \
  --from-literal=smtp-user=noreply@example.com \
  --from-literal=smtp-password=app-password \
  -n default
```

## Example 4: Cron Binding Component

### Generated YAML: `reminder-scheduler.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-scheduler
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "@every 1m"  # Every minute
    - name: direction
      value: "input"
scopes:
  - notification-service
```

### Handling Cron Triggers

```python
from fastapi import FastAPI, Request
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.post("/cron/check-reminders")
async def check_reminders(request: Request):
    """Dapr calls this endpoint every minute"""
    logger.info("Cron triggered: Checking for due reminders...")

    # Query database for reminders due now
    reminders = await get_due_reminders()

    for reminder in reminders:
        # Publish reminder.due event
        await publish_reminder_due_event(reminder)

    return {"processed": len(reminders)}

async def get_due_reminders():
    """Get reminders due in the next minute"""
    now = datetime.now(timezone.utc)
    # Query database
    return []

async def publish_reminder_due_event(reminder):
    """Publish reminder.due event to Kafka"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/kafka-pubsub/reminders",
            json={
                "event_type": "reminder.due",
                "reminder_id": str(reminder.id),
                "task_id": str(reminder.task_id),
                "user_id": str(reminder.user_id)
            }
        )
```

## Example 5: Dapr Subscription YAML

### Generated YAML: `dapr-subscription.yaml`

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: notification-reminders-sub
  namespace: default
spec:
  pubsubname: kafka-pubsub
  topic: reminders
  routes:
    default: /events/reminders
scopes:
  - notification-service
```

## Example 6: Service Invocation

### Calling Another Service via Dapr

```python
async def get_task_from_backend(task_id: str) -> dict:
    """Call backend-api service via Dapr service invocation"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:3500/v1.0/invoke/backend-api/method/api/v1/tasks/{task_id}"
        )
        return response.json()

async def notify_user(user_id: str, message: str):
    """Call notification-service via Dapr"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/invoke/notification-service/method/send",
            json={"user_id": user_id, "message": message}
        )
```

## Example 7: Deployment with Dapr Annotations

### Kubernetes Deployment with Dapr Sidecar

```yaml
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
```

## Example 8: Redis State Store (Alternative)

### Generated YAML: `redis-statestore.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: redis-statestore
  namespace: default
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis:6379"
    - name: redisPassword
      secretKeyRef:
        name: redis-secret
        key: password
    - name: enableTLS
      value: "false"
scopes:
  - backend-api
```

## Example 9: RabbitMQ Pub/Sub (Alternative)

### Generated YAML: `rabbitmq-pubsub.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: rabbitmq-pubsub
  namespace: default
spec:
  type: pubsub.rabbitmq
  version: v1
  metadata:
    - name: host
      value: "amqp://rabbitmq:5672"
    - name: durable
      value: "true"
    - name: deletedWhenUnused
      value: "false"
    - name: autoAck
      value: "false"
scopes:
  - backend-api
  - notification-service
```

## Example 10: HTTP Binding

### Generated YAML: `webhook-binding.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: webhook-binding
  namespace: default
spec:
  type: bindings.http
  version: v1
  metadata:
    - name: url
      value: "https://external-api.example.com/webhook"
    - name: direction
      value: "output"
scopes:
  - backend-api
```

### Invoking HTTP Binding

```python
async def send_webhook(data: dict):
    """Send data to external webhook via Dapr binding"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/bindings/webhook-binding",
            json={
                "operation": "create",
                "data": data
            }
        )
```

## Example 11: Complete Microservice with Multiple Components

### FastAPI Microservice Using All Dapr Components

```python
from fastapi import FastAPI, Request
import httpx
from datetime import datetime, timezone
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# === Pub/Sub: Subscribe to events ===
@app.post("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        }
    ]

@app.post("/events/task-events")
async def handle_task_event(request: Request):
    data = await request.json()
    event = data.get("data", {})

    # Process event
    if event.get("event_type") == "task.completed":
        await handle_task_completed(event)

    return {"success": True}

# === Pub/Sub: Publish events ===
async def publish_notification_sent(notification_id: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/kafka-pubsub/notifications",
            json={
                "event_type": "notification.sent",
                "notification_id": notification_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )

# === State Store: Save and retrieve ===
async def save_notification_state(notification_id: str, data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/state/statestore",
            json=[{
                "key": f"notification-{notification_id}",
                "value": data
            }]
        )

async def get_notification_state(notification_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:3500/v1.0/state/statestore/notification-{notification_id}"
        )
        if response.status_code == 204:
            return None
        return response.json()

# === Secrets: Retrieve credentials ===
async def get_smtp_credentials() -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:3500/v1.0/secrets/kubernetes-secrets/smtp-credentials"
        )
        return response.json()

# === Cron Binding: Periodic task ===
@app.post("/cron/check-reminders")
async def check_reminders():
    logger.info("Checking for due reminders...")
    # Query state store for reminders
    # Publish reminder.due events
    return {"status": "checked"}

# === Service Invocation: Call other services ===
async def get_task_details(task_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:3500/v1.0/invoke/backend-api/method/api/v1/tasks/{task_id}"
        )
        return response.json()

async def handle_task_completed(event: dict):
    task_id = event.get("task_id")
    user_id = event.get("user_id")

    # Get task details via service invocation
    task = await get_task_details(task_id)

    # Check if recurring
    if task.get("has_recurrence"):
        # Save state
        await save_notification_state(task_id, {"recurring": True})

        # Publish recurring.triggered event
        await publish_notification_sent(task_id)
```

## Testing Commands

```bash
# Initialize Dapr in Kubernetes
dapr init -k

# List all components
kubectl get components -n default

# Check component details
kubectl describe component kafka-pubsub -n default

# Check Dapr sidecar logs
kubectl logs -l app=notification-service -c daprd

# Test Pub/Sub
dapr publish \
  --publish-app-id backend-api \
  --pubsub kafka-pubsub \
  --topic task-events \
  --data '{"event_type":"task.created","task_id":"123"}'

# Test state store
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test","value":"hello"}]'

# Test secret retrieval
curl http://localhost:3500/v1.0/secrets/kubernetes-secrets/openai-api-key

# Test service invocation
curl http://localhost:3500/v1.0/invoke/backend-api/method/health
```
