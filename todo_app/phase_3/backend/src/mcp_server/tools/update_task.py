"""
update_task tool implementation.
Follows stateless MCP pattern: state in DB, no memory cache.
"""

import logging
from uuid import UUID
from mcp_server.server import mcp
from repositories.task_repository import TaskRepository
from db import get_async_session

logger = logging.getLogger(__name__)

@mcp.tool(
    name="update_task",
    description="Update a task's title or description. Use when user wants to change, rename, or edit a task."
)
async def update_task(
    user_id: str,
    task_id: str,
    title: str | None = None,
    description: str | None = None
) -> dict:
    """
    Update a task.

    Args:
        user_id: The authenticated user's ID
        task_id: The ID of the task to update
        title: New task title (optional)
        description: New task description (optional)
    """
    # 1. Validate Input
    if not title and not description:
        raise ValueError("At least one field (title or description) must be provided to update")

    if not user_id or not isinstance(user_id, str):
        raise ValueError("Invalid user_id format")

    try:
        task_id_parsed = int(task_id)
    except ValueError:
        raise ValueError("Invalid task_id format (must be integer)")

    # 2. Database Operation (Stateless)
    async for session in get_async_session():
        repo = TaskRepository(session)
        
        updates = {}
        if title:
            updates["title"] = title
        if description:
            updates["description"] = description
            
        task = await repo.update(
            task_id=task_id_parsed,
            user_id=user_id,
            **updates
        )

    return {
        "task_id": str(task.id),
        "status": "updated",
        "title": task.title,
        "description": task.description
    }
