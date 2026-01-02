"""
delete_task tool implementation.
Follows stateless MCP pattern: state in DB, no memory cache.
"""

import logging
from uuid import UUID
from mcp_server.server import mcp
from repositories.task_repository import TaskRepository
from db import get_async_session

logger = logging.getLogger(__name__)

@mcp.tool(
    name="delete_task",
    description="Permanently delete a task. Use when user wants to remove, delete, or cancel a task."
)
async def delete_task(
    user_id: str,
    task_id: str
) -> dict:
    """
    Delete a task permanently.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task to delete
    """
    if not user_id or not isinstance(user_id, str):
        raise ValueError("Invalid user_id format")

    try:
        task_id_parsed = int(task_id)
    except ValueError:
        raise ValueError("Invalid task_id format (must be integer)")

    async for session in get_async_session():
        repo = TaskRepository(session)
        success = await repo.delete(
            task_id=task_id_parsed,
            user_id=user_id
        )
        
        if not success:
            raise ValueError("Task not found or access denied")

    return {
        "task_id": str(task_id_parsed),
        "status": "deleted"
    }