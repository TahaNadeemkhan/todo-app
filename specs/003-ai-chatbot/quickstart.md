# Phase 3 Quickstart: AI-Powered Todo Chatbot

**Purpose**: Get Phase 3 running quickly for development and testing

## Prerequisites

- ✅ Phase 2 completed (Task API, JWT auth, email service, Neon DB)
- ✅ Python 3.13+ with `uv`
- ✅ Node.js 20+
- ✅ OpenAI API key
- ✅ Browser with Web Speech API (Chrome/Edge/Safari)

## Quick Setup

### 1. Environment Variables

Add to `.env`:
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
DATABASE_URL=postgresql://...
JWT_SECRET=...
EMAIL_SERVICE_URL=http://localhost:8001/send-email
```

### 2. Backend Setup

```bash
cd todo_app
cd phase_3
cd backend

# Install dependencies
uv add openai-agents-sdk mcp sqlmodel

# Run database migration
uv run alembic revision --autogenerate -m "Add conversation and message tables"
uv run alembic upgrade head

# Start backend
PYTHONPATH=src uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Access http://localhost:3000/chat
```

### 4. Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: Buy groceries"}'
```

### 5. Test Voice Input

1. Navigate to http://localhost:3000/chat
2. Click microphone button
3. Grant permission
4. Speak: "Add task buy groceries"
5. Verify text appears and sends

## Architecture Flow

```
User → Voice/Text → Chat UI → JWT Validation → Chat Service → AI Agent → MCP Tools → Task Repository → Database
                                                                             ↓
                                                                      Email Service (async)
```

## Key Files

**Backend**:
- `src/api/routes/chat.py` - Chat endpoint
- `src/services/chat_service.py` - AI orchestration
- `src/services/mcp_server.py` - 5 MCP tools
- `src/models/conversation.py` - Conversation model
- `src/models/message.py` - Message model

**Frontend**:
- `src/app/chat/page.tsx` - Chat interface
- `src/components/chat/MicrophoneButton.tsx` - Voice input
- `src/hooks/useVoiceRecognition.tsx` - Web Speech API

## Running Tests

```bash
# Backend
cd backend
uv run pytest tests/unit/mcp/
uv run pytest tests/integration/test_chat_endpoint.py
uv run pytest tests/e2e/

# Frontend
cd frontend
npm run test
npm run test:e2e
```

## Common Issues

| Issue | Fix |
|-------|-----|
| "OpenAI API key not found" | Check `.env` has `OPENAI_API_KEY` |
| "Microphone button disabled" | Use Chrome/Edge/Safari on HTTPS |
| "403 Forbidden" | JWT user_id must match path parameter |
| "Email failed but task created" | Expected (best-effort email) |

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Follow TDD: write test → implement → refactor
3. Implement foundation (MCP server, models, repositories)
4. Implement P1 user stories (create, view, complete)
5. Implement P2 enhancements (delete, update, voice)

See `plan.md` for full architectural details.
