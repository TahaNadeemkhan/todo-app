# Phase 5 Todo App - Quick Start Guide

Yeh guide aapko batayegi ke Phase 5 todo app ko kaise run karein (Urdu/English mix).

## 🚀 Local Development (Sabse Pehle Yeh Karen)

### Prerequisites (Zaroori Cheezain)

Yeh sab install hone chahiye:
- **Node.js 20+** (frontend ke liye)
- **Python 3.13+** (backend ke liye)
- **PostgreSQL** (database - Neon Serverless use kar rahe hain)
- **Docker Desktop** (optional - Kafka ke liye)

---

## Method 1: Simple Local Development (Recommended)

### Step 1: Backend Setup

```bash
# Backend directory mein jayen
cd d:\piaic\todo-app\todo_app\phase_5\backend

# Virtual environment banayen (agar nahi hai)
python -m venv venv

# Activate karein
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Dependencies install karein
pip install -r requirements.txt

# Environment variables set karein
# .env file banayen aur yeh add karein:
```

**.env file (backend):**
```env
DATABASE_URL=your_neon_postgresql_url
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET=your_secret_key_here
BETTER_AUTH_SECRET=your_auth_secret
BETTER_AUTH_URL=http://localhost:3000
```

```bash
# Database migrations run karein
alembic upgrade head

# Backend server start karein
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend ab chal raha hai: **http://localhost:8000**

---

### Step 2: Frontend Setup

```bash
# Naya terminal kholein
# Frontend directory mein jayen
cd d:\piaic\todo-app\todo_app\phase_5\frontend

# Dependencies install karein
npm install

# Environment variables set karein
# .env.local file banayen:
```

**.env.local file (frontend):**
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_USE_DAPR=false
BETTER_AUTH_SECRET=your_auth_secret
BETTER_AUTH_URL=http://localhost:3000
```

```bash
# Frontend start karein
npm run dev
```

Frontend ab chal raha hai: **http://localhost:3000**

---

### Step 3: App Use Karein! 🎉

1. Browser mein jayen: **http://localhost:3000**
2. Sign up karein
3. Tasks create karein
4. Recurring tasks try karein (daily/weekly/monthly)
5. Due dates set karein

---

## Method 2: With Kafka (Event-Driven Features)

Agar aap full event-driven features chahte hain (microservices, notifications):

### Step 1: Kafka Start Karein

```bash
# Phase 5 directory mein jayen
cd d:\piaic\todo-app\todo_app\phase_5

# Docker Compose se Kafka start karein
docker-compose up -d
```

Yeh start karega:
- Kafka (port 9092)
- PostgreSQL (agar local use kar rahe hain)

### Step 2: Backend + Microservices

```bash
# Backend (same as above)
cd backend
uvicorn main:app --reload --port 8000

# Naya terminal - Notification Service
cd services/notification-service
python -m src.main

# Naya terminal - Recurring Task Service
cd services/recurring-task-service
python -m src.main
```

### Step 3: Frontend (same as above)

```bash
cd frontend
npm run dev
```

---

## Method 3: Kubernetes Deployment (Advanced)

Agar aap Minikube ya cloud mein deploy karna chahte hain:

### Minikube Setup

```bash
# Minikube start karein
minikube start --cpus=4 --memory=8192

# Dapr install karein
dapr init -k

# Helm chart deploy karein
cd d:\piaic\todo-app\todo_app\phase_5\k8s\helm
helm install todo-app ./todo-app

# Services expose karein
minikube service frontend-service
```

---

## 🐛 Common Issues (Aam Maslay)

### Issue 1: "Module not found" errors
```bash
# Frontend mein
cd frontend
npm install

# Backend mein
cd backend
pip install -r requirements.txt
```

### Issue 2: Database connection error
- Neon PostgreSQL URL check karein
- `.env` file mein `DATABASE_URL` sahi hai?

### Issue 3: Port already in use
```bash
# Port 8000 free karein (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Port 3000 free karein
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Issue 4: CORS errors
- Backend `.env` mein `CORS_ORIGINS` add karein:
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 📁 Project Structure

```
todo_app/phase_5/
├── backend/              # FastAPI backend (port 8000)
├── frontend/             # Next.js frontend (port 3000)
├── services/
│   ├── notification-service/    # Email/Push notifications
│   └── recurring-task-service/  # Auto-create recurring tasks
├── k8s/                  # Kubernetes manifests
└── docker-compose.yml    # Kafka + PostgreSQL
```

---

## 🎯 Quick Test Checklist

Yeh sab kaam karna chahiye:

- [ ] Sign up / Login
- [ ] Create task
- [ ] Create recurring task (daily/weekly/monthly)
- [ ] Set due date and time
- [ ] Mark task complete
- [ ] See next occurrence of recurring task (agar microservices chal rahe hain)

---

## 🆘 Help Chahiye?

Agar koi issue aa raha hai:

1. **Backend logs dekhen**: Terminal mein errors check karein
2. **Frontend console dekhen**: Browser DevTools → Console
3. **Database check karein**: Neon dashboard mein tables dekhen
4. **Ports check karein**: `netstat -ano` se dekhen

---

## 🚀 Production Deployment

Production ke liye:

1. **Vercel** (Frontend): `vercel deploy`
2. **Railway/Render** (Backend): Git push se auto-deploy
3. **Kubernetes** (Full stack): Helm chart use karein

---

**Tip**: Pehle Method 1 try karein (simple local development). Jab woh kaam kare, phir Kafka aur microservices add karein.

**Questions?** Mujhe batao, main help karunga! 🚀
