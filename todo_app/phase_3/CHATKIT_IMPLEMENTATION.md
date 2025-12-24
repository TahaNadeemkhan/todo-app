# ChatKit Implementation Guide

## Overview

This Phase 3 implementation integrates **OpenAI ChatKit** for AI-powered task management with a **database-backed architecture** using PostgreSQL. The system provides a modern chat interface with persistent conversation storage and multilingual support (English + Urdu).

## Architecture

### Backend (Python FastAPI)

**Key Components:**
- **DatabaseChatKitStore** (`src/chatkit_store.py`): Maps ChatKit Store interface to PostgreSQL Conversation/Message models
- **TodoChatKitServer** (`src/chatkit_server.py`): ChatKit server with Gemini integration and multilingual support
- **FastAPI Endpoint** (`src/main.py`): `/chatkit` endpoint for streaming chat responses
- **MCP Tools Integration**: Stateless MCP tools for task management (add_task, list_tasks, complete_task, delete_task, update_task)

**Technology Stack:**
- FastAPI 0.115+
- OpenAI ChatKit 1.4.0+
- Gemini 2.0 Flash (via OpenAI-compatible API)
- SQLModel + AsyncPG for async database operations
- Neon Serverless PostgreSQL

### Frontend (Next.js + React)

**Key Components:**
- **ChatKitPanel** (`src/components/ChatKitPanel.tsx`): Main chat interface component
- **ChatKit Configuration** (`src/lib/chatkit-config.ts`): Theme, prompts, and API settings
- **Next.js Rewrites**: Proxy `/api/chatkit` to backend

**Technology Stack:**
- Next.js 16+ (App Router)
- React 19+
- OpenAI ChatKit React 1.1.1+
- TypeScript 5+
- Tailwind CSS 4

## Database Schema

### Conversation Model
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

### Message Model
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    user_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL CHECK (role IN ('user', 'assistant')),
    content VARCHAR(2000) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd todo_app/phase_3/backend
pip install -e .
```

#### Configure Environment
Copy `.env.example` to `.env` and configure:
```bash
# AI Provider (use Gemini)
GEMINI_API_KEY=your_gemini_api_key_here

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host/database?sslmode=require

# JWT Secret (from Phase 2)
JWT_SECRET=your-jwt-secret-here
```

#### Run Database Migrations
```bash
alembic upgrade head
```

#### Start Backend Server
```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup

#### Install Dependencies
```bash
cd todo_app/phase_3/frontend
npm install
```

#### Configure Environment
Create `.env.local`:
```bash
# ChatKit API Configuration
NEXT_PUBLIC_CHATKIT_API_URL=/api/chatkit
NEXT_PUBLIC_CHATKIT_API_DOMAIN_KEY=domain_pk_localhost_dev

# Backend URL for Next.js rewrites
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000

# Database (for Better Auth)
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
BETTER_AUTH_SECRET=your-secret-key
```

#### Start Frontend Server
```bash
npm run dev
```

Access the application at `http://localhost:3000/chat`

## Key Features

### 1. Database-Backed Conversations
- All conversations and messages are persisted to PostgreSQL
- Stateless server architecture (no in-memory state)
- Full conversation history retrieval
- User-scoped data access

### 2. Multilingual Support
The system prompt (`src/services/prompts/system_prompt.md`) implements language mirroring:
- Detects user's language (English, Roman Urdu, or Urdu Script)
- Responds in the same language
- Maintains conversational tone

### 3. MCP Tools Integration
The ChatKit server has access to MCP tools for task management:
- `add_task`: Create new tasks
- `list_tasks`: List tasks with filtering
- `complete_task`: Mark tasks as complete
- `delete_task`: Delete tasks
- `update_task`: Modify task details

### 4. Streaming Responses
- Real-time streaming of AI responses
- FastAPI `StreamingResponse` with `text/event-stream`
- Smooth user experience with progressive loading

## File Structure

```
todo_app/phase_3/
├── backend/
│   └── src/
│       ├── chatkit_store.py         # Database-backed Store implementation
│       ├── chatkit_server.py        # ChatKit server with Gemini
│       ├── main.py                  # FastAPI app with /chatkit endpoint
│       ├── models/
│       │   ├── conversation.py      # Conversation SQLModel
│       │   └── message.py           # Message SQLModel
│       ├── repositories/
│       │   ├── conversation_repository.py
│       │   └── message_repository.py
│       ├── services/
│       │   └── prompts/
│       │       └── system_prompt.md # Multilingual system prompt
│       └── mcp_server/
│           ├── server.py            # MCP server
│           └── tools/               # MCP tool implementations
└── frontend/
    └── src/
        ├── components/
        │   └── ChatKitPanel.tsx     # Main ChatKit component
        ├── lib/
        │   └── chatkit-config.ts    # ChatKit configuration
        ├── app/
        │   └── chat/
        │       └── page.tsx         # Chat page
        └── next.config.ts           # Next.js config with rewrites
```

## Implementation Highlights

### DatabaseChatKitStore Mapping

**ChatKit Thread ↔ Conversation Model**
```python
def _conversation_to_thread(self, conversation: Conversation) -> Thread:
    return Thread(
        id=str(conversation.id),
        created_at=int(conversation.created_at.timestamp()),
        updated_at=int(conversation.updated_at.timestamp()),
    )
```

**ChatKit ThreadItem ↔ Message Model**
```python
def _message_to_thread_item(self, message: Message) -> ThreadItem:
    return ThreadItem(
        id=str(message.id),
        role=message.role.value,  # "user" or "assistant"
        content=[{"type": "text", "text": message.content}],
        created_at=int(message.created_at.timestamp()),
    )
```

### System Prompt with Context Injection

```python
def _prepare_system_prompt(self, user_id: str) -> str:
    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    prompt = self.system_prompt
    prompt = prompt.replace("{{user_id}}", user_id)
    prompt = prompt.replace("{{current_time}}", current_time)
    return prompt
```

### Next.js API Proxy

```typescript
// next.config.ts
async rewrites() {
  return [
    {
      source: "/api/chatkit",
      destination: process.env.NEXT_PUBLIC_BACKEND_URL
        ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/chatkit`
        : "http://127.0.0.1:8000/chatkit",
    },
  ];
}
```

## Testing

### Backend Tests

Run unit tests:
```bash
cd todo_app/phase_3/backend
pytest tests/unit
```

Run integration tests:
```bash
pytest tests/integration
```

### Frontend

```bash
cd todo_app/phase_3/frontend
npm run lint
npm run build
```

## Production Deployment

### Backend (Render/Railway)

1. Set environment variables:
   - `GEMINI_API_KEY`
   - `DATABASE_URL` (Neon PostgreSQL)
   - `JWT_SECRET`

2. Update CORS middleware in `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.vercel.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. Deploy with `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Set environment variables:
   - `NEXT_PUBLIC_CHATKIT_API_URL=/api/chatkit`
   - `NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com`
   - `DATABASE_URL`
   - `BETTER_AUTH_SECRET`

2. Update ChatKit domain key for production (if applicable)

3. Deploy with Vercel CLI or GitHub integration

## Troubleshooting

### Backend Issues

**Import errors with chatkit**
```bash
pip install openai-chatkit>=1.4.0
```

**Database connection errors**
- Ensure `DATABASE_URL` uses `postgresql+asyncpg://` scheme
- Verify SSL mode is set correctly for Neon

**CORS errors**
- Check CORS middleware configuration in `main.py`
- Verify frontend origin is allowed

### Frontend Issues

**ChatKit component not rendering**
- Verify `@openai/chatkit-react` is installed: `npm install`
- Check browser console for errors
- Confirm API endpoint is reachable

**Proxy not working**
- Restart Next.js dev server after changing `next.config.ts`
- Verify `NEXT_PUBLIC_BACKEND_URL` is correct
- Check backend is running on port 8000

**Streaming issues**
- Ensure backend returns `StreamingResponse` with `text/event-stream`
- Check network tab for event-stream responses

## Limitations and Future Enhancements

### Current Limitations
1. Attachments not supported in DatabaseChatKitStore
2. MCP tools integration requires manual mapping (not fully automated)
3. No message editing/deletion in UI (append-only)

### Future Enhancements
1. Voice input integration (Phase 4 requirement)
2. File attachment support via cloud storage
3. Advanced MCP tools with function calling
4. Real-time collaboration features
5. Analytics and conversation insights

## Resources

- [ChatKit Documentation](https://platform.openai.com/docs/chatkit)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Neon PostgreSQL](https://neon.tech/docs)

## Support

For issues or questions:
1. Check this documentation first
2. Review the error logs (backend: FastAPI logs, frontend: browser console)
3. Verify environment configuration
4. Test with minimal setup (single user, simple prompts)
