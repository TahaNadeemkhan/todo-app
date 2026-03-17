from typing import List, Optional
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, or_
from models.task import Task
import uuid  # Added for UUID generation

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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
        """Create a new task with all fields."""
        task = Task(
            id=str(uuid.uuid4()),  # Generate UUID for new task
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            due_date=due_date,  # Changed from due_at to due_date
            priority=priority,
            notify_email=notify_email,
            notifications_enabled=notifications_enabled,
            tags=tags or [],
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_user(
        self, 
        user_id: str, 
        completed: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: int = 20,
        offset: int = 0
    ) -> List[Task]:
        """List tasks for a user with pagination and sorting."""
        query = select(Task).where(Task.user_id == user_id)
        if completed is not None:
            query = query.where(Task.completed == completed)
        
        # Sorting
        from sqlalchemy import asc, desc, case
        
        if sort_by:
            sort_field = None
            if sort_by == "due_date":
                sort_field = Task.due_date
            elif sort_by == "priority":
                # Custom ordering: high=1, medium=2, low=3
                sort_expression = case(
                    (Task.priority == "high", 1),
                    (Task.priority == "medium", 2),
                    (Task.priority == "low", 3),
                    else_=4
                )
                if sort_order == "desc":
                    query = query.order_by(desc(sort_expression))
                else:
                    query = query.order_by(sort_expression)
                sort_field = None # Handled above
            elif sort_by == "created_at":
                sort_field = Task.created_at
            elif sort_by == "title":
                sort_field = Task.title
            
            if sort_field:
                order_func = desc if sort_order == "desc" else asc
                query = query.order_by(order_func(sort_field).nulls_last())
        else:
            # Default sort: created_at desc
            query = query.order_by(desc(Task.created_at))
        
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_user(self, user_id: str, completed: Optional[bool] = None) -> List[Task]:
        """Backward compatibility alias for list_by_user without pagination."""
        return await self.get_by_user(user_id, completed, limit=100)

    async def get_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        query = select(Task).where(Task.id == task_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update(self, task_id: str, user_id: str, **updates) -> Task:
        """Update task and verify user ownership."""
        task = await self.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Verify user ownership
        if task.user_id != user_id:
            raise ValueError(f"Task {task_id} does not belong to user {user_id}")

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete(self, task_id: str, user_id: str) -> bool:
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

    async def get_unique_tags(self, user_id: str) -> List[str]:
        """Get all unique tags for a user."""
        # Use jsonb_array_elements_text to expand tags array, then distinct
        statement = text("""
            SELECT DISTINCT tag
            FROM tasks, jsonb_array_elements_text(tasks.tags) as tag
            WHERE tasks.user_id = :user_id
            ORDER BY tag
        """)
        result = await self.session.execute(statement, {"user_id": user_id})
        return list(result.scalars().all())

    async def search(self, user_id: str, query_text: str) -> List[Task]:
        """Search tasks by title or description."""
        query = select(Task).where(
            Task.user_id == user_id,
            or_(
                Task.title.ilike(f"%{query_text}%"),
                Task.description.ilike(f"%{query_text}%")
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def filter_by_priority(self, user_id: str, priority: str) -> List[Task]:
        """Filter tasks by priority."""
        query = select(Task).where(
            Task.user_id == user_id,
            Task.priority == priority
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def filter_by_tags(self, user_id: str, tags: List[str]) -> List[Task]:
        """Filter tasks that have at least one of the tags."""
        # Using Postgres JSONB operator ?| (exists any)
        # Note: tags argument must be a tuple for SQLAlchemy params if using tuple()
        query = select(Task).where(Task.user_id == user_id)
        query = query.where(text("tags ?| :tags")).params(tags=tuple(tags))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
