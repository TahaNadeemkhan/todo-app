# Notification Service

**Phase 5 Event-Driven Microservice for Sending Email and Push Notifications**

## Overview

The Notification Service is a Dapr-enabled microservice that consumes `reminder.due` events from Kafka and sends notifications to users via:
- **Email** (Brevo API or SMTP fallback)
- **Push Notifications** (Firebase Cloud Messaging)

### Key Features

- ✅ Dapr Pub/Sub integration for event-driven architecture
- ✅ Multi-channel notifications (email + push)
- ✅ Retry logic with exponential backoff (3 attempts)
- ✅ Idempotency tracking to prevent duplicate notifications
- ✅ Delivery status logging to database
- ✅ Publishes `notification.sent` / `notification.failed` events back to Kafka
- ✅ Prometheus metrics for monitoring
- ✅ Health checks for Kubernetes readiness/liveness probes

## Prerequisites

- Python 3.13+
- PostgreSQL database
- Dapr runtime
- Kafka (via Dapr Pub/Sub component)
- Brevo API key OR SMTP credentials (for email)
- Firebase project with FCM enabled (for push notifications)

## Quick Start

```bash
# Install dependencies
uv venv && source .venv/bin/activate
uv pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run with Dapr
dapr run --app-id notification-service --app-port 8002 -- python src/main.py
```

## API Endpoints

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `POST /reminders` - Receives reminder events from Dapr

## Testing

```bash
pytest tests/ -v
```

## Deployment

Deploy using Helm:

```bash
helm install todo-app ../../k8s/helm/todo-app
```

See the Helm chart at `../../k8s/helm/todo-app/charts/notification-service/`
