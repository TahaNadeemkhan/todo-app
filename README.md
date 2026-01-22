# Todo App

A multi-phase project evolving from a CLI to a Cloud-Native Web App with AI capabilities.

---

## Phase 3: AI-Powered Chatbot (Current)

An intelligent AI assistant integrated into the web app that lets you manage tasks using natural language.

### ✨ Features
- **AI Task Management:** Create, update, and manage tasks through natural conversation
- **Voice Input:** Speak to create tasks hands-free
- **Smart Context:** AI understands task priorities, due dates, and categories
- **Conversation History:** Persistent chat history across sessions
- **MCP Tools Integration:** Custom Model Context Protocol tools for task operations
- **ChatKit UI:** Modern streaming chat interface powered by OpenAI Agents SDK

### 🤖 AI Capabilities
- **Voice Input:** Speak naturally to add tasks - hands-free task management
- Natural language task creation: "Add buy groceries to my list"
- Bulk operations: "Mark all today's tasks as complete"
- Smart queries: "What tasks are due this week?"
- Contextual understanding of priorities and deadlines
- Real-time audio transcription and AI response

### 🚀 Getting Started

#### Prerequisites
- Node.js 20+
- Python 3.13+
- PostgreSQL Database (Neon DB)
- OpenAI API Key

#### 1. Backend Setup
```bash
cd todo_app/phase_3/backend
uv sync
cp .env.example .env
# Edit .env: Set DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY
alembic upgrade head  # Run migrations
uv run uvicorn src.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd todo_app/phase_3/frontend
npm install
cp .env.local.example .env.local
# Edit .env.local: Set NEXT_PUBLIC_API_URL and auth variables
npm run dev
```

#### 3. Usage
Open [http://localhost:3000](http://localhost:3000) and click the chatbot icon to start chatting!

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