# Tasks: Phase 2 - Full-Stack Web Application

**Feature Branch**: `002-phase2-web-app`
**Generated**: 2025-12-09
**Input**: spec.md v3.0, plan.md v3.0

---

## Execution Strategy: Vertical Slice + Senior Developer Approach

This task list implements a **vertical slice approach** with risk mitigation patterns from 50+ years of development experience:

1. **Risk-first**: Tackle unknowns (auth, DB connection) early
2. **Walking skeleton**: End-to-end flow before feature depth
3. **Contract-first**: API contracts defined before implementation
4. **Fail-fast validation**: Each phase has checkpoints

---

## Technology Stack Reference

### Backend (Python)
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | latest | Web framework |
| `uvicorn[standard]` | latest | ASGI server |
| `sqlmodel` | latest | ORM (Pydantic + SQLAlchemy) |
| `pyjwt` | latest | JWT verification |
| `python-dotenv` | latest | Environment variables |
| `psycopg2-binary` | latest | PostgreSQL driver |
| `httpx` | latest | Async HTTP client (testing) |
| `pytest` | latest | Testing framework |

### Frontend (Next.js 16+)
| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 16+ | React framework |
| `typescript` | latest | Type safety |
| `axios` | latest | HTTP client |
| `better-auth` | latest | Authentication |
| `@better-auth/jwt` | latest | JWT plugin |
| `tailwindcss` | latest | Styling |
| `@radix-ui/*` | latest | Shadcn/UI primitives |
| `lucide-react` | latest | Icons |
| `clsx` | latest | Class utilities |
| `tailwind-merge` | latest | Tailwind class merging |

---

## User Stories (from spec.md)

| ID | Story | Priority |
|----|-------|----------|
| US1 | As a user, I can create an account and log in securely | P1 |
| US2 | As a logged-in user, I can see only my own tasks | P1 |
| US3 | As a logged-in user, I can add a new task | P1 |
| US4 | As a logged-in user, I can update a task | P1 |
| US5 | As a logged-in user, I can delete a task | P1 |
| US6 | As a logged-in user, I can mark a task complete/incomplete | P1 |

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure, install dependencies, configure tooling

**Best Practice**: Use `uv` for Python (modern, fast), `pnpm` or `npm` for Node.js

### Backend Setup

- [x] T001 Create backend directory structure at `todo_app/phase_2/backend/`
- [x] T002 Initialize Python project with `uv init` in `todo_app/phase_2/backend/`
- [x] T003 Create `pyproject.toml` with all dependencies in `todo_app/phase_2/backend/pyproject.toml`
- [x] T004 [P] Create `__init__.py` files for package structure in `todo_app/phase_2/backend/src/todo_app/`
- [x] T005 [P] Create `.env.example` with required variables in `todo_app/phase_2/backend/.env.example`
- [x] T006 [P] Create `backend/CLAUDE.md` with backend-specific guidelines in `todo_app/phase_2/backend/CLAUDE.md`

### Frontend Setup

- [x] T007 Initialize Next.js 16+ project with `create-next-app` in `todo_app/phase_2/frontend/`
- [x] T008 Configure TypeScript, Tailwind CSS, ESLint in `todo_app/phase_2/frontend/`
- [x] T009 [P] Install axios and better-auth dependencies in `todo_app/phase_2/frontend/`
- [x] T010 [P] Initialize Shadcn/UI with `npx shadcn-ui@latest init` in `todo_app/phase_2/frontend/`
- [x] T011 [P] Add Shadcn components: button, input, card, label, checkbox, dialog, toast in `todo_app/phase_2/frontend/`
- [x] T012 [P] Create `.env.local.example` with required variables in `todo_app/phase_2/frontend/.env.local.example`
- [x] T013 [P] Create `frontend/CLAUDE.md` with frontend-specific guidelines in `todo_app/phase_2/frontend/CLAUDE.md`

**Checkpoint**: Both projects should initialize and run without errors

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**Risk Mitigation**: Test DB connection and auth flow BEFORE building features

### Database Foundation

- [x] T014 Create Neon PostgreSQL database on neon.tech
- [x] T015 Configure `DATABASE_URL` in `todo_app/phase_2/backend/.env`
- [x] T016 Create `config.py` with settings and env loading in `todo_app/phase_2/backend/src/todo_app/config.py`
- [x] T017 Create `db.py` with SQLModel engine and session in `todo_app/phase_2/backend/src/todo_app/db.py`
- [x] T018 Create `Task` model with SQLModel in `todo_app/phase_2/backend/src/todo_app/models.py`
- [x] T019 Add table creation on startup in `todo_app/phase_2/backend/src/todo_app/db.py`
- [x] T020 **VALIDATION**: Test database connection with simple query

### FastAPI Foundation

- [x] T021 Create `main.py` FastAPI application entry in `todo_app/phase_2/backend/src/todo_app/main.py`
- [x] T022 Configure CORS middleware for frontend origin in `todo_app/phase_2/backend/src/todo_app/main.py`
- [x] T023 [P] Create health check endpoint `GET /health` in `todo_app/phase_2/backend/src/todo_app/main.py`
- [x] T024 [P] Create `routes/__init__.py` package file in `todo_app/phase_2/backend/src/todo_app/routes/__init__.py`
- [x] T025 **VALIDATION**: Run backend with `uvicorn` and verify `/health` responds

### JWT/Auth Foundation (Backend)

- [x] T026 Create `deps.py` with dependency injection utilities in `todo_app/phase_2/backend/src/todo_app/deps.py`
- [x] T027 Implement `get_current_user` JWT verification dependency in `todo_app/phase_2/backend/src/todo_app/deps.py`
- [x] T028 Implement user_id path validation helper in `todo_app/phase_2/backend/src/todo_app/deps.py`
- [x] T029 **VALIDATION**: Test JWT verification with a mock token

### Better Auth Foundation (Frontend)

- [x] T030 Configure Better Auth with JWT plugin in `todo_app/phase_2/frontend/lib/auth.ts`
- [x] T031 Create auth client wrapper in `todo_app/phase_2/frontend/lib/auth-client.ts`
- [x] T032 Create API client with axios and interceptors in `todo_app/phase_2/frontend/lib/api.ts`
- [x] T033 Create auth context/provider for React in `todo_app/phase_2/frontend/lib/auth-provider.tsx`
- [x] T034 **VALIDATION**: Verify Better Auth can be imported without errors

### Shared Infrastructure

- [x] T035 [P] Create TypeScript interfaces for Task type in `todo_app/phase_2/frontend/lib/types.ts`
- [x] T036 [P] Create Pydantic schemas for API request/response in `todo_app/phase_2/backend/src/todo_app/schemas.py`
- [x] T037 Create root layout with auth provider in `todo_app/phase_2/frontend/app/layout.tsx`

**Checkpoint**: Foundation ready - Backend runs, DB connects, auth utilities ready

---

## Phase 3: User Story 1 - Authentication (Priority: P1)

**Goal**: User can register, login, and receive JWT token for API access

**Independent Test**:
1. Open `/register`, fill form, submit → account created
2. Open `/login`, enter credentials → redirected to dashboard with JWT stored
3. Logout → JWT cleared, redirected to login

### Backend: Auth API Route (Better Auth handles user storage)

- [x] T038 [US1] Create Better Auth API route handler in `todo_app/phase_2/frontend/app/api/auth/[...all]/route.ts`
- [x] T039 [US1] Configure Better Auth server with JWT and email/password in `todo_app/phase_2/frontend/lib/auth.ts`

### Frontend: Registration Page

- [x] T040 [US1] Create registration page structure in `todo_app/phase_2/frontend/app/register/page.tsx`
- [x] T041 [US1] Implement registration form with email/password fields in `todo_app/phase_2/frontend/app/register/page.tsx`
- [x] T042 [US1] Add client-side validation (email format, password length) in `todo_app/phase_2/frontend/app/register/page.tsx`
- [x] T043 [US1] Connect form to Better Auth signUp in `todo_app/phase_2/frontend/app/register/page.tsx`
- [x] T044 [US1] Add loading state and error handling in `todo_app/phase_2/frontend/app/register/page.tsx`
- [x] T045 [US1] Add redirect to login after successful registration in `todo_app/phase_2/frontend/app/register/page.tsx`

### Frontend: Login Page

- [x] T046 [US1] Create login page structure in `todo_app/phase_2/frontend/app/login/page.tsx`
- [x] T047 [US1] Implement login form with email/password fields in `todo_app/phase_2/frontend/app/login/page.tsx`
- [x] T048 [US1] Connect form to Better Auth signIn in `todo_app/phase_2/frontend/app/login/page.tsx`
- [x] T049 [US1] Store JWT token after successful login in `todo_app/phase_2/frontend/lib/auth-client.ts`
- [x] T050 [US1] Add redirect to dashboard after login in `todo_app/phase_2/frontend/app/login/page.tsx`
- [x] T051 [US1] Add "Create account" link to registration in `todo_app/phase_2/frontend/app/login/page.tsx`

### Frontend: Auth Middleware & Protection

- [x] T052 [US1] Create auth middleware for protected routes in `todo_app/phase_2/frontend/middleware.ts`
- [x] T053 [US1] Implement logout functionality in `todo_app/phase_2/frontend/lib/auth-client.ts`
- [x] T054 [US1] Add logout button component in `todo_app/phase_2/frontend/components/logout-button.tsx`

**Checkpoint**: User Story 1 complete - Registration, login, logout working end-to-end

---

## Phase 4: User Story 2 - View Task List (Priority: P1)

**Goal**: Logged-in user sees only their own tasks in a list

**Independent Test**:
1. Login as user A → see user A's tasks only
2. Login as user B → see user B's tasks only
3. Without login → redirected to login page

### Backend: List Tasks Endpoint

- [x] T055 [US2] Create tasks router in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T056 [US2] Implement `GET /api/{user_id}/tasks` endpoint in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T057 [US2] Add user_id validation (JWT sub must match path) in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T058 [US2] Query tasks filtered by user_id in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T059 [US2] Include tasks router in main app in `todo_app/phase_2/backend/src/todo_app/main.py`
- [x] T060 [US2] **VALIDATION**: Test endpoint with curl/httpie using mock JWT

### Frontend: Dashboard Page

- [x] T061 [US2] Create dashboard page structure in `todo_app/phase_2/frontend/app/dashboard/page.tsx`
- [x] T062 [US2] Fetch tasks on page load using API client in `todo_app/phase_2/frontend/app/dashboard/page.tsx`
- [x] T063 [US2] Create TaskList component in `todo_app/phase_2/frontend/components/task-list.tsx`
- [x] T064 [US2] Create TaskItem component in `todo_app/phase_2/frontend/components/task-item.tsx`
- [x] T065 [US2] Display tasks in a list/table format in `todo_app/phase_2/frontend/components/task-list.tsx`
- [x] T066 [US2] Show loading state while fetching in `todo_app/phase_2/frontend/app/dashboard/page.tsx`
- [x] T067 [US2] Show empty state when no tasks in `todo_app/phase_2/frontend/components/task-list.tsx`
- [x] T068 [US2] Add header with user info and logout button in `todo_app/phase_2/frontend/app/dashboard/page.tsx`

**Checkpoint**: User Story 2 complete - Dashboard shows user's tasks

---

## Phase 5: User Story 3 - Add Task (Priority: P1)

**Goal**: Logged-in user can create a new task with title and optional description

**Independent Test**:
1. Click "Add Task" button → dialog/form appears
2. Enter title "Buy milk" → submit
3. New task appears in list immediately

### Backend: Create Task Endpoint

- [x] T069 [US3] Create TaskCreate schema (title required, description optional) in `todo_app/phase_2/backend/src/todo_app/schemas.py`
- [x] T070 [US3] Implement `POST /api/{user_id}/tasks` endpoint in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T071 [US3] Validate user_id matches JWT in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T072 [US3] Create task with user_id, timestamps in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T073 [US3] Return 201 with created task in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T074 [US3] **VALIDATION**: Test endpoint creates task in database

### Frontend: Add Task UI

- [x] T075 [US3] Create AddTaskDialog component in `todo_app/phase_2/frontend/components/add-task-dialog.tsx`
- [x] T076 [US3] Implement form with title (required) and description (optional) in `todo_app/phase_2/frontend/components/add-task-dialog.tsx`
- [x] T077 [US3] Add client-side validation (title not empty) in `todo_app/phase_2/frontend/components/add-task-dialog.tsx`
- [x] T078 [US3] Connect form to POST API endpoint in `todo_app/phase_2/frontend/components/add-task-dialog.tsx`
- [x] T079 [US3] Add loading state during submission in `todo_app/phase_2/frontend/components/add-task-dialog.tsx`
- [x] T080 [US3] Close dialog and refresh task list on success in `todo_app/phase_2/frontend/components/add-task-dialog.tsx`
- [x] T081 [US3] Add "Add Task" button to dashboard header in `todo_app/phase_2/frontend/app/dashboard/page.tsx`
- [x] T082 [US3] Show toast notification on success/error in `todo_app/phase_2/frontend/components/add-task-dialog.tsx`

**Checkpoint**: User Story 3 complete - Can add tasks

---

## Phase 6: User Story 4 - Update Task (Priority: P1)

**Goal**: Logged-in user can edit task title and description

**Independent Test**:
1. Click edit on existing task → form pre-filled with current values
2. Change title to "Buy groceries" → submit
3. List shows updated title

### Backend: Update Task Endpoint

- [x] T083 [US4] Create TaskUpdate schema (optional title, description) in `todo_app/phase_2/backend/src/todo_app/schemas.py`
- [x] T084 [US4] Implement `GET /api/{user_id}/tasks/{id}` endpoint in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T085 [US4] Implement `PUT /api/{user_id}/tasks/{id}` endpoint in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T086 [US4] Validate task belongs to user (404 if not found or wrong user) in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T087 [US4] Update only provided fields, update `updated_at` in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T088 [US4] Return 200 with updated task in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`

### Frontend: Edit Task UI

- [x] T089 [US4] Create EditTaskDialog component in `todo_app/phase_2/frontend/components/edit-task-dialog.tsx`
- [x] T090 [US4] Pre-fill form with existing task data in `todo_app/phase_2/frontend/components/edit-task-dialog.tsx`
- [x] T091 [US4] Connect form to PUT API endpoint in `todo_app/phase_2/frontend/components/edit-task-dialog.tsx`
- [x] T092 [US4] Add edit button to TaskItem component in `todo_app/phase_2/frontend/components/task-item.tsx`
- [x] T093 [US4] Refresh task list on successful update in `todo_app/phase_2/frontend/components/edit-task-dialog.tsx`
- [x] T094 [US4] Show toast notification on success/error in `todo_app/phase_2/frontend/components/edit-task-dialog.tsx`

**Checkpoint**: User Story 4 complete - Can edit tasks

---

## Phase 7: User Story 5 - Delete Task (Priority: P1)

**Goal**: Logged-in user can remove a task from their list

**Independent Test**:
1. Click delete on task → confirmation appears
2. Confirm deletion → task removed from list
3. Task no longer in database

### Backend: Delete Task Endpoint

- [x] T095 [US5] Implement `DELETE /api/{user_id}/tasks/{id}` endpoint in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T096 [US5] Validate task belongs to user in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T097 [US5] Delete task from database in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T098 [US5] Return 204 No Content on success in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`

### Frontend: Delete Task UI

- [x] T099 [US5] Add delete button to TaskItem component in `todo_app/phase_2/frontend/components/task-item.tsx`
- [x] T100 [US5] Create DeleteConfirmDialog component in `todo_app/phase_2/frontend/components/delete-confirm-dialog.tsx`
- [x] T101 [US5] Connect delete to DELETE API endpoint in `todo_app/phase_2/frontend/components/task-item.tsx`
- [x] T102 [US5] Remove task from list on successful deletion in `todo_app/phase_2/frontend/app/dashboard/page.tsx`
- [x] T103 [US5] Show toast notification on success/error in `todo_app/phase_2/frontend/components/task-item.tsx`

**Checkpoint**: User Story 5 complete - Can delete tasks

---

## Phase 8: User Story 6 - Mark Complete (Priority: P1)

**Goal**: Logged-in user can toggle task completion status

**Independent Test**:
1. Click checkbox on incomplete task → task marked complete
2. Click checkbox on complete task → task marked incomplete
3. Visual indicator shows completion status

### Backend: Toggle Complete Endpoint

- [x] T104 [US6] Implement `PATCH /api/{user_id}/tasks/{id}/complete` endpoint in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T105 [US6] Toggle `completed` boolean value in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T106 [US6] Update `updated_at` timestamp in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`
- [x] T107 [US6] Return 200 with updated task in `todo_app/phase_2/backend/src/todo_app/routes/tasks.py`

### Frontend: Completion Toggle UI

- [x] T108 [US6] Add checkbox to TaskItem component in `todo_app/phase_2/frontend/components/task-item.tsx`
- [x] T109 [US6] Connect checkbox to PATCH API endpoint in `todo_app/phase_2/frontend/components/task-item.tsx`
- [x] T110 [US6] Show strikethrough for completed tasks in `todo_app/phase_2/frontend/components/task-item.tsx`
- [x] T111 [US6] Optimistic UI update for instant feedback in `todo_app/phase_2/frontend/components/task-item.tsx`
- [x] T112 [US6] Rollback on API error in `todo_app/phase_2/frontend/components/task-item.tsx`

**Checkpoint**: User Story 6 complete - Can toggle task completion

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, error handling, security hardening

### Error Handling

- [x] T113 [P] Add global error boundary in `todo_app/phase_2/frontend/app/error.tsx`
- [x] T114 [P] Add 404 page in `todo_app/phase_2/frontend/app/not-found.tsx`
- [x] T115 [P] Add loading.tsx for suspense in `todo_app/phase_2/frontend/app/loading.tsx`
- [x] T116 [P] Implement consistent error responses in backend in `todo_app/phase_2/backend/src/todo_app/main.py`

### Security Hardening

- [x] T117 [P] Verify no secrets in code (use env vars only) in all files
- [x] T118 [P] Add input sanitization for task title/description in `todo_app/phase_2/backend/src/todo_app/schemas.py`
- [x] T119 [P] Add rate limiting consideration (document for future) in `todo_app/phase_2/backend/CLAUDE.md`

### Documentation

- [x] T120 [P] Update README.md with setup instructions in `README.md`
- [x] T121 [P] Document API endpoints in `specs/002-phase2-web-app/api-docs.md`
- [x] T122 [P] Add environment variables documentation in `todo_app/phase_2/backend/.env.example`

### Home Page

- [x] T123 Create home page with redirect logic in `todo_app/phase_2/frontend/app/page.tsx`
- [x] T124 Redirect authenticated users to dashboard in `todo_app/phase_2/frontend/app/page.tsx`
- [x] T125 Redirect unauthenticated users to login in `todo_app/phase_2/frontend/app/page.tsx`

**Checkpoint**: Polish complete - App is production-ready

---

## Phase 10: Product Experience & Advanced Features

**Purpose**: Transform the existing functional todo application into a **modern, interactive, feature-rich product** with strong first impression, discoverability, and daily usability.

**Principle**: No breaking changes to existing phases. Build on top of stable CRUD foundation.

---

## User Story 7 (US7): Landing Page & Feature Discovery

**Goal**: As a visitor, I can understand what the app does and why I should sign up.

### Frontend: Landing Page

* [x] T126 Create marketing-style landing page at `/` in `frontend/app/page.tsx`
* [x] T127 Add hero section with app name, tagline, and primary CTA (Get Started)
* [x] T128 Add feature highlights section (Tasks, Auth, Productivity, Speed)
* [x] T129 Add animated mock task cards for visual preview
* [x] T130 Add secondary CTA linking to `/register`
* [x] T131 Add footer with links (Login, Register, GitHub, About)

**Checkpoint**: Unauthenticated users see a polished landing page instead of redirect

---

## User Story 8 (US8): Application Navigation System

**Goal**: As a user, I can navigate between sections of the app easily.

### Frontend: Navigation Layout

* [x] T132 Create persistent navigation component (top bar or sidebar)
* [x] T133 Add navigation links: Dashboard, Today, Upcoming, Completed, Settings
* [x] T134 Highlight active route in navigation
* [x] T135 Make navigation responsive (collapse on mobile)
* [x] T136 Integrate navigation into authenticated layout

**Checkpoint**: Users can move between sections without page confusion

---

## User Story 9 (US9): Task Metadata (Due Dates & Priority)

**Goal**: As a user, I can assign urgency and deadlines to tasks.

### Backend: Model & API Extension

* [x] T137 Extend Task model with `due_date: datetime | null`
* [x] T138 Extend Task model with `priority: low | medium | high`
* [x] T139 Update TaskCreate and TaskUpdate schemas accordingly
* [x] T140 Ensure backward compatibility for existing tasks

### Frontend: UI Support

* [x] T141 Add due date picker to Add/Edit task dialogs
* [x] T142 Add priority selector (dropdown or badges)
* [x] T143 Display due date and priority badge in TaskItem

**Checkpoint**: Tasks support deadlines and urgency

---

## User Story 10 (US10): Filtering, Search & Views

**Goal**: As a user, I can find and organize tasks efficiently.

### Backend (Optional – minimal changes)

* [x] T144 Add optional query params to GET tasks (status, priority, date)

### Frontend: Views & Filters

* [x] T145 Create Today view (tasks due today)
* [x] T146 Create Upcoming view (next 7 days)
* [x] T147 Create Completed tasks view
* [x] T148 Add search input for task title/description
* [x] T149 Add client-side filters (priority, completion)

**Checkpoint**: User can slice task data in multiple useful ways

---

## User Story 11 (US11): UX States & Onboarding

**Goal**: As a new user, I am guided instead of confused.

### Frontend: UX Enhancements

* [x] T150 Add first-time user onboarding message
* [x] T151 Add empty-state illustrations/messages
* [x] T152 Add inline hints for creating first task

**Checkpoint**: New users understand what to do immediately

---

## Phase 11: Final Polish, Motion & Product Readiness

**Purpose**: Add visual delight, motion, and production-level finishing touches.

---

## User Story 12 (US12): Motion & Interaction Layer

**Goal**: App feels smooth, modern, and premium.

### Frontend: Animations

* [x] T153 Add page transitions between routes
* [x] T154 Add hover & focus animations to task cards
* [x] T155 Add spring animation to modals/dialogs
* [x] T156 Add checkbox micro-interaction animation
* [x] T157 Add skeleton loaders for task loading states

**Checkpoint**: App feels responsive and alive

---

## User Story 13 (US13): Settings & Preferences

**Goal**: As a user, I can manage preferences and account actions.

### Frontend: Settings Page

* [x] T158 Create `/settings` page
* [x] T159 Add theme toggle (light/dark)
* [x] T160 Add logout action
* [x] T161 Display account email (read-only)

**Checkpoint**: App feels configurable and mature

---

## User Story 14 (US14): Performance, Accessibility & Readiness

**Goal**: App is ready for real users and portfolio review.

### Cross-Cutting Concerns

* [ ] T162 Audit Lighthouse performance
* [ ] T163 Improve accessibility (labels, focus states, contrast)
* [ ] T164 Optimize bundle size and API calls
* [ ] T165 Add README screenshots & demo GIFs

**Final Checkpoint**: App is production-grade, portfolio-ready, and impressive

## Phase 12: Deployment

**Purpose**: Deploy to production environment

### Backend Deployment

- [x] T166 Create `Dockerfile` for backend in `todo_app/phase_2/backend/Dockerfile`
- [x] T167 [P] Create `docker-compose.yml` for local development in `todo_app/phase_2/docker-compose.yml`
- [ ] T168 Deploy backend to Railway/Render/Fly.io
- [ ] T169 Configure production environment variables
- [ ] T170 **VALIDATION**: Test production API endpoints

### Frontend Deployment

- [ ] T171 Configure `next.config.js` for production in `todo_app/phase_2/frontend/next.config.js`
- [ ] T172 Deploy frontend to Vercel
- [ ] T173 Configure `NEXT_PUBLIC_API_URL` for production
- [ ] T174 **VALIDATION**: Test production frontend

### Final Verification

- [ ] T175 End-to-end test: Register → Login → CRUD → Logout on production
- [ ] T176 Verify user isolation on production (user A can't see user B's tasks)
- [ ] T177 Create 90-second demo video for submission

**Checkpoint**: Deployment complete - App live and working

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────┐
                                                      ▼
Phase 2 (Foundational) ──────────────────────────────┤ BLOCKS ALL USER STORIES
                                                      ▼
┌─────────────────────────────────────────────────────┴─────────────────────────────────────┐
│                                                                                           │
│  Phase 3 (US1: Auth) ────► Phase 4 (US2: View) ────► Phase 5 (US3: Add)                  │
│                                                              │                            │
│                                                              ▼                            │
│                            Phase 6 (US4: Update) ◄──────────┘                            │
│                                    │                                                      │
│                                    ▼                                                      │
│                            Phase 7 (US5: Delete)                                         │
│                                    │                                                      │
│                                    ▼                                                      │
│                            Phase 8 (US6: Complete)                                       │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
                                                      │
                                                      ▼
Phase 9 (Polish) ────────────────────────────────────┤
                                                      ▼
Phase 10 (Deployment) ───────────────────────────────┘
```

### User Story Dependencies

| Story | Can Start After | Depends On |
|-------|-----------------|------------|
| US1 (Auth) | Phase 2 | Foundation only |
| US2 (View) | US1 | Auth must work |
| US3 (Add) | US2 | Need to see tasks |
| US4 (Update) | US3 | Need existing tasks |
| US5 (Delete) | US3 | Need existing tasks |
| US6 (Complete) | US3 | Need existing tasks |

**Note**: US4, US5, US6 can technically run in parallel after US3

### Parallel Opportunities

**Within Phase 1**:
```
T004, T005, T006 can run in parallel (backend setup files)
T009, T010, T011, T012, T013 can run in parallel (frontend setup)
```

**Within Phase 2**:
```
T023, T024 can run in parallel (health check, routes init)
T035, T036 can run in parallel (TypeScript and Pydantic schemas)
```

**After US3 Complete**:
```
US4 (Update), US5 (Delete), US6 (Complete) can all start in parallel
```

---

## Implementation Strategy

### MVP First (Recommended)

1. Complete **Phase 1** (Setup) - Both projects initialized
2. Complete **Phase 2** (Foundation) - DB, Auth utilities ready
3. Complete **Phase 3** (Auth) - Can register/login
4. Complete **Phase 4** (View Tasks) - Dashboard shows tasks
5. **STOP**: You now have a working MVP!
6. Continue with remaining user stories

### Checkpoints for Demo

| After Phase | What Works | Demo-able? |
|-------------|------------|------------|
| 2 | Projects run, DB connects | No |
| 3 | Register, Login, Logout | Yes (auth demo) |
| 4 | View task list | Yes (read-only) |
| 5 | Add tasks | Yes (basic CRUD) |
| 8 | Full CRUD + completion | Yes (full feature) |
| 10 | Deployed | Yes (production) |

---

## Task Count Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| 1: Setup | 13 | 9 |
| 2: Foundational | 24 | 4 |
| 3: US1 Auth | 17 | 0 |
| 4: US2 View | 14 | 0 |
| 5: US3 Add | 14 | 0 |
| 6: US4 Update | 12 | 0 |
| 7: US5 Delete | 9 | 0 |
| 8: US6 Complete | 9 | 0 |
| 9: Polish | 13 | 9 |
| 10: Deployment | 12 | 1 |
| **TOTAL** | **137** | **23** |

---

## Notes

- **[P]** = Tasks that can run in parallel (different files, no dependencies)
- **[USn]** = Task belongs to User Story n
- **VALIDATION** = Stop and verify before proceeding
- Run `uv sync` after modifying Python dependencies
- Run `npm install` after modifying JS dependencies
- Commit after each completed phase or logical group
- Each checkpoint is a stable state suitable for demo/testing
