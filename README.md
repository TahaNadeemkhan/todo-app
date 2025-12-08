# Todo App (CLI)

A modern, interactive Command-Line Interface (CLI) for managing your tasks, built with Python and Rich.

> [!NOTE]
> This project is the Phase 1 implementation for the "Hackathon II - Todo Spec-Driven Development" challenge.

---

## ✨ Features

- **Interactive Shell:** A user-friendly REPL (`todo>`) for managing tasks.
- **Full CRUD:** Add, list, update, complete, and delete tasks.
- **Rich UI:** Beautifully formatted tables, panels, and prompts powered by the `rich` library.
- **Task Priorities:** Assign High, Medium, or Low priority to tasks.
- **Undo Functionality:** Instantly undo the last action (add, update, delete, complete).
- **Audit History:** View a complete log of all actions taken during the session.
- **Short ID Support:** Interact with tasks using convenient 8-character short IDs.
- **Data Persistence:** In-memory storage for the current session.

## 🛠️ Tech Stack

- **Language:** Python 3.12+
- **Package Management:** `uv`
- **Core Libraries:**
  - `rich` for all terminal UI.
  - `pydantic` for data validation and models.
- **Testing:** `pytest` and `pytest-cov`
- **Architecture:** Follows a clean, decoupled Service -> Repository pattern.
- **Development:** Built using a strict Test-Driven Development (TDD) workflow.

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- `uv` package manager (`pip install uv`)

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/TahaNadeemkhan/todo-app.git
    cd todo-app
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd todo_app/phase_1
    ```

3.  **Install dependencies:**
    ```bash
    uv sync
    ```

4.  **Run the application:**
    The app can be run in interactive mode or by passing a one-shot command.

    *   **Interactive Mode:**
        ```bash
        uv run python -m todo_app.main
        ```
    *   **One-shot Command:**
        ```bash
        uv run python -m todo_app.main list
        ```

## 🧪 Running Tests

To run the full unit test suite and generate a coverage report:

1.  Navigate to the project directory: `cd todo_app/phase_1`
2.  Run the test command:
    ```bash
    uv run pytest --cov=src/todo_app
    ```
