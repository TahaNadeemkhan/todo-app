"""
Database-backed ChatKit Store implementation.
Maps ChatKit Store interface to PostgreSQL Conversation/Message models.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from chatkit.store import Store
from chatkit.types import Thread, ThreadItem, ThreadMetadata, Page
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.conversation_repository import ConversationRepository
from repositories.message_repository import MessageRepository
from models.conversation import Conversation
from models.message import Message, MessageRole


class DatabaseChatKitStore(Store[str]):
    """Database-backed implementation of ChatKit Store interface.

    Maps ChatKit abstractions to PostgreSQL:
    - Thread -> Conversation model
    - ThreadItem -> Message model
    - Context type: str (user_id)
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)

    def _conversation_to_thread(self, conversation: Conversation) -> Thread:
        """Convert Conversation model to ChatKit Thread."""
        return Thread(
            id=str(conversation.id),
            created_at=int(conversation.created_at.timestamp()),
            updated_at=int(conversation.updated_at.timestamp()),
        )

    def _message_to_thread_item(self, message: Message) -> ThreadItem:
        """Convert Message model to ChatKit ThreadItem."""
        return ThreadItem(
            id=str(message.id),
            role=message.role.value,  # "user" or "assistant"
            content=[{"type": "text", "text": message.content}],
            created_at=int(message.created_at.timestamp()),
        )

    async def load_thread(self, thread_id: str, context: str) -> ThreadMetadata | None:
        """Load a thread by ID."""
        user_id = context
        try:
            conversation_uuid = UUID(thread_id)
        except ValueError:
            return None

        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            return None

        return self._conversation_to_thread(conversation)

    async def save_thread(self, thread: ThreadMetadata, context: str) -> None:
        """Save a thread (create new conversation)."""
        user_id = context
        # Check if thread already exists
        existing = await self.load_thread(thread.id, user_id)
        if existing:
            # Thread already exists, no need to create
            return

        # Create new conversation with the provided thread ID
        conversation = Conversation(
            id=UUID(thread.id),
            user_id=user_id,
        )
        self.session.add(conversation)
        await self.session.commit()

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        context: str,
    ) -> Page[Thread]:
        """Load all threads for a user with pagination."""
        user_id = context
        offset = 0
        if after:
            try:
                offset = int(after)
            except ValueError:
                offset = 0

        conversations = await self.conversation_repo.get_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        threads = [self._conversation_to_thread(c) for c in conversations]

        # Calculate next cursor and has_more
        has_more = len(threads) == limit
        next_after = str(offset + len(threads)) if has_more else None

        return Page(data=threads, has_more=has_more, after=next_after)

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: str,
    ) -> Page[ThreadItem]:
        """Load items for a thread with pagination."""
        user_id = context
        try:
            conversation_uuid = UUID(thread_id)
        except ValueError:
            return Page(data=[], has_more=False, after=None)

        # Verify thread belongs to user
        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            return Page(data=[], has_more=False, after=None)

        offset = 0
        if after:
            try:
                offset = int(after)
            except ValueError:
                offset = 0

        # Load messages (ordered by created_at ascending for chat history)
        messages = await self.message_repo.get_history(
            conversation_id=conversation_uuid,
            limit=limit
        )

        thread_items = [self._message_to_thread_item(m) for m in messages]

        # Calculate next cursor and has_more
        has_more = len(thread_items) == limit
        next_after = str(offset + len(thread_items)) if has_more else None

        return Page(data=thread_items, has_more=has_more, after=next_after)

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: str,
    ) -> None:
        """Add an item to a thread (create new message)."""
        user_id = context
        try:
            conversation_uuid = UUID(thread_id)
        except ValueError:
            raise ValueError(f"Invalid thread_id: {thread_id}")

        # Verify thread exists and belongs to user
        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            raise ValueError(f"Thread {thread_id} not found for user {user_id}")

        # Extract text content from ThreadItem
        content_text = ""
        for content_part in item.content:
            if content_part.get("type") == "text":
                content_text = content_part.get("text", "")
                break

        # Convert role to MessageRole enum
        role = MessageRole.user if item.role == "user" else MessageRole.assistant

        # Create message
        message = Message(
            id=UUID(item.id),
            conversation_id=conversation_uuid,
            user_id=user_id,
            role=role,
            content=content_text,
        )
        self.session.add(message)
        await self.session.commit()

    async def save_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: str,
    ) -> None:
        """Update an existing item (message)."""
        # For now, we don't support message updates
        # ChatKit primarily appends messages
        pass

    async def load_item(
        self,
        thread_id: str,
        item_id: str,
        context: str,
    ) -> ThreadItem | None:
        """Load a specific item (message)."""
        user_id = context
        try:
            conversation_uuid = UUID(thread_id)
            message_uuid = UUID(item_id)
        except ValueError:
            return None

        # Get the message from database
        messages = await self.message_repo.get_by_conversation(conversation_uuid, limit=1000)

        for message in messages:
            if message.id == message_uuid and message.user_id == user_id:
                return self._message_to_thread_item(message)

        return None

    async def delete_thread(self, thread_id: str, context: str) -> None:
        """Delete a thread and all its items."""
        user_id = context
        try:
            conversation_uuid = UUID(thread_id)
        except ValueError:
            return

        # Verify ownership before deletion
        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if conversation and conversation.user_id == user_id:
            await self.conversation_repo.delete(conversation_uuid)

    async def delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        context: str,
    ) -> None:
        """Delete a specific item from a thread (message)."""
        # Not implemented - we don't support individual message deletion
        pass

    async def save_attachment(
        self,
        attachment,
        context: str,
    ) -> None:
        """Save attachment data. Not supported in this implementation."""
        raise NotImplementedError("Attachments not supported in database store")

    async def load_attachment(
        self,
        attachment_id: str,
        context: str,
    ):
        """Load attachment data. Not supported in this implementation."""
        raise NotImplementedError("Attachments not supported in database store")

    async def delete_attachment(
        self,
        attachment_id: str,
        context: str,
    ) -> None:
        """Delete attachment data. Not supported in this implementation."""
        raise NotImplementedError("Attachments not supported in database store")
