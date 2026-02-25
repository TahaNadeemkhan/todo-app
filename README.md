# Phase 4: Local Kubernetes Deployment (v1.0.4)

This phase focuses on containerizing the application and deploying it to a local Kubernetes cluster using Minikube and Helm. It also introduces a major schema migration from integer IDs to UUIDs.

## Key Changes in Phase 4

- **UUID Migration:** Task IDs have been migrated from `int` to `str` (UUID v4) to support distributed systems and prevent ID collisions.
- **Kubernetes Native:** Full manifests and Helm charts for deploying Frontend and Backend services.
- **Neon Postgres Integration:** Seamless connection to Neon Serverless Postgres with `sslmode=require`.
- **CORS Handling:** Updated backend to support cross-origin requests from the local frontend.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker Desktop** (or Docker Engine)
*   **Minikube**
*   **Kubectl**
*   **Helm**
*   **Python 3.10+** (for database initialization scripts)

## Step-by-Step Deployment Guide

### 1. Start Minikube

Start your local Kubernetes cluster:

```bash
minikube start --driver=docker --cpus=2 --memory=4000
```

### 2. Build and Load Docker Images

Build the Docker images for both the frontend and backend. We are using `v1.0.4` for the backend to include critical UUID fixes.

**Backend (v1.0.4):**
```bash
cd backend
docker build -t todo-backend:v1.0.4 .
minikube image load todo-backend:v1.0.4
```

**Frontend (v1.0.0):**
```bash
cd ../frontend
docker build -t todo-frontend:v1.0.0 .
minikube image load todo-frontend:v1.0.0
```

### 3. Initialize the Database (UUID Schema)

Since we migrated to UUIDs, the existing table must be dropped and recreated. Run this script from your host (ensure `sqlalchemy` and `psycopg2-binary` are installed):

```bash
# From todo_app/phase_4/ directory
uv run --with sqlalchemy --with psycopg2-binary python manual_init_db.py
```

### 4. Deploy with Helm

Navigate to the Helm chart directory and install the application using the following command. **Note:** Use the exact `sslmode=require` parameter.

```bash
cd ../k8s/helm

helm upgrade --install todo-app ./todo-app \
  --set secrets.databaseUrl="postgresql://neondb_owner:<PASSWORD>@<HOST>/neondb?sslmode=require" \
  --set secrets.geminiApiKey="<YOUR_KEY>" \
  --set secrets.betterAuthSecret="<YOUR_SECRET>" \
  --set secrets.betterAuthUrl="http://localhost:3000"
```

### 5. Access the Application (Port Forwarding)

Because we are running in a local environment, use `kubectl port-forward` to access the services from your browser. Run these in separate terminals:

**Frontend (Port 3000):**
```bash
kubectl port-forward --address 0.0.0.0 svc/todo-app-frontend 3000:3000
```

**Backend (Port 8000):**
```bash
kubectl port-forward --address 0.0.0.0 svc/todo-app-backend 8000:8000
```

Now open [http://localhost:3000](http://localhost:3000) in your browser (Incognito mode recommended).

## Troubleshooting

- **500 Internal Server Error:** Check backend logs: `kubectl logs -l app.kubernetes.io/component=backend`. Common cause is Pydantic schema mismatch or missing database table.
- **Connection Refused:** Ensure you are using `--address 0.0.0.0` in your port-forward command to allow WSL/Windows communication.
- **CORS Issues:** The `v1.0.4` backend has wildcard CORS enabled for debugging. If issues persist, clear browser cache or use Incognito mode.

## Clean Up

```bash
helm uninstall todo-app
minikube stop
```
