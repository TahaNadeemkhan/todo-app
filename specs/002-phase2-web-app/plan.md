# Implementation Plan: Phase 2 - Full-Stack Web Application

**Version**: 3.0 (Aligned with Hackathon II PDF)
**Created**: 2025-12-09

---

## Execution Strategy: Vertical Slice Approach

Rather than building backend completely first then frontend, we implement **end-to-end features** incrementally:

```
Slice 1: Walking Skeleton (Auth + 1 endpoint working)
Slice 2: Full CRUD (All 5 Basic Level features)
Slice 3: Polish (Error handling, UI refinement)
```

---

## Phase 2A: Project Initialization

### 1. Backend Setup (FastAPI)

- [ ] Initialize Python project in `todo_app/phase_2/backend/` using `uv`
- [ ] Create `pyproject.toml` with dependencies:
  - `fastapi`, `uvicorn[standard]`
  - `sqlmodel`, `pydantic`
  - `pyjwt` (for JWT verification)
  - `python-dotenv`
  - `psycopg2-binary` (PostgreSQL driver)
- [ ] Create directory structure:
  ```
  backend/
  ├── src/todo_app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   ├── db.py
  │   ├── models.py
  │   ├── deps.py
  │   └── routes/
  │       ├── __init__.py
  │       └── tasks.py
  └── CLAUDE.md
  ```
- [ ] Create `backend/CLAUDE.md` with backend guidelines

### 2. Frontend Setup (Next.js 16+)

- [ ] Initialize Next.js project in `todo_app/phase_2/frontend/` using `create-next-app`
- [ ] Configure: TypeScript, Tailwind CSS, ESLint, App Router
- [ ] Install dependencies:
  - `axios` (HTTP client)
  - `better-auth` (authentication)
  - Shadcn/UI components
- [ ] Create directory structure:
  ```
  frontend/
  ├── app/
  │   ├── layout.tsx
  │   ├── page.tsx
  │   ├── login/page.tsx
  │   ├── register/page.tsx
  │   └── dashboard/page.tsx
  ├── components/
  ├── lib/
  │   ├── api.ts
  │   └── auth-client.ts
  └── CLAUDE.md
  ```
- [ ] Create `frontend/CLAUDE.md` with frontend guidelines

### 3. Database Setup

- [ ] Create Neon PostgreSQL database
- [ ] Configure `DATABASE_URL` in `.env`
- [ ] Test database connection

---

## Phase 2B: Authentication Layer

### 4. Better Auth Setup (Frontend)

- [ ] Configure Better Auth with JWT plugin
- [ ] Create `lib/auth-client.ts` with authClient
- [ ] Implement `/register` page with form
- [ ] Implement `/login` page with form
- [ ] Store JWT token after successful login
- [ ] Implement logout functionality

### 5. JWT Middleware (Backend)

- [ ] Create `deps.py` with `get_current_user` dependency
- [ ] Implement JWT verification using `BETTER_AUTH_SECRET`
- [ ] Extract `user_id` from token `sub` claim
- [ ] Return 401 for invalid/missing tokens

### 6. User ID Validation

- [ ] Validate `user_id` in URL matches JWT `sub`
- [ ] Return 403 if mismatch

---

## Phase 2C: Database Models & Repository

### 7. SQLModel Models

- [ ] Define `Task` model in `models.py`:
  ```python
  class Task(SQLModel, table=True):
      id: int | None = Field(default=None, primary_key=True)
      user_id: str = Field(index=True)
      title: str
      description: str | None = None
      completed: bool = False
      created_at: datetime
      updated_at: datetime
  ```
- [ ] Create database engine in `db.py`
- [ ] Implement table creation on startup

---

## Phase 2D: API Endpoints

### 8. Task CRUD Routes

All routes in `routes/tasks.py`:

- [ ] `GET /api/{user_id}/tasks` - List all tasks
- [ ] `POST /api/{user_id}/tasks` - Create new task
- [ ] `GET /api/{user_id}/tasks/{id}` - Get single task
- [ ] `PUT /api/{user_id}/tasks/{id}` - Update task
- [ ] `DELETE /api/{user_id}/tasks/{id}` - Delete task
- [ ] `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

### 9. Main Application

- [ ] Configure CORS in `main.py`
- [ ] Include task router
- [ ] Add health check endpoint

---

## Phase 2E: Frontend Implementation

### 10. API Client

- [ ] Create `lib/api.ts` with axios instance
- [ ] Add request interceptor for JWT
- [ ] Add response interceptor for 401 handling

### 11. Dashboard Page

- [ ] Create `/dashboard/page.tsx`
- [ ] Fetch and display tasks
- [ ] Add "Add Task" button/dialog
- [ ] Implement task list with checkboxes
- [ ] Add edit/delete actions

### 12. Task Components

- [ ] `TaskList` component
- [ ] `TaskItem` component
- [ ] `AddTaskDialog` component
- [ ] `EditTaskDialog` component

---

## Phase 2F: Integration & Testing

### 13. End-to-End Verification

- [ ] Test complete flow: Register -> Login -> CRUD -> Logout
- [ ] Verify user isolation (user A cannot see user B's tasks)
- [ ] Test error scenarios (401, 403, 404)

### 14. Environment Setup

- [ ] Backend `.env` configured
- [ ] Frontend `.env.local` configured
- [ ] Both services communicate correctly

---

## Phase 2G: Deployment

### 15. Deploy Backend

- [ ] Choose hosting (Railway/Render/Fly.io)
- [ ] Configure environment variables
- [ ] Deploy and test API

### 16. Deploy Frontend

- [ ] Deploy to Vercel
- [ ] Configure `NEXT_PUBLIC_API_URL`
- [ ] Test production deployment

---

## Commands Reference

```bash
# Backend
cd todo_app/phase_2/backend
uv sync
uv run uvicorn src.todo_app.main:app --reload --port 8000

# Frontend
cd todo_app/phase_2/frontend
npm install
npm run dev
```

---

## Checklist Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| 2A | Project Initialization | Pending |
| 2B | Authentication Layer | Pending |
| 2C | Database Models | Pending |
| 2D | API Endpoints | Pending |
| 2E | Frontend Implementation | Pending |
| 2F | Integration Testing | Pending |
| 2G | Deployment | Pending |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Better Auth complexity | Start with simple JWT flow, enhance later |
| Neon DB connection issues | Test connection early, have local fallback |
| CORS problems | Configure properly from start |
| JWT token handling | Use well-tested libraries (pyjwt) |

---

## Success Criteria

1. User can register and login
2. Authenticated user can perform all 5 CRUD operations
3. User can only see/modify their own tasks
4. App deployed and accessible online
5. 90-second demo video ready
