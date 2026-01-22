import pytest
from unittest.mock import MagicMock, patch
from todo_app.ui.cli import TodoApp
from todo_app.service.task_service import TaskService
from todo_app.repository.in_memory import InMemoryTaskRepository
from todo_app.domain.task import Task, TaskPriority

def test_update_interactive_with_short_id():
    """
    Tests if the 'update <short_id>' command flow works.
    This simulates the user's reported issue.
    """
    # 1. Setup a real repository and service chain, but a mock console
    console = MagicMock()
    repo = InMemoryTaskRepository()
    service = TaskService(repo)
    
    # Manually inject the service into a TodoApp instance
    app = TodoApp(console=console)
    app.service = service
    
    # 2. Add a task to get a real ID
    task_dto = app.service.create_task("Original Title", priority=TaskPriority.LOW)
    short_id = task_dto.short_id
    
    # 3. Mock user input for the interactive prompts
    # User wants to change title and priority
    with patch('rich.prompt.Prompt.ask') as mock_ask:
        # This is a bit complex, we need to mock sequential calls
        # 1st call: new title, 2nd call: new description, 3rd call: new priority
        mock_ask.side_effect = [
            "Updated Title",  # New title
            "",               # New description (empty)
            "1"               # New priority (High)
        ]
        
        # 4. Call the interactive update method
        app.update_task_interactive(short_id)

    # 5. Assertions
    # Verify the task was actually updated in the repository
    updated_task = repo.get(task_dto.id)
    assert updated_task is not None
    assert updated_task.title == "Updated Title"
    assert updated_task.priority == TaskPriority.HIGH
    
    # Verify a success message was printed
    console.print.assert_called()
    # Check the content of the last print call for success message
    last_panel = console.print.call_args[0][0]
    assert "updated successfully" in str(last_panel.renderable)
