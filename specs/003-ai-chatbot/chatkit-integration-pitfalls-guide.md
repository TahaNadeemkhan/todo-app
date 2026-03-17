# ChatKit Integration Pitfalls Guide

**Author:** Generated from debugging session (2025-12-27)
**Based on:** Phase 3 ChatKit integration with FastAPI + PostgreSQL
**ChatKit Version:** 1.4.0

## Overview

This guide documents common pitfalls encountered during ChatKit integration and how to avoid them. It covers the three major issue categories:

1. **Blank Screen** - Chatbot UI not loading or displaying properly
2. **History Not Loading** - Conversation threads not appearing in sidebar
3. **Assistant Messages Missing** - Only user messages persisting, AI responses disappearing

## Table of Contents

1. [Pre-Integration Checklist](#pre-integration-checklist)
2. [Database Setup Pitfalls](#database-setup-pitfalls)
3. [Type System Pitfalls](#type-system-pitfalls)
4. [Message Persistence Pitfalls](#message-persistence-pitfalls)
5. [Serialization Pitfalls](#serialization-pitfalls)
6. [Frontend-Backend Communication](#frontend-backend-communication)
7. [Quick Debugging Checklist](#quick-debugging-checklist)

---

## Pre-Integration Checklist

Before starting ChatKit integration, ensure:

- ✅ **Backend Environment**: `.env.local` exists in backend folder with `DATABASE_URL`
- ✅ **Frontend Environment**: `.env.local` exists in frontend with `NEXT_PUBLIC_BACKEND_URL`
- ✅ **Database Migrations**: Alembic migrations run successfully
- ✅ **Python Path**: Alembic can import your models (add `src/` to `sys.path`)
- ✅ **Network Configuration**: WSL/Windows users use `127.0.0.1` not `localhost`
- ✅ **ChatKit Studio**: Export config and apply to your frontend

---

## Database Setup Pitfalls

### ❌ **Pitfall 1: Migrations Not Run**

**Error:**
```
psycopg2.errors.UndefinedTable: relation "conversations" does not exist
```

**Root Cause:** Alembic migrations weren't run or `.env.local` missing from backend.

**Solution:**

1. **Ensure `.env.local` exists in backend:**
```bash
# backend/.env.local
DATABASE_URL=postgresql://user:pass@host/database?sslmode=require
```

2. **Fix `alembic/env.py` for model imports:**
```python
# alembic/env.py
import sys
from pathlib import Path

# Add src directory to Python path for model imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
```

3. **Run migrations:**
```bash
cd backend
alembic upgrade head
```

### ✅ **Best Practice:**

Always verify database tables exist before starting development:
```bash
# Connect to database and list tables
psql $DATABASE_URL -c "\dt"
```

You should see: `conversations`, `messages` tables.

---

## Type System Pitfalls

### ❌ **Pitfall 2: Thread vs ThreadMetadata Confusion**

**Error:**
```python
TypeError: chatkit.types.Thread() got multiple values for keyword argument 'items'
```

**Root Cause:** ChatKit has TWO separate types:
- `Thread`: Full object WITH items array (for list views)
- `ThreadMetadata`: Lightweight WITHOUT items (for single thread loading)

**Incorrect Implementation:**
```python
# ❌ WRONG - load_thread() should return ThreadMetadata, not Thread
async def load_thread(self, thread_id: str, context: str) -> Thread:
    conversation = await self.conversation_repo.get_by_id(thread_id)

    # This causes "multiple values for items" error
    return Thread(
        id=str(conversation.id),
        title="My Thread",
        items=Page(data=[], has_more=False, after=None)  # ❌ Items here
    )
```

**Correct Implementation:**
```python
# ✅ CORRECT - load_thread() returns ThreadMetadata (no items)
async def load_thread(self, thread_id: str, context: str) -> ThreadMetadata | None:
    conversation = await self.conversation_repo.get_by_id(thread_id)

    # Load first message for title
    messages = await self.message_repo.get_history(
        conversation_id=conversation.id,
        limit=1
    )

    title = "New Conversation"
    if messages:
        title = messages[0].content[:50] + ("..." if len(messages[0].content) > 50 else "")

    # Return ThreadMetadata - ChatKit loads items separately
    return ThreadMetadata(
        id=str(conversation.id),
        title=title,
        created_at=int(conversation.created_at.timestamp()),
        updated_at=int(conversation.updated_at.timestamp()),
    )
```

### ✅ **Best Practice:**

Create **separate conversion methods** for each type:

```python
async def _conversation_to_thread_metadata(self, conversation) -> ThreadMetadata:
    """Used by load_thread() - no items field"""
    # Load title from first message
    # Return ThreadMetadata WITHOUT items

async def _conversation_to_thread(self, conversation) -> Thread:
    """Used by load_threads() - empty items array"""
    # Load title from first message
    # Return Thread WITH empty items Page
```

**When to use which:**
- `load_thread(thread_id)` → Returns `ThreadMetadata` (ChatKit loads items via `load_thread_items()`)
- `load_threads()` → Returns `Page[Thread]` with empty items (UI shows list, items loaded on-demand)

---

## Message Persistence Pitfalls

### ❌ **Pitfall 3: Assistant Messages Not Saving**

**Symptom:** User messages persist, but assistant responses disappear after refresh.

**Root Cause:** Missing `store.add_thread_item()` call after streaming completes.

**Incorrect Implementation:**
```python
# ❌ WRONG - Assistant message never saved to database
async def respond(self, thread, input_user_message, context):
    # ... streaming logic ...

    full_response = ""
    async for chunk in self.model.respond_stream(chat_messages):
        full_response += chunk
        assistant_item.content = [AssistantMessageContent(type="output_text", text=full_response)]
        yield ThreadItemAddedEvent(item=assistant_item)

    # ❌ Missing: await self.store.add_thread_item(thread_id, assistant_item, user_id)
```

**Correct Implementation:**
```python
# ✅ CORRECT - Save assistant message after streaming
async def respond(self, thread, input_user_message, context):
    user_id = context
    thread_id = thread.id

    # ... streaming logic ...

    full_response = ""
    async for chunk in self.model.respond_stream(chat_messages):
        full_response += chunk
        assistant_item.content = [AssistantMessageContent(type="output_text", text=full_response)]
        yield ThreadItemAddedEvent(item=assistant_item)

    # ✅ Final update with complete message
    assistant_item.content = [AssistantMessageContent(type="output_text", text=full_response)]

    # ✅ CRITICAL: Save to database
    await self.store.add_thread_item(thread_id, assistant_item, user_id)
```

### ❌ **Pitfall 4: Content Type Not Recognized**

**Error:** Assistant messages still not saving even with `add_thread_item()` call.

**Root Cause:** ChatKit uses different content types:
- User messages: `'input_text'`
- Assistant messages: `'output_text'` (**NOT** `'text'`)

**Incorrect Implementation:**
```python
# ❌ WRONG - Only checks 'text' and 'input_text'
async def add_thread_item(self, thread_id, item, context):
    content_text = ""
    for content_part in item.content:
        if content_part.type in ("text", "input_text"):  # ❌ Missing 'output_text'
            content_text = content_part.text
            break

    # content_text will be empty for assistant messages!
```

**Correct Implementation:**
```python
# ✅ CORRECT - Accept all three content types
async def add_thread_item(self, thread_id, item, context):
    content_text = ""
    for content_part in item.content:
        # ChatKit sends:
        # - 'input_text' for user messages
        # - 'output_text' for assistant messages
        # - 'text' for generic content
        if hasattr(content_part, 'type') and content_part.type in ("text", "input_text", "output_text"):
            content_text = getattr(content_part, 'text', "")
            logger.info(f"✅ Found text content (type={content_part.type}): '{content_text}'")
            break
        else:
            logger.warning(f"⚠️ Unexpected content type: {getattr(content_part, 'type', 'NONE')}")

    if not content_text or not content_text.strip():
        raise ValueError(f"Cannot save message with empty content")
```

### ✅ **Best Practice:**

Always add comprehensive logging in `add_thread_item()`:

```python
logger.info(f"=== add_thread_item DEBUG ===")
logger.info(f"item type = {type(item)}")
logger.info(f"item.content = {item.content}")
for idx, content_part in enumerate(item.content):
    logger.info(f"content_part[{idx}] type = {content_part.type}")
    logger.info(f"content_part[{idx}] text = {getattr(content_part, 'text', 'N/A')}")
logger.info(f"=== END DEBUG ===")
```

---

## Serialization Pitfalls

### ❌ **Pitfall 5: NonStreamingResult Serialization Failing**

**Error:**
```
TypeError: Cannot destructure property 'title' of 'i' as it is undefined
```

**Backend logs show:** Threads have proper titles, but frontend receives undefined.

**Root Cause:** Trying to use `dataclasses.asdict()` on Pydantic models with nested bytes.

**Incorrect Implementation:**
```python
# ❌ WRONG - dataclasses.asdict() fails on Pydantic models
if isinstance(result, NonStreamingResult):
    result_dict = dataclasses.asdict(result)  # ❌ Fails with bytes fields
    return JSONResponse(content=result_dict)
```

**Correct Implementation:**
```python
# ✅ CORRECT - Decode pre-serialized JSON bytes
if isinstance(result, NonStreamingResult):
    # NonStreamingResult has a 'json' attribute with already-serialized JSON bytes
    import json
    json_bytes = result.json
    json_str = json_bytes.decode('utf-8')
    result_dict = json.loads(json_str)

    logger.info(f"📤 Sending response to frontend: {str(result_dict)[:500]}")

    return JSONResponse(content=result_dict)
```

### ✅ **Best Practice:**

ChatKit's `NonStreamingResult` already contains serialized JSON. Just decode it:

```python
# NonStreamingResult structure:
# - result.json: bytes (already serialized JSON)
# - DO: decode → parse → return
# - DON'T: try to convert Pydantic models manually
```

---

## Frontend-Backend Communication

### ❌ **Pitfall 6: Missing Next.js API Proxy Route**

**Symptom:** ChatKit UI loads but doesn't communicate with backend.

**Root Cause:** No proxy route to forward ChatKit requests.

**Solution:** Create `/app/api/chatkit/route.ts`:

```typescript
/**
 * ChatKit API Proxy Route
 * Forwards all ChatKit requests to the backend
 */

import { NextRequest } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.text();

    // Forward to backend
    const response = await fetch(`${BACKEND_URL}/chatkit`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...Object.fromEntries(request.headers.entries()),
      },
      body: body,
    });

    // Check if streaming response
    const contentType = response.headers.get("content-type");

    if (contentType?.includes("text/event-stream")) {
      // Return streaming response (for chat messages)
      return new Response(response.body, {
        status: response.status,
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    }

    // Return JSON response (for threads.list, threads.create, etc.)
    const data = await response.json();
    return Response.json(data, { status: response.status });
  } catch (error) {
    console.error("ChatKit proxy error:", error);
    return Response.json(
      { error: "Failed to connect to ChatKit backend" },
      { status: 500 }
    );
  }
}
```

### ❌ **Pitfall 7: WSL-Windows Network Issues**

**Error:** Frontend can't reach backend at `localhost:8000`.

**Root Cause:** WSL's `localhost` is different from Windows host.

**Solution:**

In `frontend/.env.local`:
```bash
# ❌ WRONG (WSL to Windows)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# ✅ CORRECT (WSL to Windows)
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

### ✅ **Best Practice:**

Always use `127.0.0.1` for cross-environment communication:
- WSL → Windows backend: `http://127.0.0.1:8000`
- Windows → WSL frontend: `http://127.0.0.1:3000`

---

## Quick Debugging Checklist

When ChatKit integration isn't working, check in this order:

### 1. **Database Layer**
```bash
# Verify tables exist
psql $DATABASE_URL -c "\dt"

# Check conversations count
psql $DATABASE_URL -c "SELECT COUNT(*) FROM conversations;"

# Check messages count
psql $DATABASE_URL -c "SELECT COUNT(*) FROM messages;"
```

### 2. **Backend Layer**
```bash
# Check backend logs for errors
# Look for:
# - "relation does not exist" → Run migrations
# - "got multiple values for items" → Fix Thread/ThreadMetadata
# - Empty items array → Check _conversation_to_thread()
```

### 3. **Network Layer**
```bash
# Test backend directly
curl http://127.0.0.1:8000/health

# Test ChatKit endpoint
curl -X POST http://127.0.0.1:8000/chatkit \
  -H "Content-Type: application/json" \
  -d '{"method":"threads.list","params":{}}'
```

### 4. **Frontend Layer**
```javascript
// Check browser console for:
// - "Cannot destructure property" → Fix serialization
// - Network errors → Check NEXT_PUBLIC_BACKEND_URL
// - Empty history → Check Thread conversion logic
```

### 5. **Message Persistence**
```python
# Add debug logging in chatkit_server.py respond():
logger.info(f"💾 Saving assistant message: {full_response[:100]}...")
await self.store.add_thread_item(thread_id, assistant_item, user_id)
logger.info(f"✅ Saved successfully")

# Add debug logging in chatkit_store.py add_thread_item():
logger.info(f"Content type: {content_part.type}")
logger.info(f"Content text: {content_text}")
```

---

## Common Error Messages Reference

| Error | Root Cause | Fix |
|-------|------------|-----|
| `relation "conversations" does not exist` | Migrations not run | Run `alembic upgrade head` |
| `got multiple values for keyword argument 'items'` | Wrong return type in `load_thread()` | Return `ThreadMetadata` not `Thread` |
| `Cannot destructure property 'title'` | JSON serialization failing | Decode `result.json` bytes directly |
| Empty history sidebar | Thread items not loading | Check `_conversation_to_thread()` logic |
| Assistant messages missing | Not calling `add_thread_item()` | Add after streaming completes |
| Content validation failing | Missing `'output_text'` type | Accept `text`, `input_text`, `output_text` |
| Frontend can't reach backend | Network misconfiguration | Use `127.0.0.1` not `localhost` |

---

## Summary: The Big Three Issues

### 🔴 Issue 1: Blank Screen
**Causes:**
- Missing Next.js API proxy route
- Wrong `NEXT_PUBLIC_BACKEND_URL` (use `127.0.0.1`)
- ChatKit config not applied from ChatKit Studio

**Fixes:**
- Create `/app/api/chatkit/route.ts`
- Set correct backend URL in `.env.local`
- Export and apply ChatKit Studio design config

### 🔴 Issue 2: History Not Loading
**Causes:**
- Database tables missing (migrations not run)
- Thread vs ThreadMetadata type confusion
- JSON serialization failing on `NonStreamingResult`
- Empty items array in thread conversion

**Fixes:**
- Run `alembic upgrade head`
- Return `ThreadMetadata` from `load_thread()`
- Decode `result.json` bytes directly
- Load first message for thread titles

### 🔴 Issue 3: Assistant Messages Missing
**Causes:**
- Missing `store.add_thread_item()` call
- Content type validation only accepts `'text'` and `'input_text'`

**Fixes:**
- Add `await self.store.add_thread_item()` after streaming
- Accept `'output_text'` content type for assistant messages

---

## References

- **ChatKit Documentation:** https://chatkit.docs.anthropic.com/
- **ChatKit Studio:** https://chatkit.studio/playground
- **Debugging Session PHR:** `history/prompts/003-ai-chatbot/0011-fixed-chatkit-conversation-history-persistence.green.prompt.md`
- **Implementation Files:**
  - `backend/src/chatkit_store.py` - Database-backed store
  - `backend/src/chatkit_server.py` - Server with MCP tools
  - `backend/src/main.py` - FastAPI app with serialization
  - `frontend/src/app/api/chatkit/route.ts` - Next.js proxy

---

**Last Updated:** 2025-12-27
**Based on:** Real debugging session with 6 major issues resolved
