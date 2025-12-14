from typing import Annotated, Sequence
from datetime import datetime, timezone
import asyncio

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select

from todo_app.db import get_session
from todo_app.deps import ValidatedUserId
from todo_app.models import Task, Notification
from todo_app.schemas import TaskResponse, TaskCreate, TaskUpdate, Priority
from todo_app.services.email_service import email_service

router = APIRouter(prefix="/api", tags=["tasks"])
SessionDep = Annotated[Session, Depends(get_session)]


async def send_task_notification(
    session: Session,
    task: Task,
    notification_type: str,
    message: str,
):
    """Send email notification and save to database."""
    if not task.notifications_enabled or not task.notify_email:
        return

    # Send email
    email_sent = await email_service.send_notification(
        to_email=task.notify_email,
        notification_type=notification_type,
        task_title=task.title,
        task_description=task.description,
        due_date=task.due_date,
    )

    if email_sent:
        # Save notification to database
        notification = Notification(
            user_id=task.user_id,
            task_id=task.id,
            type=notification_type,
            title=f"{notification_type.replace('_', ' ').title()}: {task.title}",
            message=message,
            email_sent_to=task.notify_email,
        )
        session.add(notification)
        session.commit()


@router.get("/{user_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    user_id: ValidatedUserId,
    session: SessionDep,
    completed: bool | None = None,
    priority: Priority | None = None,
    due_date_start: datetime | None = None,
    due_date_end: datetime | None = None,
) -> Sequence[Task]:
    """
    List all tasks for a specific user with optional filters.
    """
    statement = select(Task).where(Task.user_id == user_id)
    
    if completed is not None:
        statement = statement.where(Task.completed == completed)
    if priority is not None:
        statement = statement.where(Task.priority == priority)
    if due_date_start is not None:
        statement = statement.where(Task.due_date >= due_date_start)
    if due_date_end is not None:
        statement = statement.where(Task.due_date <= due_date_end)

    statement = statement.order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return tasks


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: ValidatedUserId,
    task_in: TaskCreate,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> Task:
    """
    Create a new task.
    """
    task = Task.model_validate(task_in, update={"user_id": user_id})
    session.add(task)
    session.commit()
    session.refresh(task)

    # Send notification in background
    if task.notifications_enabled and task.notify_email:
        background_tasks.add_task(
            send_task_notification,
            session,
            task,
            "task_created",
            f"New task '{task.title}' has been created.",
        )

    return task


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: ValidatedUserId,
    task_id: int,
    session: SessionDep,
) -> Task:
    """
    Get a single task by ID.
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: ValidatedUserId,
    task_id: int,
    task_in: TaskUpdate,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> Task:
    """
    Update a task.
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    task.sqlmodel_update(update_data)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Send notification in background
    if task.notifications_enabled and task.notify_email:
        background_tasks.add_task(
            send_task_notification,
            session,
            task,
            "task_updated",
            f"Task '{task.title}' has been updated.",
        )

    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: ValidatedUserId,
    task_id: int,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> None:
    """
    Delete a task.
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Store task info for notification before deleting
    task_title = task.title
    notify_email = task.notify_email
    notifications_enabled = task.notifications_enabled
    user_id_str = task.user_id

    session.delete(task)
    session.commit()

    # Send notification in background (create a temporary task object for email)
    if notifications_enabled and notify_email:
        # Save notification to database
        notification = Notification(
            user_id=user_id_str,
            task_id=None,  # Task is deleted
            type="task_deleted",
            title=f"Task Deleted: {task_title}",
            message=f"Task '{task_title}' has been deleted.",
            email_sent_to=notify_email,
        )
        session.add(notification)
        session.commit()

        # Send email
        background_tasks.add_task(
            email_service.send_notification,
            notify_email,
            "task_deleted",
            task_title,
            None,
            None,
        )

    return None


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    user_id: ValidatedUserId,
    task_id: int,
    session: SessionDep,
    # No input needed, just toggle
) -> Task:
    """
    Toggle task completion status.
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task