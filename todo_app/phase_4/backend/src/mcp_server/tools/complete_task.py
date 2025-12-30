"""
complete_task tool implementation.
Follows stateless MCP pattern: state in DB, no memory cache.
"""

import logging
from uuid import UUID
from mcp_server.server import mcp
from repositories.task_repository import TaskRepository
from db import get_async_session

logger = logging.getLogger(__name__)

@mcp.tool(
    name="complete_task",
    description="Mark a task as completed. Use when user says they have finished, done, or completed a task."
)
async def complete_task(
    user_id: str,
    task_id: str
) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task to complete
    """
    if not user_id or not isinstance(user_id, str):
        raise ValueError("Invalid user_id format")

    try:
        # task_id still needs to be int (SQLModel default) or UUID depending on Phase 2
        # Phase 2 Task model uses `id: int | None`. Let's assume int for now or check.
        # Actually Phase 2 `Task` model has `id: int`.
        # Wait, previous tools used `str(t.id)`.
        # If Phase 2 uses int IDs, we need to cast task_id to int.
        # Let's check `models.py` again?
        # Checked previously: `id: int | None = Field(default=None, primary_key=True)`
        # So task_id should be parsed as int.
        task_id_parsed = int(task_id)
    except ValueError:
        raise ValueError("Invalid task_id format (must be integer)")

    async for session in get_async_session():
        repo = TaskRepository(session)
        
        # We need to verify ownership!
        # repo.update usually takes user_id to verify
        task = await repo.update(
            task_id=task_id_parsed,
            user_id=user_id,
            completed=True
        )

    return {
        "task_id": str(task.id),
        "status": "completed",
        "title": task.title
    }