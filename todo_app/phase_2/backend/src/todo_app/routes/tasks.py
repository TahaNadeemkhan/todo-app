from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from todo_app.db import get_session
from todo_app.deps import ValidatedUserId
from todo_app.models import Task
from todo_app.schemas import TaskResponse, TaskCreate

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