# Implementation Plan - Phase I: Todo In-Memory Python Console App

**Feature**: Phase I: Todo In-Memory Python Console App
**Status**: Draft
**Spec**: [spec.md](spec.md)

## Technical Context

### Unknowns & Risks (Phase 0)

<!--
  ACTION REQUIRED: Identify unknowns that need research.
  Format: - [ ] [NEEDS CLARIFICATION: Question?]
-->

- [ ] [NEEDS CLARIFICATION: Best practices for implementing Command Pattern with Python's type system for undo/redo?]
- [ ] [NEEDS CLARIFICATION: How to mock `rich` console output effectively for TDD integration tests?]

### Technical Stack Decisions

<!--
  ACTION REQUIRED: List key tech choices.
-->

- **Language**: Python 3.13+
- **Dependency Manager**: `uv`
- **Testing Framework**: `pytest`
- **UI Library**: `rich`
- **Storage**: In-Memory (Dict/List)
- **Architecture**: Service/Repository Layering

## Constitution Check

<!--
  ACTION REQUIRED: Verify alignment with Constitution.
-->

- [x] **Principle I (Spec-Driven)**: Spec is defined before code.
- [x] **Principle II (Separation)**: Plan enforces UI (Rich) -> Service -> Repository (Memory).
- [x] **Principle III (Domain-First)**: Models will be Pydantic, enforcing valid state.
- [x] **Principle IX (TDD)**: Plan explicitly mandates test-first workflow.
- [x] **Principle X (Modern Tooling)**: `uv` is the primary tool.

## Implementation Steps

### Phase 1: Research & Design

1.  **Research Command Pattern in Python**: Determine the cleanest way to implement reversible commands (Add/Update/Delete) while maintaining strong typing.
2.  **Research Testing `rich`**: Find the standard pattern for capturing stdout/stderr when `rich` is handling formatting.
3.  **Define Data Model**: Create `data-model.md` detailing the `Task` entity, `AuditLog` entity, and the `Command` interface.
4.  **Define Contracts**: Define the Python Interface (Protocol) for the `TaskRepository`.

### Phase 2: Foundation (TDD Cycle 1)

1.  **Project Setup**: Initialize `uv` project, configure `pytest`, `ruff`, `mypy`.
2.  **Domain Layer**:
    - Define `Task` Pydantic model.
    - Define `TaskRepository` Protocol (Interface).
    - Implement `InMemoryTaskRepository` (Test: Verify storage/retrieval).
3.  **Service Layer**:
    - Define `TaskService` class.
    - Implement `add_task` (Test: mocking repo).
    - Implement `get_tasks` (Test: mocking repo).

### Phase 3: Advanced Logic (TDD Cycle 2)

1.  **Command Pattern**:
    - Define `Command` abstract base class.
    - Implement `AddCommand`, `DeleteCommand`, `UpdateCommand`.
    - Implement `CommandInvoker` (the "Undo Stack").
    - **Tests**: Verify executing a command performs the action, and calling `undo()` reverses it.
2.  **Audit Logging**:
    - Integrate logging into the Service or Command layer to record actions to the `AuditLog` list.

### Phase 4: UI & Integration (TDD Cycle 3)

1.  **Rich UI Components**:
    - Create `ConsoleRenderer` class to handle `rich` tables/status colors.
    - **Test**: Verify string output matches expected format (mocking `Console`).
2.  **CLI Entrypoint**:
    - Create `main.py` using `argparse` or raw input loop (per requirements).
    - Wire up `CommandInvoker` -> `TaskService` -> `InMemoryTaskRepository`.
3.  **Demo Mode**:
    - Implement `demo` command that loops through a predefined list of commands and executes them.

## Verification Plan

### Automated Tests
- **Unit**: 100% coverage of Service, Repository, and Command classes.
- **Integration**: End-to-end flow tests (simulating user input -> checking state).

### Manual Verification
- Run `uv run main.py demo` and verify the "Wow" factor (colors, tables).
- Add task -> Delete task -> Undo -> Verify task is back.