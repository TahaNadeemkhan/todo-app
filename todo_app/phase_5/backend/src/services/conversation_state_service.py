"""
T058: Conversation State Service - Dapr State Store for conversation history

Migrates conversation storage from direct PostgreSQL to Dapr State Store.
This provides portability across different state backends (PostgreSQL, Redis, CosmosDB).

Key Benefits:
- Portable across cloud providers
- Automatic state management via Dapr
- Simplified conversation history retrieval
- Support for TTL and metadata
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel

from services.dapr_state_service import DaprStateService


logger = logging.getLogger(__name__)


class ConversationState(BaseModel):
    """Conversation state stored in Dapr State Store."""
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class MessageState(BaseModel):
    """Message state stored in Dapr State Store."""
    id: UUID
    conversation_id: UUID
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime


class ConversationStateService:
    """
    T058: Service for managing conversation state using Dapr State Store.
    
    Replaces direct PostgreSQL access with Dapr State API for portability.
    """

    def __init__(self, dapr_state_service: Optional[DaprStateService] = None):
        """
        Initialize ConversationStateService.
        
        Args:
            dapr_state_service: DaprStateService instance (creates new if None)
        """
        self.state_service = dapr_state_service or DaprStateService(store_name="statestore")
        logger.info("ConversationStateService initialized")

    def _conversation_key(self, conversation_id: UUID) -> str:
        """Generate state key for conversation."""
        return f"conversation:{conversation_id}"

    def _user_conversations_key(self, user_id: str) -> str:
        """Generate state key for user's conversation list."""
        return f"user:{user_id}:conversations"

    def _messages_key(self, conversation_id: UUID) -> str:
        """Generate state key for conversation messages."""
        return f"conversation:{conversation_id}:messages"

    async def create_conversation(self, user_id: str) -> ConversationState:
        """
        Create a new conversation for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            ConversationState: Created conversation
        """
        conversation_id = uuid4()
        now = datetime.utcnow()
        
        conversation = ConversationState(
            id=conversation_id,
            user_id=user_id,
            created_at=now,
            updated_at=now
        )
        
        # Save conversation state
        await self.state_service.save_state(
            key=self._conversation_key(conversation_id),
            value=conversation.model_dump(mode="json")
        )
        
        # Add to user's conversation list
        user_conversations = await self.state_service.get_state(
            key=self._user_conversations_key(user_id),
            default=[]
        )
        user_conversations.append(str(conversation_id))
        
        await self.state_service.save_state(
            key=self._user_conversations_key(user_id),
            value=user_conversations
        )
        
        logger.info(f"Conversation created: id={conversation_id}, user_id={user_id}")
        
        return conversation

    async def get_conversation(self, conversation_id: UUID) -> Optional[ConversationState]:
        """
        Get conversation by ID.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            ConversationState or None if not found
        """
        conversation_data = await self.state_service.get_state(
            key=self._conversation_key(conversation_id)
        )
        
        if not conversation_data:
            return None
        
        return ConversationState(**conversation_data)

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[ConversationState]:
        """
        Get conversations for a user with pagination.
        
        Args:
            user_id: User ID
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
            
        Returns:
            List of ConversationState objects
        """
        conversation_ids = await self.state_service.get_state(
            key=self._user_conversations_key(user_id),
            default=[]
        )
        
        # Apply pagination
        paginated_ids = conversation_ids[offset:offset + limit]
        
        # Fetch conversations
        conversations = []
        for conv_id_str in paginated_ids:
            conv_id = UUID(conv_id_str)
            conversation = await self.get_conversation(conv_id)
            if conversation:
                conversations.append(conversation)
        
        # Sort by updated_at descending
        conversations.sort(key=lambda c: c.updated_at, reverse=True)
        
        return conversations

    async def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str
    ) -> MessageState:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role ("user" or "assistant")
            content: Message content
            
        Returns:
            MessageState: Created message
        """
        message_id = uuid4()
        now = datetime.utcnow()
        
        message = MessageState(
            id=message_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=now
        )
        
        # Get existing messages
        messages = await self.state_service.get_state(
            key=self._messages_key(conversation_id),
            default=[]
        )
        
        # Append new message
        messages.append(message.model_dump(mode="json"))
        
        # Save updated messages
        await self.state_service.save_state(
            key=self._messages_key(conversation_id),
            value=messages
        )
        
        # Update conversation's updated_at timestamp
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = now
            await self.state_service.save_state(
                key=self._conversation_key(conversation_id),
                value=conversation.model_dump(mode="json")
            )
        
        logger.info(
            f"Message added: conversation_id={conversation_id}, "
            f"role={role}, message_id={message_id}"
        )
        
        return message

    async def get_conversation_history(
        self,
        conversation_id: UUID,
        limit: int = 50
    ) -> List[MessageState]:
        """
        Get conversation message history.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to return
            
        Returns:
            List of MessageState objects (ordered by created_at ascending)
        """
        messages_data = await self.state_service.get_state(
            key=self._messages_key(conversation_id),
            default=[]
        )
        
        # Convert to MessageState objects
        messages = [MessageState(**msg) for msg in messages_data]
        
        # Sort by created_at ascending (oldest first)
        messages.sort(key=lambda m: m.created_at)
        
        # Apply limit (get most recent N messages)
        if len(messages) > limit:
            messages = messages[-limit:]
        
        return messages

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        # Get conversation to find user_id
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        # Delete conversation state
        await self.state_service.delete_state(
            key=self._conversation_key(conversation_id)
        )
        
        # Delete messages
        await self.state_service.delete_state(
            key=self._messages_key(conversation_id)
        )
        
        # Remove from user's conversation list
        user_conversations = await self.state_service.get_state(
            key=self._user_conversations_key(conversation.user_id),
            default=[]
        )
        
        if str(conversation_id) in user_conversations:
            user_conversations.remove(str(conversation_id))
            await self.state_service.save_state(
                key=self._user_conversations_key(conversation.user_id),
                value=user_conversations
            )
        
        logger.info(f"Conversation deleted: id={conversation_id}")
        
        return True

    def close(self) -> None:
        """Close Dapr State Service and cleanup resources."""
        if self.state_service:
            self.state_service.close()
            logger.info("ConversationStateService closed")


# ============================================================================
# Factory Function
# ============================================================================

def create_conversation_state_service() -> ConversationStateService:
    """
    Factory function to create ConversationStateService instance.
    
    Returns:
        ConversationStateService: Configured instance
    """
    return ConversationStateService()
