from typing import List, Optional
from .base import Command

class CommandInvoker:
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._undo_stack.append(command)
        if len(self._undo_stack) > self.max_history:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> Optional[Command]:
        if not self._undo_stack:
            return None
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return command
        
    def can_undo(self) -> bool:
        return bool(self._undo_stack)
    
    def clear_history(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()

    def history(self) -> List[str]:
        return [cmd.description for cmd in self._undo_stack]