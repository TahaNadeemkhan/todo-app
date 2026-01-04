# Feature Specification: Phase 2 - Full-Stack Web Application

**Feature Branch**: `002-phase2-web-app`
**Created**: 2025-12-09
**Status**: Active
**Version**: 3.0 (Aligned with Hackathon II PDF)

---

## 1. Objective

Transform the Phase 1 console app into a modern **multi-user web application** with persistent storage using Claude Code and Spec-Kit Plus.

---

## 2. Requirements (Basic Level - 5 Features)

Per hackathon requirements, Phase 2 implements **Basic Level functionality only**:

1. **Add Task** - Create new todo items
2. **Delete Task** - Remove tasks from the list
3. **Update Task** - Modify existing task details
4. **View Task List** - Display all tasks
5. **Mark as Complete** - Toggle task completion status

Plus:
- **Authentication** - User signup/signin using Better Auth

---

## 3. Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16+ (App Router) |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Spec-Driven | Claude Code + Spec-Kit Plus |
| Authentication | Better Auth |

---

## 4. API Endpoints

**Base URL**: `/api`

All endpoints require valid JWT token in `Authorization: Bearer <token>` header.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

### 4.1 Response Examples

**GET /api/{user_id}/tasks** (200 OK):
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-09T10:00:00Z",
    "updated_at": "2025-12-09T10:00:00Z"
  }
]
```

**POST /api/{user_id}/tasks** (201 Created):
```json
{
  "title": "New Task Title",
  "description": "Optional details"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing JWT
- `403 Forbidden`: user_id in path does not match JWT
- `404 Not Found`: Task does not exist
- `422 Unprocessable Entity`: Validation error

---

## 5. Authentication Flow (Better Auth + FastAPI)

### 5.1 How It Works

1. **User logs in on Frontend** -> Better Auth creates session and issues JWT token
2. **Frontend makes API call** -> Includes JWT in `Authorization: Bearer <token>` header
3. **Backend receives request** -> Extracts token, verifies signature using shared secret
4. **Backend identifies user** -> Decodes token to get user ID, matches with URL user_id
5. **Backend filters data** -> Returns only tasks belonging to that user

### 5.2 The Shared Secret

Both frontend (Better Auth) and backend (FastAPI) use the same secret key:
```
BETTER_AUTH_SECRET=<high-entropy-secret-string>
```

### 5.3 What Needs to Change

| Component | Changes Required |
|-----------|------------------|
| Better Auth Config | Enable JWT plugin to issue tokens |
| Frontend API Client | Attach JWT token to every API request header |
| FastAPI Backend | Add middleware to verify JWT and extract user |
| API Routes | Filter all queries by authenticated user's ID |

### 5.4 API Behavior After Auth

- All endpoints require valid JWT token
- Requests without token receive `401 Unauthorized`
- Each user only sees/modifies their own tasks
- Task ownership is enforced on every operation

---

## 6. Database Schema

### 6.1 Users Table (Managed by Better Auth)

| Field | Type | Constraints |
|-------|------|-------------|
| id | string | Primary Key |
| email | string | Unique |
| name | string | |
| created_at | timestamp | |

### 6.2 Tasks Table

| Field | Type | Constraints |
|-------|------|-------------|
| id | integer | Primary Key |
| user_id | string | Foreign Key -> users.id |
| title | string | Not Null |
| description | text | Nullable |
| completed | boolean | Default: false |
| created_at | timestamp | |
| updated_at | timestamp | |

### 6.3 Indexes

- `tasks.user_id` (for filtering by user)
- `tasks.completed` (for status filtering)

---

## 7. Monorepo Project Structure

Per hackathon PDF guidance:

```
todo-app/
├── .spec-kit/
│   └── config.yaml
├── specs/
│   ├── overview.md
│   ├── features/
│   │   ├── task-crud.md
│   │   └── authentication.md
│   ├── api/
│   │   └── rest-endpoints.md
│   ├── database/
│   │   └── schema.md
│   └── ui/
│       ├── components.md
│       └── pages.md
├── CLAUDE.md                    # Root Claude Code instructions
├── todo_app/
│   └── phase_2/
│       ├── backend/
│       │   ├── CLAUDE.md        # Backend-specific guidelines
│       │   ├── pyproject.toml
│       │   └── src/
│       │       └── todo_app/
│       │           ├── main.py          # FastAPI entrypoint
│       │           ├── models.py        # SQLModel models
│       │           ├── db.py            # Database connection
│       │           └── routes/
│       │               └── tasks.py     # API route handlers
│       └── frontend/
│           ├── CLAUDE.md        # Frontend-specific guidelines
│           ├── package.json
│           ├── app/             # Next.js App Router pages
│           ├── components/      # Reusable UI components
│           └── lib/
│               ├── api.ts       # API client
│               └── auth-client.ts # Better Auth client
├── docker-compose.yml
└── README.md
```

---

## 8. Frontend Specification

### 8.1 Pages

| Page | Purpose | Auth |
|------|---------|------|
| `/register` | User signup | Public |
| `/login` | User signin | Public |
| `/dashboard` | Task list (main workspace) | Protected |

### 8.2 UI Components (Shadcn/UI)

- `Button`, `Input`, `Card`, `Label`
- `Table`, `Checkbox`, `Dialog`
- `Select`, `Toast`

### 8.3 API Client

```typescript
// /frontend/lib/api.ts
const apiClient = axios.create({ baseURL: '/api' });

apiClient.interceptors.request.use(config => {
  const token = getJwtFromStorage();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 8.4 TypeScript Interfaces

```typescript
interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}
```

---

## 9. Backend Specification

### 9.1 FastAPI Structure

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 9.2 JWT Verification Middleware

```python
# deps.py
from fastapi import Depends, HTTPException, Header
import jwt

async def get_current_user(authorization: str = Header(...)):
    """Extract and verify JWT, return user_id"""
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        return payload["sub"]  # user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")
```

### 9.3 User ID Validation

```python
# routes/tasks.py
@router.get("/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Operation not permitted")
    # ... return user's tasks
```

---

## 10. Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@host/dbname
BETTER_AUTH_SECRET=your-shared-secret-key

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api
BETTER_AUTH_SECRET=your-shared-secret-key
```

---

## 11. User Stories

| Priority | Story |
|----------|-------|
| P1 | As a user, I can create an account and log in securely |
| P1 | As a logged-in user, I can see only my own tasks |
| P1 | As a logged-in user, I can add a new task |
| P1 | As a logged-in user, I can update a task |
| P1 | As a logged-in user, I can delete a task |
| P1 | As a logged-in user, I can mark a task complete/incomplete |

---

## 12. Acceptance Criteria

### 12.1 Authentication
- [ ] User can register with email/password
- [ ] User can login and receive JWT
- [ ] JWT is sent with every API request
- [ ] Invalid/missing JWT returns 401
- [ ] User can only access their own tasks

### 12.2 Task CRUD
- [ ] Create task with title (required) and description (optional)
- [ ] List all tasks for current user
- [ ] Update task title/description
- [ ] Delete task by ID
- [ ] Toggle task completion status

### 12.3 Security
- [ ] No task data exposed without authentication
- [ ] User cannot access other users' tasks (403)
- [ ] Secrets stored in environment variables

---

## 13. Deliverables

1. **GitHub Repository** with:
   - `/specs` folder with specification files
   - `/todo_app/phase_2/backend` - FastAPI server
   - `/todo_app/phase_2/frontend` - Next.js app
   - `CLAUDE.md` with Claude Code instructions
   - `README.md` with setup instructions

2. **Deployed Application**:
   - Frontend on Vercel
   - Backend API URL

3. **Working Features**:
   - User registration and login
   - Task CRUD operations
   - User data isolation

---

## 14. References

- [Hackathon II PDF](./Hackathon%20II%20-%20Todo%20Spec-Driven%20Development.pdf) - Official requirements
- [Better Auth Docs](https://www.better-auth.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js 16 Docs](https://nextjs.org/docs)
- [SQLModel Docs](https://sqlmodel.tiangolo.com/)
