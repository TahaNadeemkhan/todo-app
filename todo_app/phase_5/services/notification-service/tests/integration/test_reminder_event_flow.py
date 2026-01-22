"""
T128: Integration test for reminder.due event processing end-to-end
"""

import pytest
import json
from datetime import datetime
from httpx import AsyncClient
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text

# Note: This test requires running Docker for testcontainers
# Run with: pytest tests/integration/test_reminder_event_flow.py -v


@pytest.fixture(scope="module")
def postgres_container():
    """Start PostgreSQL container for testing."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        # Create tables
        engine = create_engine(postgres.get_connection_url())
        with engine.begin() as conn:
            # Create notifications table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS notifications (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    task_id VARCHAR(255),
                    type VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    sent_at TIMESTAMP,
                    delivery_status VARCHAR(20) NOT NULL,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )

            # Create event_log table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS event_log (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR(255) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    consumer_service VARCHAR(100) NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    UNIQUE(event_id, consumer_service)
                )
            """
                )
            )

        yield postgres.get_connection_url()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_reminder_event_end_to_end(postgres_container, monkeypatch):
    """
    Test complete flow:
    1. Receive reminder.due event via /reminders endpoint
    2. Process event (send email - mocked)
    3. Log to database
    4. Check idempotency (duplicate event handling)
    """
    # Set environment variables
    monkeypatch.setenv("DATABASE_URL", postgres_container.replace("postgresql://", "postgresql+asyncpg://"))
    monkeypatch.setenv("SMTP_USERNAME", "test@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "testpass")
    monkeypatch.setenv("BREVO_API_KEY", "")  # Disable Brevo for test

    # Import app after setting env vars
    from main import app

    # Create test event
    reminder_event = {
        "id": "cloudevent-123",
        "source": "reminder-scheduler",
        "specversion": "1.0",
        "type": "reminder.due.v1",
        "datacontenttype": "application/json",
        "data": {
            "event_id": "event-test-123",
            "event_type": "reminder.due.v1",
            "schema_version": "1.0",
            "timestamp": "2026-01-10T17:00:00Z",
            "data": {
                "reminder_id": 1,
                "task_id": "task-abc",
                "user_id": "user-xyz",
                "user_email": "test@example.com",
                "task_title": "Test Task",
                "task_description": "Test description",
                "due_at": "2026-01-10T18:00:00Z",
                "remind_before": "PT1H",
                "channels": ["email"],
            },
        },
    }

    # Mock email sending
    from unittest.mock import AsyncMock, patch

    with patch(
        "handlers.email_handler.EmailHandler.send_reminder_email",
        new_callable=AsyncMock,
        return_value=True,
    ):
        # Send event to app
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First request - should process
            response = await client.post("/reminders", json=reminder_event)

            assert response.status_code == 200
            assert response.json()["status"] == "SUCCESS"

            # Verify notification logged to database
            engine = create_engine(postgres_container)
            with engine.begin() as conn:
                result = conn.execute(
                    text("SELECT * FROM notifications WHERE user_id = 'user-xyz'")
                )
                notifications = result.fetchall()
                assert len(notifications) == 1
                assert notifications[0][3] == "email"  # type column
                assert notifications[0][6] == "sent"  # delivery_status column

                # Verify event logged for idempotency
                result = conn.execute(
                    text(
                        "SELECT * FROM event_log WHERE event_id = 'event-test-123'"
                    )
                )
                event_logs = result.fetchall()
                assert len(event_logs) == 1

            # Second request - same event (should skip due to idempotency)
            response2 = await client.post("/reminders", json=reminder_event)

            assert response2.status_code == 200

            # Verify still only 1 notification (not duplicated)
            with engine.begin() as conn:
                result = conn.execute(
                    text("SELECT * FROM notifications WHERE user_id = 'user-xyz'")
                )
                notifications = result.fetchall()
                assert len(notifications) == 1  # Still 1, not 2!


@pytest.mark.asyncio
@pytest.mark.integration
async def test_health_check():
    """Test health check endpoint."""
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "email_configured" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_dapr_subscribe():
    """Test Dapr subscription endpoint."""
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/dapr/subscribe")

        assert response.status_code == 200
        subscriptions = response.json()
        assert len(subscriptions) == 1
        assert subscriptions[0]["topic"] == "reminders"
        assert subscriptions[0]["route"] == "/reminders"
