import pytest
from unittest.mock import MagicMock
from rich.console import Console
from todo_app.ui.cli import TodoApp

def test_add_task_success():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    app.add_task("Buy Milk")
    
    console.print.assert_called_once()

def test_add_task_empty_error():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    app.add_task("")
    
    console.print.assert_called_once()

def test_list_tasks():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    app.add_task("Task 1")
    console.reset_mock()
    
    app.list_tasks()
    
    console.print.assert_called()

def test_complete_task():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    task = app.service.create_task("Task to complete")
    
    console.reset_mock()
    app.complete_task(task.id)
    
    console.print.assert_called()
    updated = app.repository.get(task.id)
    assert updated.status == "COMPLETED"

def test_complete_task_not_found():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    app.complete_task("fake-id")
    
    console.print.assert_called()

def test_update_task():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    task = app.service.create_task("Old Title")
    
    console.reset_mock()
    app.update_task(task.id, title="New Title")
    
    console.print.assert_called()
    assert app.repository.get(task.id).title == "New Title"

def test_delete_task():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    task = app.service.create_task("To Delete")
    
    console.reset_mock()
    app.delete_task(task.id)
    
    console.print.assert_called()
    assert app.repository.get(task.id) is None

def test_undo():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    app.add_task("Undo Me")
    
    console.reset_mock()
    app.undo()
    
    console.print.assert_called()
    assert len(app.service.list_tasks()) == 0

def test_history():
    console = MagicMock(spec=Console)
    app = TodoApp(console=console)
    
    app.add_task("Task 1")
    console.reset_mock()
    
    app.history()
    
    console.print.assert_called()
