from uuid import UUID
from typing import List
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.message import Message, MessageRole

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        conversation_id: UUID,
        user_id: str,
        role: MessageRole,
        content: str
    ) -> Message:
        """Create a new message."""
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_by_conversation(
        self,
        conversation_id: UUID,
        limit: int = 20,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation with pagination."""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_history(self, conversation_id: UUID, limit: int = 50) -> List[Message]:
        """Get conversation history ordered by created_at ascending (oldest first)."""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        messages = list(result.scalars().all())
        # Reverse to get oldest first
        return list(reversed(messages))
