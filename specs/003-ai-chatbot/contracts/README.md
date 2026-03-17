# API Contracts: Phase 3 AI Chatbot

This directory contains API schemas, MCP tool definitions, and system prompts for Phase 3.

## Files

1. **chat_endpoint.openapi.yaml** - OpenAPI spec for POST /api/{user_id}/chat endpoint
2. **mcp_tools.json** - MCP tool definitions (5 tools with Pydantic schemas)
3. **system_prompt.md** - Multilingual system prompt for AI agent

## Chat Endpoint

**POST /api/{user_id}/chat**

Request:
```json
{
  "message": "Add task: Buy groceries",
  "conversation_id": "uuid" // optional, null for new conversation
}
```

Response:
```json
{
  "conversation_id": "uuid",
  "response": "I've added 'Buy groceries' to your task list.",
  "tool_calls": [...],
  "created_at": "2025-12-17T10:00:00Z"
}
```

## MCP Tools

5 tools for task management:
1. **add_task** - Create new task + trigger email notification
2. **list_tasks** - List user tasks with optional status filter
3. **complete_task** - Mark task as completed
4. **delete_task** - Permanently delete task
5. **update_task** - Update task title/description

All tools validate user_id matches authenticated user (FR-007).

## System Prompt

Multilingual prompt supporting English and Urdu (Roman/Script) with automatic language detection.

See full specifications in individual files.
