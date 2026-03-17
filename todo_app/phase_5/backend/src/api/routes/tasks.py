"""
Task CRUD API endpoints for Phase 3.
Adapted from Phase 2 with async/await patterns.
Refactored for Phase 5 to use TaskService and Event-Driven Architecture.
"""

import asyncio
import logging
from typing import Sequence, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_session
from models.task import Task
from schemas import (
    TaskResponse, 
    TaskCreate, 
    TaskUpdate, 
    Priority, 
    RecurrenceResponse, 
    ReminderCreate, 
    ReminderResponse
)
from deps import get_task_service
from services.task_service import TaskService
from services.recurrence_service import RecurrenceService
from services.reminder_service import ReminderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["tasks"])


@router.get("/{user_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str,
    completed: bool | None = None,
    priority: Priority | None = None,
    tags: str | None = None, # Comma separated
    search: str | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
    due_date_start: datetime | None = None,
    due_date_end: datetime | None = None,
    task_service: TaskService = Depends(get_task_service),
) -> Sequence[Task]:
    """
    List all tasks for a specific user with optional filters and sorting.
    """
    tag_list = tags.split(",") if tags else None
    priority_val = priority.value if priority else None

    # Use TaskService to list tasks
    tasks = await task_service.list_user_tasks(
        user_id=user_id, 
        completed=completed,
        priority=priority_val,
        tags=tag_list,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # Apply date filters in memory (until moved to repo)
    if due_date_start is not None:
        tasks = [t for t in tasks if t.due_date and t.due_date >= due_date_start]
    if due_date_end is not None:
        tasks = [t for t in tasks if t.due_date and t.due_date <= due_date_end]

    return tasks


@router.get("/{user_id}/tags", response_model=List[str])
async def get_user_tags(
    user_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> List[str]:
    """
    Get all unique tags used by a user.
    """
    return await task_service.get_unique_tags(user_id)


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_in: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
) -> Task:
    """
    Create a new task via TaskService (publishes task.created event).
    """
    # Prepare arguments for TaskService
    create_kwargs = {
        "user_id": user_id,
        "title": task_in.title,
        "description": task_in.description,
        "priority": task_in.priority.value,
        "tags": task_in.tags,
        "due_date": task_in.due_date,
        "notify_email": task_in.notify_email,
        "notifications_enabled": task_in.notifications_enabled,
        "has_recurrence": task_in.has_recurrence,
        "recurrence_pattern": task_in.recurrence_pattern.value if task_in.recurrence_pattern else None,
        "recurrence_interval": task_in.recurrence_interval,
        "recurrence_days_of_week": task_in.recurrence_days_of_week,
        "recurrence_day_of_month": task_in.recurrence_day_of_month,
    }

    # Process reminders
    if task_in.reminders:
        create_kwargs["reminders"] = [
            {
                "remind_before": r.remind_before,
                "channels": r.channels
            }
            for r in task_in.reminders
        ]

    # Delegate to TaskService
    task = await task_service.create_task(**create_kwargs)
    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> Task:
    """
    Get a single task by ID.
    """
    task = await task_service.get_task(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: str,
    task_in: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
) -> Task:
    """
    Update a task via TaskService (publishes task.updated event).
    """
    # Build update dict
    update_data = task_in.model_dump(exclude_unset=True)

    # Convert priority enum to string if present
    if "priority" in update_data and update_data["priority"] is not None:
        update_data["priority"] = update_data["priority"].value

    try:
        updated_task = await task_service.update_task(
            task_id=task_id,
            user_id=user_id,
            changes=update_data
        )
        return updated_task
    except ValueError as e:
        # Handle not found or not authorized
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> None:
    """
    Delete a task via TaskService (publishes task.deleted event).
    """
    try:
        deleted = await task_service.delete_task(task_id, user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return None


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    user_id: str,
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> Task:
    """
    Toggle task completion status via TaskService (publishes task.completed event).
    Note: Currently TaskService.complete_task only sets completed=True.
    Toggle logic is handled here or in service? 
    TaskService.complete_task() sets completed=True.
    If we want toggle, we need logic. For now, let's assume this endpoint marks COMPLETE.
    """
    # Check current status first
    task = await task_service.get_task(task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.completed:
        # Mark complete
        return await task_service.complete_task(task_id, user_id)
    else:
        # Mark incomplete (reopen) - TaskService doesn't have explicit reopen_task yet
        # We fall back to update_task for reopening
        return await task_service.update_task(
            task_id=task_id,
            user_id=user_id,
            changes={"completed": False, "completed_at": None}
        )


# ============================================================================
# T083-T084: Recurrence Management Endpoints
# ============================================================================

@router.get("/{user_id}/tasks/{task_id}/recurrence", response_model=RecurrenceResponse)
async def get_task_recurrence(
    user_id: str,
    task_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    T083: Get recurrence information for a task.
    """
    # Verify task exists and belongs to user
    # We can keep using Repositories directly for read-only sub-resources if TaskService doesn't wrap them yet
    # Or inject RecurrenceService directly (which is what was done before)
    
    # ... (Keep implementation but maybe verify task using TaskService?)
    # For now, let's keep it as is, using session directly for recurrence/reminders
    # as TaskService might not expose granular sub-resource methods yet.
    
    # ... (Implementation unchanged from previous file content for recurrence/reminders)
    pass # Replaced by original content in subsequent block



# ============================================================================
# T083-T084: Recurrence Management Endpoints
# ============================================================================

@router.get("/{user_id}/tasks/{task_id}/recurrence", response_model=RecurrenceResponse)
async def get_task_recurrence(
    user_id: str,
    task_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    T083: Get recurrence information for a task.

    Returns recurrence pattern, interval, days_of_week, next_due_at, etc.
    """
    # Verify task exists and belongs to user
    task_repo = TaskRepository(session)
    task = await task_repo.get_by_id(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get recurrence
    recurrence_service = RecurrenceService(session)
    recurrence = await recurrence_service.get_recurrence(task_id)

    if not recurrence:
        raise HTTPException(
            status_code=404,
            detail="Task does not have recurrence"
        )

    return recurrence


@router.delete("/{user_id}/tasks/{task_id}/recurrence")
async def stop_task_recurrence(
    user_id: str,
    task_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    T084: Stop recurrence for a task (deactivate).

    Future occurrences will not be generated when the task is completed.
    """
    # Verify task exists and belongs to user
    task_repo = TaskRepository(session)
    task = await task_repo.get_by_id(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Stop recurrence
    recurrence_service = RecurrenceService(session)
    try:
        updated_recurrence = await recurrence_service.stop_recurrence(
            task_id=task_id,
            user_id=user_id
        )

        return {
            "message": "Recurrence stopped successfully",
            "recurrence_id": updated_recurrence.id,
            "active": updated_recurrence.active
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# T103-T104: Reminder Management Endpoints
# ============================================================================

@router.get("/{user_id}/tasks/{task_id}/reminders", response_model=list[ReminderResponse])
async def get_task_reminders(
    user_id: str,
    task_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> list:
    """
    T103: Get all reminders for a task.

    Returns list of reminders with their configuration (remind_before, channels, sent_at).
    """
    # Verify task exists and belongs to user
    task_repo = TaskRepository(session)
    task = await task_repo.get_by_id(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get reminders
    reminder_service = ReminderService(session)
    reminders = await reminder_service.get_reminders_for_task(task_id)

    return reminders


@router.post("/{user_id}/tasks/{task_id}/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def add_reminder_to_task(
    user_id: str,
    task_id: str,
    reminder_in: ReminderCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    T104: Add a reminder to an existing task.

    Creates a new reminder for the task with the specified remind_before and channels.

    Requires:
    - Task must have a due_date set (cannot remind for task without due date)
    - Task must belong to the user
    """
    # Verify task exists and belongs to user
    task_repo = TaskRepository(session)
    task = await task_repo.get_by_id(task_id)

    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify task has due_date
    if not task.due_date:
        raise HTTPException(
            status_code=400,
            detail="Cannot add reminder to task without due date"
        )

    # Create reminder
    reminder_service = ReminderService(session)
    try:
        reminder = await reminder_service.create_reminder(
            task_id=task_id,
            user_id=user_id,
            remind_before=reminder_in.remind_before,
            channels=reminder_in.channels
        )

        return reminder

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
