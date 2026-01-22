# Feature Specification: Phase I: Todo In-Memory Python Console App

**Feature Branch**: `001-phase1-console`
**Created**: 2025-12-08
**Status**: Draft
**Input**: User description: "write a clear detailed specification by considering consitituion.md file, remember you are 50+ years experienced spec driven developer so you have to work accordingly by covering each and every aspects of the Hackathon II requiremnts. Don't forget to mention that we will go phase by phase"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Task (Priority: P1)

The user adds a new task to their todo list to keep track of pending work.

**Why this priority**: Adding data is the most fundamental operation; without it, the system is empty.

**Independent Test**: Verify a task can be added and then retrieved (conceptually) or simply that the add operation returns a success confirmation with a valid ID.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** the user chooses "Add Task" and enters "Buy Groceries", **Then** the system confirms "Task 'Buy Groceries' added with ID [X]".
2. **Given** the application is running, **When** the user chooses "Add Task" and enters an empty title, **Then** the system displays an error "Title cannot be empty".

---

### User Story 2 - View Task List (Priority: P1)

The user views all their tasks to see what needs to be done.

**Why this priority**: Visibility of data is critical for the app's utility.

**Independent Test**: Add multiple tasks, then invoke list. Verify all added tasks appear.

**Acceptance Scenarios**:

1. **Given** the list has tasks [A, B], **When** the user chooses "View Tasks", **Then** the system displays a formatted list containing [A, B] with their IDs and status.
2. **Given** the list is empty, **When** the user chooses "View Tasks", **Then** the system displays "No tasks found".

---

### User Story 3 - Mark as Complete (Priority: P1)

The user marks a task as finished.

**Why this priority**: Core value prop of a todo list is tracking completion.

**Independent Test**: Add a task, mark it complete, verify status is updated in list.

**Acceptance Scenarios**:

1. **Given** a task exists with ID 1 (Pending), **When** the user chooses "Complete Task" for ID 1, **Then** the system confirms "Task 1 marked as completed".
2. **Given** a task 1 is completed, **When** user lists tasks, **Then** task 1 shows status [DONE] or similar.

---

### User Story 4 - Update Task (Priority: P2)

The user corrects a typo or changes details of a task.

**Why this priority**: Data maintenance is important but less critical than the creation/completion flow for an MVP.

**Independent Test**: Add task, update it, verify changes persist.

**Acceptance Scenarios**:

1. **Given** task 1 exists, **When** user updates task 1 title to "New Title", **Then** the system confirms the update.
2. **Given** user tries to update non-existent task 99, **Then** system displays "Task 99 not found".

---

### User Story 5 - Delete Task (Priority: P2)

The user removes a task they no longer need.

**Why this priority**: Cleanup is useful but not strictly required for the "happy path" of doing work.

**Independent Test**: Add task, delete it, verify it's gone.

**Acceptance Scenarios**:

1. **Given** task 1 exists, **When** user deletes task 1, **Then** system confirms deletion and task 1 no longer appears in list.

### User Story 6 - Undo Last Action (Priority: P2 - Delighter)

The user accidentally deletes or modifies a task and wants to revert the change immediately.

**Why this priority**: Demonstrates advanced "Command Pattern" architecture and provides a "safety net" for users, elevating the UX above a basic homework assignment.

**Independent Test**: Add task -> Delete task -> Invoke Undo -> Verify task is back.

**Acceptance Scenarios**:

1. **Given** the user just deleted task 1, **When** they type `undo`, **Then** the system restores task 1 and confirms "Deletion of Task 1 undone".
2. **Given** no actions have been taken, **When** user types `undo`, **Then** system says "Nothing to undo".

---

### User Story 7 - View Audit History (Priority: P3 - Delighter)

The user wants to see a log of what happened in the session (e.g., "What time did I finish that?").

**Why this priority**: Precursor to Event Sourcing (Phase 5) and adds professional-grade transparency.

**Independent Test**: Perform actions -> View History -> Verify log matches actions.

**Acceptance Scenarios**:

1. **Given** user added Task A and completed Task A, **When** user types `history`, **Then** system displays a chronological list:
    - [10:00:01] Created Task A
    - [10:00:05] Completed Task A

---

### User Story 8 - Demo Mode (Priority: P3 - Delighter)

The user wants to see the app's capabilities without typing manual data.

**Why this priority**: "Time to Wow". Allows instant visualization of the Rich UI.

**Independent Test**: Start app -> Run `demo` -> Verify list is populated.

**Acceptance Scenarios**:

1. **Given** an empty state, **When** user types `demo`, **Then** system generates 5 realistic sample tasks with mixed statuses and displays them.

### Edge Cases

- What happens when the user enters an invalid UUID format? (Should handle gracefully)
- What happens when `undo` is called on a non-reversible action (e.g., listing tasks)? (Should be ignored/handled)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow adding tasks with a required title (1-200 chars) and optional description.
- **FR-002**: System MUST list all tasks using the `rich` library for TUI (Tables, Colors, Borders).
- **FR-003**: System MUST allow marking a task as completed/incomplete by unique ID.
- **FR-004**: System MUST allow updating task title or description by unique ID.
- **FR-005**: System MUST allow deleting a task by unique ID.
- **FR-006**: System MUST use in-memory storage (Python list/dict) for Phase 1.
- **FR-007**: System MUST validate all inputs at the domain level (not just UI).
- **FR-008**: System MUST adhere to the "Phased Evolution" principle, implementing ONLY Phase 1 features.
- **FR-009**: System MUST provide a text-based Console UI (CLI) for interaction.
- **FR-010**: System MUST implement an `undo` command using the Command Design Pattern (stack-based).
- **FR-011**: System MUST maintain an in-memory session log of actions accessible via `history` command.
- **FR-012**: System MUST include a `demo` command to populate sample data.

### Key Entities

- **Task**:
    - `id` (UUID): Unique identifier (String).
    - `title` (String): Brief summary of work.
    - `description` (String): Optional details.
    - `status` (Enum): PENDING | COMPLETED.
    - `created_at` (Datetime): UTC timestamp.
    - `updated_at` (Datetime): UTC timestamp.

- **AuditLog**:
    - `timestamp` (Datetime): When it happened.
    - `action` (String): What happened (e.g., "TASK_CREATED").
    - `details` (String): Readable summary.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully perform the full CRUD cycle (Create, Read, Update, Delete) via the CLI.
- **SC-002**: Codebase achieves 100% unit test coverage for Service and Repository layers using `pytest`.
- **SC-003**: Architecture strictly follows the `Service -> Repository` layering defined in the Constitution.
- **SC-004**: Project dependencies are managed strictly via `uv` with a valid `pyproject.toml`.
- **SC-005**: The `view` command renders a formatted table using `rich` with colored status indicators (Green/Red).
- **SC-006**: The `undo` command successfully reverts the last state-changing operation (Create/Update/Delete).