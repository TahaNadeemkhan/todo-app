---
id: 0007
title: updated-add-task-tool-to-use-mcp-decorator
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
  - refactor
  - testing
links:
  spec: specs/003-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/mcp_server/server.py
  - backend/src/mcp_server/tools/add_task.py
  - backend/tests/unit/mcp/test_add_task.py
tests:
  - backend/tests/unit/mcp/test_add_task.py
---

## Prompt

Update `add_task.py` to use the `@mcp.tool` decorator immediately.

## Response snapshot

Updated the MCP implementation to strictly follow the `mcp-tool-writer` agent's "Stateless FastMCP" pattern with explicit decorators.

### Key Changes
1.  **Central Server**: Created `backend/src/mcp_server/server.py` to initialize the `mcp` object using `FastMCP`.
2.  **Tool Refactor**: Modified `backend/src/mcp_server/tools/add_task.py` to:
    - Import the central `mcp` object.
    - Use the `@mcp.tool` decorator.
    - Change function signature to use Python primitives (user_id: str) instead of Pydantic models, as preferred by FastMCP for schema auto-generation.
    - Validate `user_id` format internally.
3.  **Test Update**: Rewrote `backend/tests/unit/mcp/test_add_task.py` to test the new function signature and dict return type.

### Outcome
The `add_task` tool now fully aligns with the official MCP Python SDK patterns while maintaining testability and statelessness. All tests passed.