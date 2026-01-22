# Research Findings: Phase I Console App

## Topic 1: Command Pattern in Python 3.13+

**Decision**: Implement the Command Pattern using `typing.Protocol` for the interface and a stack-based `CommandInvoker` for Undo/Redo.

**Rationale**:
- **Protocol vs ABC**: `typing.Protocol` (duck typing) is more Pythonic and flexible than inheriting from `ABC`. It allows any class with `execute()` and `undo()` to function as a command without explicit inheritance, which decouples the code.
- **Stack Approach**: Using two stacks (`undo_stack` and `redo_stack`) is the standard, robust algorithm for this feature.
- **State Management**: Each ConcreteCommand (e.g., `AddTextCommand`) will hold the *specific state* needed to reverse itself (e.g., the ID of the task it added, or the previous state of the task it modified). This is cleaner than snapshotting the entire application state for a simple Todo app.

**Alternatives Considered**:
- **Abstract Base Classes (ABC)**: Rejected because Protocols offer better flexibility and composition.
- **Memento Pattern**: Rejected as overkill for a simple "Undo" of atomic CRUD operations. The Command objects themselves can hold the necessary "memento" state.

## Topic 2: Testing `rich` Console Output

**Decision**: Inject a `rich.console.Console` instance into the `ConsoleRenderer` class, initialized with `file=io.StringIO()` during tests.

**Rationale**:
- **Isolation**: Redirecting output to `io.StringIO` is cleaner and faster than capturing `sys.stdout` via `capsys`. It prevents test noise from leaking to the actual console.
- **Verification**: We can assert against `console.file.getvalue()` to verify the exact text output.
- **Formatting**: We can use `console.export_text(styles=False)` (requires `record=True`) if we only care about the content, or verify raw string output if we want to check for ANSI codes (though plain text is usually sufficient for logic verification).

**Alternatives Considered**:
- **pytest `capsys` fixture**: Useful for `print()`, but `rich` provides a dedicated `file` argument for this exact purpose, which is more robust.
- **Mocking `print`**: `rich` does complex formatting that `print` mocking would miss.

## Summary of Architectural Decisions

1.  **Command Interface**:
    ```python
    class Command(Protocol):
        def execute(self) -> None: ...
        def undo(self) -> None: ...
    ```
2.  **Invoker**:
    - `undo_stack: list[Command]`
    - `redo_stack: list[Command]`
3.  **UI Testing**:
    - `Console(file=io.StringIO(), force_terminal=True, width=80)` for deterministic output capture.
