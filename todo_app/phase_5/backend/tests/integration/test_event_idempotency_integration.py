"""
T052-TEST: Integration test - Event idempotency (duplicate event_id handling)
TDD Red Phase - This test will FAIL until idempotency mechanism is implemented

Critical test for exactly-once event processing guarantee.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from uuid import uuid4

from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer
from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="module")
def postgres_container():
    """Spin up PostgreSQL container for event_log table testing."""
    postgres = PostgresContainer(image="postgres:16-alpine")
    postgres.start()

    connection_url = postgres.get_connection_url()
    print(f"PostgreSQL started at: {connection_url}")

    # Create event_log table
    engine = create_engine(connection_url)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS event_log (
                event_id VARCHAR(100) PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                consumer_service VARCHAR(50) NOT NULL,
                processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                data JSONB,
                status VARCHAR(20) DEFAULT 'processed' NOT NULL,
                error TEXT,
                expires_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX idx_event_log_consumer_service ON event_log(consumer_service);
            CREATE INDEX idx_event_log_processed_at ON event_log(processed_at);
            CREATE INDEX idx_event_log_expires_at ON event_log(expires_at);
        """))
        conn.commit()

    yield connection_url

    postgres.stop()


@pytest.fixture(scope="module")
def kafka_container():
    """Spin up Kafka container for integration testing."""
    kafka = KafkaContainer(image="bitnami/kafka:3.6")
    kafka.start()

    bootstrap_servers = kafka.get_bootstrap_server()
    print(f"Kafka started at: {bootstrap_servers}")

    yield bootstrap_servers

    kafka.stop()


@pytest.fixture
def db_session(postgres_container):
    """Create database session connected to test PostgreSQL."""
    engine = create_engine(postgres_container)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def kafka_producer(kafka_container):
    """Create Kafka producer for publishing test events."""
    producer = KafkaProducer(
        bootstrap_servers=kafka_container,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    yield producer

    producer.close()


@pytest.fixture
def kafka_consumer(kafka_container):
    """Create Kafka consumer for reading test events."""
    consumer = KafkaConsumer(
        "task-events",
        bootstrap_servers=kafka_container,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="test-consumer-group-idempotency",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=5000
    )

    yield consumer

    consumer.close()


class TestEventIdempotency:
    """
    Integration tests for event idempotency using event_log table.

    Critical requirement: Events with duplicate event_id must not be processed twice.
    This ensures exactly-once semantics.
    """

    @pytest.mark.asyncio
    async def test_duplicate_event_id_is_rejected(
        self, kafka_container, kafka_producer, db_session
    ):
        """
        T052-TEST: Test that consuming an event with duplicate event_id is rejected.

        Flow:
        1. Publish event with event_id = "abc-123"
        2. Consumer processes event → inserts into event_log
        3. Publish same event again (duplicate event_id)
        4. Consumer checks event_log → sees duplicate → skips processing
        5. Verify event was NOT processed twice
        """
        # Import will fail until EventLogService is implemented (TDD Red)
        from services.event_log_service import EventLogService
        from services.event_consumer import EventConsumer

        event_log_service = EventLogService(db_session=db_session)
        event_consumer = EventConsumer(
            event_log_service=event_log_service,
            kafka_bootstrap_servers=kafka_container
        )

        # Create test event
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "event_type": "task.created.v1",
            "schema_version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "task_id": str(uuid4()),
                "user_id": str(uuid4()),
                "title": "Test task",
                "priority": "high",
                "tags": [],
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        }

        # Publish event TWICE (same event_id)
        kafka_producer.send("task-events", value=event)
        kafka_producer.send("task-events", value=event)
        kafka_producer.flush()

        await asyncio.sleep(2)

        # Start consumer (will process both messages)
        processed_count = await event_consumer.consume_events(
            topic="task-events",
            consumer_service="test-service",
            max_messages=2
        )

        # Verify only ONE event was processed (duplicate was rejected)
        assert processed_count == 1, "Duplicate event should be rejected"

        # Verify event_log has only one entry
        event_log_count = event_log_service.count_by_event_id(event_id)
        assert event_log_count == 1, "event_log should have exactly one entry"

    @pytest.mark.asyncio
    async def test_event_log_records_processed_events(
        self, kafka_container, kafka_producer, db_session
    ):
        """
        T052-TEST: Test that successfully processed events are recorded in event_log.
        """
        from services.event_log_service import EventLogService
        from services.event_consumer import EventConsumer

        event_log_service = EventLogService(db_session=db_session)
        event_consumer = EventConsumer(
            event_log_service=event_log_service,
            kafka_bootstrap_servers=kafka_container
        )

        # Create and publish event
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "event_type": "task.completed.v1",
            "schema_version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "task_id": str(uuid4()),
                "user_id": str(uuid4()),
                "completed_at": datetime.utcnow().isoformat() + "Z",
                "has_recurrence": False
            }
        }

        kafka_producer.send("task-events", value=event)
        kafka_producer.flush()

        await asyncio.sleep(1)

        # Process event
        await event_consumer.consume_events(
            topic="task-events",
            consumer_service="notification-service",
            max_messages=1
        )

        # Verify event is in event_log
        log_entry = event_log_service.get_by_event_id(event_id)
        assert log_entry is not None
        assert log_entry.event_id == event_id
        assert log_entry.event_type == "task.completed.v1"
        assert log_entry.consumer_service == "notification-service"
        assert log_entry.status == "processed"
        assert log_entry.processed_at is not None

    @pytest.mark.asyncio
    async def test_failed_event_processing_records_error(
        self, kafka_container, kafka_producer, db_session
    ):
        """
        T052-TEST: Test that failed event processing records error in event_log.

        This allows retry logic and DLQ (Dead Letter Queue) handling.
        """
        from services.event_log_service import EventLogService
        from services.event_consumer import EventConsumer

        event_log_service = EventLogService(db_session=db_session)

        # Create consumer with intentional processing failure
        async def failing_handler(event):
            raise ValueError("Simulated processing failure")

        event_consumer = EventConsumer(
            event_log_service=event_log_service,
            kafka_bootstrap_servers=kafka_container,
            event_handler=failing_handler  # This will fail
        )

        # Create and publish event
        event_id = str(uuid4())
        event = {
            "event_id": event_id,
            "event_type": "task.created.v1",
            "schema_version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {
                "task_id": str(uuid4()),
                "user_id": str(uuid4()),
                "title": "Test task",
                "priority": "medium",
                "tags": [],
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
        }

        kafka_producer.send("task-events", value=event)
        kafka_producer.flush()

        await asyncio.sleep(1)

        # Attempt to process event (will fail)
        try:
            await event_consumer.consume_events(
                topic="task-events",
                consumer_service="test-service",
                max_messages=1
            )
        except Exception:
            pass  # Expected to fail

        # Verify error is recorded in event_log
        log_entry = event_log_service.get_by_event_id(event_id)
        assert log_entry is not None
        assert log_entry.status == "failed"
        assert log_entry.error is not None
        assert "Simulated processing failure" in log_entry.error

    @pytest.mark.asyncio
    async def test_concurrent_duplicate_events_handled_correctly(
        self, kafka_container, kafka_producer, db_session
    ):
        """
        T052-TEST: Test that concurrent duplicate events (race condition) are handled.

        Critical edge case: Two consumers process the same event simultaneously.
        Database constraint (PRIMARY KEY on event_id) must prevent duplicates.
        """
        from services.event_log_service import EventLogService

        event_log_service = EventLogService(db_session=db_session)

        event_id = str(uuid4())
        event_data = {
            "task_id": str(uuid4()),
            "user_id": str(uuid4()),
            "title": "Concurrent test",
            "priority": "high",
            "tags": [],
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

        # Simulate two consumers trying to insert same event_id concurrently
        async def attempt_insert():
            try:
                await event_log_service.record_event(
                    event_id=event_id,
                    event_type="task.created.v1",
                    consumer_service="test-service",
                    data=event_data,
                    status="processed"
                )
                return True
            except Exception as e:
                # Expected: PRIMARY KEY violation for duplicate
                return False

        # Run concurrent inserts
        results = await asyncio.gather(
            attempt_insert(),
            attempt_insert(),
            return_exceptions=True
        )

        # Verify only ONE insert succeeded
        successful_inserts = sum(1 for r in results if r is True)
        assert successful_inserts == 1, "Only one concurrent insert should succeed"

        # Verify event_log has exactly one entry
        log_count = event_log_service.count_by_event_id(event_id)
        assert log_count == 1

    @pytest.mark.asyncio
    async def test_event_log_cleanup_old_entries(
        self, db_session
    ):
        """
        T052-TEST: Test that old event_log entries are cleaned up after retention period.

        As per spec: event_log has expires_at field for automatic cleanup.
        Prevents unbounded table growth.
        """
        from services.event_log_service import EventLogService

        event_log_service = EventLogService(db_session=db_session)

        # Insert old event (expired 8 days ago)
        old_event_id = str(uuid4())
        await event_log_service.record_event(
            event_id=old_event_id,
            event_type="task.created.v1",
            consumer_service="test-service",
            data={"task_id": str(uuid4())},
            status="processed",
            expires_at=datetime.utcnow() - timedelta(days=8)  # Already expired
        )

        # Insert recent event (expires in 6 days)
        recent_event_id = str(uuid4())
        await event_log_service.record_event(
            event_id=recent_event_id,
            event_type="task.created.v1",
            consumer_service="test-service",
            data={"task_id": str(uuid4())},
            status="processed",
            expires_at=datetime.utcnow() + timedelta(days=6)  # Not expired
        )

        # Run cleanup job
        deleted_count = await event_log_service.cleanup_expired_events()

        # Verify old event was deleted
        assert deleted_count >= 1

        old_event = event_log_service.get_by_event_id(old_event_id)
        assert old_event is None, "Expired event should be deleted"

        recent_event = event_log_service.get_by_event_id(recent_event_id)
        assert recent_event is not None, "Recent event should still exist"

    @pytest.mark.asyncio
    async def test_different_consumers_can_process_same_event(
        self, db_session
    ):
        """
        T052-TEST: Test that different consumer services can process the same event.

        Idempotency is per (event_id, consumer_service) pair, not just event_id.
        This allows:
        - notification-service to process task.completed event
        - recurring-task-service to also process task.completed event
        """
        from services.event_log_service import EventLogService

        event_log_service = EventLogService(db_session=db_session)

        event_id = str(uuid4())
        event_data = {
            "task_id": str(uuid4()),
            "user_id": str(uuid4()),
            "completed_at": datetime.utcnow().isoformat() + "Z",
            "has_recurrence": True,
            "recurrence_pattern": "daily"
        }

        # notification-service processes event
        await event_log_service.record_event(
            event_id=event_id,
            event_type="task.completed.v1",
            consumer_service="notification-service",
            data=event_data,
            status="processed"
        )

        # recurring-task-service also processes same event (should succeed)
        await event_log_service.record_event(
            event_id=event_id,
            event_type="task.completed.v1",
            consumer_service="recurring-task-service",
            data=event_data,
            status="processed"
        )

        # Verify both entries exist
        entries = event_log_service.get_all_by_event_id(event_id)
        assert len(entries) == 2

        services = [entry.consumer_service for entry in entries]
        assert "notification-service" in services
        assert "recurring-task-service" in services

        # But same consumer cannot process twice
        with pytest.raises(Exception):  # PRIMARY KEY violation
            await event_log_service.record_event(
                event_id=event_id,
                event_type="task.completed.v1",
                consumer_service="notification-service",  # Duplicate
                data=event_data,
                status="processed"
            )
