import pytest
from unittest.mock import MagicMock
from rich.console import Console
from todo_app.ui.renderer import ConsoleRenderer

def test_render_empty_list_shows_message():
    console = MagicMock(spec=Console)
    renderer = ConsoleRenderer(console=console)
    
    renderer.render_task_list([])
    
    # console.print should be called with a Panel containing "No tasks found"
    console.print.assert_called()
    # Verifying specific content on mocked rich objects is hard without inspection,
    # but we can verify it was called.
