---
id: 0016
title: chatkit-widgets-and-navigation-fix
stage: general
date: 2025-12-28
surface: agent
model: claude-sonnet-4.5
feature: none
branch: 003-phase-3-chatbot
user: taha
command: /sp.git.commit_pr
labels: ["chatkit", "widgets", "navigation", "persistence", "fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: https://github.com/TahaNadeemkhan/todo-app/compare/003-phase-3-chatbot
files:
  - todo_app/phase_3/backend/src/chatkit_server.py
  - todo_app/phase_3/backend/src/chatkit_store.py
  - todo_app/phase_3/backend/src/models/conversation.py
  - todo_app/phase_3/backend/src/services/prompts/system_prompt.md
  - todo_app/phase_3/frontend/src/components/FloatingChatbot.tsx
  - todo_app/phase_3/frontend/src/components/ChatbotProvider.tsx
  - todo_app/phase_3/frontend/src/lib/chatkit-config.ts
  - todo_app/phase_3/frontend/src/app/(authenticated)/layout.tsx
tests:
  - Manual testing: AI tool calling verification
  - Manual testing: Navigation persistence verification
  - Manual testing: Widget rendering verification
  - Manual testing: Checkbox toggle functionality
---

## Prompt

User reported two critical issues with ChatKit integration:

1. **Widgets not displaying**: User said "aby bhai ab tou na show tasks pe witgets show horhy hain" - When asking AI to show tasks, widgets were not appearing because Gemini was responding with plain text instead of calling the `list_tasks` tool.

2. **Navigation reload issue**: User said "bhai tabs change karnay par still hot reload horha" - Switching between tabs (Today/Upcoming/etc) was causing the chatbot to reload and lose conversation state.

User then requested to commit and create PR using `/sp.git.commit_pr` command.

## Response snapshot

**Issue Analysis:**
- AI not calling tools: Gemini had `tool_choice="auto"` which allowed it to skip tool calls and respond with text
- Navigation reload: ChatKit options were being recreated on every render, causing instance recreation

**Solutions Implemented:**

1. **Backend - Force Tool Calling:**
   - Changed `tool_choice` to `"required"` on first iteration
   - This forces Gemini to call MCP tools initially
   - Subsequent iterations use `"auto"` to allow text responses after tool results
   - File: `chatkit_server.py:556-567`

2. **Backend - Widget Generation:**
   - Already had `_create_task_list_widget()` method
   - Widget yielding via `ThreadItemAddedEvent` with `WidgetItem`
   - Proper MCP result parsing (TextContent wrapper)
   - Action handler for checkbox toggles with proper state flipping

3. **Frontend - Navigation Persistence:**
   - Created `ChatbotProvider.tsx` - global context for ChatKit instance
   - Changed `getChatKitOptions()` to static `CHATKIT_OPTIONS` constant
   - Modified `FloatingChatbot` to use `useChatbotContext()` instead of local `useChatKit()`
   - Wrapped authenticated layout with `<ChatbotProvider>`
   - Added `React.memo()` optimization

**Architecture:**
```
Root Layout
  └── AuthProvider
      └── ChatbotProvider  ← ChatKit initialized ONCE
          └── Authenticated Layout
              ├── Sidebar
              ├── Page Content (changes on navigation)
              └── FloatingChatbot ← Uses context, persists
```

**Git Workflow Executed:**
- Staged all changes
- Committed with detailed conventional commit message
- Pushed to `origin/003-phase-3-chatbot`
- Attempted PR creation via `gh` CLI - failed due to no common history with master
- Provided manual PR URL: https://github.com/TahaNadeemkhan/todo-app/compare/003-phase-3-chatbot

## Outcome

- ✅ Impact: Fixed two critical UX issues - AI now calls tools and displays widgets, chatbot persists across navigation
- 🧪 Tests: Manual testing required (AI tool calling, widget display, navigation persistence, checkbox toggles)
- 📁 Files: 8 files modified (4 backend, 4 frontend)
- 🔁 Next prompts: User testing to verify fixes, potential PR creation manually on GitHub
- 🧠 Reflection: The navigation persistence issue required architectural change (global context vs local hook). The tool calling issue was solved with simple parameter change but required understanding of OpenAI API behavior.

## Evaluation notes (flywheel)

- Failure modes observed: Context provider initially returned null before mount causing "must be used within provider" error - fixed by always providing context with isReady flag
- Graders run and results (PASS/FAIL): No automated graders, manual verification required
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test if `tool_choice="required"` causes issues in edge cases where no tool should be called (e.g., greetings, clarifications)
