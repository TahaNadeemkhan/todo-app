# Todo App

A multi-phase project evolving from a CLI to a Cloud-Native Web App.

---

## Phase 2: Full-Stack Web App

A modern task management application featuring a Next.js frontend and FastAPI backend with secure authentication and PostgreSQL storage.

### ✨ Features
- **Authentication:** Secure Signup/Login using Better Auth and JWT.
- **Task Management:** Create, Read, Update, Delete tasks.
- **Modern UI:** Built with Shadcn/UI and Tailwind CSS.
- **Secure Backend:** FastAPI with Pydantic validation and SQLModel.

### 🚀 Getting Started

#### Prerequisites
- Node.js 20+
- Python 3.12+
- `uv` package manager
- PostgreSQL Database (Neon DB recommended)

#### 1. Backend Setup
```bash
cd todo_app/phase_2/backend
uv sync
cp .env.example .env
# Edit .env: Set DATABASE_URL and BETTER_AUTH_SECRET
uv run uvicorn src.todo_app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd todo_app/phase_2/frontend
npm install
cp .env.local.example .env.local
# Edit .env.local: Copy values from backend .env
# Run Migration (First time only)
node migrate-postgres.mjs
npm run dev
```

#### 3. Usage
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Phase 1: CLI Console App

A robust command-line interface for managing tasks locally.

### 🚀 Getting Started

```bash
cd todo_app/phase_1
uv sync
uv run python -m todo_app.main
```