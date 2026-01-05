# Feature Specification: AI-Powered Todo Chatbot

**Feature Branch**: `003-ai-chatbot`
**Created**: 2025-12-17
**Status**: Draft
**Input**: User description: "Phase 3: AI-Powered Todo Chatbot with OpenAI ChatKit, Agents SDK, and MCP Tools - implementing conversational interface for task management through natural language, stateless chat endpoint with database-persisted conversations, MCP server with 5 tools (add, list, complete, delete, update), OpenAI Agents SDK integration, and complete TDD workflow"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P1)

As a user, I want to create tasks by simply telling the chatbot what I need to do, so I can quickly capture todos without learning command syntax or clicking through forms.

**Example interactions**:
- User: "Add task: Buy groceries"
- User: "I need to remember to call mom tonight"
- User: "Create a task for the dentist appointment"

**Why this priority**: This is the most fundamental interaction - users must be able to add tasks conversationally before any other chatbot features are useful. Without this, the chatbot has no purpose.

**Independent Test**: Can be fully tested by sending natural language messages requesting task creation and verifying that tasks appear in the user's task list with correctly extracted information. Delivers immediate value as users can create tasks via chat without any other features.

**Acceptance Scenarios**:

1. **Given** the user is authenticated, **When** they send "Add task: Buy groceries", **Then** a new task is created with title "Buy groceries" and belongs to that user AND an email notification is sent to the user's registered email address
2. **Given** the user is authenticated, **When** they send "I need to remember to call mom", **Then** a new task is created with the essential information extracted from the message AND an email notification is triggered
3. **Given** the user sends a vague message like "Add task", **When** the chatbot cannot determine what to add, **Then** it asks clarifying questions
4. **Given** the user provides task details in a follow-up message, **When** the chatbot has context from previous messages, **Then** it creates the task with the combined information AND sends email notification
5. **Given** the user sends a message in Urdu (Roman) like "Task add karo: Doodh khareedna hai", **When** the chatbot detects Urdu language, **Then** it creates the task and responds in Urdu
6. **Given** the user sends a message in Urdu (Script) like "ٹاسک شامل کریں: دودھ خریدنا ہے", **When** the chatbot detects Urdu script, **Then** it creates the task and responds in Urdu script

---

### User Story 2 - Natural Language Task Viewing (Priority: P1)

As a user, I want to see my tasks by asking the chatbot in natural language, so I can quickly review what I need to do without navigating to a separate interface.

**Example interactions**:
- User: "Show me my tasks"
- User: "What's on my todo list?"
- User: "List all my pending tasks"

**Why this priority**: Equally critical to creation - users need to view their tasks to make the chatbot useful. These two features together form the minimum viable chatbot.

**Independent Test**: Can be fully tested by having the user request their task list and verifying the chatbot returns all their tasks in a readable format. Works independently as users can see their tasks even if other features aren't implemented.

**Acceptance Scenarios**:

1. **Given** the user has 5 tasks in their list, **When** they ask "Show my tasks", **Then** the chatbot displays all 5 tasks with their status and details
2. **Given** the user has no tasks, **When** they ask to see their tasks, **Then** the chatbot responds with a friendly message indicating the list is empty
3. **Given** the user asks "What's pending?", **When** they have both completed and pending tasks, **Then** the chatbot filters and shows only pending tasks
4. **Given** the user asks for tasks, **When** they have many tasks, **Then** the chatbot presents them in a structured, readable format (not overwhelming)
5. **Given** the user asks in Urdu "Meray tasks dikhao", **When** Urdu is detected, **Then** the chatbot responds with task list in Urdu language

---

### User Story 3 - Natural Language Task Completion (Priority: P1)

As a user, I want to mark tasks as complete by telling the chatbot, so I can update my progress without switching to another interface.

**Example interactions**:
- User: "Mark task 3 as done"
- User: "I finished buying groceries"
- User: "Complete the dentist appointment task"

**Why this priority**: Completes the basic task lifecycle (create → view → complete). These three stories form the absolute minimum for a functional todo chatbot that delivers value.

**Independent Test**: Can be fully tested by having tasks in the system, requesting completion via natural language, and verifying the task status changes. Delivers value independently as users can manage task lifecycle completely through chat.

**Acceptance Scenarios**:

1. **Given** the user has a task with ID 3, **When** they say "Mark task 3 as done", **Then** that task's status changes to completed
2. **Given** the user just listed their tasks and task "Buy groceries" was shown, **When** they say "Mark it as done", **Then** the chatbot understands the context and marks "Buy groceries" complete
3. **Given** the user says "I finished buying groceries", **When** a task matching that description exists, **Then** the chatbot completes the matching task
4. **Given** the user references a task that doesn't exist, **When** they try to complete it, **Then** the chatbot responds with a helpful error explaining the task wasn't found
5. **Given** the user says in Urdu "Task 3 complete kar do", **When** Urdu is detected, **Then** the task is marked complete and response is in Urdu

---

### User Story 4 - Natural Language Task Deletion (Priority: P2)

As a user, I want to remove tasks I no longer need by telling the chatbot, so I can keep my task list clean and relevant.

**Example interactions**:
- User: "Delete task 2"
- User: "Remove the grocery shopping task"
- User: "I don't need the dentist task anymore"

**Why this priority**: Important for task list maintenance, but users can still get value from create/view/complete without deletion. Enhances usability but isn't critical for core functionality.

**Independent Test**: Can be fully tested by having tasks in the system, requesting deletion via natural language, and verifying the task is removed. Works independently as a way to clean up the task list.

**Acceptance Scenarios**:

1. **Given** the user has a task with ID 2, **When** they say "Delete task 2", **Then** that task is removed from their list
2. **Given** the user says "Remove the grocery task", **When** a task matching that description exists, **Then** the chatbot confirms deletion and removes it
3. **Given** multiple tasks match the user's deletion request, **When** the chatbot can't determine which one, **Then** it asks for clarification listing the matching tasks
4. **Given** the user tries to delete a non-existent task, **When** the task ID or description doesn't match any tasks, **Then** the chatbot explains no matching task was found

---

### User Story 5 - Natural Language Task Updates (Priority: P2)

As a user, I want to modify existing tasks by telling the chatbot what to change, so I can correct mistakes or update task details without manual editing.

**Example interactions**:
- User: "Change task 1 to 'Call mom tonight'"
- User: "Update the grocery task to add milk and eggs"
- User: "Rename task 5"

**Why this priority**: Useful for maintaining accurate task information, but users can work around by deleting and recreating. Enhances experience but isn't critical for basic functionality.

**Independent Test**: Can be fully tested by having tasks in the system, requesting updates via natural language, and verifying the task content changes correctly. Works independently as a way to modify existing tasks.

**Acceptance Scenarios**:

1. **Given** the user has task 1 with title "Call mom", **When** they say "Change task 1 to Call mom tonight", **Then** the task title updates to "Call mom tonight"
2. **Given** the user says "Update the grocery task description", **When** they provide new details in a follow-up message, **Then** the chatbot updates the task with the new information
3. **Given** the user provides an ambiguous update command, **When** the chatbot can't determine what to change, **Then** it asks clarifying questions
4. **Given** the user tries to update a non-existent task, **When** the task doesn't exist, **Then** the chatbot explains the task wasn't found

---

### User Story 6 - Persistent Conversation History (Priority: P2)

As a user, I want my conversations with the chatbot to be saved, so I can resume where I left off across different sessions and devices.

**Why this priority**: Enhances user experience by maintaining context over time, but users can still accomplish all task operations without conversation persistence. Important for long-term usability but not critical for initial value delivery.

**Independent Test**: Can be fully tested by starting a conversation, closing the session, reopening it, and verifying the chatbot remembers the previous context. Works independently as a way to maintain user experience continuity.

**Acceptance Scenarios**:

1. **Given** the user has had a conversation with the chatbot, **When** they return later and start a new session, **Then** the conversation history is available and the chatbot maintains context
2. **Given** the user switches devices, **When** they access the chatbot from a different device, **Then** their conversation history is accessible
3. **Given** a conversation becomes very long, **When** it exceeds reasonable memory limits, **Then** the system maintains recent context while efficiently managing storage
4. **Given** the server restarts, **When** the user returns to the chatbot, **Then** their conversation history persists and is not lost

---

### User Story 7 - Multi-turn Contextual Understanding (Priority: P3)

As a user, I want the chatbot to remember what we just talked about, so I can make follow-up requests without repeating information.

**Example interactions**:
- User: "Show my tasks" → Chatbot: [lists tasks] → User: "Mark the first one as done"
- User: "Add task: Call mom" → Chatbot: "Task created" → User: "Actually, change it to call mom tonight"

**Why this priority**: Improves conversation flow and feels more natural, but users can accomplish everything by being explicit in each message. This is a delighter feature that makes the chatbot feel smarter but isn't essential for core functionality.

**Independent Test**: Can be fully tested by conducting multi-turn conversations with implied references and verifying the chatbot correctly resolves them from context. Works independently as a conversation quality enhancement.

**Acceptance Scenarios**:

1. **Given** the user just listed their tasks, **When** they say "Mark the first one complete" without specifying which task, **Then** the chatbot correctly identifies and completes the first task from the previous list
2. **Given** the user just created a task, **When** they immediately say "Delete it", **Then** the chatbot understands "it" refers to the just-created task
3. **Given** the user says "Add task: Buy milk" followed by "Also add buy eggs", **When** the second message uses contextual clues, **Then** the chatbot correctly creates a second task
4. **Given** the conversation context becomes ambiguous, **When** the chatbot can't resolve a reference, **Then** it asks for clarification rather than guessing incorrectly

---

### User Story 8 - Voice-to-Text Input (Priority: P2)

As a user, I want to speak my tasks and commands into the chatbot using voice input, so I can interact hands-free or more naturally without typing.

**Example interactions**:
- User clicks microphone button and says "Add task buy groceries"
- User speaks "Show me my tasks" and it's converted to text automatically
- User says "Task add karo doodh khareedna hai" in Urdu

**Why this priority**: Enhances accessibility and provides hands-free interaction, but all features work perfectly via text input. This is a delighter that makes the chatbot more accessible but isn't critical for core functionality.

**Independent Test**: Can be fully tested by clicking the microphone button, speaking commands, verifying text appears in the input field, and confirming it sends to chat endpoint correctly. Works independently as an input method enhancement.

**Acceptance Scenarios**:

1. **Given** the user is on the chat interface, **When** they click the microphone button, **Then** the browser requests microphone permission (if not already granted)
2. **Given** microphone permission is granted, **When** the user speaks "Add task buy groceries", **Then** the text "Add task buy groceries" appears in the input field
3. **Given** the user has spoken a command, **When** speech recognition completes, **Then** the text is automatically sent to the chat endpoint
4. **Given** the user speaks in Urdu, **When** Web Speech API detects Urdu language, **Then** the Urdu text (Roman or Script based on API) appears in the input field
5. **Given** the browser doesn't support Web Speech API, **When** the user accesses the chat interface, **Then** the microphone button is hidden or disabled with a tooltip explaining why
6. **Given** the user denies microphone permission, **When** they click the microphone button, **Then** a helpful error message explains permission is needed
7. **Given** speech recognition fails or times out, **When** no speech is detected, **Then** the microphone button returns to normal state with error feedback

---

### Edge Cases

- **Empty task title**: What happens when user says "Add task" without providing any task description? → Chatbot should ask "What task would you like to add?"
- **Invalid task reference**: How does system handle "Mark task 999 as done" when task 999 doesn't exist? → Return friendly error: "I couldn't find task 999 in your list. Would you like to see your current tasks?"
- **Ambiguous commands**: User says "Complete it" without prior context → Chatbot asks "Which task would you like to complete?"
- **Multiple matching tasks**: User says "Delete the shopping task" when there are 3 tasks with "shopping" in the title → Chatbot lists options: "I found 3 tasks with 'shopping'. Which one? 1. Buy groceries, 2. Shopping list, 3. Shopping mall visit"
- **Server restart mid-conversation**: What happens when the server restarts while user is chatting? → Conversation history persists in database, user can resume seamlessly
- **Very long messages**: How does system handle user sending a paragraph of text? → Extract actionable tasks or ask for clarification on what action is needed
- **No authentication token**: What happens when an unauthenticated request arrives? → Return 401 Unauthorized with message to log in
- **Token/user_id mismatch**: MCP tool receives user_id that doesn't match JWT token → Reject operation with security error
- **Conversation not found**: User sends conversation_id that doesn't exist or belong to them → Create new conversation or return error depending on context
- **Rapid successive messages**: User sends multiple messages quickly before first completes → Queue and process in order, maintaining conversation coherence
- **Email notification failure**: What happens when task is created successfully but email service fails? → Log error, return success response to user, task creation should not be rolled back
- **Mixed language input**: User sends message with both English and Urdu words → Detect dominant language and respond accordingly
- **Language switching mid-conversation**: User switches from English to Urdu in the middle of conversation → Detect language change and respond in the new language
- **Urdu Roman vs Script**: User sends Urdu in Roman script (e.g., "Shukriya") vs Urdu script (e.g., "شکریہ") → Detect both correctly and maintain consistency in responses
- **Voice input unsupported browser**: What happens when user accesses chat from browser without Web Speech API support? → Hide/disable microphone button, display tooltip explaining feature unavailable
- **Microphone permission denied**: User clicks microphone but denies permission → Display clear error message with instructions to grant permission in browser settings
- **Voice recognition timeout**: User activates microphone but doesn't speak within timeout period → Return microphone to inactive state, show timeout message
- **Background noise interference**: Voice input captures background noise instead of command → Web Speech API handles filtering; if gibberish detected, no text sent
- **Multiple languages in voice input**: User speaks mixed English-Urdu in single voice command → Web Speech API transcribes as detected, then text-based language detection handles response language
- **Voice input while typing**: User has typed partial message and then activates voice input → Voice text should append or replace based on UI design decision (needs clarification)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a chat endpoint that accepts natural language messages and returns AI-generated responses
- **FR-002**: System MUST create a new conversation automatically when no conversation_id is provided in the request
- **FR-003**: System MUST store every message (both user and assistant) in the database with the conversation_id, user_id, role, content, and timestamp
- **FR-004**: System MUST fetch conversation history from the database on every request to maintain stateless server operation
- **FR-005**: System MUST validate that the authenticated user (from JWT token) matches the user_id in the request path for all operations
- **FR-006**: System MUST implement MCP (Model Context Protocol) server with exactly 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
- **FR-007**: Each MCP tool MUST validate that the user_id parameter matches the authenticated user before performing any database operations
- **FR-008**: Each MCP tool MUST return structured JSON containing task_id, status, and title (where applicable)
- **FR-009**: System MUST use OpenAI Agents SDK to orchestrate tool calls based on user messages
- **FR-010**: System MUST configure the AI agent with a system prompt that instructs it to: (1) interpret task-related natural language, (2) detect and respond in user's language (English or Urdu Roman/Script), (3) determine when to call which tools
- **FR-011**: System MUST integrate the MCP tools as capabilities available to the AI agent
- **FR-012**: System MUST persist conversation state exclusively in the database with no in-memory session storage
- **FR-013**: System MUST return conversation_id in every chat response to enable conversation continuity
- **FR-014**: System MUST include tool_calls array in the response showing which MCP tools were invoked
- **FR-015**: System MUST handle errors gracefully, returning user-friendly error messages when tool calls fail or user intent is unclear
- **FR-016**: MCP add_task tool MUST accept user_id, title (required), and description (optional) parameters
- **FR-017**: MCP list_tasks tool MUST accept user_id (required) and status filter (optional: "all", "pending", "completed")
- **FR-018**: MCP complete_task tool MUST accept user_id (required) and task_id (required) parameters
- **FR-019**: MCP delete_task tool MUST accept user_id (required) and task_id (required) parameters
- **FR-020**: MCP update_task tool MUST accept user_id (required), task_id (required), title (optional), and description (optional) parameters
- **FR-021**: System MUST limit conversation history retrieval to the most recent 50 messages to prevent performance degradation
- **FR-022**: Chat endpoint MUST require JWT authentication token in the Authorization header
- **FR-023**: Chat endpoint MUST extract user_id from the JWT token and validate it matches the path parameter
- **FR-024**: System MUST support resuming conversations by providing the existing conversation_id in subsequent requests
- **FR-025**: All timestamps MUST be stored in UTC datetime format
- **FR-026**: System MUST handle cases where the AI agent cannot determine user intent by asking clarifying questions
- **FR-027**: System MUST provide clear error messages when required parameters are missing from user messages
- **FR-028**: MCP tools MUST operate independently with no shared state between tool invocations
- **FR-029**: System MUST ensure every code file includes TDD tests written before implementation
- **FR-030**: System MUST follow Test-Driven Development: Red (failing test) → Green (minimal passing code) → Refactor cycle
- **FR-031**: System MUST support multilingual conversations in both English and Urdu (Roman/Script) based on user's language preference detected from their messages
- **FR-032**: System MUST trigger the existing Phase 2 notification service to send an email alert to the user upon successful task creation via the chatbot
- **FR-033**: Frontend UI MUST provide a microphone button that uses the browser's Web Speech API to convert user voice input into text before sending it to the chat endpoint

### Key Entities *(include if feature involves data)*

- **Conversation**: Represents a chat session between a user and the AI assistant
  - Belongs to a specific user
  - Contains multiple messages
  - Tracks creation and last update timestamps
  - Persists across server restarts and user sessions

- **Message**: Represents a single message in a conversation
  - Belongs to a specific conversation
  - Has a role (either "user" or "assistant")
  - Contains the message content/text
  - Includes timestamp for ordering
  - Links to the user who owns the conversation

- **Task** (existing entity from Phase 2): Represents a todo item
  - Enhanced to support natural language creation from chat messages
  - Title and description fields populated from AI extraction
  - Managed through MCP tools rather than direct API access

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully create tasks using natural language in 100% of clear, unambiguous requests (e.g., "Add task: Buy groceries")
- **SC-002**: Users can view their task list by asking in natural language with 90%+ accuracy in understanding intent
- **SC-003**: Users can mark tasks complete using natural language with correct task identification in 90%+ of cases where task reference is unambiguous
- **SC-004**: Chat endpoint responds within 3 seconds for simple single-tool operations (95th percentile)
- **SC-005**: Conversation history persists correctly across server restarts with zero data loss
- **SC-006**: System handles 50 concurrent users having active conversations without degradation
- **SC-007**: Multi-turn conversations maintain context accurately for at least 5 consecutive exchanges
- **SC-008**: 95% of task operations requested via chat result in correct database changes
- **SC-009**: All TDD tests pass with 90%+ code coverage for chat endpoint, MCP tools, and agent integration
- **SC-010**: System successfully rejects unauthorized access attempts (wrong user_id, missing token) 100% of the time
- **SC-011**: Users can resume conversations from any device using conversation_id with full history restored
- **SC-012**: AI agent correctly interprets and executes at least 85% of common task-related commands without requiring clarification
- **SC-013**: System correctly detects and responds in Urdu (Roman and Script) with 90%+ accuracy when user sends Urdu messages
- **SC-014**: Email notifications are successfully sent for 95%+ of task creation events
- **SC-015**: System handles email notification failures gracefully without blocking task creation in 100% of cases
- **SC-016**: Voice input successfully transcribes to text with 85%+ accuracy in supported browsers (Chrome, Edge, Safari)
- **SC-017**: Voice-to-text conversion completes within 2 seconds of user finishing speech in 90% of cases

### User Experience Outcomes

- **SC-018**: Users report that chatting with the bot feels natural and conversational (qualitative feedback)
- **SC-019**: Users successfully complete their first task operation via chat without needing documentation
- **SC-020**: Error messages provide clear guidance on how to rephrase or correct commands
- **SC-021**: Users can accomplish all task CRUD operations without ever using the traditional web UI
- **SC-022**: Urdu-speaking users can conduct full task management conversations in their preferred language (Roman or Script)
- **SC-023**: Users with accessibility needs can successfully use voice input for hands-free task management
- **SC-024**: Microphone button provides clear visual feedback during voice recording state

## Assumptions

1. **Authentication Infrastructure**: Phase 2's Better Auth JWT implementation is fully functional and provides valid user_id in token payload
2. **Database Schema**: Task table from Phase 2 exists with user_id, title, description, completed fields
3. **OpenAI API Access**: Valid OpenAI API key is available for Agents SDK usage
4. **MCP Protocol**: Official Python MCP SDK provides stable transport mechanism for tool registration
5. **Natural Language Understanding**: OpenAI's models can reliably extract task intent from conversational language without fine-tuning
6. **Conversation Memory**: 50 messages of history provide sufficient context for most user conversations
7. **Response Time**: Users tolerate 2-3 seconds of "thinking" time for AI responses
8. **Concurrent Users**: Initial deployment targets ≤100 concurrent users (can scale horizontally later)
9. **Message Length**: Average user messages are ≤500 characters; system handles up to 2000 characters
10. **Task Matching**: When users reference tasks by description (not ID), simple keyword matching suffices for MVP
11. **Email Service Availability**: Phase 2's notification service provides a reliable email API that accepts user_id, task_title, and task_description
12. **Language Detection**: OpenAI's models can reliably detect and respond in both English and Urdu (Roman/Script) without additional fine-tuning
13. **User Email Registration**: All authenticated users have valid email addresses registered in Phase 2's user database
14. **Email Notification Non-Blocking**: Email service failures should not block task creation - notifications are best-effort
15. **Browser Web Speech API Support**: Target browsers (Chrome, Edge, Safari) provide Web Speech API for speech recognition
16. **Voice Input Accuracy**: Browser's speech recognition accuracy is sufficient for task management commands without custom training
17. **Microphone Access**: Users can grant microphone permission through browser settings when requested
18. **Voice Language Support**: Web Speech API supports both English and Urdu language detection for voice transcription
19. **Progressive Enhancement**: Users on unsupported browsers can still use all features via text input (voice is enhancement only)

## Test-Driven Development (TDD) Requirements

### TDD Workflow Mandate

All implementation MUST follow strict Test-Driven Development:

1. **RED Phase**: Write a failing test that defines the desired behavior before writing any implementation code
2. **GREEN Phase**: Write the minimal code necessary to make the test pass
3. **REFACTOR Phase**: Clean up the code while ensuring tests continue to pass
4. **Commit**: Commit after each complete Red-Green-Refactor cycle with test and implementation together

### Test Coverage Requirements

- **Unit Tests**: 90%+ coverage for all MCP tools, data models, and repository methods
- **Integration Tests**: 100% coverage for chat endpoint handling all user story scenarios
- **Agent Tests**: Verify AI agent correctly calls MCP tools based on natural language input
- **End-to-End Tests**: At least one E2E test per user story covering full request-response cycle

### Test Organization

```
backend/tests/
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
    ├── test_complete_task_workflow.py
    ├── test_delete_task_workflow.py
    └── test_update_task_workflow.py

frontend/tests/
├── unit/
│   ├── components/
│   │   ├── test_microphone_button.test.tsx
│   │   ├── test_voice_input.test.tsx
│   │   └── test_chat_input.test.tsx
│   └── hooks/
│       └── test_use_voice_recognition.test.tsx
├── integration/
│   └── test_voice_to_chat_flow.test.tsx
└── e2e/
    ├── test_voice_input_task_creation.spec.ts
    └── test_voice_input_browser_permissions.spec.ts
```

### Example TDD Test Cases Required

**For MCP add_task tool**:
- Test creates task with valid user_id and title
- Test rejects request with empty user_id
- Test rejects request with mismatched user_id
- Test handles optional description parameter
- Test returns correct JSON structure

**For Chat Endpoint**:
- Test creates new conversation when conversation_id is null
- Test resumes existing conversation when conversation_id is provided
- Test saves user message before calling agent
- Test saves assistant response after agent completes
- Test returns conversation_id in response
- Test requires valid JWT token
- Test validates user_id matches token
- Test handles agent errors gracefully
- Test detects Urdu (Roman) messages and responds in Urdu
- Test detects Urdu (Script) messages and responds in Urdu script
- Test triggers email notification on successful task creation
- Test handles email notification failure gracefully without blocking task creation

**For Agent Integration**:
- Test agent calls add_task tool when user says "Add task"
- Test agent calls list_tasks tool when user says "Show my tasks"
- Test agent asks clarification when intent is ambiguous
- Test agent maintains context across multiple turns

**For Voice Input (Frontend)**:
- Test microphone button renders and is clickable
- Test requests microphone permission on first click
- Test speech recognition starts when permission granted
- Test transcribed text appears in input field
- Test auto-submit after transcription completes
- Test microphone button disabled when Web Speech API unavailable
- Test graceful handling of permission denial
- Test timeout handling when no speech detected
- Test visual feedback during recording state (button color/animation)
- Test Urdu language detection in voice input
- Test error messages display correctly for various failure modes

### Test Execution Requirements

- All tests MUST pass before any code is merged
- Tests MUST run in isolation (no dependencies between tests)
- Tests MUST use test database or mocks (never production data)
- Tests MUST clean up after themselves (no side effects)
- Test execution MUST complete in <30 seconds for unit tests, <2 minutes for integration tests

## Dependencies

### Internal Dependencies

- **Phase 2 Completion**: Requires existing Task model, authentication infrastructure, and Neon database connection
- **Better Auth JWT**: Depends on Phase 2's JWT token generation and validation middleware
- **Task Repository**: Depends on Phase 2's TaskRepository implementation for CRUD operations
- **Phase 2 Notification Service**: Requires existing email notification service API for sending task creation alerts
- **User Email Data**: Depends on Phase 2's user database containing registered email addresses

### External Dependencies

- **OpenAI API**: Requires active OpenAI API account with sufficient credits for Agents SDK usage
- **OpenAI Agents SDK**: Requires `openai-agents-sdk` Python package (version 0.2+)
- **Official MCP SDK**: Requires `mcp` Python package for MCP server implementation
- **Neon Database**: Requires Neon PostgreSQL instance from Phase 2 with new tables for conversations and messages
- **ChatKit**: Requires OpenAI ChatKit for frontend (hosted option) with domain allowlist configuration

### Technical Dependencies

**Backend**:
- **SQLModel**: For Conversation and Message model definitions
- **FastAPI**: For chat endpoint REST API
- **Pydantic**: For request/response validation
- **pytest**: For running TDD test suite
- **httpx** or **requests**: For testing HTTP endpoints

**Frontend**:
- **React**: For UI components including microphone button
- **Next.js 15+**: App Router for chat interface
- **Web Speech API**: Browser native API for speech-to-text (no package needed)
- **TypeScript**: For type-safe frontend development
- **Vitest** or **Jest**: For frontend unit/integration testing
- **Playwright**: For E2E testing of voice input workflows

## Out of Scope

The following are explicitly excluded from Phase 3:

- **Voice Output (Text-to-Speech)**: AI speaking responses back to user (voice input is IN scope, voice output is out of scope)
- **Additional Languages**: Support for languages other than English and Urdu (e.g., Arabic, Hindi - reserved for future)
- **Advanced NLP**: Custom fine-tuning or training of language models
- **Complex Task Scheduling**: Recurring tasks, due dates, reminders (reserved for Phase 5)
- **Task Priorities or Tags**: Intermediate-level features (could be added later)
- **Real-time Notifications**: Push notifications or real-time updates outside chat
- **Collaborative Features**: Sharing tasks or conversations between users
- **Analytics Dashboard**: Tracking task completion rates or chatbot usage metrics
- **Custom System Prompts**: User-configurable AI personality or behavior
- **File Attachments**: Uploading files or images in chat
- **Rich Message Formatting**: Markdown, code blocks, or advanced formatting in chat
- **Conversation Export**: Downloading or exporting conversation history
- **Search Across Conversations**: Finding specific messages across all conversations
- **Conversation Summaries**: AI-generated summaries of long conversations
- **Task Suggestions**: AI proactively suggesting tasks based on patterns
