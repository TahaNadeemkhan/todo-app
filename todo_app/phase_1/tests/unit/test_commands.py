import pytest
from unittest.mock import MagicMock
from todo_app.commands.task_commands import AddTaskCommand, DeleteTaskCommand
from todo_app.repository.base import TaskRepository
from todo_app.domain.task import Task

def test_add_command_execute():
    repo = MagicMock(spec=TaskRepository)
    task = Task(title="Test")
    cmd = AddTaskCommand(repo, task)
    
    cmd.execute()
    
    repo.add.assert_called_with(task)

def test_add_command_undo():
    repo = MagicMock(spec=TaskRepository)
    task = Task(title="Test")
    cmd = AddTaskCommand(repo, task)
    
    cmd.undo()
    
    repo.delete.assert_called_with(task.id)

def test_delete_command_undo_restores():
    repo = MagicMock(spec=TaskRepository)
    task = Task(title="Test")
    cmd = DeleteTaskCommand(repo, task.id)
    # To undo delete, we need the task. So Command likely needs to fetch it before delete, 
    # OR we pass the task object to DeleteCommand constructor if known.
    # Service delete_task fetches it.
    # Let's assume DeleteTaskCommand takes (repo, task_object) or (repo, id) and fetches.
    # If it takes task object, undo is easy.
    # Let's assume constructor takes `task`.
    cmd = DeleteTaskCommand(repo, task)
    
    cmd.execute() # Should delete
    repo.delete.assert_called_with(task.id)
    
    cmd.undo() # Should restore
    repo.add.assert_called_with(task)
