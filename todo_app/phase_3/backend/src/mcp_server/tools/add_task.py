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

async def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    notify_email: str | None = None,
    tags: list[str] | None = None
) -> dict:
    """
    Add a new task to the user's todo list.

    Args:
        user_id: The authenticated user's ID (UUID string)
        title: Task title (required, 1-200 characters)
        description: Optional task description (max 1000 characters)
        notify_email: Optional email address for task notifications. If not provided, will look up user's registered email.
        tags: Optional list of tags to associate with the task.
    """
    # Use string user_id directly (Phase 2 uses string IDs)
    if not user_id or not isinstance(user_id, str):
        raise ValueError("Invalid user_id format")

    # 2. Database Operation (Stateless)
    email_to_use = notify_email
    
    async for session in get_async_session():
        # If no email provided, try to look it up from User table
        if not email_to_use:
            try:
                # Query User table
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user and user.email:
                    email_to_use = user.email
                    logger.info(f"📧 Found registered email for user {user_id}: {email_to_use}")
                else:
                    logger.warning(f"⚠️ No user found or no email for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to lookup user email: {e}")

        # Create Task
        repo = TaskRepository(session)
        task = await repo.create(
            user_id=user_id,
            title=title,
            description=description,
            notify_email=email_to_use, # Save the email we found/used
            tags=tags
        )

    # 3. Side Effect: Email Notification (only if email found)
    email_sent = False
    if email_to_use:
        try:
            asyncio.create_task(
                email_service.send_notification(
                    to_email=email_to_use,
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
        "email_sent": email_sent,
        "tags": [tag.name for tag in task.tags] if hasattr(task, 'tags') and task.tags else []
    }
