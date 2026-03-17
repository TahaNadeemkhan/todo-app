# Todo App Deployment Guide

**Phase**: 004 - Kubernetes Deployment
**Last Updated**: 2026-01-01

## Prerequisites

Ensure these tools are installed:
- Docker 20.10+
- Minikube 1.30+
- Helm 3.12+
- kubectl 1.28+

## Quick Start

### 1. Start Minikube

```bash
minikube start --driver=docker --cpus=2 --memory=3072
```

### 2. Build Docker Images

```bash
# Build frontend
docker build -t todo-frontend:v1.0.0 ./todo_app/phase_4/frontend

# Build backend
docker build -t todo-backend:v1.0.0 ./todo_app/phase_4/backend
```

### 3. Load Images into Minikube

```bash
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0
```

### 4. Deploy with Helm

```bash
cd todo_app/phase_4/k8s/helm/todo-app

helm upgrade --install todo-app ./todo-app \
  --set secrets.databaseUrl="YOUR_DATABASE_URL" \
  --set secrets.geminiApiKey="YOUR_GEMINI_API_KEY" \
  --set secrets.betterAuthSecret="YOUR_BETTER_AUTH_SECRET" \
  --set secrets.betterAuthUrl="http://localhost:30080"
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods

# Check services
kubectl get services

# Access frontend
minikube service todo-app-frontend --url
```

## Access the Application

Frontend will be available at:
```
http://localhost:30080
```

Backend API:
```
http://todo-app-backend:8000 (internal)
```

## Configuration

### Helm Values

Edit `values.yaml` to customize:

```yaml
frontend:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

backend:
  replicaCount: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 250m
      memory: 256Mi
```

### Enabling Auto-Scaling

```bash
helm upgrade --install todo-app ./todo-app \
  --set frontend.autoscaling.enabled=true \
  --set backend.autoscaling.enabled=true \
  --set secrets.databaseUrl="..." \
  ...
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Health check failures

Check if the application is responding:
```bash
kubectl exec <pod-name> -- curl http://localhost:3000/
```

### Restart pods

```bash
kubectl rollout restart deployment/todo-app-frontend
kubectl rollout restart deployment/todo-app-backend
```

## Uninstall

```bash
helm uninstall todo-app
minikube delete
```

## Architecture

```
┌─────────────────────────────────────┐
│         Minikube Cluster            │
│  ┌──────────┐    ┌──────────┐      │
│  │Frontend  │    │ Backend  │      │
│  │(NodePort)│    │(ClusterIP)│      │
│  │ :30080   │    │ :8000    │      │
│  └──────────┘    └──────────┘      │
│         │              │            │
│         └──────────────┘            │
│                   │                 │
│              ConfigMap/Secret       │
└─────────────────────────────────────┘
         │
    Neon PostgreSQL
```

## Files

```
todo_app/phase_4/
├── frontend/
│   └── Dockerfile
├── backend/
│   └── Dockerfile
└── k8s/
    └── helm/
        └── todo-app/
            ├── Chart.yaml
            ├── values.yaml
            └── templates/
                ├── deployment-frontend.yaml
                ├── deployment-backend.yaml
                ├── service-frontend.yaml
                ├── service-backend.yaml
                ├── configmap.yaml
                ├── secret.yaml
                ├── hpa.yaml
                └── pdb.yaml
```
