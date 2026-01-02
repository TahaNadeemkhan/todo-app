---
name: sqlmodel-db
description: Define database models and queries using SQLModel. Use when creating tables, writing queries, defining relationships, or interacting with the database layer. Triggers on mentions of SQLModel, database, ORM, migrations, or SQL queries.
---

# SQLModel Database Skill

## Instructions

When working with SQLModel for database operations, follow these strict guidelines:

### 1. Table vs DTO Models

**Database tables** use `table=True`:

```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=200, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
```

**DTOs** (Create/Read/Update schemas) do NOT have `table=True`:

```python
class TaskCreate(SQLModel):
    title: str = Field(max_length=200)
    description: str | None = None

class TaskRead(SQLModel):
    id: UUID
    title: str
    status: TaskStatus
```

### 2. Query Syntax

Always use `session.exec(select(...))`:

```python
from sqlmodel import Session, select

# Single item
task = session.get(Task, task_id)

# Filtered list
statement = select(Task).where(Task.user_id == user_id)
results = session.exec(statement)
tasks = list(results.all())

# With ordering and pagination
statement = (
    select(Task)
    .where(Task.status == TaskStatus.PENDING)
    .order_by(Task.created_at.desc())
    .offset(skip)
    .limit(limit)
)
```

**Never use** legacy `session.query()` syntax.

### 3. Foreign Keys

Always define foreign keys explicitly:

```python
class Task(SQLModel, table=True):
    user_id: UUID = Field(
        foreign_key="users.id",
        index=True,
        ondelete="CASCADE"
    )
```

### 4. Relationships

Define bidirectional relationships:

```python
from sqlmodel import Relationship

class User(SQLModel, table=True):
    tasks: list["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    user: User | None = Relationship(back_populates="tasks")
```

### 5. No Raw SQL

Use SQLModel/SQLAlchemy constructs instead of raw SQL:

```python
# Aggregation
from sqlmodel import func
count = session.exec(select(func.count(Task.id))).one()

# Complex filters
statement = select(Task).where(
    Task.priority.in_([TaskPriority.HIGH, TaskPriority.MEDIUM])
)
```

## CRUD Pattern

```python
# CREATE
task = Task(**task_create.model_dump(), user_id=user_id)
session.add(task)
session.commit()
session.refresh(task)

# UPDATE (partial)
update_data = task_update.model_dump(exclude_unset=True)
for key, value in update_data.items():
    setattr(task, key, value)
session.add(task)
session.commit()

# DELETE
session.delete(task)
session.commit()
```

## Checklist

- [ ] Database models use `table=True`
- [ ] DTOs do NOT have `table=True`
- [ ] Using `session.exec(select(...))` for queries
- [ ] Foreign keys defined with `Field(foreign_key=...)`
- [ ] No raw SQL statements
- [ ] Indexes on frequently queried columns
