from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.task import Task

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, title: str, description: Optional[str] = None) -> Task:
        """Create a new task."""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_user(
        self, 
        user_id: str, 
        completed: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """List tasks for a user with pagination."""
        query = select(Task).where(Task.user_id == user_id)
        if completed is not None:
            query = query.where(Task.completed == completed)
        
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_user(self, user_id: str, completed: Optional[bool] = None) -> List[Task]:
        """Backward compatibility alias for list_by_user without pagination."""
        return await self.get_by_user(user_id, completed, limit=100)

    async def get_by_id(self, task_id: int, user_id: str) -> Optional[Task]:
        """Get task by ID and user_id."""
        query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, task_id: int, user_id: str, **updates) -> Task:
        """Update task."""
        task = await self.get_by_id(task_id, user_id)
        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: int, user_id: str) -> bool:
        """Delete task."""
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True
