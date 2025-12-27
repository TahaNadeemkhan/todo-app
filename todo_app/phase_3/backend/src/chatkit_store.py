"""
Database-backed ChatKit Store implementation.
Maps ChatKit Store interface to PostgreSQL Conversation/Message models.
"""

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
import hashlib
import logging

from chatkit.store import Store
from chatkit.types import Thread, ThreadItem, ThreadMetadata, Page, UserMessageItem, AssistantMessageItem, AssistantMessageContent
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

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

    def _string_to_uuid(self, string_id: str) -> UUID:
        """Convert any string to a deterministic UUID.

        ChatKit generates thread IDs that are not valid UUIDs.
        This method creates a deterministic UUID from any string.
        """
        try:
            # Try to parse as UUID first
            return UUID(string_id)
        except ValueError:
            # Generate deterministic UUID from string using MD5 hash
            hash_bytes = hashlib.md5(string_id.encode()).digest()
            return UUID(bytes=hash_bytes)

    async def _conversation_to_thread_metadata(self, conversation: Conversation) -> ThreadMetadata:
        """Convert Conversation to ThreadMetadata (without items).

        Used by load_thread() - ChatKit will load items separately via load_thread_items().
        """
        # Load first message for title
        messages = await self.message_repo.get_history(
            conversation_id=conversation.id,
            limit=1
        )

        title = "New Conversation"
        if messages:
            title = messages[0].content[:50] + ("..." if len(messages[0].content) > 50 else "")
            logger.info(f"📝 Loaded title for thread metadata {conversation.id}: '{title}'")

        # Return ThreadMetadata (no items field - ChatKit adds them separately)
        return ThreadMetadata(
            id=str(conversation.id),
            title=title,
            created_at=int(conversation.created_at.timestamp()),
            updated_at=int(conversation.updated_at.timestamp()),
        )

    async def _conversation_to_thread(self, conversation: Conversation) -> Thread:
        """Convert Conversation to Thread (with empty items).

        Used by load_threads() - items array is empty as they're loaded on-demand.
        """
        # Load first message for title
        messages = await self.message_repo.get_history(
            conversation_id=conversation.id,
            limit=1
        )

        title = "New Conversation"
        if messages:
            title = messages[0].content[:50] + ("..." if len(messages[0].content) > 50 else "")
            logger.info(f"📝 Loaded title for thread {conversation.id}: '{title}'")

        # Return Thread with empty items (ChatKit loads items separately when needed)
        return Thread(
            id=str(conversation.id),
            title=title,
            created_at=int(conversation.created_at.timestamp()),
            updated_at=int(conversation.updated_at.timestamp()),
            items=Page(data=[], has_more=False, after=None),
        )

    def _message_to_thread_item(self, message: Message) -> ThreadItem:
        """Convert Message model to ChatKit ThreadItem.

        ThreadItem is a Union type (UserMessageItem | AssistantMessageItem).
        We must instantiate the specific type based on the message role.

        Based on actual ChatKit structure from debug logs, UserMessageItem requires:
        - id, thread_id, created_at, type, content, attachments, quoted_text, inference_options
        """
        from chatkit.types import UserMessageTextContent

        if message.role == MessageRole.user:
            # User message - provide all required fields
            return UserMessageItem(
                id=str(message.id),
                thread_id=str(message.conversation_id),
                created_at=int(message.created_at.timestamp()),
                type="user_message",
                content=[UserMessageTextContent(type="input_text", text=message.content)],
                attachments=[],
                quoted_text="",
                inference_options={"tool_choice": None, "model": None},
            )
        else:
            # Assistant message - use proper AssistantMessageContent type
            return AssistantMessageItem(
                id=str(message.id),
                thread_id=str(message.conversation_id),
                created_at=int(message.created_at.timestamp()),
                type="assistant_message",
                content=[AssistantMessageContent(type="output_text", text=message.content)],
                attachments=[],
            )

    async def load_thread(self, thread_id: str, context: str) -> ThreadMetadata | None:
        """Load a thread by ID (returns metadata only, items loaded separately)."""
        user_id = context
        conversation_uuid = self._string_to_uuid(thread_id)

        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            return None

        return await self._conversation_to_thread_metadata(conversation)

    async def save_thread(self, thread: ThreadMetadata, context: str) -> None:
        """Save a thread (create new conversation)."""
        user_id = context
        logger.info(f"💾 save_thread called: thread_id={thread.id}, user_id={user_id}")

        # Check if thread already exists
        existing = await self.load_thread(thread.id, user_id)
        if existing:
            # Thread already exists, no need to create
            logger.info(f"✅ Thread {thread.id} already exists, skipping")
            return

        # Create new conversation with deterministic UUID from thread ID
        conversation = Conversation(
            id=self._string_to_uuid(thread.id),
            user_id=user_id,
        )
        self.session.add(conversation)
        await self.session.commit()
        logger.info(f"✅ Created new conversation: {conversation.id} for thread {thread.id}")

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        context: str,
        order: str = "desc",  # Added missing parameter
    ) -> Page[Thread]:
        """Load all threads for a user with pagination.

        Args:
            limit: Maximum number of threads to return
            after: Pagination cursor
            context: User ID
            order: Sort order - "desc" (newest first) or "asc" (oldest first)
        """
        user_id = context
        offset = 0
        if after:
            try:
                offset = int(after)
            except ValueError:
                offset = 0

        logger.info(f"📋 load_threads called: user_id={user_id}, limit={limit}, offset={offset}, order={order}")

        conversations = await self.conversation_repo.get_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        logger.info(f"📋 Found {len(conversations)} conversations in database")

        # Convert conversations to threads (with titles but empty items)
        threads = []
        for c in conversations:
            thread = await self._conversation_to_thread(c)
            threads.append(thread)

        # Apply ordering (repository returns newest first by default)
        if order == "asc":
            threads.reverse()

        # Calculate next cursor and has_more
        has_more = len(threads) == limit
        next_after = str(offset + len(threads)) if has_more else None

        logger.info(f"📋 Returning {len(threads)} threads (has_more={has_more}, next_after={next_after})")
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
        conversation_uuid = self._string_to_uuid(thread_id)

        logger.info(f"💬 load_thread_items called: thread_id={thread_id}, limit={limit}, order={order}")

        # Verify thread belongs to user
        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            logger.warning(f"⚠️ Thread {thread_id} not found or doesn't belong to user {user_id}")
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

        logger.info(f"💬 Loaded {len(messages)} messages from database")
        for msg in messages:
            logger.info(f"  - {msg.role}: {msg.content[:50]}...")

        thread_items = [self._message_to_thread_item(m) for m in messages]

        logger.info(f"💬 Converted to {len(thread_items)} thread items")

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
        conversation_uuid = self._string_to_uuid(thread_id)  # ✅ Use helper method

        # Verify thread exists and belongs to user
        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            raise ValueError(f"Thread {thread_id} not found for user {user_id}")

        # Extract text content from ThreadItem (Pydantic models, not dicts)
        # DEBUG: Log the item structure
        logger.info(f"=== add_thread_item DEBUG ===")
        logger.info(f"item type = {type(item)}")
        logger.info(f"item.__class__.__name__ = {item.__class__.__name__}")
        logger.info(f"item.content type = {type(item.content)}")
        logger.info(f"item.content length = {len(item.content) if hasattr(item.content, '__len__') else 'N/A'}")
        logger.info(f"item.content = {item.content}")
        logger.info(f"item dict = {item.model_dump() if hasattr(item, 'model_dump') else item.__dict__}")

        content_text = ""
        for idx, content_part in enumerate(item.content):
            logger.info(f"content_part[{idx}] type = {type(content_part)}")
            logger.info(f"content_part[{idx}] = {content_part}")
            logger.info(f"content_part[{idx}] dict = {content_part.model_dump() if hasattr(content_part, 'model_dump') else content_part.__dict__ if hasattr(content_part, '__dict__') else 'no dict'}")

            # content_part is a Pydantic object with .type and .text attributes
            # ChatKit sends:
            # - 'input_text' for user messages
            # - 'output_text' for assistant messages (NOT 'text'!)
            if hasattr(content_part, 'type') and content_part.type in ("text", "input_text", "output_text"):
                content_text = getattr(content_part, 'text', "")
                logger.info(f"✅ Found text content (type={content_part.type}): '{content_text}'")
                break
            else:
                logger.warning(f"⚠️ content_part type is {getattr(content_part, 'type', 'NONE')}, expected 'text', 'input_text', or 'output_text'")

        logger.info(f"Final content_text = '{content_text}'")
        logger.info(f"=== END DEBUG ===")

        # Validate content is not empty
        if not content_text or not content_text.strip():
            logger.error(f"❌ Content is empty! item.content was: {item.content}")
            raise ValueError(f"Cannot save message with empty content. Item: {item.model_dump() if hasattr(item, 'model_dump') else item}")

        # Convert role to MessageRole enum (determine from item type)
        role = MessageRole.user if isinstance(item, UserMessageItem) else MessageRole.assistant

        # Create message with deterministic UUID
        message = Message(
            id=self._string_to_uuid(item.id),  # ✅ Use helper method
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
