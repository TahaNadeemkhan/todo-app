from todo_app.commands.invoker import CommandInvoker

def test_invoker_undo_empty_returns_none():
    invoker = CommandInvoker()
    assert invoker.undo() is None
    assert invoker.can_undo() is False
