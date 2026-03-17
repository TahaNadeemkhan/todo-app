---
id: "0006"
title: "implemented-task-sorting"
stage: "tasks"
date: "2026-01-25"
surface: "agent"
model: "gemini-2.0-flash-exp"
feature: "005-event-driven-cloud"
branch: "005-event-driven-cloud"
user: "user"
command: "implement task sorting"
labels: ["sorting", "frontend", "backend", "repository"]
links:
  spec: "specs/005-event-driven-cloud/spec.md"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
  - "todo_app/phase_5/backend/src/repositories/task_repository.py"
  - "todo_app/phase_5/backend/src/services/task_service.py"
  - "todo_app/phase_5/backend/src/api/routes/tasks.py"
  - "todo_app/phase_5/frontend/src/components/sort-selector.tsx"
  - "todo_app/phase_5/frontend/src/components/dashboard-content.tsx"
tests:
  - "todo_app/phase_5/backend/tests/unit/repositories/test_task_repository_sorting.py"
  - "todo_app/phase_5/backend/tests/contract/test_sorting_api.py"
---

# Implemented Task Sorting

## Context
Implemented User Story 5 (Flexible Task Sorting) for Phase 5. This allows users to sort their task list by due date, priority, created date, or title.

## Changes

### Backend
1.  **Repository**:
    - Updated `TaskRepository.get_by_user` to accept `sort_by` and `sort_order` parameters.
    - Implemented sorting logic using SQLAlchemy `order_by`, `asc`, `desc`.
    - Added custom sorting logic for `Priority` enum (High > Medium > Low).

2.  **Service & API**:
    - Updated `TaskService.list_user_tasks` to pass sorting parameters.
    - Updated `GET /api/{user_id}/tasks` endpoint to expose `sort_by` and `sort_order` query parameters.

### Frontend
1.  **Components**:
    - Created `SortSelector` component for selecting sort field and order.
    - Integrated `SortSelector` into `DashboardContent`.

2.  **State Management**:
    - Added `sortBy` and `sortOrder` state to `DashboardContent`.
    - Persisted sort preference in `localStorage`.
    - Updated `fetchTasks` to pass sorting parameters to the backend API.

## Testing
- Unit tests for `TaskRepository` sorting (Passed).
- Contract tests for `GET /tasks` with sorting parameters (Passed).

## Next Steps
- Validate microservices (Notification, Recurring Task) manually.
- Deploy to Minikube (Phase 12).