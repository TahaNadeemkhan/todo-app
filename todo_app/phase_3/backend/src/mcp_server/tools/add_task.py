"""
add_task tool implementation.
Follows stateless MCP pattern: state in DB, no memory cache.
"""

import asyncio
import logging
from uuid import UUID
from mcp_server.schemas import AddTaskInput, AddTaskOutput
from mcp_server.context import ToolContext
from repositories.task_repository import TaskRepository
from services.email_service import email_service
from db import get_async_session
from mcp_server.server import mcp

logger = logging.getLogger(__name__)

class ToolSecurityError(Exception):
    """Raised when a tool is called with unauthorized parameters."""
    pass

@mcp.tool(
    name="add_task",
    description="Create a new task in the database. Use when user wants to add, create, or remember a new todo item."
)
async def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    notify_email: str | None = None
    # Context is injected by FastMCP if declared? 
    # FastMCP supports Context injection but usually via `ctx: Context` type hint.
    # Our requirements used `ToolContext`. We might need to adapt.
    # For now, let's keep the user's defined Schema logic BUT FastMCP prefers primitive types in signature 
    # to auto-generate schema.
    # However, the user specifically asked for "Pydantic schemas for MCP tools" (Task T010).
    # FastMCP works BEST with Python primitives + Docstrings.
    # BUT we can use Pydantic models.
    
    # Wait, the mcp-tool-writer prompt said: "Input schema (all required and optional parameters)"
    # and "Create tool specifications with ... Input schema".
    # FastMCP *auto-generates* from signature.
    
    # I will adapt the function signature to match FastMCP best practices (primitives) 
    # OR keep Pydantic if FastMCP supports it well (it does).
    
    # Crucially: We need to handle `ToolContext`. 
    # If I change the signature, I break the tests I just wrote.
    # But I promised to match the agent.
    
    # Let's try to keep the signature close to what we had but add the decorator.
) -> dict:
    """
    Add a new task to the user's todo list.

    Args:
        user_id: The authenticated user's ID (UUID string)
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)
        notify_email: Optional email address for task notifications
    """
    # NOTE: In a real FastMCP integration with an Agent, `context` usually comes from 
    # the request context (e.g. injected via a Context parameter or context var).
    # Since we are "Stateless HTTP", the context must be passed in the arguments or headers.
    # The `mcp-tool-writer` agent example showed: `def add_task(user_id: str, ...)`
    # It didn't explicitly show `context` injection in the signature in the example.
    
    # Security: We need to verify `user_id`. In a real HTTP call, 
    # the Auth middleware would verify the JWT and ensure the caller is `user_id`.
    # Here, we accept `user_id` as an arg.
    
    # Use string user_id directly (Phase 2 uses string IDs)
    if not user_id or not isinstance(user_id, str):
        raise ValueError("Invalid user_id format")

    # 2. Database Operation (Stateless)
    async for session in get_async_session():
        repo = TaskRepository(session)
        task = await repo.create(
            user_id=user_id,
            title=title,
            description=description,
            notify_email=notify_email
        )

    # 3. Side Effect: Email Notification (only if email provided)
    email_sent = False
    if notify_email:
        try:
            asyncio.create_task(
                email_service.send_notification(
                    to_email=notify_email,
                    notification_type="task_created",
                    task_title=task.title,
                    task_description=task.description
                )
            )
            email_sent = True
        except Exception as e:
            logger.error(f"Failed to trigger email notification: {e}")
            email_sent = False

    return {
        "task_id": str(task.id),
        "status": "created",
        "title": task.title,
        "email_sent": email_sent
    }
