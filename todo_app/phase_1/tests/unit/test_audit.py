import pytest
from datetime import datetime
from todo_app.service.audit_service import AuditLog, AuditLogEntry

def test_audit_log_records_action():
    audit = AuditLog()
    audit.log("CREATE", "Task created")
    
    history = audit.get_history()
    assert len(history) == 1
    assert history[0].action == "CREATE"
    assert history[0].details == "Task created"
    assert isinstance(history[0].timestamp, datetime)

def test_audit_log_chronological():
    audit = AuditLog()
    audit.log("1", "One")
    audit.log("2", "Two")
    
    history = audit.get_history()
    assert history[0].action == "1"
    assert history[1].action == "2"
