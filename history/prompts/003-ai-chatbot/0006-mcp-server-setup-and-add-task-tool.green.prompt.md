---
id: 0006
title: mcp-server-setup-and-add-task-tool
stage: green
date: 2025-12-18
surface: agent
model: gemini-2.0-flash-exp
feature: 003-ai-chatbot
branch: 003-phase-3-chatbot
user: taha
command: /sp.implement
labels:
  - mcp
  - backend
  - tools
  - tdd
links:
  spec: specs/003-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/models/conversation.py
  - backend/src/models/message.py
  - backend/src/repositories/conversation_repository.py
  - backend/src/repositories/message_repository.py
  - backend/src/repositories/task_repository.py
  - backend/src/mcp_server/tools/add_task.py
  - backend/src/db.py
  - backend/alembic/versions/2f396b4cc71c_add_conversation_and_message_tables.py
  - backend/tests/unit/models/test_conversation.py
  - backend/tests/unit/models/test_message.py
  - backend/tests/unit/repositories/test_conversation_repository.py
  - backend/tests/unit/repositories/test_message_repository.py
  - backend/tests/unit/mcp/test_add_task.py
tests:
  - backend/tests/unit/models/test_conversation.py
  - backend/tests/unit/models/test_message.py
  - backend/tests/unit/repositories/test_conversation_repository.py
  - backend/tests/unit/repositories/test_message_repository.py
  - backend/tests/unit/mcp/test_add_task.py
---

## User Prompt

Now I want you to start the implementation and the setup of the MCP server and implement the `add_task` tool as per the specifications in specs/003-ai-chatbot/spec.md. Ensure that the `add_task` tool is a stateless, pure async function that interacts with the database via the repository layer. Follow best practices for MCP tool development as outlined in the `mcp-tool-writer` agent guidelines. Additionally, write unit tests for the `add_task` tool to validate its functionality and security aspects.

## Assistant Response

Implemented the phase 1 and corrected the implementation of the `add_task` MCP tool to be a stateless, pure async function that interacts with the database via a repository, following the `mcp-tool-writer` agent's best practices.

### Key Changes
1.  **Dependencies**: Added `asyncpg` and `aiosqlite` for asynchronous database access.
2.  **Database Configuration**: Updated `src/config/settings.py` and created `src/db.py` to support `AsyncSession`.
3.  **Refactoring**: Rewrote `src/mcp_server/tools/add_task.py` to remove the incorrect `FastMCP` server instantiation and instead implement a clean tool function that accepts `ToolContext`.
4.  **Testing**: Added and passed `tests/unit/mcp/test_add_task.py`, ensuring security validation and database interaction work correctly.

### Outcome
The `add_task` tool is now correctly architected as a modular component ready for registration in the main MCP server, fulfilling the stateless requirement. All unit tests for models, repositories, and the MCP tool are passing.