# Phase 3 Backend: AI-Powered Todo Chatbot

AI chatbot backend for Phase 3, implementing conversational task management with OpenAI integration.

## Project Structure

```
backend/
├── src/
│   ├── models/           # Database models (SQLModel)
│   │   ├── conversation.py  # ✅ Conversation model
│   │   └── message.py       # ✅ Message model with MessageRole enum
│   ├── repositories/     # Data access layer (TODO)
│   ├── mcp_server/       # MCP tools for AI agent (TODO)
│   └── chat_service/     # AI orchestration (TODO)
├── tests/
│   ├── unit/             # Unit tests
│   │   ├── models/       # ✅ Model tests (13/13 passing)
│   │   └── mcp/          # TODO: MCP tool tests
│   └── integration/      # TODO: Integration tests
└── pyproject.toml        # Dependencies and config
```

## Completed Tasks

- ✅ **Task 1.1**: Conversation Model (TDD)
  - UUID primary key, user_id (indexed FK), timestamps
  - 5/5 tests passing

- ✅ **Task 1.2**: Message Model (TDD)
  - UUID PK, conversation_id FK, user_id FK, MessageRole enum
  - 8/8 tests passing

## Setup

### Prerequisites
- Python 3.13+
- `uv` package manager

### Installation

```bash
cd todo_app/phase_3/backend

# Create virtual environment
uv venv

# Install dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# All tests
PYTHONPATH=src uv run pytest -v

# Model tests only
PYTHONPATH=src uv run pytest tests/unit/models/ -v

# Specific test file
PYTHONPATH=src uv run pytest tests/unit/models/test_conversation.py -v
```

## Database Models

### Conversation
```python
class Conversation(SQLModel, table=True):
    id: str              # UUID primary key
    user_id: str         # Indexed FK to users.id (Phase 2)
    created_at: datetime # Auto-generated
    updated_at: datetime # Auto-generated
```

### Message
```python
class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    id: str              # UUID primary key
    conversation_id: str # Indexed FK to conversations.id
    user_id: str         # Indexed FK to users.id (Phase 2)
    role: MessageRole    # Enum: USER or ASSISTANT
    content: str         # Max 2000 characters
    created_at: datetime # Indexed for temporal queries
```

## Next Tasks

- [ ] Task 1.3: ConversationRepository (TDD)
- [ ] Task 1.4: MessageRepository (TDD)
- [ ] Task 1.5: Database Migration
- [ ] Phase 2: MCP Server (5 tools)
- [ ] Phase 3: Chat Service (AI orchestration)
- [ ] Phase 4: Integration with Phase 2

## References

- Spec: `/specs/003-ai-chatbot/spec.md`
- Plan: `/specs/003-ai-chatbot/plan.md`
- Tasks: `/specs/003-ai-chatbot/tasks.md`
- Data Model: `/specs/003-ai-chatbot/data-model.md`
