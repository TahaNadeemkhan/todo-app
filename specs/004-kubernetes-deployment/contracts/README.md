# Contracts: Local Kubernetes Deployment

**Feature**: 004-kubernetes-deployment
**Date**: 2025-12-26

---

## Overview

Phase 4 does not introduce new API endpoints. It deploys existing Phase 3 APIs to Kubernetes.

This directory contains **deployment contracts** - the interface definitions for infrastructure components.

---

## Helm Chart Contract

### Install Command Interface

```bash
helm install <release-name> ./helm/todo-app \
  --set secrets.databaseUrl=<DATABASE_URL> \
  --set secrets.openaiApiKey=<OPENAI_API_KEY> \
  --set secrets.betterAuthSecret=<BETTER_AUTH_SECRET> \
  [--set frontend.replicaCount=<N>] \
  [--set backend.replicaCount=<N>]
```

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `secrets.databaseUrl` | string | PostgreSQL connection string |
| `secrets.openaiApiKey` | string | OpenAI API key (sk-...) |
| `secrets.betterAuthSecret` | string | Better Auth secret |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `frontend.replicaCount` | int | 2 | Frontend pod replicas |
| `backend.replicaCount` | int | 2 | Backend pod replicas |
| `frontend.service.nodePort` | int | 30080 | NodePort for frontend |
| `global.imagePullPolicy` | string | IfNotPresent | Image pull policy |

### Output Contract

| Resource | Name | Type |
|----------|------|------|
| Deployment | todo-frontend | apps/v1 |
| Deployment | todo-backend | apps/v1 |
| Service | todo-frontend-svc | NodePort |
| Service | todo-backend-svc | ClusterIP |
| Secret | todo-secrets | Opaque |
| ConfigMap | todo-config | v1 |

---

## Docker Build Contract

### Frontend Build Interface

```bash
docker build \
  -t <image-name>:<tag> \
  -f Dockerfile \
  --build-arg NODE_ENV=production \
  .
```

**Input**: `./frontend` directory with:
- `package.json`
- `package-lock.json`
- `src/` directory
- `next.config.js`

**Output**: Docker image with:
- Port 3000 exposed
- Non-root user
- Standalone Next.js build

### Backend Build Interface

```bash
docker build \
  -t <image-name>:<tag> \
  -f Dockerfile \
  .
```

**Input**: `./backend` directory with:
- `pyproject.toml` or `requirements.txt`
- `src/` directory
- `main.py` or equivalent entrypoint

**Output**: Docker image with:
- Port 8000 exposed
- Non-root user
- Uvicorn server

---

## Health Check Contract

### Backend Health Endpoint

```
GET /health HTTP/1.1
Host: todo-backend-svc:8000

Response:
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "healthy",
  "timestamp": "2025-12-26T10:00:00Z"
}
```

### Frontend Health (Implicit)

Next.js responds 200 on root `/` when healthy.

---

## Minikube Service Contract

### Access Frontend

```bash
minikube service todo-frontend-svc --url
# Returns: http://192.168.49.2:30080
```

### Access Backend (for debugging)

```bash
kubectl port-forward svc/todo-backend-svc 8000:8000
# Access: http://localhost:8000
```

---

## Environment Variable Contract

### Frontend Container

| Variable | Source | Description |
|----------|--------|-------------|
| `NEXT_PUBLIC_API_URL` | ConfigMap | Backend API URL |
| `NODE_ENV` | ConfigMap | production |

### Backend Container

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Secret | PostgreSQL connection string |
| `OPENAI_API_KEY` | Secret | OpenAI API key |
| `BETTER_AUTH_SECRET` | Secret | Auth secret |
| `LOG_LEVEL` | ConfigMap | info |

---

## Image Tag Contract

### Versioning Scheme

```
<repository>:<version>

Examples:
- todo-frontend:v1.0.0
- todo-backend:v1.0.0
- todo-frontend:latest (dev only)
```

### Load to Minikube

```bash
minikube image load <repository>:<version>
```

---

## Error Contracts

### Helm Install Failures

| Error | Cause | Resolution |
|-------|-------|------------|
| `secret not found` | Missing --set secrets.* | Provide required secrets |
| `image pull failed` | Image not in Minikube | Run `minikube image load` |
| `insufficient resources` | Minikube too small | Increase Minikube resources |

### Pod Failures

| State | Cause | Debug Command |
|-------|-------|---------------|
| `Pending` | No resources | `kubectl describe pod` |
| `CrashLoopBackOff` | App crash | `kubectl logs <pod>` |
| `ImagePullBackOff` | Image missing | `minikube image ls` |

---

## Verification Contract

### Deployment Success Criteria

```bash
# All pods running
kubectl get pods | grep -E "frontend|backend" | grep Running

# Services created
kubectl get svc | grep -E "frontend|backend"

# Frontend accessible
curl $(minikube service todo-frontend-svc --url)

# Backend health check
kubectl exec -it <backend-pod> -- curl localhost:8000/health
```
