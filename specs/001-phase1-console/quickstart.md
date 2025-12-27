# Quickstart: Phase I Console App

## Prerequisites

- Python 3.12+
- `uv` package manager

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/TahaNadeemkhan/todo-app.git
    cd todo-app/todo_app/phase_1
    ```

2.  **Sync Dependencies**:
    ```bash
    uv sync
    ```

## Usage

### Running the App

The application is run via the module entrypoint.

```bash
uv run python -m todo_app.main [command] [options]
```

### Commands

1.  **Demo Mode (Try this first!)**
    Populates the list with sample data to show off the UI.
    ```bash
    uv run python -m todo_app.main demo
    ```

2.  **Add a Task**
    ```bash
    uv run python -m todo_app.main add "Buy Groceries" "Milk, Eggs, Bread"
    ```

3.  **List Tasks**
    Shows a rich table of tasks.
    ```bash
    uv run python -m todo_app.main list
    ```

4.  **Complete a Task**
    ```bash
    uv run python -m todo_app.main complete [TASK_UUID]
    ```

5.  **Delete a Task**
    ```bash
    uv run python -m todo_app.main delete [TASK_UUID]
    ```

6.  **Undo**
    Reverts the last action (Add/Update/Delete).
    ```bash
    uv run python -m todo_app.main undo
    ```

7.  **History**
    View the session audit log.
    ```bash
    uv run python -m todo_app.main history
    ```

## Development

### Running Tests

Run all unit and integration tests with coverage report:

```bash
uv run pytest --cov=src
```