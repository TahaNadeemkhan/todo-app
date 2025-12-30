"""
Task CRUD API endpoints for Phase 3.
Adapted from Phase 2 with async/await patterns.
"""

import asyncio
import logging
from typing import Sequence
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_session
from models.task import Task
from schemas import TaskResponse, TaskCreate, TaskUpdate, Priority
from repositories.task_repository import TaskRepository
from services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks"])


async def send_email_notification(
    user_id: str,
    task_id: int,
    notify_email: str,
    notification_type: str,
    task_title: str,
    task_description: str | None,
    due_date: datetime | None,
):
    """Send email notification in background (fire and forget)."""
    try:
        logger.info(f"[EmailBG] Starting email send to: {notify_email}")
        email_sent = await email_service.send_notification(
            to_email=notify_email,
            notification_type=notification_type,
            task_title=task_title,
            task_description=task_description,
            due_date=due_date,
        )
        logger.info(f"[EmailBG] Email sent: {email_sent}")
    except Exception as e:
        logger.error(f"[EmailBG] Error: {e}")


@router.get("/{user_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str,
    session: AsyncSession = Depends(get_async_session),
    completed: bool | None = None,
    priority: Priority | None = None,
    due_date_start: datetime | None = None,
    due_date_end: datetime | None = None,
) -> Sequence[Task]:
    """
    List all tasks for a specific user with optional filters.
    """
    repo = TaskRepository(session)

    # For now, use basic filtering via repository
    # Future: Add advanced filters to repository
    tasks = await repo.get_by_user(user_id=user_id, completed=completed)

    # Apply additional filters in memory (can be optimized later)
    if priority is not None:
        tasks = [t for t in tasks if t.priority == priority.value]
    if due_date_start is not None:
        tasks = [t for t in tasks if t.due_date and t.due_date >= due_date_start]
    if due_date_end is not None:
        tasks = [t for t in tasks if t.due_date and t.due_date <= due_date_end]

    return tasks


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_in: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Task:
    """
    Create a new task.
    """
    repo = TaskRepository(session)

    task = await repo.create(
        user_id=user_id,
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        priority=task_in.priority.value,
        notify_email=task_in.notify_email,
        notifications_enabled=task_in.notifications_enabled,
    )

    # Queue email notification in a fire-and-forget manner
    if task.notifications_enabled and task.notify_email:
        logger.info(f"[CreateTask] Queueing notification for task: {task.title}")
        asyncio.create_task(
            send_email_notification(
                user_id=task.user_id,
                task_id=task.id,
                notify_email=task.notify_email,
                notification_type="task_created",
                task_title=task.title,
                task_description=task.description,
                due_date=task.due_date,
            )
        )

    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Task:
    """
    Get a single task by ID.
    """
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    task_in: TaskUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> Task:
    """
    Update a task.
    """
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Build update dict from request
    update_data = task_in.model_dump(exclude_unset=True)

    # Convert priority enum to string if present
    if "priority" in update_data and update_data["priority"] is not None:
        update_data["priority"] = update_data["priority"].value

    # Update task
    updated_task = await repo.update(
        task_id=task_id,
        user_id=user_id,
        **update_data
    )

    # Send notification in background
    if updated_task.notifications_enabled and updated_task.notify_email:
        asyncio.create_task(
            send_email_notification(
                user_id=updated_task.user_id,
                task_id=updated_task.id,
                notify_email=updated_task.notify_email,
                notification_type="task_updated",
                task_title=updated_task.title,
                task_description=updated_task.description,
                due_date=updated_task.due_date,
            )
        )

    return updated_task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Delete a task.
    """
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Store task info for notification before deleting
    task_title = task.title
    notify_email = task.notify_email
    notifications_enabled = task.notifications_enabled

    await repo.delete(task_id, user_id)

    # Send notification in background
    if notifications_enabled and notify_email:
        asyncio.create_task(
            send_email_notification(
                user_id=user_id,
                task_id=task_id,
                notify_email=notify_email,
                notification_type="task_deleted",
                task_title=task_title,
                task_description=None,
                due_date=None,
            )
        )

    return None


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    user_id: str,
    task_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Task:
    """
    Toggle task completion status.
    """
    repo = TaskRepository(session)
    task = await repo.get_by_id(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Toggle completion
    updated_task = await repo.update(
        task_id=task_id,
        user_id=user_id,
        completed=not task.completed
    )

    return updated_task
