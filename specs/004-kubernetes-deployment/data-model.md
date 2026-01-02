# Data Model: Local Kubernetes Deployment

**Feature**: 004-kubernetes-deployment
**Date**: 2025-12-26

---

## Overview

Phase 4 is primarily a **DevOps/Infrastructure** phase. It does not introduce new application data models but rather defines **Kubernetes resource entities** and **configuration artifacts**.

---

## Kubernetes Resource Entities

### 1. Deployment

Manages pod replicas for frontend and backend services.

| Field | Type | Description |
|-------|------|-------------|
| metadata.name | string | `todo-frontend` or `todo-backend` |
| spec.replicas | integer | Number of pod replicas (default: 2) |
| spec.selector | object | Label selector for pods |
| spec.template | PodTemplateSpec | Pod configuration |

**Relationships**:
- Owns → Pods (manages lifecycle)
- References → Secrets, ConfigMaps (via env)

---

### 2. Service

Provides stable network endpoint for pods.

| Field | Type | Description |
|-------|------|-------------|
| metadata.name | string | `todo-frontend-svc` or `todo-backend-svc` |
| spec.type | enum | `NodePort` (frontend) or `ClusterIP` (backend) |
| spec.ports | array | Port mappings |
| spec.selector | object | Pod label selector |

**Relationships**:
- Selects → Pods (by label)
- Exposes → Deployment

---

### 3. Secret

Stores sensitive configuration data.

| Field | Type | Description |
|-------|------|-------------|
| metadata.name | string | `todo-secrets` |
| type | string | `Opaque` |
| data.DATABASE_URL | base64 | Neon PostgreSQL connection string |
| data.OPENAI_API_KEY | base64 | OpenAI API key |
| data.BETTER_AUTH_SECRET | base64 | Authentication secret |

**Relationships**:
- Referenced by → Deployment (envFrom)

---

### 4. ConfigMap

Stores non-sensitive configuration.

| Field | Type | Description |
|-------|------|-------------|
| metadata.name | string | `todo-config` |
| data.NEXT_PUBLIC_API_URL | string | Backend API URL |
| data.NODE_ENV | string | `production` |
| data.LOG_LEVEL | string | `info` |

**Relationships**:
- Referenced by → Deployment (envFrom)

---

### 5. Pod (Managed by Deployment)

Smallest deployable unit containing containers.

| Field | Type | Description |
|-------|------|-------------|
| metadata.labels | object | `app: frontend` or `app: backend` |
| spec.containers | array | Container definitions |
| spec.containers[].image | string | Docker image reference |
| spec.containers[].ports | array | Container ports |
| spec.containers[].resources | object | CPU/memory limits |
| spec.containers[].livenessProbe | object | Health check config |
| spec.containers[].readinessProbe | object | Readiness check config |

---

## Helm Values Schema

The `values.yaml` acts as the configuration data model for the entire deployment.

```yaml
# values.yaml schema
global:
  namespace: string        # default: "default"
  imagePullPolicy: string  # default: "IfNotPresent"

frontend:
  enabled: boolean         # default: true
  replicaCount: integer    # default: 2
  image:
    repository: string     # default: "todo-frontend"
    tag: string           # default: "v1.0.0"
  service:
    type: string          # default: "NodePort"
    port: integer         # default: 3000
    nodePort: integer     # default: 30080
  resources:
    requests:
      cpu: string         # default: "100m"
      memory: string      # default: "128Mi"
    limits:
      cpu: string         # default: "500m"
      memory: string      # default: "512Mi"
  env:
    NEXT_PUBLIC_API_URL: string  # default: "http://todo-backend-svc:8000"

backend:
  enabled: boolean         # default: true
  replicaCount: integer    # default: 2
  image:
    repository: string     # default: "todo-backend"
    tag: string           # default: "v1.0.0"
  service:
    type: string          # default: "ClusterIP"
    port: integer         # default: 8000
  resources:
    requests:
      cpu: string         # default: "100m"
      memory: string      # default: "256Mi"
    limits:
      cpu: string         # default: "500m"
      memory: string      # default: "512Mi"
  healthPath: string      # default: "/health"

secrets:
  databaseUrl: string     # REQUIRED at install time
  openaiApiKey: string    # REQUIRED at install time
  betterAuthSecret: string # REQUIRED at install time
```

---

## Docker Image Entities

### Frontend Image Layers

| Layer | Base | Purpose |
|-------|------|---------|
| deps | node:20-alpine | Install npm dependencies |
| builder | node:20-alpine | Build Next.js app |
| runner | node:20-alpine | Runtime with standalone output |

### Backend Image Layers

| Layer | Base | Purpose |
|-------|------|---------|
| builder | python:3.13-slim | Install uv and dependencies |
| runner | python:3.13-slim | Runtime with minimal packages |

---

## Entity Relationships Diagram

```
┌─────────────┐       ┌─────────────┐
│   Secret    │       │  ConfigMap  │
│ todo-secrets│       │ todo-config │
└──────┬──────┘       └──────┬──────┘
       │                     │
       │   envFrom           │   envFrom
       ▼                     ▼
┌─────────────────────────────────────┐
│           Deployment                │
│  ┌─────────────┐  ┌─────────────┐  │
│  │  frontend   │  │   backend   │  │
│  │  replicas:2 │  │  replicas:2 │  │
│  └──────┬──────┘  └──────┬──────┘  │
└─────────┼────────────────┼─────────┘
          │                │
          │ manages        │ manages
          ▼                ▼
    ┌──────────┐     ┌──────────┐
    │   Pod    │     │   Pod    │
    │ frontend │     │ backend  │
    └────┬─────┘     └────┬─────┘
         │                │
         │ selected by    │ selected by
         ▼                ▼
    ┌──────────┐     ┌──────────┐
    │ Service  │     │ Service  │
    │ NodePort │     │ClusterIP │
    │  :30080  │────▶│  :8000   │
    └──────────┘     └──────────┘
         │
         │ minikube service
         ▼
    ┌──────────┐
    │ Browser  │
    └──────────┘
```

---

## State Transitions

### Pod Lifecycle States

```
Pending ──▶ Running ──▶ Succeeded
    │          │
    │          ▼
    └─────▶ Failed ──▶ (Restart if RestartPolicy=Always)
```

### Deployment Rollout States

```
Progressing ──▶ Available
     │
     ▼
  Degraded (if replicas unhealthy)
```

---

## Validation Rules

### Helm Values Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| secrets.databaseUrl | Required, non-empty | "Database URL is required" |
| secrets.openaiApiKey | Required, starts with "sk-" | "Valid OpenAI API key required" |
| frontend.replicaCount | >= 1 | "At least 1 frontend replica required" |
| backend.replicaCount | >= 1 | "At least 1 backend replica required" |
| resources.requests.memory | < resources.limits.memory | "Request cannot exceed limit" |

### Docker Build Validation

| Check | Rule |
|-------|------|
| Image size | Frontend < 500MB, Backend < 300MB |
| Non-root user | Container runs as non-root |
| Health check | Dockerfile includes HEALTHCHECK instruction |

---

## Notes

- No new application database tables in Phase 4
- All data models are Kubernetes-native resources
- Configuration is externalized via Helm values
- Secrets are never stored in source code
