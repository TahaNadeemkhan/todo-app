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

### 2. ChatKit Server Implementation (`server.py`)

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
        thread_id: str,
        user_id: str,
    ) -> AsyncIterator[str]:
        """Generate streaming response to user message."""

        # Load conversation history
        items, _ = await self.store.load_thread_items(
            thread_id=thread_id,
            user_id=user_id,
            limit=MAX_RECENT_ITEMS
        )

        # Convert items to agent input format
        agent_input = [item.to_agent_input() for item in items]

        # Stream responses from the model
        async for chunk in self.model.respond_stream(agent_input):
            yield chunk


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
    """Handle ChatKit requests with streaming responses."""
    payload = await request.json()
    result = chat_server.handle_request(payload)
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

### 7. Package Configuration (`package.json`)

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
