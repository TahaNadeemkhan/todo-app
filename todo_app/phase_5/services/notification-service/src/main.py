"""
T136-T140: Notification Service - FastAPI app with Dapr Pub/Sub consumer

This service:
1. Subscribes to "reminders" Kafka topic via Dapr Pub/Sub
2. Processes reminder.due events
3. Sends notifications via email/push
4. Publishes notification.sent/failed events back to Kafka
5. Exposes /health and /metrics endpoints
"""

import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

from config import get_settings
from handlers import NotificationHandler
from schemas import ReminderDueEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Prometheus Metrics
REMINDERS_PROCESSED = Counter(
    "reminders_processed_total",
    "Total number of reminder events processed",
    ["status"]  # status: success, error
)

NOTIFICATIONS_SENT = Counter(
    "notifications_sent_total",
    "Total number of notifications sent",
    ["channel", "status"]  # channel: email/push, status: success/failure
)

EVENT_PROCESSING_TIME = Histogram(
    "event_processing_seconds",
    "Time spent processing reminder events",
)


# Global notification handler
notification_handler: NotificationHandler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app."""
    global notification_handler

    logger.info("Starting notification-service...")
    logger.info(f"Dapr HTTP Port: {settings.dapr_http_port}")
    logger.info(f"Email configured: {settings.email_configured}")
    logger.info(f"FCM configured: {settings.fcm_configured}")

    # Initialize notification handler
    notification_handler = NotificationHandler()

    yield

    # Cleanup
    logger.info("Shutting down notification-service...")
    if notification_handler:
        await notification_handler.close()


app = FastAPI(
    title="Notification Service",
    description="Microservice for sending email and push notifications",
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================================
# Dapr Pub/Sub Endpoints
# ============================================================================

@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """
    Dapr subscription endpoint.

    Tells Dapr which topics this service subscribes to.
    """
    subscriptions = [
        {
            "pubsubname": settings.dapr_pubsub_name,
            "topic": settings.dapr_reminders_topic,
            "route": "/reminders",
        }
    ]
    logger.info(f"Dapr subscriptions: {subscriptions}")
    return subscriptions


@app.post("/reminders")
async def handle_reminder_event(request: Request):
    """
    Handle reminder.due events from Dapr Pub/Sub.

    Dapr sends CloudEvent format:
    {
        "id": "event-id",
        "source": "source",
        "specversion": "1.0",
        "type": "reminder.due.v1",
        "datacontenttype": "application/json",
        "data": { ... ReminderDueEvent payload ... }
    }
    """
    start_time = time.time()

    try:
        # Parse CloudEvent from Dapr
        cloud_event = await request.json()
        logger.info(f"Received CloudEvent: {cloud_event.get('type')}")

        # Extract our event from CloudEvent wrapper
        event_data = cloud_event.get("data", {})

        # Parse as ReminderDueEvent
        reminder_event = ReminderDueEvent(**event_data)

        # Process event
        await notification_handler.handle_reminder_due(reminder_event)

        # Record metrics
        REMINDERS_PROCESSED.labels(status="success").inc()
        EVENT_PROCESSING_TIME.observe(time.time() - start_time)

        # Return success to Dapr
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing reminder event: {e}", exc_info=True)

        REMINDERS_PROCESSED.labels(status="error").inc()
        EVENT_PROCESSING_TIME.observe(time.time() - start_time)

        # Return RETRY to Dapr (will retry based on Dapr resiliency policy)
        return JSONResponse(
            status_code=500,
            content={"status": "RETRY", "error": str(e)}
        )


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health")
@app.get("/healthz")
async def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes."""
    return {
        "status": "healthy",
        "service": "notification-service",
        "email_configured": settings.email_configured,
        "fcm_configured": settings.fcm_configured,
    }


# ============================================================================
# Prometheus Metrics Endpoint
# ============================================================================

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "notification-service",
        "version": "1.0.0",
        "description": "Microservice for sending email and push notifications",
        "subscriptions": [
            {"topic": settings.dapr_reminders_topic, "route": "/reminders"}
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        log_level=settings.log_level.lower(),
        reload=False,
    )
