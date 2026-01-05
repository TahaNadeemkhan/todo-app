# FastAPI Examples

## Complete CRUD Router

```python
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task_create: TaskCreate, session: SessionDep) -> TaskRead:
    task = Task(**task_create.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskRead.model_validate(task)

@router.get("/", response_model=list[TaskRead])
async def list_tasks(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[TaskRead]:
    tasks = session.exec(select(Task).offset(skip).limit(limit)).all()
    return [TaskRead.model_validate(t) for t in tasks]

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, session: SessionDep) -> TaskRead:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)

@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: UUID, task_update: TaskUpdate, session: SessionDep) -> TaskRead:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return TaskRead.model_validate(task)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, session: SessionDep) -> None:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
```

## main.py Structure

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routers import tasks, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

def create_app() -> FastAPI:
    app = FastAPI(title="Todo API", lifespan=lifespan)
    app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
    return app

app = create_app()
```
