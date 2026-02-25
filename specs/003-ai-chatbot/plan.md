# Implementation Plan: AI-Powered Todo Chatbot

**Branch**: `003-ai-chatbot` | **Date**: 2025-12-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot/spec.md`

## Summary

Implement a stateless AI-powered chatbot that enables users to manage tasks through natural language conversations in English and Urdu (Roman/Script). The system uses OpenAI Agents SDK for AI orchestration, MCP (Model Context Protocol) for tool integration, database-persisted conversation history, and Web Speech API for voice input. Email notifications are sent upon task creation via Phase 2's notification service.

**Core Architecture**:
- **Stateless AI Agent**: OpenAI Agents SDK orchestrates tool calls with no in-memory session state
- **MCP Tools**: 5 tools (add_task, list_tasks, complete_task, delete_task, update_task) as the agent's capabilities
- **Database State**: All conversation and message history persisted in PostgreSQL (Neon)
- **Multilingual Support**: System prompt engineered for English and Urdu (Roman/Script) detection and response
- **Voice Input**: Frontend microphone button using Web Speech API for speech-to-text
- **Email Integration**: add_task tool triggers Phase 2 notification service asynchronously

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK (0.2+), Official MCP SDK, Pydantic, Better Auth JWT middleware
- Frontend: Next.js 15+ (App Router), React 18+, TypeScript, Web Speech API (browser native)
**Storage**: Neon Serverless PostgreSQL (existing from Phase 2 + new Conversation and Message tables)
**Testing**: pytest (backend), Vitest/Jest (frontend unit), Playwright (E2E)
**Target Platform**: Linux server (backend), Modern browsers with Web Speech API support (frontend)
**Project Type**: Web application (FastAPI backend + Next.js frontend)
**Performance Goals**:
- Chat endpoint <3s response time (p95) for single-tool operations
- Voice-to-text transcription <2s (90% of cases)
- Support 50 concurrent users without degradation
**Constraints**:
- Stateless backend: no in-memory sessions, all state in database
- Conversation history limited to 50 messages per request
- Email notification non-blocking (best-effort)
- Progressive enhancement: voice input optional, text input required
**Scale/Scope**:
- 8 user stories (3 P1 MVP, 5 P2 enhancements)
- 33 functional requirements
- 5 MCP tools with strict Pydantic schemas
- 2 new database models (Conversation, Message)
- Multilingual system prompt (English + Urdu)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Spec-Driven Discipline
- **Status**: PASS
- **Evidence**: Complete specification in `specs/003-ai-chatbot/spec.md` with 8 user stories, 33 FRs, TDD requirements
- **ADR Required**: Stateless conversation design (database-only state vs in-memory sessions)

### ✅ Principle II: Architectural Separation
- **Status**: PASS
- **Layering**:
  - UI Layer: Next.js chat interface with microphone button (frontend-only voice processing)
  - Service Layer: ChatService orchestrates AI agent, MCP tools, conversation persistence
  - Repository Layer: ConversationRepository, MessageRepository, TaskRepository (existing)
- **Dependency Rule**: Service layer depends on repository interfaces, not implementations

### ✅ Principle III: Domain-First Modeling
- **Status**: PASS
- **Models**: Conversation and Message as SQLModel entities with strict validation
- **Validation**: Pydantic schemas for MCP tool inputs, JWT claims validation for user_id
- **Type Safety**: Python 3.13+ type hints, TypeScript for frontend

### ✅ Principle IV: Security by Design
- **Status**: PASS
- **Hostile Backend**: JWT validation middleware extracts user_id; never trust client-provided user_id in request body
- **MCP Tool Security**: Each tool validates user_id matches authenticated user before database operations
- **Secrets**: OpenAI API key, Neon DB credentials via environment variables

### ✅ Principle V: Deterministic AI & Tooling
- **Status**: PASS (Critical for Phase 3)
- **Strict Schemas**: All 5 MCP tools defined with Pydantic input/output schemas
- **Stateless Agent**: AI agent derives context from database-fetched conversation history only
- **Tool-First**: Agent can only perform actions via defined MCP tools; no direct database access

### ✅ Principle VI: Immutable Infrastructure
- **Status**: PASS
- **Logging**: Structured JSON logs for chat endpoint, MCP tool invocations, email notification attempts
- **Observability**: Request tracing with conversation_id correlation

### ⚠️ Principle VII: Event-Driven Decoupling
- **Status**: PARTIAL COMPLIANCE
- **Email Notifications**: add_task tool triggers email service asynchronously (non-blocking)
- **Justification**: Inline async call acceptable for Phase 3; full event-driven (Kafka/Dapr) deferred to Phase 5
- **Mitigation**: Email failures logged but don't block task creation response

### ✅ Principle VIII: Phased Evolution
- **Status**: PASS
- **Dependencies**: Builds on Phase 1 (Task model) and Phase 2 (JWT auth, Task API, notification service)
- **No Rewrites**: Extends existing TaskRepository; adds new Conversation/Message repositories
- **Compliance**: Follows Phase 3 hackathon requirements (OpenAI ChatKit, Agents SDK, MCP)

### ✅ Principle IX: Test-Driven Development (TDD)
- **Status**: PASS
- **Mandate**: Red-Green-Refactor cycle for all MCP tools, chat endpoint, voice input components
- **Coverage**: 90%+ unit, 100% integration for chat endpoint, E2E per user story
- **Framework**: pytest (backend), Vitest/Jest + Playwright (frontend)

### ✅ Principle X: Modern Python Tooling
- **Status**: PASS
- **Package Manager**: `uv` for all Python dependencies
- **Runtime**: Python 3.13+

### ✅ Principle XI: Nine Pillars of AI-Driven Development
- **Status**: PASS
- **Spec-Driven**: Plan follows spec.md as source of truth
- **Deterministic Tooling**: MCP schemas enforce strict contracts
- **Stateless Architecture**: No in-memory sessions
- **Security by Design**: JWT validation, user_id verification
- **Event-Driven Architecture**: Email notifications prepared for async (Phase 5 full event-driven)

### Summary
**Overall**: PASS with 1 partial compliance justified
**Proceed to Phase 0**: YES
**Re-check after Phase 1**: Required

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot/
├── spec.md              # User stories, requirements, success criteria
├── plan.md              # This file (architecture and design decisions)
├── research.md          # Phase 0: Technology research and decisions
├── data-model.md        # Phase 1: Conversation and Message models
├── quickstart.md        # Phase 1: Developer onboarding guide
├── contracts/           # Phase 1: API schemas and MCP tool definitions
│   ├── chat_endpoint.openapi.yaml
│   ├── mcp_tools.json
│   └── system_prompt.md
├── checklists/          # Requirements validation
│   └── requirements.md
└── tasks.md             # Phase 2: Implementation tasks (/sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py              # Existing from Phase 2
│   │   ├── user.py              # Existing from Phase 2
│   │   ├── conversation.py      # NEW: Conversation SQLModel
│   │   └── message.py           # NEW: Message SQLModel
│   ├── repositories/
│   │   ├── task_repository.py   # Existing from Phase 2
│   │   ├── conversation_repository.py  # NEW
│   │   └── message_repository.py       # NEW
│   ├── services/
│   │   ├── task_service.py      # Existing from Phase 2
│   │   ├── auth_service.py      # Existing from Phase 2
│   │   ├── email_service.py     # Existing from Phase 2
│   │   ├── chat_service.py      # NEW: Orchestrates agent + conversation
│   │   └── mcp_server.py        # NEW: MCP server with 5 tools
│   ├── api/
│   │   ├── routes/
│   │   │   ├── tasks.py         # Existing from Phase 2
│   │   │   ├── auth.py          # Existing from Phase 2
│   │   │   └── chat.py          # NEW: Chat endpoint
│   │   └── middleware/
│   │       └── auth_middleware.py  # Existing from Phase 2
│   ├── config/
│   │   ├── settings.py          # Existing + OpenAI API key
│   │   └── database.py          # Existing + new tables
│   └── prompts/
│       └── system_prompt.py     # NEW: Multilingual system prompt
└── tests/
    ├── unit/
    │   ├── models/
    │   │   ├── test_conversation.py
    │   │   └── test_message.py
    │   ├── repositories/
    │   │   ├── test_conversation_repository.py
    │   │   └── test_message_repository.py
    │   └── mcp/
    │       ├── test_add_task.py
    │       ├── test_list_tasks.py
    │       ├── test_complete_task.py
    │       ├── test_delete_task.py
    │       └── test_update_task.py
    ├── integration/
    │   ├── test_chat_endpoint.py
    │   ├── test_agent_integration.py
    │   └── test_mcp_server.py
    └── e2e/
        ├── test_create_task_workflow.py
        ├── test_list_tasks_workflow.py
        └── test_complete_task_workflow.py

frontend/
├── src/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx         # NEW: Chat interface page
│   │   ├── tasks/               # Existing from Phase 2
│   │   └── layout.tsx           # Existing
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInput.tsx        # NEW: Text input + mic button
│   │   │   ├── ChatMessage.tsx      # NEW: Message display
│   │   │   ├── MicrophoneButton.tsx # NEW: Voice input button
│   │   │   └── ChatHistory.tsx      # NEW: Conversation display
│   │   └── tasks/               # Existing from Phase 2
│   ├── hooks/
│   │   ├── useVoiceRecognition.tsx  # NEW: Web Speech API hook
│   │   ├── useChat.tsx              # NEW: Chat state management
│   │   └── useTasks.tsx         # Existing from Phase 2
│   ├── services/
│   │   ├── chatService.ts       # NEW: Chat API client
│   │   └── taskService.ts       # Existing from Phase 2
│   └── types/
│       ├── chat.ts              # NEW: Chat types
│       └── task.ts              # Existing from Phase 2
└── tests/
    ├── unit/
    │   ├── components/
    │   │   ├── MicrophoneButton.test.tsx
    │   │   ├── ChatInput.test.tsx
    │   │   └── ChatMessage.test.tsx
    │   └── hooks/
    │       ├── useVoiceRecognition.test.tsx
    │       └── useChat.test.tsx
    ├── integration/
    │   └── voice_to_chat_flow.test.tsx
    └── e2e/
        ├── voice_input_task_creation.spec.ts
        └── voice_input_permissions.spec.ts
```

**Structure Decision**: Web application structure (Option 2) with existing Phase 2 backend/frontend foundation. New components added for chat, conversation persistence, MCP server, and voice input. Maintains Phase 2 architectural separation.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Event-Driven partial (inline email) | Phase 3 timeline; full event-driven in Phase 5 | Synchronous email blocks task creation response; need non-blocking but not yet Kafka infrastructure |

## Architectural Decisions

### ADR-001: Stateless Conversation Architecture

**Context**: Phase 3 requires chatbot with conversation persistence. Two approaches: (1) in-memory sessions with sticky routing, (2) database-persisted state with stateless servers.

**Decision**: Database-persisted conversation state with stateless backend.

**Rationale**:
- Aligns with Constitution Principle V (Stateless Agents) and Principle XI (Stateless Architecture pillar)
- Enables horizontal scaling without session affinity complexity
- Survives server restarts with zero data loss (FR-005 requirement)
- Supports multi-device access with conversation_id (FR-024 requirement)
- Conversation history fetch on every request maintains context (FR-004 requirement)

**Consequences**:
- Database query overhead on every chat request (acceptable: 50 concurrent users target)
- Conversation history limited to 50 messages to control query size (Assumption 6)
- Simpler deployment: no need for Redis/session store or sticky sessions

**Alternatives Considered**:
- In-memory sessions: Rejected due to statelessness requirement and restart persistence need
- Hybrid (cache + DB): Deferred complexity; database-only sufficient for Phase 3 scale

---

### ADR-002: MCP as Agent-Tool Abstraction Layer

**Context**: AI agent needs to perform task operations. Two approaches: (1) agent calls task API directly, (2) agent uses MCP tools that wrap task operations.

**Decision**: MCP (Model Context Protocol) server with 5 tools as abstraction layer between AI and task operations.

**Rationale**:
- Enforces Constitution Principle V (Deterministic AI & Tooling)
- Pydantic schemas provide strict input validation before business logic (FR-006, FR-007)
- Tools are independently testable and composable (FR-028 requirement)
- OpenAI Agents SDK natively supports MCP tool integration (FR-009, FR-011)
- Future extensibility: new capabilities added as tools without agent prompt changes

**Consequences**:
- Additional abstraction layer complexity
- MCP tools must validate user_id independently (security requirement FR-007)
- Tool responses must be structured JSON for agent parsing (FR-008)

**Alternatives Considered**:
- Direct API calls from agent: Rejected due to lack of structured schemas and security validation
- Custom tool protocol: Rejected in favor of standard MCP for ecosystem compatibility

---

### ADR-003: Email Notification Integration Pattern

**Context**: FR-032 requires email notifications on task creation. Two approaches: (1) synchronous email send, (2) async fire-and-forget.

**Decision**: Asynchronous fire-and-forget email notification with error logging.

**Rationale**:
- Email service failure must not block task creation (FR-015, Assumption 14)
- Aligns with Constitution Principle VII (Event-Driven Decoupling) intent
- User feedback: task creation success, email delivery is best-effort
- Edge case handled: "Email notification failure" logs error, returns success (Edge Cases section)

**Consequences**:
- User may create task successfully but not receive email (acceptable per requirements)
- Email delivery failures logged for monitoring but not retried (Phase 3 scope)
- Inline async call acceptable for Phase 3; full event-driven queue in Phase 5

**Implementation**:
```python
# In add_task MCP tool
task = task_repository.create(user_id, title, description)
asyncio.create_task(email_service.send_task_created(user_id, task.id))
return {"task_id": task.id, "status": "created"}
```

**Alternatives Considered**:
- Synchronous email: Rejected due to blocking requirement and SLA dependency
- Event queue (Kafka): Deferred to Phase 5 (Constitution Principle VIII - phased evolution)

---

### ADR-004: Multilingual System Prompt Engineering

**Context**: FR-031 requires English and Urdu (Roman/Script) support. Two approaches: (1) separate agents per language, (2) single multilingual agent.

**Decision**: Single agent with multilingual system prompt that detects and responds in user's language.

**Rationale**:
- OpenAI models support multilingual understanding without fine-tuning (Assumption 12)
- Simpler architecture: one agent, one prompt, one deployment
- System prompt instructs: "Detect user language (English or Urdu Roman/Script) and respond in same language" (FR-010)
- Language switching mid-conversation handled naturally (Edge Case: "Language switching mid-conversation")

**Consequences**:
- System prompt complexity increases (multilingual instructions)
- Language detection accuracy depends on model capability (90%+ target per SC-013)
- Urdu Roman vs Script detection left to model (both supported per FR-031)

**System Prompt Structure**:
```text
You are a helpful task management assistant. You can understand and respond in:
- English
- Urdu (Roman script, e.g., "Task add karo")
- Urdu (Urdu script, e.g., "ٹاسک شامل کریں")

Detect the user's language and respond in the same language.
Use the following tools to help users manage tasks: add_task, list_tasks, complete_task, delete_task, update_task.
```

**Alternatives Considered**:
- Separate agents: Rejected due to deployment complexity and language switching difficulty
- Language parameter in request: Rejected; auto-detection preferred per requirements

---

### ADR-005: Frontend Voice Input Architecture

**Context**: FR-033 requires voice-to-text input. Two approaches: (1) frontend-only Web Speech API, (2) backend speech-to-text service.

**Decision**: Frontend-only implementation using browser's Web Speech API.

**Rationale**:
- Maintains stateless backend architecture (no audio upload/processing)
- Progressive enhancement: voice optional, text required (Assumption 19)
- Web Speech API supported in target browsers (Chrome, Edge, Safari - Assumption 15)
- Zero backend cost: browser handles speech recognition
- Transcribed text sent to chat endpoint like typed text (FR-033)

**Consequences**:
- Browser compatibility: feature detection required, fallback to text-only
- Accuracy depends on browser's speech engine (85%+ target per SC-016)
- Urdu language support depends on Web Speech API capability (Assumption 18)
- Privacy: audio processing local to browser

**Implementation Flow**:
1. User clicks microphone button
2. Request microphone permission (if not granted)
3. Web Speech API starts listening
4. Speech transcribed to text, appears in input field
5. Text auto-submitted to chat endpoint (or manually sent)

**Alternatives Considered**:
- Backend speech-to-text (e.g., Whisper API): Rejected due to stateless requirement and cost
- Third-party speech service: Rejected in favor of native browser capability

## Phase 0: Research & Technology Validation

*NEEDS CLARIFICATION items from Technical Context resolved through research*

### Research Tasks

1. **OpenAI Agents SDK 0.2+ Integration**
   - Research: Official MCP tool integration patterns
   - Research: Stateless agent context management (conversation history injection)
   - Research: Error handling for tool call failures
   - **Output**: `research.md` - OpenAI Agents SDK best practices

2. **MCP (Model Context Protocol) SDK**
   - Research: Python MCP SDK tool definition patterns
   - Research: Pydantic schema integration for tool inputs/outputs
   - Research: Security best practices (user_id validation in tools)
   - **Output**: `research.md` - MCP tool development patterns

3. **Web Speech API Browser Compatibility**
   - Research: SpeechRecognition API support (Chrome, Edge, Safari)
   - Research: Urdu language support in Web Speech API
   - Research: Permission handling and fallback strategies
   - **Output**: `research.md` - Browser compatibility matrix

4. **Multilingual Prompt Engineering**
   - Research: OpenAI model Urdu language capabilities
   - Research: Language detection without explicit language parameter
   - Research: Urdu Roman vs Script detection reliability
   - **Output**: `research.md` - Multilingual prompt patterns

5. **Phase 2 Integration Points**
   - Research: Better Auth JWT middleware integration
   - Research: Notification service API contract (email alerts)
   - Research: Task API and TaskRepository interface
   - **Output**: `research.md` - Phase 2 integration guide

### Research Deliverable

File: `specs/003-ai-chatbot/research.md`

Expected sections:
- OpenAI Agents SDK: Context injection, tool registration, error handling
- MCP SDK: Tool schemas, security validation, testing patterns
- Web Speech API: Browser support matrix, permission flow, error handling
- Multilingual AI: Prompt engineering, language detection, Urdu support
- Phase 2 Integration: JWT extraction, email service contract, task repository usage

## Phase 1: Design & Contracts

### Data Models

File: `specs/003-ai-chatbot/data-model.md`

#### Conversation Model (SQLModel)

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174001",
                "created_at": "2025-12-17T10:00:00Z",
                "updated_at": "2025-12-17T10:05:00Z"
            }
        }
```

**Validation Rules**:
- `user_id`: Must exist in `users` table (foreign key constraint)
- `created_at`, `updated_at`: UTC datetime, auto-managed
- Index on `user_id` for efficient user conversation queries

**State Transitions**: None (conversations don't have explicit states)

---

#### Message Model (SQLModel)

```python
from sqlmodel import Field, SQLModel, Relationship, Enum
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum as PyEnum

class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)  # Denormalized for security
    role: MessageRole = Field(sa_column=Column(Enum(MessageRole)))
    content: str = Field(max_length=2000)  # Max message length per Assumption 9
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "789e4567-e89b-12d3-a456-426614174002",
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "456e4567-e89b-12d3-a456-426614174001",
                "role": "user",
                "content": "Add task: Buy groceries",
                "created_at": "2025-12-17T10:00:00Z"
            }
        }
```

**Validation Rules**:
- `conversation_id`: Must exist in `conversations` table (foreign key constraint)
- `user_id`: Must match conversation owner (validated in repository layer)
- `role`: Enum - either "user" or "assistant" (strict type)
- `content`: Non-empty, max 2000 characters (Assumption 9)
- `created_at`: UTC datetime, auto-managed
- Composite index on `(conversation_id, created_at)` for efficient history queries

**State Transitions**: None (messages are immutable once created)

---

### API Contracts

File: `specs/003-ai-chatbot/contracts/chat_endpoint.openapi.yaml`

#### Chat Endpoint (POST /api/{user_id}/chat)

**Request Schema**:
```yaml
paths:
  /api/{user_id}/chat:
    post:
      summary: Send message to AI chatbot
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  maxLength: 2000
                  description: User's natural language message
                conversation_id:
                  type: string
                  format: uuid
                  nullable: true
                  description: Existing conversation ID (null for new conversation)
              example:
                message: "Add task: Buy groceries"
                conversation_id: "123e4567-e89b-12d3-a456-426614174000"
      responses:
        '200':
          description: Successful response from chatbot
          content:
            application/json:
              schema:
                type: object
                required:
                  - conversation_id
                  - response
                properties:
                  conversation_id:
                    type: string
                    format: uuid
                    description: Conversation ID (new or existing)
                  response:
                    type: string
                    description: AI-generated response
                  tool_calls:
                    type: array
                    items:
                      type: object
                      properties:
                        tool:
                          type: string
                          enum: [add_task, list_tasks, complete_task, delete_task, update_task]
                        parameters:
                          type: object
                        result:
                          type: object
                  created_at:
                    type: string
                    format: date-time
              example:
                conversation_id: "123e4567-e89b-12d3-a456-426614174000"
                response: "I've added 'Buy groceries' to your task list."
                tool_calls:
                  - tool: "add_task"
                    parameters:
                      user_id: "456e4567-e89b-12d3-a456-426614174001"
                      title: "Buy groceries"
                    result:
                      task_id: "789e4567-e89b-12d3-a456-426614174003"
                      status: "created"
                created_at: "2025-12-17T10:00:00Z"
        '400':
          description: Bad request (invalid message, malformed JSON)
        '401':
          description: Unauthorized (missing or invalid JWT)
        '403':
          description: Forbidden (user_id mismatch with token)
        '500':
          description: Internal server error (AI agent failure, DB error)
```

**Security Requirements** (FR-005, FR-022, FR-023):
- JWT token required in `Authorization: Bearer <token>` header
- Extract `user_id` claim from JWT
- Validate `user_id` in path matches JWT claim
- Reject request if mismatch (403 Forbidden)

---

### MCP Tool Definitions

File: `specs/003-ai-chatbot/contracts/mcp_tools.json`

#### Tool 1: add_task

```json
{
  "name": "add_task",
  "description": "Create a new task for the user",
  "input_schema": {
    "type": "object",
    "required": ["user_id", "title"],
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "User ID (must match authenticated user)"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "Task title"
      },
      "description": {
        "type": "string",
        "maxLength": 1000,
        "description": "Optional task description"
      }
    }
  },
  "output_schema": {
    "type": "object",
    "required": ["task_id", "status", "title"],
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid"
      },
      "status": {
        "type": "string",
        "enum": ["created"]
      },
      "title": {
        "type": "string"
      },
      "email_sent": {
        "type": "boolean",
        "description": "Whether email notification was sent (best-effort)"
      }
    }
  }
}
```

**Security**: Validates `user_id` matches authenticated user before database operation (FR-007).
**Side Effect**: Triggers email notification asynchronously (FR-032).

---

#### Tool 2: list_tasks

```json
{
  "name": "list_tasks",
  "description": "Retrieve user's task list with optional status filter",
  "input_schema": {
    "type": "object",
    "required": ["user_id"],
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "User ID (must match authenticated user)"
      },
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "default": "all",
        "description": "Filter tasks by status"
      }
    }
  },
  "output_schema": {
    "type": "object",
    "required": ["tasks", "count"],
    "properties": {
      "tasks": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "task_id": {"type": "string", "format": "uuid"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "completed": {"type": "boolean"},
            "created_at": {"type": "string", "format": "date-time"}
          }
        }
      },
      "count": {
        "type": "integer",
        "description": "Total number of tasks returned"
      }
    }
  }
}
```

**Security**: Validates `user_id` matches authenticated user (FR-007).

---

#### Tool 3: complete_task

```json
{
  "name": "complete_task",
  "description": "Mark a task as completed",
  "input_schema": {
    "type": "object",
    "required": ["user_id", "task_id"],
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "User ID (must match authenticated user)"
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "Task ID to mark as completed"
      }
    }
  },
  "output_schema": {
    "type": "object",
    "required": ["task_id", "status", "title"],
    "properties": {
      "task_id": {"type": "string", "format": "uuid"},
      "status": {"type": "string", "enum": ["completed"]},
      "title": {"type": "string"}
    }
  }
}
```

**Security**: Validates `user_id` matches authenticated user AND task belongs to user (FR-007).

---

#### Tool 4: delete_task

```json
{
  "name": "delete_task",
  "description": "Delete a task permanently",
  "input_schema": {
    "type": "object",
    "required": ["user_id", "task_id"],
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "User ID (must match authenticated user)"
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "Task ID to delete"
      }
    }
  },
  "output_schema": {
    "type": "object",
    "required": ["task_id", "status"],
    "properties": {
      "task_id": {"type": "string", "format": "uuid"},
      "status": {"type": "string", "enum": ["deleted"]}
    }
  }
}
```

**Security**: Validates `user_id` matches authenticated user AND task belongs to user (FR-007).

---

#### Tool 5: update_task

```json
{
  "name": "update_task",
  "description": "Update task title and/or description",
  "input_schema": {
    "type": "object",
    "required": ["user_id", "task_id"],
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "User ID (must match authenticated user)"
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "Task ID to update"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "New task title (optional)"
      },
      "description": {
        "type": "string",
        "maxLength": 1000,
        "description": "New task description (optional)"
      }
    }
  },
  "output_schema": {
    "type": "object",
    "required": ["task_id", "status", "title"],
    "properties": {
      "task_id": {"type": "string", "format": "uuid"},
      "status": {"type": "string", "enum": ["updated"]},
      "title": {"type": "string"},
      "description": {"type": "string"}
    }
  }
}
```

**Security**: Validates `user_id` matches authenticated user AND task belongs to user (FR-007).
**Validation**: At least one of `title` or `description` must be provided (validated in tool logic).

---

### System Prompt

File: `specs/003-ai-chatbot/contracts/system_prompt.md`

```markdown
# Task Management Assistant - System Prompt

You are a helpful task management assistant. Your job is to help users manage their todo lists through natural conversation.

## Language Support

You can understand and respond in the following languages:
- **English**: Standard English language
- **Urdu (Roman script)**: E.g., "Task add karo", "Meray tasks dikhao"
- **Urdu (Urdu script)**: E.g., "ٹاسک شامل کریں", "میرے ٹاسک دکھاؤ"

**Important**: Detect the user's language from their message and respond in the SAME language. If the user switches languages mid-conversation, switch your responses to match.

## Available Tools

You have access to these tools to help users:

1. **add_task**: Create a new task
2. **list_tasks**: Show user's tasks (all, pending, or completed)
3. **complete_task**: Mark a task as done
4. **delete_task**: Remove a task
5. **update_task**: Change task title or description

## Conversation Guidelines

1. **Be conversational**: Respond naturally, not like a command line
2. **Confirm actions**: When you create/update/delete a task, confirm what you did
3. **Ask for clarification**: If the user's intent is unclear, ask questions
4. **Show context awareness**: Remember what was just discussed in the conversation
5. **Handle errors gracefully**: If a task doesn't exist or an operation fails, explain kindly

## Examples

**English**:
- User: "Add task: Buy groceries"
- You: "I've added 'Buy groceries' to your task list." [use add_task tool]

**Urdu (Roman)**:
- User: "Meray tasks dikhao"
- You: "Yahaan aapke tasks hain:" [use list_tasks tool]

**Urdu (Script)**:
- User: "ٹاسک شامل کریں: دودھ خریدنا"
- You: "میں نے 'دودھ خریدنا' آپ کی ٹاسک لسٹ میں شامل کر دیا ہے۔" [use add_task tool]

## Important Notes

- Always use tools to perform actions; never claim to do something without calling the tool
- The user_id parameter for tools is provided by the system; use it as-is
- When listing tasks, format them clearly (e.g., numbered list)
- If a tool call fails, explain the error to the user simply
```

---

### Quickstart Guide

File: `specs/003-ai-chatbot/quickstart.md`

```markdown
# Phase 3: AI Chatbot - Developer Quickstart

## Prerequisites

- Phase 2 completed and running (Task API, JWT auth, notification service, Neon DB)
- Python 3.13+ with `uv` package manager
- Node.js 20+ for frontend
- OpenAI API key
- Browser with Web Speech API support (Chrome, Edge, Safari) for voice features

## Environment Setup

Add to `.env`:
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# Existing Phase 2 vars
DATABASE_URL=postgresql://...
JWT_SECRET=...
EMAIL_SERVICE_URL=http://localhost:8001/send-email
```

## Backend Setup

### Install Dependencies

```bash
cd backend
uv pip install openai-agents-sdk mcp pydantic sqlmodel
```

### Database Migration

Create new tables:
```bash
# Run Alembic migration (or manual SQL)
alembic revision --autogenerate -m "Add conversation and message tables"
alembic upgrade head
```

### Run MCP Server

```bash
cd backend
uv run python -m src.services.mcp_server
# Should register 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
```

### Run Backend

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

Test chat endpoint:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: Buy groceries"}'
```

## Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Run Frontend

```bash
cd frontend
npm run dev
# Access at http://localhost:3000
```

Navigate to `/chat` to access chatbot interface.

### Test Voice Input

1. Click microphone button
2. Grant microphone permission when prompted
3. Speak: "Add task buy groceries"
4. Text should appear in input field
5. Message auto-submitted to chat endpoint

## Running Tests

### Backend Tests

```bash
cd backend
uv run pytest tests/unit/mcp/  # MCP tools
uv run pytest tests/integration/test_chat_endpoint.py  # Chat API
uv run pytest tests/e2e/  # End-to-end workflows
```

### Frontend Tests

```bash
cd frontend
npm run test  # Unit tests (Vitest/Jest)
npm run test:e2e  # E2E tests (Playwright)
```

## Architecture Overview

```
User (Browser)
  ├── Voice Input (Web Speech API) → Text
  └── Text Input
         ↓
  Next.js Chat UI
         ↓
  POST /api/{user_id}/chat
         ↓
  FastAPI Chat Endpoint
    ├── Validate JWT (extract user_id)
    ├── Fetch conversation history (last 50 messages)
    ├── Call OpenAI Agents SDK
    │     └── System Prompt (multilingual)
    │     └── Conversation history
    │     └── User message
    │            ↓
    │     AI Agent decides which tool to call
    │            ↓
    ├── MCP Server (5 tools)
    │   ├── add_task → TaskRepository.create() → Email Service (async)
    │   ├── list_tasks → TaskRepository.list()
    │   ├── complete_task → TaskRepository.update()
    │   ├── delete_task → TaskRepository.delete()
    │   └── update_task → TaskRepository.update()
    │
    ├── Save user message to DB
    ├── Save assistant response to DB
    └── Return response + conversation_id
```

## Key Files to Understand

**Backend**:
- `src/api/routes/chat.py` - Chat endpoint handler
- `src/services/chat_service.py` - Orchestrates agent + conversation
- `src/services/mcp_server.py` - MCP tool definitions
- `src/prompts/system_prompt.py` - Multilingual system prompt
- `src/models/conversation.py` - Conversation SQLModel
- `src/models/message.py` - Message SQLModel

**Frontend**:
- `src/app/chat/page.tsx` - Chat interface
- `src/components/chat/ChatInput.tsx` - Text + mic button
- `src/components/chat/MicrophoneButton.tsx` - Voice input
- `src/hooks/useVoiceRecognition.tsx` - Web Speech API hook
- `src/hooks/useChat.tsx` - Chat state management

## Common Issues

**Issue**: "OpenAI API key not found"
**Fix**: Check `.env` has `OPENAI_API_KEY` set

**Issue**: "Microphone button disabled"
**Fix**: Use Chrome/Edge/Safari; check HTTPS (localhost OK)

**Issue**: "403 Forbidden on chat endpoint"
**Fix**: JWT user_id must match path parameter `{user_id}`

**Issue**: "Email notification failed but task created"
**Fix**: This is expected behavior (best-effort email). Check email service logs.

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Follow TDD: write test → implement → refactor
3. Implement foundation (MCP server, DB models, repositories)
4. Implement P1 user stories (create, view, complete tasks)
5. Implement P2 enhancements (delete, update, voice input)
```

## Agent Context Update

**Action**: Run `.specify/scripts/bash/update-agent-context.sh claude` after Phase 1 artifacts generated.

**Technologies to Add**:
- OpenAI Agents SDK (AI orchestration)
- MCP SDK (tool protocol)
- Web Speech API (voice input)
- SQLModel Conversation and Message models

**Note**: Preserve existing Phase 2 technologies (FastAPI, Next.js, Better Auth, etc.).

## Phase 2 Readiness

This plan completes Phase 1 (Design & Contracts). The next command is `/sp.tasks` to generate dependency-ordered implementation tasks with TDD test cases.

**Deliverables Ready**:
- ✅ plan.md (this file)
- ⏳ research.md (Phase 0 - to be generated)
- ⏳ data-model.md (Phase 1 - to be generated)
- ⏳ contracts/ (Phase 1 - to be generated)
- ⏳ quickstart.md (Phase 1 - to a be generated)

**Constitution Re-Check** (Post-Design): PASS - all architectural decisions align with principles.

---
---

## Addendum: Implementation Plan for Tags & Rich Notes

**Date**: 2026-01-05 | **Spec Addendum**: [spec.md](./spec.md) (User Stories 9 & 10)

This addendum details the plan to implement Task Tags and Rich Notes (Markdown) functionality, enhancing the core task model.

### 1. Backend Changes

#### 1.1. Database Schema (SQLModel)

We will introduce two new models for the many-to-many relationship and update the `Task` model.

**New Model: `Tag`**
File: `backend/src/models/tag.py`
```python
import uuid
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

class Tag(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True) # Initially global, can be scoped to user later
    user_id: str = Field(index=True)
    color: Optional[str] = Field(default=None)
    tasks: List["Task"] = Relationship(back_populates="tags", link_model=TaskTagLink)
```

**New Model: `TaskTagLink` (Join Table)**
File: `backend/src/models/task_tag_link.py`
```python
from sqlmodel import Field, SQLModel
import uuid

class TaskTagLink(SQLModel, table=True):
    task_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tasks.id", primary_key=True)
    tag_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tags.id", primary_key=True)
```

**Update `Task` Model**
File: `backend/src/models/task.py` (Update)
- Add the `tags` relationship.
- Ensure `description` can handle larger text for Markdown.

```python
# In models/task.py
from typing import List
from sqlmodel import Relationship

class Task(SQLModel, table=True):
    # ... existing fields
    tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)
    # Ensure description has a TEXT type in the DB via `sa_column=Column(Text)` if needed
```

#### 1.2. Task Repository (`task_repository.py`)

The repository will be updated to manage tags.

- **`create()`**:
    - Accept an optional `tags: List[str]` argument.
    - For each tag string, find it in the `tags` table or create it (`find_or_create`).
    - Associate the found/created tags with the new task.
- **`update()`**:
    - Accept `tags_to_add: List[str]` and `tags_to_remove: List[str]`.
    - Handle adding and removing associations in the `tasktaglinks` table.
- **`list_by_user()`**:
    - Accept an optional `tags: List[str]` filter.
    - Modify the query to join with `tasktaglinks` and `tags` to filter tasks.

#### 1.3. MCP Tools (`mcp_server/tools/`)

The tool schemas and logic will be updated.

- **`add_task`**:
    - Add `tags: Optional[List[str]] = None` to the function signature and schema.
    - Pass the tags to the `task_repository.create()` method.
- **`update_task`**:
    - Add `tags_to_add: Optional[List[str]] = None` and `tags_to_remove: Optional[List[str]] = None`.
    - Pass them to the `task_repository.update()` method.
- **`list_tasks`**:
    - Add `tags: Optional[List[str]] = None` to filter the task list.
- **System Prompt**: Update the agent's system prompt to inform it about the new `tags` parameter and how to use it, especially with hashtags (`#tag`).

### 2. Frontend Changes

#### 2.1. UI Components

- **`TagInput` Component**:
    - Create a new component for selecting and creating tags.
    - It should support autocompletion for existing tags.
    - It should allow creating new tags on the fly.
    - Use a library like `shadcn-multi-select` or build a custom one using `cmdk`.
- **`TagBadge` Component**:
    - A simple component to display a tag with a colored badge.
- **`MarkdownRenderer` Component**:
    - Use a library like `react-markdown` with plugins for GitHub Flavored Markdown (`remark-gfm`).
    - This component will be used to render the task `description` wherever it's displayed (e.g., in a task detail view).

#### 2.2. View Modifications

- **`add-task-dialog.tsx`**:
    - Integrate the new `TagInput` component to allow users to add tags when creating a task.
- **`task-item.tsx`**:
    - Use the `TagBadge` component to display the tags associated with each task in the list.
- **Task Detail View** (if it exists, or create one):
    - Use the `MarkdownRenderer` to display the task's `description` (notes).

### 3. ADR-006: Many-to-Many Relationship for Tags

**Context**: We need to associate tasks with multiple tags, and a single tag can be used across multiple tasks.

**Decision**: Implement a Many-to-Many relationship using a third join table (`TaskTagLink`).

**Rationale**:
- **Scalability**: A many-to-many relationship is the standard, scalable way to model this. It avoids data duplication (like storing tags as a comma-separated string) and allows for efficient querying.
- **Extensibility**: It allows `Tag` to become a rich entity in the future (e.g., with its own color, description, etc.) without changing the `Task` model.
- **SQLModel Support**: `SQLModel` provides a clear and idiomatic way to define many-to-many relationships using `Relationship` and `link_model`.

**Consequences**:
- Requires an additional table in the database (`tasktaglinks`).
- Database queries for tasks with tags will be slightly more complex, involving a `JOIN`.
- Requires an Alembic migration script to create the new tables and relationships.

**Alternatives Considered**:
- **JSON Field/Array in `Task` model**: Storing tags as an array in a JSON field. Rejected because it makes querying/filtering by tag inefficient and non-standard across different SQL databases.
- **Comma-Separated String**: Rejected for being an anti-pattern that is difficult to query, maintain, and scale.
