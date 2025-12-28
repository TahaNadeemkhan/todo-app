---
name: fastapi-design
description: Design RESTful APIs using FastAPI modern best practices. Use when creating endpoints, routers, or API structures. Triggers on mentions of FastAPI, REST API, endpoints, routers, or API design.
---

# FastAPI Design Skill

## Mandatory Rules

### 1. Annotated Dependencies (REQUIRED)

```python
# CORRECT
SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/tasks")
async def list_tasks(session: SessionDep) -> list[TaskRead]: ...

# WRONG - Never use bare Depends
async def list_tasks(session: Session = Depends(get_session)): ...
```

### 2. Pydantic v2 Methods (REQUIRED)

```python
# CORRECT
task = Task.model_validate(data)
data = task.model_dump(exclude_unset=True)

# WRONG - Deprecated v1
task = Task.from_orm(data)  # NEVER
data = task.dict()          # NEVER
```

### 3. Router Modularity (REQUIRED)

- `main.py` = App config, middleware, CORS only
- `routers/*.py` = All endpoint logic via `APIRouter`

### 4. Strict Typing (REQUIRED)

- No `Any` type
- All functions have return type annotations
- All endpoints have `response_model`

For detailed examples, see [examples.md](examples.md).

## Checklist

- [ ] `Annotated[T, Depends(...)]` for all dependencies
- [ ] `model_validate()` / `model_dump()` (Pydantic v2)
- [ ] All endpoints in routers, not `main.py`
- [ ] No `Any` types
- [ ] Response models on all endpoints
