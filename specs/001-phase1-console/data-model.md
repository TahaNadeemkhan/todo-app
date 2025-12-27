# Data Model - Phase I: Todo In-Memory Python Console App

## Entities

### 1. Task

The core unit of work.

| Field | Type | Description | Constraints |
|---|---|---|---|
| `id` | `str` (UUID) | Unique identifier | Valid UUIDv4 string. Immutable. |
| `title` | `str` | Short summary | 1-200 chars. Required. |
| `description` | `str` | Detailed info | Optional. Max 1000 chars. |
| `status` | `TaskStatus` | Current state | Enum: `PENDING`, `COMPLETED`. Default: `PENDING`. |
| `created_at` | `datetime` | Creation time | UTC, Timezone-aware. |
| `updated_at` | `datetime` | Last modified | UTC, Timezone-aware. |

**Pydantic Model (Draft):**
```python
class TaskStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### 2. AuditLogEntry

Represents a single historical action for the session log.

| Field | Type | Description |
|---|---|---|
| `timestamp` | `datetime` | When the action occurred (UTC). |
| `action` | `str` | Short code (e.g., "CREATE", "UPDATE"). |
| `details` | `str` | Human-readable summary (e.g., "Task 'Buy Milk' created"). |

## Interfaces (Protocols)

### 1. TaskRepository (Protocol)

Abstraction for data persistence. Phase 1 implementation will be `InMemoryTaskRepository`.

```python
class TaskRepository(Protocol):
    def add(self, task: Task) -> Task: ...
    def get(self, task_id: str) -> Optional[Task]: ...
    def get_all(self) -> List[Task]: ...
    def update(self, task: Task) -> Task: ...
    def delete(self, task_id: str) -> None: ...
```

### 2. Command (Protocol)

Abstraction for reversible user actions.

```python
class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...
```
