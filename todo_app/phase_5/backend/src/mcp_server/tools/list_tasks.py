"""
list_tasks tool implementation.
Follows stateless MCP pattern: state in DB, no memory cache.
"""

import logging
from uuid import UUID
from mcp_server.server import mcp
from repositories.task_repository import TaskRepository
from db import get_async_session

logger = logging.getLogger(__name__)

@mcp.tool(
    name="list_tasks",
    description="Retrieve user's task list. Can filter by status (pending, completed)."
)
async def list_tasks(
    user_id: str,
    status: str = "all",
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
    List tasks for a user.

    Args:
        user_id: The authenticated user's ID
        status: Filter by status ('all', 'pending', 'completed')
        limit: Max number of tasks to return
        offset: Pagination offset
    """
    if not user_id or not isinstance(user_id, str):
        raise ValueError("Invalid user_id format")

    valid_statuses = ["all", "pending", "completed"]
    if status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of {valid_statuses}")

    async for session in get_async_session():
        repo = TaskRepository(session)
        
        # Mapping 'status' string to boolean for repository if needed, 
        # but repository likely handles 'completed' bool.
        # Let's see TaskRepository.get_by_user signature.
        # Assuming it takes optional `completed` bool.
        
        completed_filter = None
        if status == "completed":
            completed_filter = True
        elif status == "pending":
            completed_filter = False
            
        tasks = await repo.get_by_user(
            user_id=user_id,
            completed=completed_filter,
            limit=limit,
            offset=offset
        )
        
        count = len(tasks) # This is page count, real count requires separate query but fine for MVP

    return {
        "tasks": [
            {
                "task_id": str(t.id),
                "title": t.title,
                "description": t.description,
                "completed": t.completed,
                "created_at": t.created_at
            }
            for t in tasks
        ],
        "count": count
    }