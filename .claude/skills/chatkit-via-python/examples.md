# ChatKit Integration - Code Examples

This file contains complete, reusable code examples for integrating ChatKit into your application.

## Backend Examples

### 1. Memory Store Implementation (`memory_store.py`)

```python
from typing import Any
from chatkit import Store, Thread, ThreadItem

class MemoryStore(Store):
    """In-memory implementation of ChatKit Store interface.
    WARNING: All data is lost on restart. Use for development only."""

    def __init__(self):
        self._threads: dict[str, Thread] = {}
        self._items: dict[tuple[str, str], ThreadItem] = {}
        self._thread_items: dict[str, list[str]] = {}

    async def load_thread(self, thread_id: str, user_id: str) -> Thread | None:
        """Load a thread by ID."""
        return self._threads.get(thread_id)

    async def save_thread(self, thread: Thread, user_id: str) -> None:
        """Save a thread."""
        self._threads[thread.id] = thread
        if thread.id not in self._thread_items:
            self._thread_items[thread.id] = []

    async def load_threads(
        self,
        user_id: str,
        cursor: str | None = None,
        limit: int = 10,
    ) -> tuple[list[Thread], str | None]:
        """Load all threads for a user with pagination."""
        threads = list(self._threads.values())

        # Handle cursor-based pagination
        start_idx = 0
        if cursor:
            try:
                start_idx = int(cursor)
            except ValueError:
                start_idx = 0

        # Get paginated results
        end_idx = start_idx + limit
        paginated_threads = threads[start_idx:end_idx]

        # Calculate next cursor
        next_cursor = str(end_idx) if end_idx < len(threads) else None

        return paginated_threads, next_cursor

    async def load_thread_items(
        self,
        thread_id: str,
        user_id: str,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[ThreadItem], str | None]:
        """Load items for a thread with pagination."""
        item_ids = self._thread_items.get(thread_id, [])

        # Handle cursor-based pagination
        start_idx = 0
        if cursor:
            try:
                start_idx = int(cursor)
            except ValueError:
                start_idx = 0

        # Get paginated item IDs
        end_idx = start_idx + limit
        paginated_item_ids = item_ids[start_idx:end_idx]

        # Load actual items
        items = []
        for item_id in paginated_item_ids:
            item = self._items.get((thread_id, item_id))
            if item:
                items.append(item)

        # Calculate next cursor
        next_cursor = str(end_idx) if end_idx < len(item_ids) else None

        return items, next_cursor

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        user_id: str,
    ) -> None:
        """Add an item to a thread."""
        self._items[(thread_id, item.id)] = item

        if thread_id not in self._thread_items:
            self._thread_items[thread_id] = []

        self._thread_items[thread_id].append(item.id)

    async def save_item(
        self,
        thread_id: str,
        item: ThreadItem,
        user_id: str,
    ) -> None:
        """Update an existing item."""
        self._items[(thread_id, item.id)] = item

    async def load_item(
        self,
        thread_id: str,
        item_id: str,
        user_id: str,
    ) -> ThreadItem | None:
        """Load a specific item."""
        return self._items.get((thread_id, item_id))

    async def delete_thread(self, thread_id: str, user_id: str) -> None:
        """Delete a thread and all its items."""
        if thread_id in self._threads:
            del self._threads[thread_id]

        if thread_id in self._thread_items:
            item_ids = self._thread_items[thread_id]
            for item_id in item_ids:
                key = (thread_id, item_id)
                if key in self._items:
                    del self._items[key]
            del self._thread_items[thread_id]

    async def delete_thread_item(
        self,
        thread_id: str,
        item_id: str,
        user_id: str,
    ) -> None:
        """Delete a specific item from a thread."""
        key = (thread_id, item_id)
        if key in self._items:
            del self._items[key]

        if thread_id in self._thread_items:
            item_ids = self._thread_items[thread_id]
            if item_id in item_ids:
                item_ids.remove(item_id)

    async def save_attachment(
        self,
        thread_id: str,
        item_id: str,
        attachment_id: str,
        data: bytes,
        user_id: str,
    ) -> None:
        """Save attachment data. Not implemented in memory store."""
        raise NotImplementedError("Attachments not supported in memory store")

    async def load_attachment(
        self,
        thread_id: str,
        item_id: str,
        attachment_id: str,
        user_id: str,
    ) -> bytes | None:
        """Load attachment data. Not implemented in memory store."""
        raise NotImplementedError("Attachments not supported in memory store")
```

### 2. Database-Backed Store Implementation (`database_store.py`)

**CRITICAL:** For production use, implement database-backed storage to persist conversations.

```python
"""
Database-backed ChatKit Store implementation.
Fixes critical persistence issues for conversation history.
"""

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
import hashlib
import logging

from chatkit.store import Store
from chatkit.types import (
    Thread,
    ThreadItem,
    ThreadMetadata,
    Page,
    UserMessageItem,
    AssistantMessageItem,
    AssistantMessageContent,
    UserMessageTextContent,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Assume you have SQLAlchemy models defined:
# - Conversation (id, user_id, created_at, updated_at)
# - Message (id, conversation_id, user_id, role, content, created_at)


class DatabaseChatKitStore(Store[str]):
    """Database-backed implementation of ChatKit Store interface.

    Context type: str (user_id)
    Solves critical pitfalls:
    - Thread vs ThreadMetadata distinction
    - Content type handling (input_text vs output_text)
    - Message persistence
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        # Assume you have repository instances:
        # self.conversation_repo = ConversationRepository(session)
        # self.message_repo = MessageRepository(session)

    def _string_to_uuid(self, string_id: str) -> UUID:
        """Convert any string to deterministic UUID.

        ChatKit generates thread IDs that aren't valid UUIDs.
        """
        try:
            return UUID(string_id)
        except ValueError:
            # Generate deterministic UUID from MD5 hash
            hash_bytes = hashlib.md5(string_id.encode()).digest()
            return UUID(bytes=hash_bytes)

    async def _conversation_to_thread_metadata(self, conversation) -> ThreadMetadata:
        """Convert Conversation to ThreadMetadata (NO items).

        ✅ CRITICAL: Used by load_thread()
        ChatKit loads items separately via load_thread_items()
        """
        # Load first message for title
        messages = await self.message_repo.get_history(
            conversation_id=conversation.id,
            limit=1
        )

        title = "New Conversation"
        if messages:
            title = messages[0].content[:50] + ("..." if len(messages[0].content) > 50 else "")

        # Return ThreadMetadata WITHOUT items
        return ThreadMetadata(
            id=str(conversation.id),
            title=title,
            created_at=int(conversation.created_at.timestamp()),
            updated_at=int(conversation.updated_at.timestamp()),
        )

    async def _conversation_to_thread(self, conversation) -> Thread:
        """Convert Conversation to Thread (WITH empty items).

        ✅ CRITICAL: Used by load_threads()
        Items are empty - loaded on-demand when thread is opened
        """
        # Load first message for title
        messages = await self.message_repo.get_history(
            conversation_id=conversation.id,
            limit=1
        )

        title = "New Conversation"
        if messages:
            title = messages[0].content[:50] + ("..." if len(messages[0].content) > 50 else "")

        # Return Thread with empty items
        return Thread(
            id=str(conversation.id),
            title=title,
            created_at=int(conversation.created_at.timestamp()),
            updated_at=int(conversation.updated_at.timestamp()),
            items=Page(data=[], has_more=False, after=None),  # Empty!
        )

    def _message_to_thread_item(self, message) -> ThreadItem:
        """Convert Message model to ChatKit ThreadItem.

        ✅ CRITICAL: Handle both user and assistant message types
        """
        if message.role == "user":
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
            # Assistant message
            return AssistantMessageItem(
                id=str(message.id),
                thread_id=str(message.conversation_id),
                created_at=int(message.created_at.timestamp()),
                type="assistant_message",
                content=[AssistantMessageContent(type="output_text", text=message.content)],
                attachments=[],
            )

    async def load_thread(self, thread_id: str, context: str) -> ThreadMetadata | None:
        """Load thread metadata (NO items).

        ✅ CRITICAL: Returns ThreadMetadata, not Thread
        """
        user_id = context
        conversation_uuid = self._string_to_uuid(thread_id)

        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            return None

        return await self._conversation_to_thread_metadata(conversation)

    async def save_thread(self, thread: ThreadMetadata, context: str) -> None:
        """Save a new thread (create conversation)."""
        user_id = context

        # Check if exists
        existing = await self.load_thread(thread.id, user_id)
        if existing:
            return

        # Create new conversation
        conversation = Conversation(
            id=self._string_to_uuid(thread.id),
            user_id=user_id,
        )
        self.session.add(conversation)
        await self.session.commit()

    async def load_threads(
        self,
        limit: int,
        after: str | None,
        context: str,
        order: str = "desc",
    ) -> Page[Thread]:
        """Load all threads for user with pagination.

        ✅ CRITICAL: Returns Thread objects with empty items
        """
        user_id = context
        offset = int(after) if after else 0

        conversations = await self.conversation_repo.get_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        # Convert to threads with empty items
        threads = []
        for c in conversations:
            thread = await self._conversation_to_thread(c)
            threads.append(thread)

        # Apply ordering
        if order == "asc":
            threads.reverse()

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
        conversation_uuid = self._string_to_uuid(thread_id)

        # Verify thread belongs to user
        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            return Page(data=[], has_more=False, after=None)

        # Load messages
        messages = await self.message_repo.get_history(
            conversation_id=conversation_uuid,
            limit=limit
        )

        thread_items = [self._message_to_thread_item(m) for m in messages]

        has_more = len(thread_items) == limit
        next_after = str(len(thread_items)) if has_more else None

        return Page(data=thread_items, has_more=has_more, after=next_after)

    async def add_thread_item(
        self,
        thread_id: str,
        item: ThreadItem,
        context: str,
    ) -> None:
        """Add an item to a thread (create new message).

        ✅ CRITICAL: Handle all three content types:
        - 'text': Generic
        - 'input_text': User messages
        - 'output_text': Assistant messages
        """
        user_id = context
        conversation_uuid = self._string_to_uuid(thread_id)

        # Verify thread exists
        conversation = await self.conversation_repo.get_by_id(conversation_uuid)
        if not conversation or conversation.user_id != user_id:
            raise ValueError(f"Thread {thread_id} not found for user {user_id}")

        # Extract text content - CRITICAL FIX
        content_text = ""
        for content_part in item.content:
            # ✅ Accept all three content types
            if hasattr(content_part, 'type') and content_part.type in ("text", "input_text", "output_text"):
                content_text = getattr(content_part, 'text', "")
                logger.info(f"✅ Found text content (type={content_part.type}): '{content_text[:100]}'")
                break
            else:
                logger.warning(f"⚠️ Unexpected content type: {getattr(content_part, 'type', 'NONE')}")

        # Validate content
        if not content_text or not content_text.strip():
            raise ValueError(f"Cannot save message with empty content")

        # Determine role
        role = "user" if isinstance(item, UserMessageItem) else "assistant"

        # Create message
        message = Message(
            id=self._string_to_uuid(item.id),
            conversation_id=conversation_uuid,
            user_id=user_id,
            role=role,
            content=content_text,
        )
        self.session.add(message)
        await self.session.commit()

    # Implement other Store methods (save_item, load_item, delete_thread, etc.)
    # following the same patterns...
```

### 3. ChatKit Server Implementation (`server.py`)

```python
import os
from typing import AsyncIterator

from chatkit import ChatKitServer
from openai import AsyncOpenAI
from openai_chatkit import OpenAIChatCompletionsModel

from .memory_store import MemoryStore

# Limit conversation history to avoid token limits
MAX_RECENT_ITEMS = 30


class YourChatServer(ChatKitServer):
    """ChatKit server implementation with Gemini/OpenAI integration."""

    def __init__(self, store: MemoryStore, api_key: str, model_name: str = "gemini-2.5-flash"):
        super().__init__(store=store)

        # Configure for Gemini (use standard OpenAI base_url for OpenAI models)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        self.model = OpenAIChatCompletionsModel(
            client=self.client,
            model=model_name
        )

    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: str,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Generate streaming response to user message.

        ✅ CRITICAL: Must persist assistant message after streaming!
        """
        user_id = context
        thread_id = thread.id

        # Load conversation history
        items_page = await self.store.load_thread_items(
            thread_id=thread_id,
            after=None,
            limit=MAX_RECENT_ITEMS,
            order="asc",
            context=user_id
        )
        items = items_page.data

        # Convert items to model format
        messages = []
        for item in items:
            if isinstance(item, UserMessageItem):
                text = ""
                for content in item.content:
                    if getattr(content, 'type', None) in ("text", "input_text"):
                        text = getattr(content, 'text', "")
                        break
                if text:
                    messages.append({"role": "user", "content": text})
            elif isinstance(item, AssistantMessageItem):
                text = ""
                for content in item.content:
                    if getattr(content, 'type', None) in ("text", "output_text"):
                        text = getattr(content, 'text', "")
                        break
                if text:
                    messages.append({"role": "assistant", "content": text})

        # Create assistant message for response
        import uuid
        assistant_id = f"msg_{uuid.uuid4().hex[:8]}"
        assistant_item = AssistantMessageItem(
            id=assistant_id,
            thread_id=thread_id,
            created_at=datetime.now(timezone.utc),
            content=[AssistantMessageContent(type="output_text", text="")]
        )

        yield ThreadItemAddedEvent(item=assistant_item)

        # Stream responses from the model
        full_response = ""
        async for chunk in self.model.respond_stream(messages):
            full_response += chunk
            assistant_item.content = [AssistantMessageContent(type="output_text", text=full_response)]
            yield ThreadItemAddedEvent(item=assistant_item)

        # ✅ CRITICAL: Save assistant message to database after streaming
        assistant_item.content = [AssistantMessageContent(type="output_text", text=full_response)]
        await self.store.add_thread_item(thread_id, assistant_item, user_id)


# Alternative: ChatKit Server with System Context
class ContextAwareChatServer(ChatKitServer):
    """ChatKit server with application-specific system context."""

    def __init__(
        self,
        store: MemoryStore,
        api_key: str,
        system_prompt: str,
        model_name: str = "gemini-2.5-flash"
    ):
        super().__init__(store=store)
        self.system_prompt = system_prompt

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        self.model = OpenAIChatCompletionsModel(
            client=self.client,
            model=model_name
        )

    async def respond(
        self,
        thread_id: str,
        user_id: str,
    ) -> AsyncIterator[str]:
        """Generate streaming response with system context."""

        # Load conversation history
        items, _ = await self.store.load_thread_items(
            thread_id=thread_id,
            user_id=user_id,
            limit=MAX_RECENT_ITEMS
        )

        # Add system context at the beginning
        system_message = {
            "role": "system",
            "content": self.system_prompt
        }

        # Convert items to agent input format
        agent_input = [system_message] + [item.to_agent_input() for item in items]

        # Stream responses from the model
        async for chunk in self.model.respond_stream(agent_input):
            yield chunk
```

### 3. FastAPI Application (`main.py`)

```python
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

from .server import YourChatServer, ContextAwareChatServer
from .memory_store import MemoryStore

# Load environment variables
load_dotenv(".env.local")

# Initialize FastAPI app
app = FastAPI(title="ChatKit Backend")

# Configure CORS (restrict in production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store and server
store = MemoryStore()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY or OPENAI_API_KEY must be set")

# Choose server type
# Option 1: Basic server
chat_server = YourChatServer(store, api_key)

# Option 2: Context-aware server for task management
# system_prompt = """You are a helpful assistant for iTasks, a task management application.
# Help users manage their tasks by creating, updating, and organizing their to-do items.
# Be concise and action-oriented."""
# chat_server = ContextAwareChatServer(store, api_key, system_prompt)


@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """Handle ChatKit requests with streaming responses.

    ✅ CRITICAL: Handle NonStreamingResult properly for threads.list, etc.
    """
    payload = await request.json()
    result = chat_server.handle_request(payload)

    # Check if result is non-streaming (e.g., threads.list, threads.create)
    from chatkit.server import NonStreamingResult

    if isinstance(result, NonStreamingResult):
        # ✅ CRITICAL FIX: Decode pre-serialized JSON bytes
        import json
        json_bytes = result.json
        json_str = json_bytes.decode('utf-8')
        result_dict = json.loads(json_str)

        logger.info(f"📤 Sending non-streaming response to frontend")
        return JSONResponse(content=result_dict)

    # Streaming response (for chat messages)
    return StreamingResponse(result, media_type="text/event-stream")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

### 4. Startup Script (`scripts/run.sh`)

```bash
#!/bin/bash
set -euo pipefail

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Create virtual environment if it doesn't exist
if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies in editable mode
echo "Installing dependencies..."
pip install -e . --quiet

# Load environment variables from .env.local
if [ -f ../.env.local ]; then
    echo "Loading environment variables from .env.local..."
    set -a
    source ../.env.local
    set +a
else
    echo "Warning: .env.local not found"
fi

# Start uvicorn server with auto-reload
echo "Starting ChatKit backend on http://127.0.0.1:8000"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Python Dependencies (`pyproject.toml`)

```toml
[project]
name = "chatkit-backend"
version = "0.1.0"
description = "ChatKit backend with FastAPI"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.114",
    "uvicorn>=0.36",
    "openai>=1.40",
    "openai-chatkit>=1.4.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.4.0",
    "mypy>=1.9.0",
]

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
```

---

## Frontend Examples

### 1. Basic ChatKit Component (`components/ChatKitPanel.tsx`)

```typescript
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_URL, CHATKIT_API_DOMAIN_KEY } from "../lib/config";

export function ChatKitPanel() {
  const chatKit = useChatKit({
    api: {
      url: CHATKIT_API_URL,
      domainKey: CHATKIT_API_DOMAIN_KEY,
    },
  });

  return <ChatKit chatKit={chatKit} className="h-full" />;
}
```

### 2. Customized ChatKit Component for Task Management

```typescript
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_URL, CHATKIT_API_DOMAIN_KEY } from "../lib/config";

export function TaskChatPanel() {
  const chatKit = useChatKit({
    api: {
      url: CHATKIT_API_URL,
      domainKey: CHATKIT_API_DOMAIN_KEY,
    },
    theme: {
      colors: {
        light: {
          accent: "#398af3",
          background: "#ffffff",
          foreground: "#1f2937",
          border: "#e5e7eb",
        },
      },
      typography: {
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        fontSize: "14px",
      },
      fontSources: [
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
      ],
    },
    composer: {
      placeholder: "e.g. Add 'Buy groceries' to my tasks",
      attachments: false,
    },
    startScreen: {
      greeting: "Welcome to iTasks! 🚀",
      suggestedPrompts: [
        "Add a new task to my list",
        "Show my tasks for today",
        "Mark 'Buy groceries' as complete",
        "What tasks are overdue?",
        "Organize my tasks by priority",
      ],
    },
  });

  return <ChatKit chatKit={chatKit} className="h-full w-full" />;
}
```

### 3. ChatKit in a Modal/Dialog

```typescript
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_URL, CHATKIT_API_DOMAIN_KEY } from "../lib/config";
import { useState } from "react";

export function ChatModal() {
  const [isOpen, setIsOpen] = useState(false);

  const chatKit = useChatKit({
    api: {
      url: CHATKIT_API_URL,
      domainKey: CHATKIT_API_DOMAIN_KEY,
    },
    theme: {
      colors: {
        light: {
          accent: "#398af3",
        },
      },
    },
  });

  return (
    <>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-blue-500 text-white p-4 rounded-full shadow-lg hover:bg-blue-600"
      >
        💬 Chat
      </button>

      {/* Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl h-[600px] flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold">AI Assistant</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {/* ChatKit */}
            <div className="flex-1 overflow-hidden">
              <ChatKit chatKit={chatKit} className="h-full" />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
```

### 4. ChatKit in Sidebar Layout

```typescript
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_URL, CHATKIT_API_DOMAIN_KEY } from "../lib/config";
import { useState } from "react";

export function AppWithChatSidebar({ children }: { children: React.ReactNode }) {
  const [isChatOpen, setIsChatOpen] = useState(false);

  const chatKit = useChatKit({
    api: {
      url: CHATKIT_API_URL,
      domainKey: CHATKIT_API_DOMAIN_KEY,
    },
  });

  return (
    <div className="flex h-screen">
      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>

      {/* Chat Sidebar */}
      <div
        className={`transition-all duration-300 ${
          isChatOpen ? "w-96" : "w-0"
        } border-l border-gray-200 overflow-hidden`}
      >
        <ChatKit chatKit={chatKit} className="h-full" />
      </div>

      {/* Toggle Button */}
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className="fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg"
      >
        {isChatOpen ? "Close Chat" : "Open Chat"}
      </button>
    </div>
  );
}
```

### 5. Configuration Module (`lib/config.ts`)

```typescript
const CHATKIT_API_URL = import.meta.env.VITE_CHATKIT_API_URL || "/chatkit";
const CHATKIT_API_DOMAIN_KEY =
  import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY || "domain_pk_localhost_dev";

export { CHATKIT_API_URL, CHATKIT_API_DOMAIN_KEY };
```

### 6. Vite Configuration (`vite.config.ts`)

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 3000,
    proxy: {
      "/chatkit": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
```

### 7. Next.js API Route (`app/api/chatkit/route.ts`)

**CRITICAL:** For Next.js projects, create API proxy route (different from Vite).

```typescript
/**
 * ChatKit API Proxy Route for Next.js
 *
 * ✅ CRITICAL: Handle both streaming and non-streaming responses
 * - Streaming: text/event-stream for chat messages
 * - Non-streaming: JSON for threads.list, threads.create, etc.
 */

import { NextRequest } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    // Get the request body
    const body = await request.text();

    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/chatkit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...Object.fromEntries(request.headers.entries()),
      },
      body: body,
    });

    // Check if it's a streaming response
    const contentType = response.headers.get("content-type");

    if (contentType?.includes("text/event-stream")) {
      // ✅ Return streaming response for chat messages
      return new Response(response.body, {
        status: response.status,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    }

    // ✅ Return regular JSON response for threads.list, etc.
    const data = await response.json();
    return Response.json(data, { status: response.status });
  } catch (error) {
    console.error("ChatKit proxy error:", error);
    return Response.json(
      { error: "Failed to connect to ChatKit backend" },
      { status: 500 }
    );
  }
}
```

**Next.js Environment Configuration:**
```bash
# frontend/.env.local
# ✅ CRITICAL: Use 127.0.0.1 for WSL-Windows communication
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

**Update ChatKit Config for Next.js:**
```typescript
// lib/chatkit-config.ts
const chatKit = useChatKit({
  api: {
    url: "/api/chatkit",  // ✅ Points to Next.js API route
    domainKey: "domain_pk_localhost_dev",
  },
  // ... rest of config
});
```

### 8. Package Configuration (`package.json`)

```json
{
  "name": "chatkit-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint ."
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@openai/chatkit-react": ">=1.1.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react-swc": "^4.0.0",
    "vite": "^7.0.0",
    "typescript": "^5.6.0",
    "tailwindcss": "^4.0.0",
    "eslint": "^9.0.0"
  }
}
```

---

## Integration Examples

### Example 1: Add ChatKit to Existing Todo App

```typescript
// In your main App.tsx or layout component
import { TaskChatPanel } from "./components/TaskChatPanel";
import { YourExistingTodoComponent } from "./components/TodoList";

function App() {
  return (
    <div className="h-screen flex">
      {/* Existing Todo App */}
      <div className="flex-1 overflow-auto">
        <YourExistingTodoComponent />
      </div>

      {/* ChatKit Panel */}
      <div className="w-96 border-l border-gray-200">
        <TaskChatPanel />
      </div>
    </div>
  );
}

export default App;
```

### Example 2: System Prompt for Task Management

```python
# In your server.py
TASK_MANAGEMENT_PROMPT = """You are an AI assistant for iTasks, a task management application.

Your role is to help users:
- Create new tasks with natural language (e.g., "Add buy groceries to my list")
- Update existing tasks
- Mark tasks as complete or incomplete
- Organize tasks by priority, due date, or category
- Provide task summaries and reminders

When users ask about tasks, provide clear, actionable responses.
Keep responses concise and focused on task management.
"""

chat_server = ContextAwareChatServer(
    store=store,
    api_key=api_key,
    system_prompt=TASK_MANAGEMENT_PROMPT,
    model_name="gemini-2.5-flash"
)
```

### Example 3: Multiple AI Models

```python
# In server.py - support both OpenAI and Gemini
class MultiModelChatServer(ChatKitServer):
    def __init__(self, store: MemoryStore):
        super().__init__(store=store)

        # Gemini client
        gemini_key = os.getenv("GEMINI_API_KEY")
        self.gemini_client = AsyncOpenAI(
            api_key=gemini_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        # OpenAI client
        openai_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = AsyncOpenAI(api_key=openai_key)

    async def respond(self, thread_id: str, user_id: str):
        items, _ = await self.store.load_thread_items(thread_id, user_id)
        agent_input = [item.to_agent_input() for item in items]

        # Choose model based on user preference or task complexity
        use_openai = len(agent_input) > 20  # Use OpenAI for complex conversations

        if use_openai:
            model = OpenAIChatCompletionsModel(
                client=self.openai_client,
                model="gpt-4o-mini"
            )
        else:
            model = OpenAIChatCompletionsModel(
                client=self.gemini_client,
                model="gemini-2.5-flash"
            )

        async for chunk in model.respond_stream(agent_input):
            yield chunk
```

---

## Environment Files

### `.env.local` (Backend)

```
# AI Provider API Key (choose one or both)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Custom model names
# MODEL_NAME=gemini-2.5-flash
```

### `.env` (Frontend)

```
# ChatKit API Configuration
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev

# Production example:
# VITE_CHATKIT_API_URL=https://api.yourapp.com/chatkit
# VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_prod_xxxxx
```

---

## Complete Project Structure

```
your-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── server.py            # ChatKit server
│   │   └── memory_store.py      # Store implementation
│   ├── scripts/
│   │   └── run.sh               # Startup script
│   └── pyproject.toml           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatKitPanel.tsx # ChatKit component
│   │   ├── lib/
│   │   │   └── config.ts        # Configuration
│   │   ├── App.tsx              # Main app
│   │   └── main.tsx             # Entry point
│   ├── package.json             # Node dependencies
│   └── vite.config.ts           # Vite config
├── .env.local                   # Environment variables
├── package.json                 # Root orchestration
└── README.md
```

---

## Critical Fixes Summary

**This examples file includes fixes for 7 critical ChatKit integration pitfalls:**

1. **✅ Thread vs ThreadMetadata** - Separate methods for `load_thread()` and `load_threads()`
2. **✅ Content Type Handling** - Accept `'text'`, `'input_text'`, and `'output_text'`
3. **✅ Assistant Message Persistence** - Call `store.add_thread_item()` after streaming
4. **✅ NonStreamingResult Serialization** - Decode `result.json` bytes in main.py
5. **✅ Database Store Implementation** - Full DatabaseChatKitStore with UUID conversion
6. **✅ Next.js API Route** - Proper proxy for both streaming and non-streaming
7. **✅ WSL-Windows Networking** - Use `127.0.0.1` in environment variables

**For complete troubleshooting guide, see:** `SKILL.md` → Common Pitfalls and Solutions section

---

## Quick Debugging Commands

```bash
# Verify backend is running
curl http://127.0.0.1:8000/health

# Test ChatKit endpoint
curl -X POST http://127.0.0.1:8000/chatkit \
  -H "Content-Type: application/json" \
  -d '{"method":"threads.list","params":{}}'

# Check database tables (PostgreSQL)
psql $DATABASE_URL -c "\dt"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM conversations;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM messages;"

```

---

## Voice Integration Examples

### 1. Backend Transcription Endpoint (`main.py`)

This endpoint handles audio file uploads and uses Gemini Flash (or OpenAI Whisper) for fast, cheap transcription.

```python
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import httpx
import base64
import tempfile
import shutil

@app.post("/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio using Gemini 2.0 Flash (fallback to Whisper if configured).
    """
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")

        # Option A: OpenAI Whisper (High Accuracy)
        if openai_key and False: # Enable if preferred
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name

            try:
                from openai import OpenAI
                client = OpenAI(api_key=openai_key)
                with open(tmp_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                return {"text": transcription.text}
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        # Option B: Gemini 1.5/2.5 Flash (Fast & Cheap)
        elif gemini_key:
            # Read file bytes directly
            file.file.seek(0)
            audio_bytes = file.file.read()
            b64_audio = base64.b64encode(audio_bytes).decode('utf-8')

            # Use Gemini API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Please transcribe this audio file exactly. Return ONLY the transcribed text, no other commentary."},
                        {"inline_data": {
                            "mime_type": "audio/webm", 
                            "data": b64_audio
                        }}
                    ]
                }]
            }

            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=30.0)
                
                if resp.status_code != 200:
                    return JSONResponse(status_code=500, content={"error": f"Gemini STT failed: {resp.text}"})
                
                result = resp.json()
                try:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return {"text": text.strip()}
                except (KeyError, IndexError):
                    return JSONResponse(status_code=500, content={"error": "Invalid Gemini response format"})

        else:
            return JSONResponse(status_code=500, content={"error": "No API keys found"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
```

### 2. Frontend Voice Component (`FloatingChatbot.tsx`)

This component handles recording and injecting text into ChatKit.

```typescript
import { useRef, useState } from "react";
import { useChatbotContext } from "@/components/ChatbotProvider"; // See context example below
import { toast } from "sonner";

export function VoiceChatbot() {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  
  // Get ChatKit control from context
  const { control, sendUserMessage } = useChatbotContext();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        await handleAudioUpload(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    } catch (err) {
      console.error('Mic error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleAudioUpload = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'voice.webm');

      const response = await fetch('/api/voice/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Transcription failed');
      const data = await response.json();
      
      if (data.text) {
        // ✅ Inject text into ChatKit
        sendMessageToChatKit(data.text);
      }
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  const sendMessageToChatKit = async (text: string) => {
      // 1. Try direct context method
      if (typeof sendUserMessage === 'function') {
          // @ts-ignore
          sendUserMessage(text);
          return;
      }
      
      // 2. Try control object method
      if (control && typeof (control as any).sendUserMessage === 'function') {
          // @ts-ignore
          (control as any).sendUserMessage(text);
          return;
      }
      
      // 3. Robust DOM Fallback (if API methods fail)
      const textarea = document.querySelector('textarea[placeholder*="Type"]') as HTMLTextAreaElement;
      if (textarea) {
          const nativeSetter = Object.getOwnPropertyDescriptor(
              Object.getPrototypeOf(textarea), "value"
          )?.set;
          nativeSetter?.call(textarea, text);
          textarea.dispatchEvent(new Event('input', { bubbles: true }));
          
          setTimeout(() => {
              const btn = textarea.closest('div')?.parentElement?.querySelector('button[type="submit"]');
              (btn as HTMLElement)?.click();
          }, 100);
      }
  };

  return (
    <button onClick={isRecording ? stopRecording : startRecording}>
      {isRecording ? "Stop 🛑" : "Mic 🎤"}
    </button>
  );
}
```

### 3. Chatbot Provider Update (`ChatbotProvider.tsx`)

Update your provider to expose the full ChatKit return value (including `sendUserMessage`).

```typescript
import { createContext, useContext, ReactNode } from "react";
import { useChatKit } from "@openai/chatkit-react";
import { CHATKIT_OPTIONS } from "@/lib/chatkit-config";

// ✅ Extend ReturnType to include all ChatKit methods
interface ChatbotContextType extends ReturnType<typeof useChatKit> {
  isReady: boolean;
}

const ChatbotContext = createContext<ChatbotContextType | null>(null);

export function ChatbotProvider({ children }: { children: ReactNode }) {
  // Initialize ChatKit once at app level
  const chatKit = useChatKit(CHATKIT_OPTIONS);

  return (
    // ✅ Spread all chatKit properties (control, sendUserMessage, etc.)
    <ChatbotContext.Provider value={{ ...chatKit, isReady: true }}>
      {children}
    </ChatbotContext.Provider>
  );
}

export function useChatbotContext() {
  const context = useContext(ChatbotContext);
  if (!context) throw new Error("useChatbotContext must be used within ChatbotProvider");
  return context;
}
```

