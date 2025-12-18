from uuid import UUID
from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.conversation import Conversation

class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID) -> Conversation:
        """Create a new conversation for a user."""
        conversation = Conversation(user_id=user_id)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def get_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get conversation by ID."""
        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: UUID, limit: int = 20, offset: int = 0) -> List[Conversation]:
        """Get conversations for a user with pagination."""
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def delete(self, conversation_id: UUID) -> bool:
        """Delete a conversation by ID."""
        conversation = await self.get_by_id(conversation_id)
        if not conversation:
            return False
        
        await self.session.delete(conversation)
        await self.session.commit()
        return True
