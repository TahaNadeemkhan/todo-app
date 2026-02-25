from typing import List
from todo_app.domain.audit import AuditLogEntry

class AuditLog:
    def __init__(self) -> None:
        self._entries: List[AuditLogEntry] = []

    def log(self, action: str, details: str) -> None:
        entry = AuditLogEntry(action=action, details=details)
        self._entries.append(entry)

    def get_history(self) -> List[AuditLogEntry]:
        return list(self._entries)
