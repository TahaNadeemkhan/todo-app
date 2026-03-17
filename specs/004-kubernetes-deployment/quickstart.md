# Quickstart: Local Kubernetes Deployment

**Feature**: 004-kubernetes-deployment
**Date**: 2026-01-02
**Time to Complete**: ~15 minutes (if prerequisites installed)

---

## Prerequisites

### Required Tools

| Tool | Version | Install Command |
|------|---------|-----------------|
| Docker | 20.10+ | [docker.com](https://docs.docker.com/get-docker/) |
| Minikube | 1.30+ | `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube` |
| kubectl | 1.28+ | `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo install kubectl /usr/local/bin/kubectl` |
| Helm | 3.12+ | `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \| bash` |

### Required Credentials (from Phase 3)

```bash
DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
BETTER_AUTH_SECRET="your-auth-secret"
GEMINI_API_KEY="your-gemini-key"  # For AI chatbot
```

### System Requirements

- **RAM**: 8GB minimum (4GB for Minikube)
- **CPU**: 4 cores minimum (2 for Minikube)
- **Disk**: 20GB free space

---

## Quick Deploy (Copy-Paste Commands)

### Step 1: Start Minikube

```bash
# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=4096

# Verify it's running
minikube status
```

### Step 2: Build Docker Images

```bash
# Navigate to Phase 4 directory
cd /mnt/d/piaic/todo-app/todo_app/phase_4

# Build Frontend image
docker build -t todo-frontend:v1.0.0 -f frontend/Dockerfile frontend/

# Build Backend image
docker build -t todo-backend:v1.0.0 -f backend/Dockerfile backend/
```

### Step 3: Load Images into Minikube

```bash
# Load images into Minikube's registry
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

# Verify images are loaded
minikube image ls | grep todo
```

### Step 4: Deploy with Helm

```bash
# Navigate to Helm chart directory
cd /mnt/d/piaic/todo-app/todo_app/phase_4/k8s/helm

# Deploy (replace with YOUR actual values)
helm install todo-app ./todo-app \
  --set secrets.databaseUrl="postgresql://neondb_owner:YOUR_PASSWORD@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require" \
  --set secrets.betterAuthSecret="YOUR_BETTER_AUTH_SECRET" \
  --set secrets.betterAuthUrl="http://localhost:3000" \
  --set secrets.geminiApiKey="YOUR_GEMINI_API_KEY"

# Verify pods are running
kubectl get pods -w
```

### Step 5: Setup Port Forwards (IMPORTANT!)

```bash
# Terminal 1: Frontend port-forward
kubectl port-forward svc/todo-app-frontend 3000:3000

# Terminal 2: Backend port-forward
kubectl port-forward svc/todo-app-backend 8000:8000
```

**Or run both in background:**

```bash
kubectl port-forward svc/todo-app-frontend 3000:3000 > /dev/null 2>&1 &
kubectl port-forward svc/todo-app-backend 8000:8000 > /dev/null 2>&1 &
```

### Step 6: Access Application

Open browser: **http://localhost:3000**

---

## One-Liner Quick Start (After Prerequisites)

```bash
# Full deployment in one command (run from project root)
cd /mnt/d/piaic/todo-app/todo_app/phase_4 && \
docker build -t todo-frontend:v1.0.0 -f frontend/Dockerfile frontend/ && \
docker build -t todo-backend:v1.0.0 -f backend/Dockerfile backend/ && \
minikube image load todo-frontend:v1.0.0 && \
minikube image load todo-backend:v1.0.0 && \
cd k8s/helm && \
helm upgrade --install todo-app ./todo-app \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
  --set secrets.betterAuthUrl="http://localhost:3000" \
  --set secrets.geminiApiKey="$GEMINI_API_KEY" && \
kubectl port-forward svc/todo-app-frontend 3000:3000 &
kubectl port-forward svc/todo-app-backend 8000:8000 &
echo "App running at http://localhost:3000"
```

---

## Verification Commands

```bash
# Check all pods are running
kubectl get pods
# Expected: 2 frontend pods, 2 backend pods (STATUS: Running)

# Check services
kubectl get svc
# Expected: todo-app-frontend (NodePort 30080), todo-app-backend (NodePort 30081)

# Check backend health
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Check frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Expected: 200

# View pod logs
kubectl logs -l app.kubernetes.io/component=frontend --tail=20
kubectl logs -l app.kubernetes.io/component=backend --tail=20
```

---

## Common Commands Reference

### View Logs

```bash
# Frontend logs (live)
kubectl logs -l app.kubernetes.io/component=frontend -f

# Backend logs (live)
kubectl logs -l app.kubernetes.io/component=backend -f
```

### Restart Deployments

```bash
kubectl rollout restart deployment todo-app-frontend
kubectl rollout restart deployment todo-app-backend
```

### Scale Replicas

```bash
kubectl scale deployment todo-app-frontend --replicas=3
kubectl scale deployment todo-app-backend --replicas=3
```

### Update Configuration

```bash
helm upgrade todo-app ./todo-app \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3
```

### Check Resource Usage

```bash
kubectl top pods
kubectl top nodes
```

### Exec into Pod

```bash
# Frontend
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}') -- sh

# Backend
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}') -- sh
```

---

## Cleanup Commands

```bash
# Stop port-forwards
pkill -f "kubectl port-forward"

# Uninstall Helm release
helm uninstall todo-app

# Stop Minikube
minikube stop

# Delete Minikube cluster (full reset)
minikube delete
```

---

## Troubleshooting

### Error: `ERR_CONNECTION_REFUSED` on localhost:3000

**Cause:** Port-forward not running or local dev server blocking port

**Fix:**
```bash
# Kill any local dev servers
pkill -f "next dev"

# Restart port-forward
kubectl port-forward svc/todo-app-frontend 3000:3000
```

### Error: Tasks not loading (backend connection refused)

**Cause:** Backend port-forward stopped

**Fix:**
```bash
# Check if port 8000 is listening
ss -tlnp | grep 8000

# If not, restart port-forward
kubectl port-forward svc/todo-app-backend 8000:8000
```

### Error: Pods in `Pending` state

**Cause:** Insufficient Minikube resources or images not loaded

**Fix:**
```bash
# Check pod events
kubectl describe pod <pod-name>

# Reload images
minikube image load todo-frontend:v1.0.0 --overwrite
minikube image load todo-backend:v1.0.0 --overwrite
```

### Error: `CrashLoopBackOff`

**Cause:** Application crash (usually missing env vars or DB connection)

**Fix:**
```bash
# Check logs
kubectl logs <pod-name> --previous

# Verify secrets are set
kubectl get secret todo-app-secret -o yaml
```

### Error: Images not found

**Cause:** Images not loaded into Minikube

**Fix:**
```bash
# Option 1: Load images
minikube image load todo-frontend:v1.0.0

# Option 2: Use Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t todo-frontend:v1.0.0 -f frontend/Dockerfile frontend/
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                        │
│                                                             │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │  Frontend Pods (2)  │    │  Backend Pods (2)   │        │
│  │  Next.js App        │───▶│  FastAPI Server     │        │
│  │  Port: 3000         │    │  Port: 8000         │        │
│  └─────────────────────┘    └─────────────────────┘        │
│           │                          │                      │
│           ▼                          ▼                      │
│  ┌─────────────────────┐    ┌─────────────────────┐        │
│  │  NodePort: 30080    │    │  NodePort: 30081    │        │
│  └─────────────────────┘    └─────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
           │                          │
           ▼                          ▼
    kubectl port-forward        kubectl port-forward
    localhost:3000 ─────────▶   localhost:8000 ─────────▶
           │                          │
           ▼                          ▼
    ┌───────────┐              ┌─────────────────┐
    │  Browser  │              │  Neon Database  │
    │  User     │              │  (External)     │
    └───────────┘              └─────────────────┘
```

---

## File Structure

```
todo_app/phase_4/
├── frontend/
│   ├── Dockerfile           # Multi-stage Next.js build
│   ├── src/                 # Next.js app code
│   └── package.json
├── backend/
│   ├── Dockerfile           # Multi-stage FastAPI build
│   ├── main.py              # FastAPI entry point
│   └── requirements.txt
└── k8s/
    └── helm/
        └── todo-app/
            ├── Chart.yaml           # Helm chart metadata
            ├── values.yaml          # Configuration values
            └── templates/
                ├── frontend-deployment.yaml
                ├── frontend-service.yaml
                ├── backend-deployment.yaml
                ├── backend-service.yaml
                ├── configmap.yaml
                └── secret.yaml
```

---

## Service Ports Reference

| Service | Internal Port | NodePort | Port-Forward |
|---------|---------------|----------|--------------|
| Frontend | 3000 | 30080 | localhost:3000 |
| Backend | 8000 | 30081 | localhost:8000 |

---

## Environment Variables

### Frontend (Next.js)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_URL` | Frontend URL | `http://localhost:3000` |
| `DATABASE_URL` | Neon PostgreSQL | `postgresql://...` |
| `BETTER_AUTH_SECRET` | Auth secret | `random-secret` |

### Backend (FastAPI)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL | `postgresql://...` |
| `GEMINI_API_KEY` | AI chatbot key | `AIzaSy...` |
| `BETTER_AUTH_SECRET` | Auth secret | `random-secret` |
| `BETTER_AUTH_URL` | Auth server URL | `http://localhost:3000` |

---

## Quick Reference Card

```bash
# Start everything
minikube start && \
kubectl port-forward svc/todo-app-frontend 3000:3000 & \
kubectl port-forward svc/todo-app-backend 8000:8000 &

# Check status
kubectl get pods && kubectl get svc

# View logs
kubectl logs -l app.kubernetes.io/component=frontend -f
kubectl logs -l app.kubernetes.io/component=backend -f

# Stop everything
pkill -f "kubectl port-forward" && minikube stop
```

**App URL:** http://localhost:3000
