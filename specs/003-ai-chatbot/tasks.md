# Implementation Tasks: Tags & Rich Notes

**Branch**: `003-ai-chatbot` | **Date**: 2026-01-05
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

## Overview

This task list breaks down the implementation of the Tags and Rich Notes features into atomic, TDD-ready tasks, ordered by dependency.

---

## Phase 1: Backend - Database Models for Tags

**Goal**: Create the database schema for a many-to-many relationship between Tasks and Tags.

### [x] [T040] [P1] [US9] Create Tag and TaskTagLink SQLModels
- **File**: `backend/src/models/tag.py`, `backend/src/models/task_tag_link.py`
- Define `Tag` model: `id`, `name`, `user_id`, `color`.
- Define `TaskTagLink` model for the join table: `task_id`, `tag_id`.

### [x] [T041] [P1] [US9] Write tests for Tag and TaskTagLink models
- **File**: `backend/tests/unit/models/test_tag.py`
- Test: `Tag` creation with valid data.
- Test: `TaskTagLink` creation.

### [x] [T042] [P1] [US9] Update Task model with Tags relationship
- **File**: `backend/src/models/task.py` (Update)
- Add `tags: List["Tag"] = Relationship(back_populates="tasks", link_model=TaskTagLink)` to the `Task` model.

### [x] [T043] [P1] [US9] Create Alembic migration for new Tag tables
- **File**: `backend/alembic/versions/xxx_add_tag_tables.py`
- Run `alembic revision --autogenerate` to create the migration script for the `tags` and `tasktaglinks` tables.
- Verify the script correctly creates tables, foreign keys, and indexes.

---

## Phase 2: Backend - Repository and MCP Tool Logic

**Goal**: Update the data layer and AI tools to be aware of tags.

### [x] [T044] [P1] [US9] Update TaskRepository to manage Tags
- **File**: `backend/src/repositories/task_repository.py` (Update)
- Implement `find_or_create_tags(tag_names: List[str]) -> List[Tag]`.
- Update `create()` to accept `tags: List[str]`, call `find_or_create_tags`, and link them to the new task.
- Update `get_by_id()` to eagerly load associated tags using `selectinload`.
- Update `list_by_user()` to accept a `tags` filter and join correctly.

### [x] [T045] [P1] [US9] Write tests for TaskRepository Tag logic
- **File**: `backend/tests/unit/repositories/test_task_repository.py` (Update)
- Test: `create()` with tags correctly creates and links them.
- Test: `list_by_user()` with a tag filter returns the correct tasks.
- Test: `get_by_id()` returns a task with its tags attached.

### [x] [T046] [P1] [US9] Update MCP `add_task` tool for Tags
- **File**: `backend/src/mcp_server/tools/add_task.py` (Update)
- Add `tags: Optional[List[str]] = None` to the function signature.
- Pass the tags list to `task_repository.create()`.
- Update the Pydantic schema in `schemas.py` to include the `tags` field.

### [x] [T047] [P1] [US9] Update MCP `list_tasks` tool for Tag Filtering
- **File**: `backend/src/mcp_server/tools/list_tasks.py` (Update)
- Add `tags: Optional[List[str]] = None` to the function signature.
- Pass the tags list to `task_repository.list_by_user()`.
- Update the Pydantic schema in `schemas.py`.

### [x] [T048] [P1] [US9] Write tests for MCP tools with Tags
- **File**: `backend/tests/unit/mcp/test_add_task.py`, `test_list_tasks.py` (Update)
- Test `add_task` with a `tags` argument.
- Test `list_tasks` with a `tags` filter.

### [x] [T049] [P1] [US9] Update AI Agent System Prompt
- **File**: `backend/src/services/prompts/system_prompt.md` (Update)
- Add instructions for the AI on how to recognize and use hashtags (`#tag`) to populate the `tags` parameter in tool calls.

---

## Phase 3: Frontend - UI for Tags and Rich Notes

**Goal**: Build the user interface for creating, viewing, and managing tags and notes.

### [x] [T050] [P2] [US9] Create `TagBadge` component
- **File**: `frontend/src/components/ui/TagBadge.tsx`
- A simple component that displays a tag name inside a colored, rounded badge.

### [x] [T051] [P2] [US9] Create `TagInput` component
- **File**: `frontend/src/components/ui/TagInput.tsx`
- A multi-select combobox for adding/creating tags.
- Use `cmdk` and `shadcn/ui` components as a base.
- It should allow selecting from existing tags and creating new ones by typing and hitting Enter.

### [x] [T052] [P2] [US9] Integrate `TagInput` into `add-task-dialog.tsx`
- **File**: `frontend/src/components/add-task-dialog.tsx` (Update)
- Add the `TagInput` component to the dialog form.
- Update the `handleSubmit` function to pass the selected tags to the backend API.

### [x] [T053] [P2] [US9] Display Tags in `task-item.tsx`
- **File**: `frontend/src/components/task-item.tsx` (Update)
- If a task has tags, use the `TagBadge` component to display them.

### [x] [T054] [P2] [US10] Integrate Markdown Renderer
- **File**: `frontend/src/components/ui/MarkdownRenderer.tsx`
- Create a wrapper component around `react-markdown`.
- Add `remark-gfm` for tables, strikethrough, etc.
- Style the output to match the app's theme (headings, lists, blockquotes).

### [x] [T055] [P2] [US10] Update Task Detail View for Rich Notes
- **File**: `frontend/src/components/task-item.tsx` or a new detail view.
- Use the `MarkdownRenderer` component to render the `task.description` field.
- If no dedicated detail view exists, ensure task descriptions in modals or expanded views are rendered as Markdown.

### [ ] [T056] [P2] [US10] Write tests for new Frontend components
- **File**: `frontend/tests/unit/components/`
- Add tests for `TagBadge.tsx`, `TagInput.tsx`, and `MarkdownRenderer.tsx`.

---

## Summary

- **Total Tasks**: 17
- **Backend**: 10 tasks (T040-T049)
- **Frontend**: 7 tasks (T050-T056)
- **Dependency Flow**: Backend models → Backend logic → Frontend UI.
- **First Step**: Begin with `[T040]` to define the database schema.