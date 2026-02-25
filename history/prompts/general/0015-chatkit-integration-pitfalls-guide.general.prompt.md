---
id: 0015
title: chatkit-integration-pitfalls-guide
stage: general
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5
feature: none
branch: 003-phase-3-chatbot
user: TahaNadeemkhan
command: documentation-request
labels: ["chatkit", "documentation", "best-practices", "debugging-guide", "pitfalls", "troubleshooting"]
links:
  spec: specs/003-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-chatbot/chatkit-integration-pitfalls-guide.md
tests:
  - Manual: Verified all code examples match actual fixes from debugging session
  - Manual: Cross-referenced error messages with PHR 0011
  - Manual: Validated Quick Debugging Checklist against real issues encountered
---

## Prompt

User asked:
"Great, now it's correct. Now I want to ask you something - you had the chatkit-via-python skill I gave you and I think you used it for help, but we had 3 major issues: first the chatbot showed blank screen when opening, second history wasn't loading, third assistant messages weren't appearing, etc. So my question is - if I need to integrate ChatKit in a new project in the future, how can I overcome these common pitfalls?"

## Response snapshot

Created comprehensive ChatKit Integration Pitfalls Guide covering all issues encountered during debugging session.

**Structure:**
1. Pre-Integration Checklist
2. Database Setup Pitfalls (migrations, alembic config)
3. Type System Pitfalls (Thread vs ThreadMetadata)
4. Message Persistence Pitfalls (content types, add_thread_item)
5. Serialization Pitfalls (NonStreamingResult handling)
6. Frontend-Backend Communication (proxy routes, WSL-Windows)
7. Quick Debugging Checklist

**The Big Three Issues Documented:**

**Issue 1: Blank Screen**
- Missing Next.js API proxy route `/app/api/chatkit/route.ts`
- Wrong backend URL (localhost vs 127.0.0.1 for WSL-Windows)
- ChatKit Studio config not applied

**Issue 2: History Not Loading**
- Database tables missing (migrations not run)
- Thread vs ThreadMetadata type confusion in `load_thread()`
- NonStreamingResult JSON serialization failing
- Empty items array (not loading thread titles)

**Issue 3: Assistant Messages Missing**
- Missing `await self.store.add_thread_item()` after streaming
- Content type validation only accepted 'text' and 'input_text', not 'output_text'

**Guide Features:**
- ✅ Code examples showing WRONG vs CORRECT implementations
- ✅ All code snippets taken from actual fixes (chatkit_store.py, chatkit_server.py, main.py)
- ✅ Common Error Messages Reference table
- ✅ Quick Debugging Checklist (5-step verification)
- ✅ Line number references to actual implementation files
- ✅ Best practices for each pitfall category

**Practical Examples Included:**
- Database verification commands
- alembic/env.py configuration
- Thread/ThreadMetadata conversion methods
- Content type handling for all three types
- NonStreamingResult.json decoding
- Next.js proxy route implementation
- WSL network configuration

## Outcome

- ✅ Impact: Created actionable guide to prevent 7 major pitfalls in future ChatKit integrations, directly addressing user's three main issues
- 🧪 Tests: Verified all code examples match actual debugging fixes, cross-referenced with PHR 0011
- 📁 Files: 1 documentation file created (comprehensive pitfalls guide)
- 🔁 Next prompts: User may want to add this guide to project README or create automated tests based on checklist
- 🧠 Reflection: Guide distills 6 hours of debugging into actionable prevention strategies. Each pitfall includes both the error symptom and root cause, making it easier to diagnose issues quickly. The "Big Three" summary maps directly to user's concerns.

## Evaluation notes (flywheel)

- Failure modes observed: N/A (documentation task, not implementation)
- Graders run and results (PASS/FAIL): Manual review PASS - all code examples validated against actual fixes
- Prompt variant (if applicable): User request in Roman Urdu for practical troubleshooting guide based on real debugging session
- Next experiment (smallest change to try): Add this guide reference to chatkit-via-python skill for future agents to leverage lessons learned
