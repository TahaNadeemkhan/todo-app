# Tasks: Phase I - Todo In-Memory Python Console App

**Input**: Design documents from `/specs/001-phase1-console/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: TDD is MANDATORY per Constitution Principle IX - Red-Green-Refactor workflow enforced.

**Organization**: Tasks grouped by user story for independent implementation. Use `tdd-runner` agent for automated TDD cycles.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths included in descriptions

## Path Conventions

```
src/todo_app/
├── domain/          # Pydantic models (Task, TaskStatus)
├── repository/      # Data access (InMemoryTaskRepository)
├── service/         # Business logic (TaskService)
├── commands/        # Command pattern (AddCommand, etc.)
└── ui/              # Rich console (ConsoleRenderer)

tests/
├── unit/            # Unit tests per layer
└── integration/     # End-to-end tests
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: UV project initialization and tooling configuration

- [x] T001 Initialize UV project with `uv init todo-app`
- [x] T002 Configure `pyproject.toml` with dependencies: pydantic, rich
- [x] T003 [P] Configure `pyproject.toml` dev dependencies: pytest, pytest-cov, ruff, mypy
- [x] T004 [P] Create source directory structure: `src/todo_app/{domain,repository,service,commands,ui}/__init__.py`
- [x] T005 [P] Create test directory structure: `tests/{unit,integration}/__init__.py`
- [x] T006 [P] Configure `ruff.toml` for linting (line-length=88, select=["E", "F", "I"])
- [x] T007 [P] Configure `mypy` in `pyproject.toml` (strict=true)
- [x] T008 Verify setup: `uv run pytest --version` and `uv run ruff --version`

**Checkpoint**: Project skeleton ready - can run `uv run pytest` successfully (0 tests)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain models and repository that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### 2.1 Domain Layer - Task Model (TDD)

> **TDD Cycle**: RED → GREEN → REFACTOR

- [x] T009 [RED] Write failing test `tests/unit/test_task.py::test_create_task_with_title`
  - Assert: `Task(title="Buy groceries")` creates task with PENDING status
- [x] T010 [GREEN] Implement `Task` model in `src/todo_app/domain/task.py`
  - Fields: id (UUID default), title (1-200 chars), description (optional, max 1000), status (PENDING default), created_at, updated_at
- [x] T011 [REFACTOR] Add docstrings and verify type hints

- [x] T012 [RED] Write failing test `tests/unit/test_task.py::test_task_title_validation`
  - Assert: Empty title raises ValidationError
  - Assert: Title > 200 chars raises ValidationError
- [x] T013 [GREEN] Pydantic validators handle constraints automatically - verify tests pass
- [x] T014 [REFACTOR] Clean up any redundant code

- [x] T015 [RED] Write failing test `tests/unit/test_task.py::test_task_status_enum`
  - Assert: `TaskStatus.PENDING` and `TaskStatus.COMPLETED` exist
- [x] T016 [GREEN] Implement `TaskStatus` enum in `src/todo_app/domain/task.py`
- [x] T017 [REFACTOR] Export from `src/todo_app/domain/__init__.py`

### 2.2 Repository Layer - In-Memory Storage (TDD)

- [x] T018 [RED] Write failing test `tests/unit/test_repository.py::test_add_task_stores_task`
  - Assert: `repo.add(task)` returns task with ID, `repo.get(id)` returns same task
- [x] T019 [GREEN] Implement `InMemoryTaskRepository.add()` and `get()` in `src/todo_app/repository/in_memory.py`
- [x] T020 [REFACTOR] Add type hints matching `TaskRepository` Protocol

- [x] T021 [RED] Write failing test `tests/unit/test_repository.py::test_get_all_returns_list`
  - Assert: After adding 3 tasks, `repo.get_all()` returns list of 3
- [x] T022 [GREEN] Implement `InMemoryTaskRepository.get_all()`
- [x] T023 [REFACTOR] Ensure consistent return types

- [x] T024 [RED] Write failing test `tests/unit/test_repository.py::test_update_modifies_task`
  - Assert: Update task title, `repo.get(id).title` reflects change
- [x] T025 [GREEN] Implement `InMemoryTaskRepository.update()`
- [x] T026 [REFACTOR] Handle `updated_at` timestamp auto-update

- [x] T027 [RED] Write failing test `tests/unit/test_repository.py::test_delete_removes_task`
  - Assert: Delete task, `repo.get(id)` returns None
- [x] T028 [GREEN] Implement `InMemoryTaskRepository.delete()`
- [x] T029 [REFACTOR] Consider raising error vs returning None for not found

- [x] T030 Define `TaskRepository` Protocol in `src/todo_app/repository/base.py`
  - Methods: add, get, get_all, update, delete (per contracts/service_contract.py)

**Checkpoint**: Foundation ready - `uv run pytest tests/unit/` passes with domain + repository tests

---

## Phase 3: User Story 1 - Add Task (Priority: P1) 🎯 MVP

**Goal**: User can add a new task via CLI and see confirmation

**Independent Test**: Run app → Add task "Buy groceries" → See confirmation with ID

**Acceptance Criteria**:
1. Given app running, when user adds "Buy Groceries", then system confirms "Task 'Buy Groceries' added with ID [X]"
2. Given app running, when user enters empty title, then system displays "Title cannot be empty"

### Tests for US1

- [x] T031 [RED] [US1] Write failing test `tests/unit/test_service.py::test_create_task_returns_task`
  - Assert: `service.create_task("Buy milk")` returns TaskDTO with title and ID
- [x] T032 [RED] [US1] Write failing test `tests/unit/test_service.py::test_create_task_empty_title_raises`
  - Assert: `service.create_task("")` raises ValueError

### Implementation for US1

- [x] T033 [GREEN] [US1] Implement `TaskService.create_task()` in `src/todo_app/service/task_service.py`
  - Create Task, call `repository.add()`, return TaskDTO
- [x] T034 [REFACTOR] [US1] Extract `TaskDTO` to `src/todo_app/service/dto.py` for response objects
- [x] T035 [US1] Create CLI handler for "add" command in `src/todo_app/ui/cli.py`
  - Input: title string, Output: rich-formatted confirmation
- [x] T036 [US1] Add input validation error display using Rich Panel (red border)

**Checkpoint**: US1 complete - Can add tasks via CLI, see confirmation

---

## Phase 4: User Story 2 - View Task List (Priority: P1) 🎯 MVP

**Goal**: User can see all tasks in a beautiful Rich table

**Independent Test**: Add 3 tasks → View list → All 3 appear with ID, title, status

**Acceptance Criteria**:
1. Given list has tasks [A, B], when user views, then Rich table shows both with IDs and status
2. Given empty list, when user views, then system shows "No tasks found"

### Tests for US2

- [x] T037 [RED] [US2] Write failing test `tests/unit/test_service.py::test_list_tasks_returns_all`
  - Assert: After adding 2 tasks, `service.list_tasks()` returns list of 2 DTOs
- [x] T038 [RED] [US2] Write failing test `tests/unit/test_renderer.py::test_render_empty_list_shows_message`
  - Assert: Renderer output contains "No tasks found" when list empty

### Implementation for US2

- [x] T039 [GREEN] [US2] Implement `TaskService.list_tasks()` in `src/todo_app/service/task_service.py`
- [x] T040 [GREEN] [US2] Implement `ConsoleRenderer` in `src/todo_app/ui/renderer.py`
  - `render_task_list(tasks: List[TaskDTO])` → Rich Table
  - Columns: ID (cyan), Title (white), Status (green=COMPLETED, yellow=PENDING), Created
- [x] T041 [REFACTOR] [US2] Add status color coding: `[green]✓ DONE[/]` vs `[yellow]○ PENDING[/]`
- [x] T042 [US2] Create CLI handler for "list" / "view" command
- [x] T043 [US2] Handle empty state with Rich Panel message

**Checkpoint**: US2 complete - Beautiful task list renders in terminal

---

## Phase 5: User Story 3 - Mark as Complete (Priority: P1) 🎯 MVP

**Goal**: User can toggle task completion status

**Independent Test**: Add task → Mark complete → List shows COMPLETED status

**Acceptance Criteria**:
1. Given task 1 (PENDING), when user completes task 1, then confirmation shows "Task 1 marked as completed"
2. Given task 1 (COMPLETED), when user lists, then status shows [DONE]

### Tests for US3

- [x] T044 [RED] [US3] Write failing test `tests/unit/test_service.py::test_complete_task_changes_status`
  - Assert: After `service.complete_task(id)`, task status is COMPLETED
- [x] T045 [RED] [US3] Write failing test `tests/unit/test_service.py::test_complete_nonexistent_raises`
  - Assert: `service.complete_task("fake-id")` raises TaskNotFoundError

### Implementation for US3

- [x] T046 [GREEN] [US3] Implement `TaskService.complete_task()`
  - Get task, toggle status, update repository
- [x] T047 [REFACTOR] [US3] Create `TaskNotFoundError` in `src/todo_app/domain/exceptions.py`
- [x] T048 [US3] Create CLI handler for "complete" / "done" command
- [x] T049 [US3] Add Rich confirmation message with task title

**Checkpoint**: US3 complete - Core MVP done (Add, View, Complete)

---

## Phase 6: User Story 4 - Update Task (Priority: P2)

**Goal**: User can modify task title/description

**Independent Test**: Add task → Update title → List shows new title

**Acceptance Criteria**:
1. Given task 1, when user updates title to "New Title", then confirmation shows update
2. Given fake ID, when user updates, then system shows "Task not found"

### Tests for US4

- [x] T050 [RED] [US4] Write failing test `tests/unit/test_service.py::test_update_task_changes_title`
- [x] T051 [RED] [US4] Write failing test `tests/unit/test_service.py::test_update_nonexistent_raises`

### Implementation for US4

- [x] T052 [GREEN] [US4] Implement `TaskService.update_task(task_id, title=None, description=None)`
- [x] T053 [REFACTOR] [US4] Ensure `updated_at` timestamp changes on update
- [x] T054 [US4] Create CLI handler for "update" / "edit" command
- [x] T055 [US4] Add Rich confirmation with before/after comparison

**Checkpoint**: US4 complete - Full CRUD except Delete

---

## Phase 7: User Story 5 - Delete Task (Priority: P2)

**Goal**: User can permanently remove a task

**Independent Test**: Add task → Delete → List shows empty

**Acceptance Criteria**:
1. Given task 1, when user deletes, then task no longer in list

### Tests for US5

- [x] T056 [RED] [US5] Write failing test `tests/unit/test_service.py::test_delete_task_removes`
- [x] T057 [RED] [US5] Write failing test `tests/unit/test_service.py::test_delete_nonexistent_raises`

### Implementation for US5

- [x] T058 [GREEN] [US5] Implement `TaskService.delete_task(task_id)`
- [x] T059 [REFACTOR] [US5] Add confirmation prompt before delete (optional enhancement)
- [x] T060 [US5] Create CLI handler for "delete" / "remove" command
- [x] T061 [US5] Add Rich confirmation with deleted task title

**Checkpoint**: US5 complete - Full CRUD operations work

---

## Phase 8: User Story 6 - Undo Last Action (Priority: P2 - Delighter) ⭐

**Goal**: User can undo last state-changing operation using Command Pattern

**Independent Test**: Add task → Delete task → Undo → Task restored

**Acceptance Criteria**:
1. Given user just deleted task 1, when they type `undo`, then task 1 restored
2. Given no actions taken, when user types `undo`, then "Nothing to undo"

**Reference**: `.claude/skills/command-pattern/skill.md` for implementation pattern

### Tests for US6

- [x] T062 [RED] [US6] Write failing test `tests/unit/test_commands.py::test_add_command_execute`
  - Assert: Executing AddCommand adds task to repository
- [x] T063 [RED] [US6] Write failing test `tests/unit/test_commands.py::test_add_command_undo`
  - Assert: Undoing AddCommand removes the added task
- [x] T064 [RED] [US6] Write failing test `tests/unit/test_commands.py::test_delete_command_undo_restores`
  - Assert: Undoing DeleteCommand restores the deleted task
- [x] T065 [RED] [US6] Write failing test `tests/unit/test_invoker.py::test_invoker_undo_empty_returns_none`
  - Assert: Undoing with empty stack returns None

### Implementation for US6

- [x] T066 [GREEN] [US6] Implement `Command` Protocol in `src/todo_app/commands/base.py`
  - Methods: execute(), undo(), description property
- [x] T067 [GREEN] [US6] Implement `AddTaskCommand` in `src/todo_app/commands/task_commands.py`
- [x] T068 [GREEN] [US6] Implement `DeleteTaskCommand` (stores deleted task for restore)
- [x] T069 [GREEN] [US6] Implement `UpdateTaskCommand` (stores previous state)
- [x] T070 [GREEN] [US6] Implement `CompleteTaskCommand` (stores previous status)
- [x] T071 [GREEN] [US6] Implement `CommandInvoker` in `src/todo_app/commands/invoker.py`
  - undo_stack, max_history=50, execute(), undo(), can_undo(), history()
- [x] T072 [REFACTOR] [US6] Integrate CommandInvoker into TaskService (replace direct repo calls)
- [x] T073 [US6] Create CLI handler for "undo" command
- [x] T074 [US6] Add Rich confirmation showing what was undone

**Checkpoint**: US6 complete - Undo functionality works (the "Delighter" feature!)

---

## Phase 9: User Story 7 - View Audit History (Priority: P3 - Delighter) ⭐

**Goal**: User can see chronological session log of all actions

**Independent Test**: Add task → Complete task → View history → See both actions with timestamps

**Acceptance Criteria**:
1. Given user added Task A and completed it, when `history`, then chronological list shown

### Tests for US7

- [x] T075 [RED] [US7] Write failing test `tests/unit/test_audit.py::test_audit_log_records_action`
  - Assert: After add_task, audit log has entry with "CREATE" action
- [x] T076 [RED] [US7] Write failing test `tests/unit/test_audit.py::test_audit_log_chronological`
  - Assert: Entries are in timestamp order

### Implementation for US7

- [x] T077 [GREEN] [US7] Implement `AuditLogEntry` model in `src/todo_app/domain/audit.py`
  - Fields: timestamp (UTC), action (str), details (str)
- [x] T078 [GREEN] [US7] Implement `AuditLog` class in `src/todo_app/service/audit_service.py`
  - Methods: log(action, details), get_history() -> List[AuditLogEntry]
- [x] T079 [REFACTOR] [US7] Integrate audit logging into Command execution
- [x] T080 [US7] Create CLI handler for "history" / "log" command
- [x] T081 [US7] Add Rich table for history display (timestamp, action, details)

**Checkpoint**: US7 complete - Full audit trail visible

---

## Phase 10: User Story 8 - Demo Mode (Priority: P3 - Delighter) ⭐

**Goal**: Instant visualization of app capabilities with sample data

**Independent Test**: Run `demo` → See 5 sample tasks with mixed statuses

**Acceptance Criteria**:
1. Given empty state, when `demo`, then 5 realistic tasks generated and displayed

### Tests for US8

- [x] T082 [RED] [US8] Write failing test `tests/unit/test_demo.py::test_demo_creates_sample_tasks`
  - Assert: After demo, service has 5 tasks with varied statuses
- [x] T083 [RED] [US8] Write failing test `tests/unit/test_demo.py::test_demo_displays_list`
  - Assert: Demo output includes Rich table

### Implementation for US8

- [x] T084 [GREEN] [US8] Implement `DemoService` in `src/todo_app/service/demo_service.py`
  - Predefined list of 5 sample tasks (realistic titles, mixed statuses)
- [x] T085 [REFACTOR] [US8] Make demo idempotent (clear existing before demo or check if exists)
- [x] T086 [US8] Create CLI handler for "demo" command
- [x] T087 [US8] Auto-display task list after demo population

**Checkpoint**: US8 complete - "Time to Wow" feature ready

---

## Phase 11: CLI Integration & Polish

**Purpose**: Wire everything together into polished CLI experience

### CLI Main Loop

- [x] T088 Implement main CLI loop in `src/todo_app/main.py`
  - Commands: add, list, complete, update, delete, undo, history, demo, help, exit
- [x] T089 Add Rich welcome banner/header
- [x] T090 Implement help command showing all available commands
- [x] T091 Add graceful exit with goodbye message
- [x] T092 Handle invalid commands with helpful error message

### Error Handling

- [x] T093 [P] Implement consistent error display using Rich Panel (red)
- [x] T094 [P] Add input validation feedback (yellow warnings)
- [x] T095 Handle KeyboardInterrupt (Ctrl+C) gracefully

### Testing Verification

- [x] T096 Run full test suite: `uv run pytest -v --cov=src/todo_app --cov-report=term-missing`
- [x] T097 Verify 100% coverage on Service and Repository layers (SC-002)
- [x] T098 Run type checker: `uv run mypy src/`
- [x] T099 Run linter: `uv run ruff check src/ tests/`

**Checkpoint**: All features integrated - Ready for final validation

---

## Phase 12: Final Validation & Documentation

**Purpose**: Ensure all success criteria met

### Manual Verification (per spec.md)

- [x] T100 Run `uv run python -m todo_app.main`
- [x] T101 Execute demo command → Verify Rich table with colors (SC-005)
- [x] T102 Add task → Delete task → Undo → Verify task restored (SC-006)
- [x] T103 Full CRUD cycle test: Add → View → Update → Complete → Delete (SC-001)
- [x] T104 Verify architecture: UI → Service → Repository layering (SC-003)

### Documentation

- [x] T105 [P] Update quickstart.md with installation and usage instructions
- [x] T106 [P] Add inline comments for complex logic (Command Pattern)

### Final Cleanup

- [x] T107 Remove any debug print statements
- [x] T108 Ensure all `__init__.py` exports are correct
- [x] T109 Final `uv run pytest -v` - All tests passing

**Checkpoint**: Phase 1 COMPLETE - Ready for submission! 🎉

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──────────────────────────────────────────────────────────┐
                                                                          │
Phase 2 (Foundation) ─────────────────────────────────────────────────────┤
         ↓ BLOCKS ALL USER STORIES                                        │
    ┌────┴────────────────────────────────────────────────────────────┐   │
    │                                                                 │   │
Phase 3 (US1-Add)     → MVP                                          │   │
    │                    │                                            │   │
Phase 4 (US2-List)    → MVP ─────────────────────────────────────────┤   │
    │                    │                                            │   │
Phase 5 (US3-Complete)→ MVP DONE ────────────────────────────────────┤   │
    │                                                                 │   │
Phase 6 (US4-Update)  ───────────────────────────────────────────────┤   │
    │                                                                 │   │
Phase 7 (US5-Delete)  ───────────────────────────────────────────────┤   │
    │                                                                 │   │
Phase 8 (US6-Undo)    → Uses Command Pattern skill                   │   │
    │                                                                 │   │
Phase 9 (US7-History) ───────────────────────────────────────────────┤   │
    │                                                                 │   │
Phase 10 (US8-Demo)   ───────────────────────────────────────────────┘   │
                                                                          │
Phase 11 (Integration) ───────────────────────────────────────────────────┤
                                                                          │
Phase 12 (Validation) ────────────────────────────────────────────────────┘
```

### Priority Order (if doing sequentially)

1. **P1 MVP (Phases 1-5)**: Setup → Foundation → Add → List → Complete
2. **P2 Features (Phases 6-8)**: Update → Delete → Undo (delighter)
3. **P3 Delighters (Phases 9-10)**: History → Demo
4. **Polish (Phases 11-12)**: Integration → Validation

### Parallel Opportunities

- **Phase 1**: T003-T007 all parallel (different config files)
- **Phase 2**: T009-T017 (domain) can parallel with nothing; T018-T030 (repo) sequential
- **Within each US**: Tests [P] can run parallel, then implementation sequential
- **Across US**: After Phase 2, US1-US5 could theoretically parallel (different services)

---

## TDD Agent Usage

For each user story, invoke the `tdd-runner` agent:

```
Run TDD for US1: Add Task
```

The agent will:
1. Read acceptance criteria from this tasks.md
2. Write failing tests (RED)
3. Implement minimum code (GREEN)
4. Refactor and clean up (REFACTOR)
5. Report cycle completion

---

## Success Criteria Mapping

| Criteria | Tasks | Verification |
|----------|-------|--------------|
| SC-001: Full CRUD | T031-T061 | T103 manual test |
| SC-002: 100% coverage | T096-T097 | `pytest --cov` |
| SC-003: Service→Repo layering | All impl tasks | T104 architecture review |
| SC-004: UV dependencies | T001-T002 | `pyproject.toml` check |
| SC-005: Rich table with colors | T040-T043 | T101 demo command |
| SC-006: Undo reverts operation | T062-T074 | T102 undo test |

---

## Notes

- All tasks follow TDD: Write test → Verify FAIL → Implement → Verify PASS → Refactor
- Use `command-pattern` skill for US6 implementation guidance
- Commit after each phase completion (logical checkpoints)
- Run `uv run pytest -v` frequently to catch regressions
- Total: 109 tasks organized across 12 phases
