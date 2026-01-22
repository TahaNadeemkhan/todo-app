"""
T073: Integration test - Create recurring task → complete → verify next occurrence
TDD Red Phase - This test will FAIL until full recurring task flow is implemented

Critical test for US1 MVP: Ensures recurring tasks auto-generate next occurrence.
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer
from kafka import KafkaConsumer
import json


@pytest.fixture(scope="module")
def postgres_container():
    """Spin up PostgreSQL for testing."""
    postgres = PostgresContainer(image="postgres:16-alpine")
    postgres.start()
    yield postgres.get_connection_url()
    postgres.stop()


@pytest.fixture(scope="module")
def kafka_container():
    """Spin up Kafka for event testing."""
    kafka = KafkaContainer(image="bitnami/kafka:3.6")
    kafka.start()
    yield kafka.get_bootstrap_server()
    kafka.stop()


@pytest.fixture
async def test_db_session(postgres_container):
    """Create test database session."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(postgres_container)
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    session = SessionLocal()

    yield session

    await session.close()


@pytest.fixture
def kafka_consumer(kafka_container):
    """Create Kafka consumer for reading events."""
    consumer = KafkaConsumer(
        "task-events",
        bootstrap_servers=kafka_container,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="test-recurring-tasks",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=10000
    )
    yield consumer
    consumer.close()


class TestRecurringTasksIntegration:
    """Integration tests for recurring task end-to-end flow."""

    @pytest.mark.asyncio
    async def test_complete_daily_recurring_task_creates_next_occurrence(
        self,
        test_db_session,
        kafka_consumer
    ):
        """
        T073: MVP Test - Complete daily recurring task → verify next occurrence created.

        Flow:
        1. Create daily recurring task (due today at 10 AM)
        2. Complete the task
        3. Verify task.completed event published
        4. Verify Recurring Task Service creates next occurrence (due tomorrow at 10 AM)
        5. Verify task.created event published for next occurrence
        """
        from services.task_service import TaskService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        dapr_client = DaprClient()
        kafka_service = KafkaService(dapr_client=dapr_client)
        task_service = TaskService(db_session=test_db_session, kafka_service=kafka_service)

        user_id = str(uuid4())

        # Step 1: Create daily recurring task
        task_data = {
            "user_id": user_id,
            "title": "Daily standup",
            "priority": "high",
            "tags": ["meetings"],
            "due_at": datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0),
            "has_recurrence": True,
            "recurrence_pattern": "daily",
            "recurrence_interval": 1
        }

        original_task = await task_service.create_task(**task_data)
        assert original_task is not None

        await asyncio.sleep(2)  # Wait for event

        # Step 2: Complete the task
        completed_task = await task_service.complete_task(
            task_id=original_task.id,
            user_id=user_id
        )
        assert completed_task.completed is True

        await asyncio.sleep(3)  # Wait for events

        # Step 3: Consume events from Kafka
        events = []
        for message in kafka_consumer:
            events.append(message.value)
            if len(events) >= 3:  # task.created (original) + task.completed + task.created (next)
                break

        # Step 4: Verify task.completed event
        completed_events = [e for e in events if e["event_type"] == "task.completed.v1"]
        assert len(completed_events) >= 1

        completed_event = completed_events[0]
        assert completed_event["data"]["task_id"] == original_task.id
        assert completed_event["data"]["has_recurrence"] is True
        assert completed_event["data"]["recurrence_pattern"] == "daily"

        # Step 5: Verify next occurrence created (second task.created event)
        created_events = [e for e in events if e["event_type"] == "task.created.v1"]
        assert len(created_events) >= 2  # Original + next occurrence

        next_occurrence_event = created_events[1]  # Second task.created event
        assert next_occurrence_event["data"]["title"] == "Daily standup"
        assert next_occurrence_event["data"]["has_recurrence"] is True

        # Verify due date is tomorrow (1 day after original)
        next_due_at = datetime.fromisoformat(
            next_occurrence_event["data"]["due_at"].replace("Z", "+00:00")
        )
        original_due_at = task_data["due_at"]
        expected_next_due = original_due_at + timedelta(days=1)

        assert next_due_at.date() == expected_next_due.date()
        assert next_due_at.hour == 10  # Preserves time

    @pytest.mark.asyncio
    async def test_complete_weekly_recurring_task_creates_next_occurrence(
        self,
        test_db_session
    ):
        """Test weekly recurring task creates next occurrence on correct day."""
        from services.task_service import TaskService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        kafka_service = KafkaService(dapr_client=DaprClient())
        task_service = TaskService(db_session=test_db_session, kafka_service=kafka_service)

        user_id = str(uuid4())

        # Create weekly recurring task (Monday, Wednesday, Friday)
        task_data = {
            "user_id": user_id,
            "title": "Team sync",
            "priority": "medium",
            "tags": ["meetings"],
            "due_at": datetime.now(timezone.utc),  # Assume today is one of the days
            "has_recurrence": True,
            "recurrence_pattern": "weekly",
            "recurrence_interval": 1,
            "recurrence_days_of_week": [0, 2, 4]  # Monday, Wednesday, Friday
        }

        original_task = await task_service.create_task(**task_data)
        completed_task = await task_service.complete_task(original_task.id, user_id)

        await asyncio.sleep(3)  # Wait for Recurring Task Service to process

        # Verify next occurrence exists in database
        from repositories.task_repository import TaskRepository
        task_repo = TaskRepository(test_db_session)
        user_tasks = await task_repo.get_by_user(user_id, completed=False)

        # Should have at least 1 task (next occurrence)
        assert len(user_tasks) >= 1

        next_occurrence = user_tasks[0]
        assert next_occurrence.title == "Team sync"
        assert next_occurrence.due_at is not None

        # Verify next due date is on one of the specified days (Monday/Wednesday/Friday)
        next_due_day = next_occurrence.due_at.weekday()
        assert next_due_day in [0, 2, 4]

    @pytest.mark.asyncio
    async def test_complete_monthly_recurring_task_edge_case_31st(
        self,
        test_db_session
    ):
        """
        Test monthly recurring task handles 31st day edge case.

        Critical: January 31 → February (only 28/29 days) → March 31
        """
        from services.task_service import TaskService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        kafka_service = KafkaService(dapr_client=DaprClient())
        task_service = TaskService(db_session=test_db_session, kafka_service=kafka_service)

        user_id = str(uuid4())

        # Create monthly recurring task on 31st
        task_data = {
            "user_id": user_id,
            "title": "Monthly report",
            "priority": "high",
            "tags": ["reports"],
            "due_at": datetime(2026, 1, 31, 10, 0, 0, tzinfo=timezone.utc),
            "has_recurrence": True,
            "recurrence_pattern": "monthly",
            "recurrence_interval": 1,
            "recurrence_day_of_month": 31
        }

        original_task = await task_service.create_task(**task_data)
        completed_task = await task_service.complete_task(original_task.id, user_id)

        await asyncio.sleep(3)

        # Verify next occurrence
        from repositories.task_repository import TaskRepository
        task_repo = TaskRepository(test_db_session)
        user_tasks = await task_repo.get_by_user(user_id, completed=False)

        assert len(user_tasks) >= 1
        next_occurrence = user_tasks[0]

        # February 2026 has only 28 days, so next due should be February 28
        assert next_occurrence.due_at.month == 2
        assert next_occurrence.due_at.day == 28  # Last day of February
        assert next_occurrence.due_at.hour == 10  # Preserves time

    @pytest.mark.asyncio
    async def test_stop_recurrence_no_next_occurrence_created(
        self,
        test_db_session
    ):
        """Test that stopped recurrence does not create next occurrence."""
        from services.task_service import TaskService
        from services.recurrence_service import RecurrenceService
        from services.kafka_service import KafkaService
        from dapr.clients import DaprClient

        kafka_service = KafkaService(dapr_client=DaprClient())
        task_service = TaskService(db_session=test_db_session, kafka_service=kafka_service)
        recurrence_service = RecurrenceService(db_session=test_db_session)

        user_id = str(uuid4())

        # Create daily recurring task
        task_data = {
            "user_id": user_id,
            "title": "Daily backup",
            "priority": "high",
            "has_recurrence": True,
            "recurrence_pattern": "daily",
            "recurrence_interval": 1
        }

        original_task = await task_service.create_task(**task_data)

        # Stop recurrence
        await recurrence_service.stop_recurrence(task_id=original_task.id, user_id=user_id)

        # Complete the task
        completed_task = await task_service.complete_task(original_task.id, user_id)

        await asyncio.sleep(3)

        # Verify NO next occurrence was created
        from repositories.task_repository import TaskRepository
        task_repo = TaskRepository(test_db_session)
        user_tasks = await task_repo.get_by_user(user_id, completed=False)

        # Should be 0 (no next occurrence because recurrence was stopped)
        assert len(user_tasks) == 0
