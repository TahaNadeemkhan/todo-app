from typing import Annotated, Sequence
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from todo_app.db import get_session
from todo_app.deps import ValidatedUserId
from todo_app.models import Task
from todo_app.schemas import TaskResponse, TaskCreate, TaskUpdate

router = APIRouter(prefix="/api", tags=["tasks"])
SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/{user_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    user_id: ValidatedUserId,
    session: SessionDep,
) -> Sequence[Task]:
    """
    List all tasks for a specific user.
    """
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()
    return tasks


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: ValidatedUserId,
    task_in: TaskCreate,
    session: SessionDep,
) -> Task:
    """
    Create a new task.
    """
    task = Task.model_validate(task_in, update={"user_id": user_id})
    session.add(task)
    session.commit()
    session.refresh(task)
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
    return task


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: ValidatedUserId,
    task_id: int,
    session: SessionDep,
) -> None:
    """
    Delete a task.
    """
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return None


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    user_id: ValidatedUserId,
    task_id: int,
    session: SessionDep,
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
