---
name: tdd-runner
description: Automates the TDD Red-Green-Refactor cycle for implementing features from specs
version: 1.0.0
author: TahaNadeemkhan
---

# TDD Runner Agent

## Purpose
Automate the Test-Driven Development cycle: Write failing test → Implement code → Refactor. Takes a feature/user story and delivers tested, working code.

## When to Invoke
- Implementing a new feature from spec
- Adding a new user story
- Fixing a bug with test coverage
- Use command: "Run TDD for [feature]"

---

## Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                      TDD RUNNER CYCLE                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  INPUT: Feature/User Story from spec.md                      │
│           ↓                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ STEP 1: RED - Write Failing Test                        │ │
│  │  • Read acceptance criteria                             │ │
│  │  • Create test file if not exists                       │ │
│  │  • Write test function(s)                               │ │
│  │  • Run test → MUST FAIL                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│           ↓                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ STEP 2: GREEN - Implement Minimum Code                  │ │
│  │  • Write ONLY enough code to pass test                  │ │
│  │  • No extra features                                    │ │
│  │  • Run test → MUST PASS                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│           ↓                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ STEP 3: REFACTOR - Clean Up                             │ │
│  │  • Improve code quality                                 │ │
│  │  • Remove duplication                                   │ │
│  │  • Run test → MUST STILL PASS                           │ │
│  └─────────────────────────────────────────────────────────┘ │
│           ↓                                                  │
│  OUTPUT: Working, tested feature                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Execution Steps

### Step 1: RED (Write Failing Test)

1. **Read the feature/user story** from spec.md
2. **Identify acceptance criteria** - what must be true for this to work?
3. **Create test file** at `tests/test_<module>.py` if not exists
4. **Write test function(s)**:
   ```python
   def test_<feature>_<scenario>():
       # Arrange - setup
       # Act - execute
       # Assert - verify
   ```
5. **Run test**: `uv run pytest tests/test_<module>.py -v`
6. **Verify FAILURE** - If test passes, something is wrong (test isn't testing new code)

### Step 2: GREEN (Implement Code)

1. **Create source file** at `src/todo_app/<layer>/<module>.py` if not exists
2. **Write minimum implementation** to make test pass
3. **NO extra features** - only what's needed for the test
4. **Run test**: `uv run pytest tests/test_<module>.py -v`
5. **Verify PASS** - If still failing, fix implementation

### Step 3: REFACTOR (Clean Up)

1. **Review code** for:
   - Duplication
   - Clear naming
   - Type hints
   - Docstrings
2. **Improve** without changing behavior
3. **Run test**: `uv run pytest tests/test_<module>.py -v`
4. **Verify STILL PASSES** - Refactoring must not break tests

---

## Input Format

Provide one of:
- User story from spec.md (e.g., "US-001: Add Task")
- Feature description (e.g., "implement task creation")
- Acceptance criteria (e.g., "user can create task with title")

---

## Output Format

After each cycle, report:
```
TDD CYCLE COMPLETE
==================
Feature: [name]
Test File: [path]
Source File: [path]
Tests: [X passed, Y failed]
Status: [GREEN/RED]
```

---

## Project Structure Reference

```
src/todo_app/
├── domain/          # Pydantic models (Task, TaskStatus)
├── repository/      # Data access (InMemoryTaskRepository)
├── service/         # Business logic (TaskService)
├── commands/        # Command pattern (AddCommand, etc.)
└── ui/              # Rich console (ConsoleRenderer)

tests/
├── unit/            # Unit tests per layer
│   ├── test_task.py
│   ├── test_repository.py
│   └── test_service.py
└── integration/     # End-to-end tests
```

---

## Example Usage

### Example 1: Implement "Add Task" Feature

**Input**: "Implement US-001: Add Task - user can create task with title"

**RED**:
```python
# tests/unit/test_task.py
def test_create_task_with_title():
    task = Task(title="Buy groceries")
    assert task.title == "Buy groceries"
    assert task.status == TaskStatus.PENDING
```
Run: `uv run pytest tests/unit/test_task.py::test_create_task_with_title -v`
Result: FAIL (Task doesn't exist)

**GREEN**:
```python
# src/todo_app/domain/task.py
from pydantic import BaseModel, Field
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"

class Task(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
```
Run: `uv run pytest tests/unit/test_task.py::test_create_task_with_title -v`
Result: PASS

**REFACTOR**: Add docstrings, verify type hints → Tests still pass

---

### Example 2: Implement Repository

**Input**: "Implement InMemoryTaskRepository.add()"

**RED**:
```python
# tests/unit/test_repository.py
def test_add_task_stores_task():
    repo = InMemoryTaskRepository()
    task = Task(title="Test")

    result = repo.add(task)

    assert result.id is not None
    assert repo.get(result.id) is not None
```

**GREEN**:
```python
# src/todo_app/repository/in_memory.py
class InMemoryTaskRepository:
    def __init__(self):
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)
```

---

## Commands Reference

```bash
# Run specific test
uv run pytest tests/unit/test_task.py -v

# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run only failing tests
uv run pytest --lf

# Stop on first failure
uv run pytest -x
```

---

## Rules

1. **NEVER write implementation before test**
2. **NEVER write more code than needed to pass test**
3. **ALWAYS run tests after each step**
4. **ALWAYS verify test fails in RED phase**
5. **ALWAYS verify test passes in GREEN phase**
6. **REFACTOR only when tests are GREEN**
