# Implementation Tasks: AI-Powered Todo Chatbot

**Branch**: `003-ai-chatbot` | **Date**: 2025-12-17
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

## Overview

Implementation decomposed into atomic, independently completable tasks following TDD cycles.

**Key Principles:**
- Each task is 1-2 hours, immediately executable
- Tests written before implementation (TDD)
- Tasks ordered by dependency (foundational → features → polish)

---

## Phase 1: Foundation - Database Models

**Goal**: Create database schema for conversations and messages

### [ ] [T001] [P1] [US1] Create Conversation SQLModel
- File: `backend/src/models/conversation.py`
- Define Conversation model with fields: id (UUID), user_id (FK), created_at, updated_at
- Add relationship to Message model
- Ensure user_id is indexed for efficient queries

### [ ] [T002] [P1] [US1] Write tests for Conversation model
- File: `backend/tests/unit/models/test_conversation.py`
- Test: conversation creation with valid user_id
- Test: auto-generated UUID and timestamps
- Test: user_id index exists

### [ ] [T003] [P1] [US1] Create Message SQLModel with MessageRole enum
- File: `backend/src/models/message.py`
- Define MessageRole enum (USER, ASSISTANT)
- Define Message model with fields: id (UUID), conversation_id (FK), user_id (FK), role, content (max 2000 chars), created_at
- Ensure conversation_id, user_id, and created_at are indexed

### [ ] [T004] [P1] [US1] Write tests for Message model
- File: `backend/tests/unit/models/test_message.py`
- Test: message creation with valid fields
- Test: MessageRole enum validation
- Test: content max length (2000 chars)
- Test: required indexes exist

### [ ] [T005] [P1] [US1] Create ConversationRepository
- File: `backend/src/repositories/conversation_repository.py`
- Implement: create_conversation(user_id) → Conversation
- Implement: get_by_id(conversation_id) → Conversation | None
- Implement: get_by_user(user_id, limit, offset) → list[Conversation]
- Implement: delete_conversation(conversation_id) → bool

### [ ] [T006] [P1] [US1] Write tests for ConversationRepository
- File: `backend/tests/unit/repositories/test_conversation_repository.py`
- Test: create conversation returns valid Conversation
- Test: get_by_id returns None for non-existent ID
- Test: get_by_user returns paginated results
- Test: delete_conversation removes conversation

### [ ] [T007] [P1] [US1] Create MessageRepository
- File: `backend/src/repositories/message_repository.py`
- Implement: create_message(conversation_id, user_id, role, content) → Message
- Implement: get_by_conversation(conversation_id, limit, offset) → list[Message]
- Implement: get_history(conversation_id) → list[Message] (ordered by created_at)

### [ ] [T008] [P1] [US1] Write tests for MessageRepository
- File: `backend/tests/unit/repositories/test_message_repository.py`
- Test: create_message returns valid Message
- Test: get_by_conversation returns paginated messages
- Test: get_history returns messages in chronological order

### [ ] [T009] [P1] [Foundation] Create Alembic migration for Conversation and Message tables
- File: `backend/alembic/versions/xxx_add_conversation_message_tables.py`
- Add conversations table with indexes
- Add messages table with indexes and foreign keys
- Include upgrade and downgrade functions

---

## Phase 2: MCP Server - AI Agent Tools

**Goal**: Implement 5 MCP tools for task management with email integration

### [ ] [T010] [P1] [US1] Define Pydantic schemas for MCP tools
- File: `backend/src/mcp_server/schemas.py`
- AddTaskInput/Output, ListTasksInput/Output, CompleteTaskInput/Output, DeleteTaskInput/Output, UpdateTaskInput/Output
- Include user_id validation in all schemas

### [ ] [T011] [P1] [US1,US4] Implement add_task MCP tool with email notification
- File: `backend/src/mcp_server/tools/add_task.py`
- Validate user_id matches authenticated user
- Create task via Phase 2 TaskRepository
- Trigger async email notification (fire-and-forget)
- Return task_id and email_sent status

### [ ] [T012] [P1] [US1,US4] Write tests for add_task tool
- File: `backend/tests/unit/mcp/test_add_task.py`
- Test: successful task creation
- Test: email notification triggered
- Test: user_id mismatch raises error
- Test: email failure doesn't block task creation

### [ ] [T013] [P1] [US2] Implement list_tasks MCP tool
- File: `backend/src/mcp_server/tools/list_tasks.py`
- Validate user_id matches authenticated user
- Support optional status filter (completed/pending)
- Return list of tasks with pagination

### [ ] [T014] [P1] [US2] Write tests for list_tasks tool
- File: `backend/tests/unit/mcp/test_list_tasks.py`
- Test: returns user's tasks only
- Test: status filter works correctly
- Test: pagination limits results

### [ ] [T015] [P2] [US3] Implement complete_task MCP tool
- File: `backend/src/mcp_server/tools/complete_task.py`
- Validate user_id and task ownership
- Mark task as completed
- Return updated task

### [ ] [T016] [P2] [US3] Write tests for complete_task tool
- File: `backend/tests/unit/mcp/test_complete_task.py`
- Test: marks task as completed
- Test: prevents completing other user's tasks

### [ ] [T017] [P2] [US6] Implement delete_task MCP tool
- File: `backend/src/mcp_server/tools/delete_task.py`
- Validate user_id and task ownership
- Delete task permanently
- Return success status

### [ ] [T018] [P2] [US6] Write tests for delete_task tool
- File: `backend/tests/unit/mcp/test_delete_task.py`
- Test: deletes task successfully
- Test: prevents deleting other user's tasks

### [ ] [T019] [P2] [US7] Implement update_task MCP tool
- File: `backend/src/mcp_server/tools/update_task.py`
- Validate user_id and task ownership
- Update task title and/or description
- Return updated task

### [ ] [T020] [P2] [US7] Write tests for update_task tool
- File: `backend/tests/unit/mcp/test_update_task.py`
- Test: updates task fields
- Test: prevents updating other user's tasks

### [ ] [T021] [P1] [Foundation] Register MCP tools with OpenAI Agents SDK
- File: `backend/src/mcp_server/server.py`
- Initialize MCP server with 5 tools
- Configure tool schemas for OpenAI agent
- Export tools list for chat service

---

## Phase 3: Chat Service - AI Orchestration

**Goal**: Implement stateless AI chat endpoint with conversation persistence

### [ ] [T022] [P1] [US1,US5] Create ChatService with OpenAI Agents SDK
- File: `backend/src/services/chat_service.py`
- Initialize OpenAI agent with MCP tools
- Implement: process_message(user_id, message, conversation_id?) → response
- Load conversation history from database
- Persist user message and assistant response

### [ ] [T023] [P1] [US1,US5] Write tests for ChatService
- File: `backend/tests/unit/services/test_chat_service.py`
- Test: creates new conversation if conversation_id is None
- Test: loads existing conversation history
- Test: calls OpenAI agent with full context
- Test: persists messages to database

### [ ] [T024] [P1] [US1,US5] Implement multilingual system prompt (English + Urdu)
- File: `backend/src/services/prompts/system_prompt.md`
- Define system prompt with language detection instructions
- Support English, Roman Urdu, and Urdu script
- Instruct agent to mirror user's language

### [ ] [T025] [P1] [US1] Create POST /api/{user_id}/chat endpoint
- File: `backend/src/api/routes/chat.py`
- Validate JWT and extract user_id
- Accept: message (str), conversation_id (UUID | None)
- Call ChatService.process_message()
- Return: conversation_id, response, tool_calls, created_at

### [ ] [T026] [P1] [US1] Write integration tests for /chat endpoint
- File: `backend/tests/integration/test_chat_endpoint.py`
- Test: creates conversation on first message
- Test: continues existing conversation
- Test: validates JWT user_id matches path parameter
- Test: returns 403 if user_id mismatch

---

## Phase 4: Frontend - Chat UI and Voice Input

**Goal**: Build React chat interface with voice input

### [ ] [T027] [P1] [US1] Create Chat page with App Router
- File: `frontend/src/app/chat/page.tsx`
- Server Component for initial layout
- Client Component for chat interaction
- Display conversation history

### [ ] [T028] [P1] [US1] Create ChatMessage component
- File: `frontend/src/components/chat/ChatMessage.tsx`
- Display user and assistant messages
- Show message timestamp
- Support markdown rendering for assistant responses

### [ ] [T029] [P1] [US1] Create ChatInput component with send button
- File: `frontend/src/components/chat/ChatInput.tsx`
- Text input for message
- Send button
- Handle Enter key to send
- Clear input after send

### [ ] [T030] [P1] [US1] Implement useChatConversation hook
- File: `frontend/src/hooks/useChatConversation.tsx`
- Manage conversation state
- Send messages to POST /api/{user_id}/chat
- Update conversation history
- Handle loading and error states

### [ ] [T031] [P2] [US8] Create useVoiceRecognition hook with Web Speech API
- File: `frontend/src/hooks/useVoiceRecognition.tsx`
- Initialize SpeechRecognition with English language
- Provide: startListening(), stopListening(), transcript state
- Handle browser compatibility (Chrome/Edge/Safari)
- Emit events: onResult, onError, onEnd

### [ ] [T032] [P2] [US8] Create MicrophoneButton component
- File: `frontend/src/components/chat/MicrophoneButton.tsx`
- Show microphone icon (inactive/active/disabled states)
- Request microphone permission on first click
- Start/stop voice recognition
- Display visual feedback during listening

### [ ] [T033] [P2] [US8] Integrate voice input with ChatInput
- File: `frontend/src/components/chat/ChatInput.tsx` (update)
- Add MicrophoneButton next to send button
- Append voice transcript to text input in real-time
- Allow user to edit before sending
- Disable during network requests

---

## Phase 5: Integration & Polish

**Goal**: Connect Phase 3 with Phase 2 and add final enhancements

### [ ] [T034] [Foundation] Configure shared database connection for Phase 2 and 3
- File: `backend/src/config/database.py`
- Ensure Phase 3 models use same DATABASE_URL as Phase 2
- Configure SQLModel metadata to include both phases

### [ ] [T035] [Foundation] Update Phase 2 Better Auth to issue JWT for Phase 3
- File: Phase 2 `frontend/auth.ts` (update)
- Ensure JWT includes user_id claim
- Configure JWT expiry and secret sharing

### [ ] [T036] [Polish] Add error handling and retry logic for OpenAI API calls
- File: `backend/src/services/chat_service.py` (update)
- Implement exponential backoff for rate limits
- Handle OpenAI API errors gracefully
- Return user-friendly error messages

### [ ] [T037] [Polish] Write E2E test for complete chat flow
- File: `backend/tests/e2e/test_chat_flow.py`
- Test: user logs in → creates conversation → sends message → receives AI response → task created → email sent

### [ ] [T038] [Polish] Add loading states and optimistic updates to frontend
- File: `frontend/src/components/chat/ChatMessage.tsx` (update)
- Show skeleton loader during API calls
- Display user message immediately (optimistic UI)
- Handle message send failures

### [ ] [T039] [Polish] Create deployment configuration for Phase 3
- File: `backend/Dockerfile`, `docker-compose.yml` (Phase 3)
- Containerize Phase 3 backend
- Configure environment variables for production
- Document deployment steps

---

## Summary

**Total Tasks**: 39
**Foundation (Blocking)**: 9 tasks (T001-T009, Phase 1)
**User Stories P1**: 17 tasks (T010-T026, Phases 2-3)
**User Stories P2**: 8 tasks (T027-T034, Phase 4)
**Polish**: 5 tasks (T035-T039, Phase 5)

**Estimated Effort**: ~60-70 hours (6-7 working days)

**Dependency Flow**:
1. Foundation (Phase 1) → All other tasks depend on this
2. MCP Server (Phase 2) → Required for Chat Service
3. Chat Service (Phase 3) → Required for Frontend
4. Frontend (Phase 4) → Can start after Chat endpoint is ready
5. Integration & Polish (Phase 5) → Final touches

**Parallelization Opportunities**:
- After Phase 1: MCP tool tests can run in parallel
- After Phase 2: Frontend development can start while Chat Service is being built
- Phase 5 tasks are independent and can be parallelized
