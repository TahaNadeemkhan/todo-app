from typing import List, Optional
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.task import Task
from models.tag import Tag

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_or_create_tags(self, user_id: str, tag_names: List[str]) -> List[Tag]:
        """Find existing tags or create new ones for a user."""
        tags = []
        for name in tag_names:
            name = name.strip().lower()
            if not name:
                continue
            statement = select(Tag).where(Tag.name == name, Tag.user_id == user_id)
            result = await self.session.execute(statement)
            tag = result.scalar_one_or_none()
            if not tag:
                tag = Tag(name=name, user_id=user_id)
                self.session.add(tag)
                # We need to flush or commit to get the ID if needed, 
                # but SQLModel/SQLAlchemy will handle it during association.
            tags.append(tag)
        return tags

    async def create(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: str = "medium",
        notify_email: Optional[str] = None,
        notifications_enabled: bool = False,
        tags: Optional[List[str]] = None,
    ) -> Task:
        """Create a new task with all fields and optional tags."""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            due_date=due_date,
            priority=priority,
            notify_email=notify_email,
            notifications_enabled=notifications_enabled,
        )
        
        if tags:
            task.tags = await self.find_or_create_tags(user_id, tags)
            
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_user(
        self, 
        user_id: str, 
        completed: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
        tags: Optional[List[str]] = None,
    ) -> List[Task]:
        """List tasks for a user with pagination and optional tag filtering."""
        query = select(Task).where(Task.user_id == user_id).options(selectinload(Task.tags))
        
        if completed is not None:
            query = query.where(Task.completed == completed)
            
        if tags:
            # Filter tasks that have ANY of the tags
            query = query.join(Task.tags).where(Tag.name.in_(tags))
        
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_user(self, user_id: str, completed: Optional[bool] = None, tags: Optional[List[str]] = None) -> List[Task]:
        """Backward compatibility alias for list_by_user without pagination."""
        return await self.get_by_user(user_id, completed, limit=100, tags=tags)

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID with tags loaded."""
        query = select(Task).where(Task.id == task_id).options(selectinload(Task.tags))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, task_id: int, user_id: str, tags: Optional[List[str]] = None, **updates) -> Task:
        """Update task and verify user ownership. Optionally update tags."""
        task = await self.get_by_id(task_id) # Already loads tags
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Verify user ownership
        if task.user_id != user_id:
            raise ValueError(f"Task {task_id} does not belong to user {user_id}")

        if tags is not None:
            task.tags = await self.find_or_create_tags(user_id, tags)

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: int, user_id: str) -> bool:
        """Delete task and verify user ownership."""
        task = await self.get_by_id(task_id)
        if not task:
            return False

        # Verify user ownership
        if task.user_id != user_id:
            raise ValueError(f"Task {task_id} does not belong to user {user_id}")

        await self.session.delete(task)
        await self.session.commit()
        return True
