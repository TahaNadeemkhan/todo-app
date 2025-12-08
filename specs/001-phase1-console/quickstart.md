# Quickstart: Phase I Console App

## Prerequisites

- Python 3.13+
- `uv` package manager

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/TahaNadeemkhan/todo-app.git
    cd todo-app
    ```

2.  **Sync Dependencies**:
    ```bash
    uv sync
    ```

## Usage

### Running the App

The application is run via the `main.py` entrypoint.

```bash
uv run src/main.py [command] [options]
```

### Commands

1.  **Demo Mode (Try this first!)**
    Populates the list with sample data to show off the UI.
    ```bash
    uv run src/main.py demo
    ```

2.  **Add a Task**
    ```bash
    uv run src/main.py add "Buy Groceries" --desc "Milk, Eggs, Bread"
    ```

3.  **List Tasks**
    Shows a rich table of tasks.
    ```bash
    uv run src/main.py list
    ```

4.  **Complete a Task**
    ```bash
    uv run src/main.py complete [TASK_UUID]
    ```

5.  **Delete a Task**
    ```bash
    uv run src/main.py delete [TASK_UUID]
    ```

6.  **Undo**
    Reverts the last action (Add/Update/Delete).
    ```bash
    uv run src/main.py undo
    ```

7.  **History**
    View the session audit log.
    ```bash
    uv run src/main.py history
    ```

## Development

### Running Tests

Run all unit and integration tests with coverage report:

```bash
uv run pytest --cov=src
```
