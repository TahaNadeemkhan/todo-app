---
name: chatkit-via-python
description: Integrate OpenAI ChatKit into applications using Python FastAPI backend and React frontend with streaming AI responses
---

# ChatKit Integration via Python

## Overview
This skill provides step-by-step guidance for integrating OpenAI's ChatKit into web applications using OpenAI Agent SDK via gemini api key and using a Python FastAPI backend and React frontend. ChatKit provides a complete chat interface with streaming responses, thread management, and customizable UI.

## When to Use This Skill
- Adding AI chat capabilities to existing web applications
- Building conversational interfaces for task management, customer support, or general chat
- Integrating Gemini or OpenAI models with a production-ready chat UI
- Creating chat experiences with custom branding and themes

## Core Architecture

### Backend (Python FastAPI)
- **ChatKit Server**: Implements `ChatKitServer` class to handle chat requests
- **In-Memory Store**: Simple dictionary-based storage for threads and messages
- **Streaming Responses**: Uses FastAPI's `StreamingResponse` for real-time updates
- **AI Provider**: Supports OpenAI-compatible APIs (OpenAI, Gemini, etc.)

### Frontend (React + TypeScript)
- **ChatKit React Component**: Official `@openai/chatkit-react` library
- **Configuration**: API endpoints, domain keys, theme customization
- **Hooks**: `useChatKit()` hook for managing chat state

## Step-by-Step Integration Instructions

### Step 1: Backend Setup

#### 1.1 Install Python Dependencies
Create or update `pyproject.toml`:
```toml
[project]
name = "your-app-backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.114",
    "uvicorn>=0.36",
    "openai>=1.40",
    "openai-chatkit>=1.4.0",
    "python-dotenv",
]
```

#### 1.2 Create Memory Store
Create `memory_store.py` to store conversations (see example.md for full implementation):
- Implement `Store` interface from `chatkit`
- Store threads and items in dictionaries
- Provide methods: `load_thread`, `save_thread`, `add_thread_item`, etc.
- Support cursor-based pagination for thread items

#### 1.3 Implement ChatKit Server
Create `server.py` extending `ChatKitServer`:
```python
from chatkit import ChatKitServer
from openai import AsyncOpenAI
from openai_chatkit import OpenAIChatCompletionsModel

class YourChatServer(ChatKitServer):
    def __init__(self, store, api_key: str):
        super().__init__(store=store)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = OpenAIChatCompletionsModel(
            client=self.client,
            model="gemini-2.5-flash"
        )

    async def respond(self, thread_id, user_id):
        # Load conversation history
        items = await self.store.load_thread_items(thread_id)

        # Convert to agent input format
        agent_input = [item.to_agent_input() for item in items]

        # Stream responses
        async for chunk in self.model.respond_stream(agent_input):
            yield chunk
```

Key patterns:
- `MAX_RECENT_ITEMS`: Limit conversation history (e.g., 30 messages)
- `to_agent_input()`: Convert ChatKit items to model format
- Streaming with `async for` and `yield`

#### 1.4 Create FastAPI Application
Create `main.py`:
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv

from .server import YourChatServer
from .memory_store import MemoryStore

load_dotenv(".env.local")

app = FastAPI()

# CORS for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store and server
store = MemoryStore()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
chat_server = YourChatServer(store, api_key)

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    payload = await request.json()
    result = chat_server.handle_request(payload)
    return StreamingResponse(result, media_type="text/event-stream")
```

### Step 2: Frontend Setup

#### 2.1 Install React Dependencies
```bash
npm install @openai/chatkit-react
# or with specific version
npm install @openai/chatkit-react@">=1.1.1"
```

#### 2.2 Create Configuration Module
Create `lib/config.ts`:
```typescript
const CHATKIT_API_URL = import.meta.env.VITE_CHATKIT_API_URL || "/chatkit";
const CHATKIT_API_DOMAIN_KEY = import.meta.env.VITE_CHATKIT_API_DOMAIN_KEY || "domain_pk_localhost_dev";

export { CHATKIT_API_URL, CHATKIT_API_DOMAIN_KEY };
```

#### 2.3 Create ChatKit Component
Create `components/ChatKitPanel.tsx`:
```typescript
import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_URL, CHATKIT_API_DOMAIN_KEY } from "../lib/config";

export function ChatKitPanel() {
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
        },
      },
      typography: {
        fontFamily: "'Inter', sans-serif",
      },
    },
    composer: {
      placeholder: "Ask me anything...",
    },
    startScreen: {
      greeting: "Welcome! How can I help you?",
      suggestedPrompts: [
        "Help me with...",
        "Explain...",
      ],
    },
  });

  return <ChatKit chatKit={chatKit} className="h-full" />;
}
```

#### 2.4 Configure Vite Proxy
In `vite.config.ts`, add proxy for development:
```typescript
export default defineConfig({
  server: {
    proxy: {
      "/chatkit": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
```

### Step 3: Environment Configuration

#### 3.1 Backend Environment Variables
Create `.env.local` at project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
```

#### 3.2 Frontend Environment Variables (Optional)
Create `.env` in frontend directory:
```
VITE_CHATKIT_API_URL=/chatkit
VITE_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev
```

### Step 4: Customization Patterns

#### Theme Customization
Customize colors, fonts, and styling via the `theme` configuration:
```typescript
theme: {
  colors: {
    light: {
      accent: "#your-brand-color",
      background: "#ffffff",
      foreground: "#000000",
    },
  },
  typography: {
    fontFamily: "'Your Font', sans-serif",
    fontSize: "14px",
  },
  fontSources: [
    "https://fonts.googleapis.com/css2?family=Your+Font",
  ],
}
```

#### Custom Prompts for Different Use Cases
For task management:
```typescript
composer: {
  placeholder: "e.g. Add 'Buy groceries'",
},
startScreen: {
  greeting: "Welcome to Your App!",
  suggestedPrompts: [
    "Add a new task",
    "Show my tasks for today",
    "Mark task as complete",
  ],
}
```

#### Model Selection
Change AI provider and model in `server.py`:
```python
# For Gemini
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel(client=client, model="gemini-2.5-flash")

# For OpenAI
client = AsyncOpenAI(api_key=api_key)
model = OpenAIChatCompletionsModel(client=client, model="gpt-4o-mini")
```

### Step 5: Running the Application

#### Development Mode
Create startup script or use `package.json`:
```json
{
  "scripts": {
    "dev": "concurrently \"npm run backend\" \"npm run frontend\"",
    "backend": "./backend/scripts/run.sh",
    "frontend": "npm --prefix frontend run dev"
  }
}
```

Backend startup script (`backend/scripts/run.sh`):
```bash
#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Create virtual environment if needed
if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies
pip install -e .

# Load environment and start server
if [ -f ../.env.local ]; then
    set -a
    source ../.env.local
    set +a
fi

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Common Integration Patterns

### Pattern 1: Integrating into Existing React App
1. Install ChatKit React dependency
2. Add ChatKit component to your app layout (sidebar, modal, or full page)
3. Configure proxy in Vite/Webpack to route `/chatkit` to backend
4. Wrap component with your app's styling/theme

### Pattern 2: Adding Context from Your Application
Modify the `respond()` method to inject application context:
```python
async def respond(self, thread_id, user_id):
    items = await self.store.load_thread_items(thread_id)

    # Add system context about the application
    system_context = {
        "role": "system",
        "content": f"You are a helpful assistant for TaskApp. User {user_id} has access to..."
    }

    agent_input = [system_context] + [item.to_agent_input() for item in items]

    async for chunk in self.model.respond_stream(agent_input):
        yield chunk
```

### Pattern 3: Persistent Storage
Replace `MemoryStore` with database storage:
- Use SQLAlchemy or async ORM for thread/item persistence
- Implement same `Store` interface methods
- Add user authentication and authorization
- Store attachments in cloud storage (S3, etc.)

### Pattern 4: Voice/Multi-modal Integration
To add voice capabilities without complex client-side STT libraries:

1. **Frontend Recording**: Use `MediaRecorder` API to capture audio blobs (webm/wav).
2. **Server-Side Transcription**: Send audio `FormData` to a backend endpoint (`/api/voice/transcribe`).
3. **AI Transcription**: Backend uses Gemini Flash or OpenAI Whisper to transcribe audio to text.
4. **Text Injection**: Frontend receives text and injects it into ChatKit using `control.sendUserMessage(text)`.

**Architecture:**
```mermaid
[Client Mic] -> [MediaRecorder] -> [POST /api/voice] -> [Backend] -> [Gemini/Whisper]
                                                                        |
[ChatKit UI] <- [control.send(text)] <- [JSON {text: "..."}] <----------+
```

## Key Implementation Notes

1. **Memory Store Limitation**: The in-memory store is for development only. Data is lost on restart.

2. **CORS Configuration**: `allow_origins=["*"]` is unsafe for production. Restrict to your frontend domain.

3. **Conversation History**: Limit with `MAX_RECENT_ITEMS` to avoid token limits and manage costs.

4. **Error Handling**: Add try/catch blocks and proper error responses in production.

5. **Authentication**: ChatKit uses domain keys for development. Implement proper auth for production.

6. **Rate Limiting**: Add rate limiting middleware to prevent API abuse.

## Common Pitfalls and Solutions

### Critical Issue 1: Thread vs ThreadMetadata Type Confusion
**Error:** `TypeError: got multiple values for keyword argument 'items'`

**Problem:** ChatKit has TWO separate types that are easily confused:
- `Thread`: Full object WITH items array (for list views like `load_threads()`)
- `ThreadMetadata`: Lightweight WITHOUT items (for single thread in `load_thread()`)

**Solution:**
```python
# ✅ CORRECT - load_thread() returns ThreadMetadata (no items)
async def load_thread(self, thread_id: str, context: str) -> ThreadMetadata | None:
    conversation = await self.get_conversation(thread_id)
    return ThreadMetadata(
        id=str(conversation.id),
        title="Thread Title",
        created_at=int(conversation.created_at.timestamp()),
        updated_at=int(conversation.updated_at.timestamp()),
    )  # No items field - ChatKit loads separately

# ✅ CORRECT - load_threads() returns Thread with empty items
async def load_threads(...) -> Page[Thread]:
    return Thread(
        id=str(conv.id),
        title="Thread Title",
        created_at=...,
        updated_at=...,
        items=Page(data=[], has_more=False, after=None)  # Empty items
    )
```

### Critical Issue 2: Content Type Not Recognized
**Error:** Assistant messages not saving even with `add_thread_item()` call

**Problem:** ChatKit uses different content types:
- User messages: `'input_text'`
- Assistant messages: `'output_text'` (NOT `'text'`)

**Solution:**
```python
async def add_thread_item(self, thread_id, item, context):
    content_text = ""
    for content_part in item.content:
        # ✅ Accept all three types
        if hasattr(content_part, 'type') and content_part.type in ("text", "input_text", "output_text"):
            content_text = getattr(content_part, 'text', "")
            break

    if not content_text.strip():
        raise ValueError("Cannot save message with empty content")

    # Save to database...
```

### Critical Issue 3: Assistant Messages Not Persisting
**Error:** User messages save but assistant responses disappear after refresh

**Problem:** Missing `store.add_thread_item()` call after streaming completes

**Solution:**
```python
async def respond(self, thread, input_user_message, context):
    # ... streaming logic ...

    full_response = ""
    async for chunk in self.model.respond_stream(messages):
        full_response += chunk
        assistant_item.content = [AssistantMessageContent(type="output_text", text=full_response)]
        yield ThreadItemAddedEvent(item=assistant_item)

    # ✅ CRITICAL: Save to database after streaming
    await self.store.add_thread_item(thread_id, assistant_item, user_id)
```

### Critical Issue 4: NonStreamingResult Serialization Failing
**Error:** `Cannot destructure property 'title'` in frontend

**Problem:** Trying to use `dataclasses.asdict()` on Pydantic models with nested bytes

**Solution:**
```python
# In main.py
if isinstance(result, NonStreamingResult):
    # ✅ CORRECT - Decode pre-serialized JSON bytes
    import json
    json_bytes = result.json
    json_str = json_bytes.decode('utf-8')
    result_dict = json.loads(json_str)
    return JSONResponse(content=result_dict)
```

### Critical Issue 5: Database Tables Missing
**Error:** `relation "conversations" does not exist`

**Problem:** Alembic migrations not run or models not importable

**Solution:**
1. Ensure `.env.local` exists in backend with `DATABASE_URL`
2. Fix `alembic/env.py` to import models:
```python
# alembic/env.py
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
```
3. Run migrations: `alembic upgrade head`

### Critical Issue 6: WSL-Windows Network Problems
**Error:** Frontend can't reach backend at `localhost:8000`

**Problem:** WSL's localhost is different from Windows host

**Solution:**
```bash
# In frontend/.env.local
# ❌ WRONG (WSL to Windows)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# ✅ CORRECT (WSL to Windows)
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

Always use `127.0.0.1` for cross-environment communication.

### Critical Issue 7: Missing Next.js API Proxy
**Error:** ChatKit UI loads but doesn't communicate with backend

**Problem:** No proxy route in Next.js (different from Vite)

**Solution:**
Create `/app/api/chatkit/route.ts`:
```typescript
import { NextRequest } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const response = await fetch(`${BACKEND_URL}/chatkit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body,
  });

  const contentType = response.headers.get("content-type");

  if (contentType?.includes("text/event-stream")) {
    // Streaming response
    return new Response(response.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
      },
    });
  }

  // JSON response
  const data = await response.json();
  return Response.json(data);
}
```

## Troubleshooting

### Backend Issues
- **Import errors**: Ensure `openai-chatkit` is installed with correct version
- **API key errors**: Check `.env.local` is loaded and API key is valid
- **CORS errors**: Verify CORS middleware configuration
- **Database errors**: Run `alembic upgrade head` and check DATABASE_URL

### Frontend Issues
- **ChatKit component not rendering**: Check API URL and domain key configuration
- **Proxy not working**: Verify Vite/Next.js proxy configuration and backend is running
- **Style conflicts**: Use scoped CSS or adjust ChatKit theme to match your app
- **Blank screen**: Check browser console for errors, verify API route exists

### Streaming Issues
- **Responses not streaming**: Ensure `StreamingResponse` with `text/event-stream` media type
- **Connection timeouts**: Check server keepalive settings

### Data Persistence Issues
- **History not loading**: Verify Thread vs ThreadMetadata types
- **Messages disappearing**: Check `add_thread_item()` is called after streaming
- **Empty conversation list**: Verify database has data and migrations ran

## Production Checklist

Before deploying to production:
- [ ] Replace in-memory store with persistent database
- [ ] Implement user authentication and authorization
- [ ] Restrict CORS to specific frontend domains
- [ ] Add rate limiting and request validation
- [ ] Set up proper logging and monitoring
- [ ] Configure production API keys securely (secrets manager)
- [ ] Add error handling and graceful degradation
- [ ] Test with production API quotas and limits
- [ ] Implement backup and recovery for conversation data
- [ ] Add analytics and usage tracking

## Resources

- ChatKit Documentation: Official OpenAI ChatKit docs
- FastAPI Documentation: https://fastapi.tiangolo.com/
- OpenAI Python SDK: https://github.com/openai/openai-python
- React ChatKit Component: `@openai/chatkit-react` package
