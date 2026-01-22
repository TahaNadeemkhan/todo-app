"""
T121-T122: FastAPI application for Recurring Task Service

Microservice that consumes task.completed events and creates next task occurrences.
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from handlers.recurrence_handler import RecurrenceHandler
from repositories.event_log_repository import EventLogRepository, Base
from consumers.task_completed_consumer import TaskCompletedConsumer
from clients.task_api_client import TaskApiClient


# ============================================================================
# Logging Configuration
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# T122: Prometheus Metrics
# ============================================================================

# Counter: Total events processed
events_processed = Counter(
    "recurring_task_events_processed_total",
    "Total number of task.completed events processed",
    ["status"]  # Labels: success, duplicate, skipped, failed
)

# Counter: Total events failed
events_failed = Counter(
    "recurring_task_events_failed_total",
    "Total number of events that failed processing",
    ["error_type"]
)

# Histogram: Event processing duration
event_processing_duration = Histogram(
    "recurring_task_event_processing_duration_seconds",
    "Duration of event processing in seconds"
)

# Counter: Tasks created
tasks_created = Counter(
    "recurring_task_tasks_created_total",
    "Total number of next occurrence tasks created",
    ["recurrence_pattern"]
)


# ============================================================================
# Database Configuration
# ============================================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/recurring_task_db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")


# ============================================================================
# Application Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown tasks.
    """
    # Startup
    logger.info("Starting Recurring Task Service...")

    # Initialize database
    await init_db()

    # Initialize dependencies
    async with AsyncSessionLocal() as session:
        event_log_repo = EventLogRepository(session)
        task_api_client = TaskApiClient(
            backend_url=os.getenv("BACKEND_API_URL", "http://localhost:8000")
        )
        recurrence_handler = RecurrenceHandler(
            task_api_client=task_api_client,
            event_log_repo=event_log_repo
        )

        # Register Dapr Pub/Sub consumer
        consumer = TaskCompletedConsumer(recurrence_handler)
        consumer.register_routes(app)

        logger.info("Recurring Task Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Recurring Task Service...")
    await engine.dispose()
    logger.info("Recurring Task Service stopped")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Recurring Task Service",
    description="Microservice for auto-generating next task occurrences",
    version="1.0.0",
    lifespan=lifespan
)


# ============================================================================
# T121: Health Check Endpoint
# ============================================================================

@app.get("/health")
async def health_check():
    """
    T121: Health check endpoint for Kubernetes liveness/readiness probes.

    Returns:
        200: Service is healthy
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "recurring-task-service",
            "version": "1.0.0"
        }
    )


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes.

    Verifies database connection is ready.

    Returns:
        200: Service is ready to accept traffic
        503: Service is not ready
    """
    try:
        # Test database connection
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")

        return JSONResponse(
            status_code=200,
            content={"status": "ready"}
        )

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "error": str(e)}
        )


@app.get("/health/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes.

    Returns:
        200: Service is alive
    """
    return JSONResponse(
        status_code=200,
        content={"status": "alive"}
    )


# ============================================================================
# T122: Prometheus Metrics Endpoint
# ============================================================================

@app.get("/metrics")
async def metrics():
    """
    T122: Prometheus metrics endpoint.

    Exposes metrics for monitoring:
    - recurring_task_events_processed_total
    - recurring_task_events_failed_total
    - recurring_task_event_processing_duration_seconds
    - recurring_task_tasks_created_total

    Returns:
        Prometheus metrics in text format
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "recurring-task-service",
        "description": "Microservice for auto-generating next task occurrences",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "readiness": "/health/ready",
            "liveness": "/health/live",
            "metrics": "/metrics",
            "dapr_subscribe": "/dapr/subscribe",
            "events": "/events"
        }
    }


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info"
    )
