# Data Model: Event-Driven Cloud Deployment

**Feature**: 005-event-driven-cloud
**Created**: 2026-01-04
**Status**: Complete

## Overview

This document defines the data model extensions for Phase 5. It builds upon existing entities from Phases 2-4 (Task, User, Conversation, Message) and adds new entities for recurring tasks, reminders, and notifications.

## Entity Relationship Diagram

```
┌─────────────┐
│    User     │ (existing from Phase 2)
│             │
│ - id: UUID  │
│ - email     │
│ - ...       │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────────────────┐
│        Task             │ (existing, extended)
│                         │
│ - id: UUID              │
│ - user_id: UUID (FK)    │
│ - title: str            │
│ - description: str?     │
│ - status: TaskStatus    │
│ - priority: Priority    │ ← NEW
│ - tags: List[str]       │ ← NEW
│ - due_at: datetime?     │ ← NEW
│ - recurrence_id: UUID?  │ ← NEW (FK to Recurrence)
│ - created_at: datetime  │
│ - updated_at: datetime  │
│ - completed_at: datetime│
└─────┬───────────────────┘
      │
      │ 1:1 (optional)
      │
┌─────▼─────────────────────────┐
│     TaskRecurrence            │ (NEW)
│                               │
│ - id: UUID (PK)               │
│ - task_id: UUID (FK)          │
│ - pattern: RecurrencePattern  │
│ - interval: int               │
│ - days_of_week: List[int]?    │
│ - day_of_month: int?          │
│ - next_due_at: datetime?      │
│ - active: bool                │
│ - created_at: datetime        │
└───────────────────────────────┘

┌─────────────────────────┐
│     TaskReminder        │ (NEW)
│                         │
│ - id: int (PK)          │
│ - task_id: UUID (FK)    │
│ - remind_before: timedelta │
│ - channels: List[str]   │
│ - sent_at: datetime?    │
│ - created_at: datetime  │
└─────┬───────────────────┘
      │
      │ 1:N
      │
┌─────▼──────────────────────┐
│    Notification            │ (NEW)
│                            │
│ - id: int (PK)             │
│ - user_id: UUID (FK)       │
│ - task_id: UUID? (FK)      │
│ - channel: NotificationChannel │
│ - status: NotificationStatus   │
│ - message: str             │
│ - sent_at: datetime?       │
│ - error: str?              │
│ - created_at: datetime     │
└────────────────────────────┘

┌────────────────────────────┐
│   Conversation             │ (existing from Phase 3)
│                            │
│ - id: UUID                 │
│ - user_id: UUID (FK)       │
│ - title: str               │
│ - created_at: datetime     │
│ - updated_at: datetime     │
└─────┬──────────────────────┘
      │
      │ 1:N
      │
┌─────▼──────────────┐
│    Message         │ (existing from Phase 3)
│                    │
│ - id: UUID         │
│ - conversation_id  │
│ - role: str        │
│ - content: str     │
│ - created_at       │
└────────────────────┘
```

## Entity Definitions

### Task (Extended)

**Purpose**: Represents a user's todo item with priority, tags, due dates, and recurrence.

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    """Task completion status."""
    PENDING = "pending"
    COMPLETED = "completed"

class Priority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Task(SQLModel, table=True):
    """Extended Task entity with Phase 5 features."""
    __tablename__ = "tasks"

    # Existing fields (from Phase 2)
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # NEW Phase 5 fields
    priority: Priority = Field(default=Priority.MEDIUM)
    tags: str = Field(default="")  # JSON array serialized as string
    due_at: Optional[datetime] = None  # Timezone-aware
    recurrence_id: Optional[UUID] = Field(default=None, foreign_key="task_recurrences.id")

    # Relationships
    recurrence: Optional["TaskRecurrence"] = Relationship(back_populates="task")
    reminders: list["TaskReminder"] = Relationship(back_populates="task")
```

**Constraints**:
- `title`: Non-empty, max 500 characters
- `tags`: JSON array of strings (e.g., `["work", "urgent"]`)
- `due_at`: Must be timezone-aware (UTC stored)
- `priority`: One of HIGH, MEDIUM, LOW
- `recurrence_id`: NULL if task is non-recurring

**Indexes**:
- `user_id` (existing)
- `(user_id, status)` composite index (existing)
- `(user_id, due_at)` composite index (NEW - for reminders query)
- `(user_id, priority)` composite index (NEW - for filtering)

---

### TaskRecurrence (NEW)

**Purpose**: Defines the recurrence pattern for a recurring task.

**SQLModel Definition**:
```python
class RecurrencePattern(str, Enum):
    """Recurrence pattern types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class TaskRecurrence(SQLModel, table=True):
    """Recurrence configuration for a task."""
    __tablename__ = "task_recurrences"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", unique=True, index=True)
    pattern: RecurrencePattern
    interval: int = Field(default=1, ge=1)  # Every N days/weeks/months
    days_of_week: Optional[str] = None  # JSON array: [0,1,2] (Mon,Tue,Wed)
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)
    next_due_at: Optional[datetime] = None  # Pre-computed next occurrence
    active: bool = Field(default=True)  # Can be stopped
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional[Task] = Relationship(back_populates="recurrence")
```

**Business Rules**:
- **DAILY**: `interval=1` means every day, `interval=2` means every 2 days
- **WEEKLY**: `days_of_week=[0,2,4]` means Mon, Wed, Fri
- **MONTHLY**: `day_of_month=15` means 15th of every month
- When task is completed and `active=True`, calculate `next_due_at` and create new task
- `next_due_at` is always UTC

**Validation**:
- If `pattern=WEEKLY`, `days_of_week` must be non-null
- If `pattern=MONTHLY`, `day_of_month` must be non-null
- `interval` must be >= 1

---

### TaskReminder (NEW)

**Purpose**: Reminder configuration for a task with due date.

**SQLModel Definition**:
```python
from datetime import timedelta

class TaskReminder(SQLModel, table=True):
    """Reminder schedule for a task."""
    __tablename__ = "task_reminders"

    id: int = Field(default=None, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", index=True)
    remind_before: str  # ISO 8601 duration (e.g., "PT1H", "P1D", "P1W")
    channels: str  # JSON array: ["email", "push"]
    sent_at: Optional[datetime] = None  # NULL if not sent yet
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    task: Optional[Task] = Relationship(back_populates="reminders")
```

**Constraints**:
- `remind_before`: ISO 8601 duration string
  - "PT1H" = 1 hour before
  - "P1D" = 1 day before
  - "P1W" = 1 week before
- `channels`: JSON array of "email" | "push"
- `sent_at`: Set when reminder is successfully published to `reminders` topic

**Indexes**:
- `task_id`
- `(sent_at, task_id)` composite (for finding unsent reminders)

---

### Notification (NEW)

**Purpose**: Log of all notifications sent (email, push) with delivery status.

**SQLModel Definition**:
```python
class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    PUSH = "push"

class NotificationStatus(str, Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

class Notification(SQLModel, table=True):
    """Notification delivery log."""
    __tablename__ = "notifications"

    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    task_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id", index=True)
    channel: NotificationChannel
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)
    message: str = Field(max_length=1000)
    sent_at: Optional[datetime] = None  # Set when status=SENT
    error: Optional[str] = Field(default=None, max_length=500)  # Set when status=FAILED
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Constraints**:
- `channel`: One of EMAIL, PUSH
- `status`: One of PENDING, SENT, FAILED
- `error`: Only set when `status=FAILED`
- `sent_at`: Only set when `status=SENT`

**Indexes**:
- `user_id`
- `task_id`
- `(status, created_at)` composite (for retry logic)

**Business Rules**:
- Notification Service consumes `reminder.due` events and creates Notification records
- After sending, publishes `notification.sent` or `notification.failed` events
- Failed notifications can be retried (query `status=FAILED` with exponential backoff)

---

## Event Schemas (Kafka Topics)

### Topic: `task-events`

**Producers**: Backend API, Recurring Task Service
**Consumers**: Recurring Task Service, Analytics (future)

#### Event: `task.created.v1`

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "task.created.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-04T12:00:00Z",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "priority": "high",
    "tags": ["shopping", "urgent"],
    "due_at": "2026-01-05T18:00:00Z",
    "has_recurrence": true,
    "recurrence_pattern": "weekly",
    "recurrence_interval": 1,
    "recurrence_days_of_week": [0, 3, 5],
    "created_at": "2026-01-04T12:00:00Z"
  }
}
```

#### Event: `task.completed.v1`

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440001",
  "event_type": "task.completed.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-04T15:00:00Z",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "completed_at": "2026-01-04T15:00:00Z",
    "has_recurrence": true,
    "recurrence_pattern": "weekly",
    "recurrence_interval": 1,
    "recurrence_days_of_week": [0, 3, 5]
  }
}
```

#### Event: `task.updated.v1`

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440002",
  "event_type": "task.updated.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-04T14:00:00Z",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "changes": {
      "priority": {"old": "medium", "new": "high"},
      "tags": {"old": ["shopping"], "new": ["shopping", "urgent"]}
    },
    "updated_at": "2026-01-04T14:00:00Z"
  }
}
```

#### Event: `task.deleted.v1`

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440003",
  "event_type": "task.deleted.v1",
  "schema_version": "1.0",
  "timestamp": "2026-01-04T16:00:00Z",
  "data": {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "789e4567-e89b-12d3-a456-426614174000",
    "deleted_at": "2026-01-04T16:00:00Z"
  }
}
```

---

### Topic: `reminders`

**Producers**: Backend API (Reminder Scheduler)
**Consumers**: Notification Service

#### Event: `reminder.due.v1`

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

---

### Topic: `notifications`

**Producers**: Notification Service
**Consumers**: Backend API (for status updates), Analytics (future)

#### Event: `notification.sent.v1`

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

#### Event: `notification.failed.v1`

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

### EventLog (NEW - For Idempotency)

**Purpose**: Track processed events to ensure exactly-once processing and prevent duplicate operations.

**SQLModel Definition**:
```python
class EventLog(SQLModel, table=True):
    """Event processing log for idempotency."""
    __tablename__ = "event_log"

    event_id: str = Field(primary_key=True, max_length=100)  # UUID from event
    event_type: str = Field(max_length=50, index=True)  # e.g., "task.completed.v1"
    consumer_service: str = Field(max_length=50)  # Which service processed it
    processed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    data: str = Field(default="{}")  # JSON snapshot of event data
    status: str = Field(default="processed", max_length=20)  # processed | failed
    error: Optional[str] = Field(default=None, max_length=500)

    # Retention policy metadata
    expires_at: datetime = Field(default=None)  # Auto-cleanup after 30 days
```

**Constraints**:
- `event_id`: Primary key, ensures uniqueness
- `event_type`: For analytics and debugging
- `consumer_service`: Track which microservice processed the event
- `expires_at`: Set to `processed_at + 30 days` for automatic cleanup

**Indexes**:
- `event_id` (primary key - unique)
- `event_type` (for monitoring)
- `processed_at` (for cleanup queries)
- `expires_at` (for TTL cleanup job)

**Business Rules**:
1. **Before processing any event**: Check if `event_id` exists in EventLog
2. **If exists**: Skip processing (idempotent - already handled)
3. **If not exists**: Process event, then insert EventLog record
4. **Retry logic**: If status=failed, allow retry with exponential backoff
5. **Cleanup**: Daily job deletes records where `expires_at < NOW()`

**Usage Example**:
```python
async def process_task_completed_event(event: dict):
    """Process task completion event with idempotency."""
    event_id = event["event_id"]

    # Check if already processed
    existing = db.query(EventLog).filter(EventLog.event_id == event_id).first()
    if existing:
        logger.info(f"Event {event_id} already processed, skipping")
        return

    try:
        # Process event: create next recurring task
        create_next_recurring_task(event["data"])

        # Log successful processing
        db.add(EventLog(
            event_id=event_id,
            event_type=event["event_type"],
            consumer_service="recurring-task-service",
            data=json.dumps(event["data"]),
            status="processed",
            expires_at=datetime.utcnow() + timedelta(days=30)
        ))
        db.commit()
    except Exception as e:
        # Log failed processing
        db.add(EventLog(
            event_id=event_id,
            event_type=event["event_type"],
            consumer_service="recurring-task-service",
            data=json.dumps(event["data"]),
            status="failed",
            error=str(e),
            expires_at=datetime.utcnow() + timedelta(days=30)
        ))
        db.commit()
        raise
```

**Data Retention**:
- Keep processed events for 30 days (compliance/debugging)
- Cleanup query: `DELETE FROM event_log WHERE expires_at < NOW()`
- Run cleanup daily via cron job or Kubernetes CronJob

---

## Migration Plan

### Alembic Migrations

**Migration 1**: Add Phase 5 columns to `tasks` table
```python
# alembic/versions/add_phase5_task_fields.py
def upgrade():
    op.add_column('tasks', sa.Column('priority', sa.String(10), nullable=False, server_default='medium'))
    op.add_column('tasks', sa.Column('tags', sa.Text(), nullable=False, server_default='[]'))
    op.add_column('tasks', sa.Column('due_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Add foreign key constraint
    op.create_foreign_key('fk_tasks_recurrence_id', 'tasks', 'task_recurrences', ['recurrence_id'], ['id'])

    # Add indexes
    op.create_index('ix_tasks_user_id_due_at', 'tasks', ['user_id', 'due_at'])
    op.create_index('ix_tasks_user_id_priority', 'tasks', ['user_id', 'priority'])

def downgrade():
    op.drop_index('ix_tasks_user_id_priority', 'tasks')
    op.drop_index('ix_tasks_user_id_due_at', 'tasks')
    op.drop_constraint('fk_tasks_recurrence_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'recurrence_id')
    op.drop_column('tasks', 'due_at')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
```

**Migration 2**: Create `task_recurrences` table
```python
# alembic/versions/create_task_recurrences.py
def upgrade():
    op.create_table(
        'task_recurrences',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('pattern', sa.String(10), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False),
        sa.Column('days_of_week', sa.Text(), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('next_due_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_task_recurrences_task_id', 'task_recurrences', ['task_id'])

def downgrade():
    op.drop_table('task_recurrences')
```

**Migration 3**: Create `task_reminders` table
```python
# alembic/versions/create_task_reminders.py
def upgrade():
    op.create_table(
        'task_reminders',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('remind_before', sa.String(20), nullable=False),
        sa.Column('channels', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_task_reminders_task_id', 'task_reminders', ['task_id'])
    op.create_index('ix_task_reminders_sent_at', 'task_reminders', ['sent_at', 'task_id'])

def downgrade():
    op.drop_table('task_reminders')
```

**Migration 4**: Create `notifications` table
```python
# alembic/versions/create_notifications.py
def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('channel', sa.String(10), nullable=False),
        sa.Column('status', sa.String(10), nullable=False, server_default='pending'),
        sa.Column('message', sa.String(1000), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_task_id', 'notifications', ['task_id'])
    op.create_index('ix_notifications_status_created_at', 'notifications', ['status', 'created_at'])

def downgrade():
    op.drop_table('notifications')
```

---

## Query Patterns

### Find tasks due soon (for reminder scheduling)

```python
from datetime import datetime, timedelta

def find_tasks_needing_reminders(db: Session, now: datetime) -> list[Task]:
    """Find tasks with unsent reminders that are due within their reminder window."""
    # Query: tasks with due_at in future, has reminders, reminders not sent
    return (
        db.query(Task)
        .join(TaskReminder)
        .filter(
            Task.due_at > now,
            Task.status == TaskStatus.PENDING,
            TaskReminder.sent_at.is_(None),
            # Calculate reminder time: due_at - remind_before
            # This is approximate; actual calculation done in app logic
        )
        .all()
    )
```

### Find completed recurring tasks (for next occurrence generation)

```python
def find_completed_recurring_tasks(db: Session, since: datetime) -> list[Task]:
    """Find recently completed tasks with active recurrence."""
    return (
        db.query(Task)
        .join(TaskRecurrence)
        .filter(
            Task.completed_at >= since,
            TaskRecurrence.active == True,
        )
        .all()
    )
```

### Find user tasks with filters (priority, tags, due date)

```python
def find_user_tasks(
    db: Session,
    user_id: UUID,
    priority: Optional[Priority] = None,
    tags: Optional[list[str]] = None,
    due_before: Optional[datetime] = None,
    status: Optional[TaskStatus] = None,
) -> list[Task]:
    """Find user tasks with optional filters."""
    query = db.query(Task).filter(Task.user_id == user_id)

    if priority:
        query = query.filter(Task.priority == priority)

    if tags:
        # JSON array search (PostgreSQL-specific)
        for tag in tags:
            query = query.filter(Task.tags.contains(f'"{tag}"'))

    if due_before:
        query = query.filter(Task.due_at < due_before)

    if status:
        query = query.filter(Task.status == status)

    return query.order_by(Task.due_at.asc().nullsfirst(), Task.created_at.desc()).all()
```

---

## Data Consistency Rules

1. **Task Creation with Recurrence**:
   - Create Task first
   - Create TaskRecurrence with `task_id`
   - Update Task with `recurrence_id`
   - All in single database transaction

2. **Task Completion with Recurrence**:
   - Mark task as completed
   - Publish `task.completed` event with recurrence data
   - Recurring Task Service consumes event, creates new task occurrence
   - Idempotency: Check event_id to avoid duplicate task creation

3. **Reminder Delivery**:
   - Scheduled job finds tasks with unsent reminders
   - Publishes `reminder.due` event
   - Sets `sent_at` on TaskReminder record
   - Notification Service consumes event, sends notification, publishes result

4. **Cascade Deletes**:
   - Delete Task → cascade delete TaskRecurrence, TaskReminders (FK constraint)
   - Delete User → cascade delete Tasks → cascade delete all related data

---

## Next Steps

- ✅ Data model defined with entity diagrams, SQLModel definitions, and event schemas
- ⏭️ Create API contracts in `/contracts/` directory
- ⏭️ Create quickstart.md with setup instructions
- ⏭️ Update agent context files
- ⏭️ Complete plan.md with architecture
