---
name: cloud-native-blueprint
description: Generate complete cloud-native deployment blueprints for full-stack applications. Creates Dockerfiles, Helm charts, and deployment pipelines for Next.js + FastAPI stacks on Kubernetes.
allowed-tools: Read, Write, Bash, Glob
---

# Cloud-Native Blueprint Skill

## Context (The Challenge)
Deploying a full-stack application (frontend + backend) to Kubernetes requires **coordinating multiple technologies**: Docker, Helm, Kubernetes, secrets management, networking, and health checks. This skill provides a **complete, end-to-end blueprint** from source code to running production cluster.

## 🚨 Critical Rules (Dos and Don'ts)

### 1. Complete Stack Integration
* **DO** generate Dockerfiles, Helm charts, and deployment scripts as a cohesive system
* **DON'T** create isolated components without considering the full workflow
* **RULE:** Every component must reference and integrate with others

### 2. Security by Default
* **DO** enforce non-root containers, secrets management, and network policies
* **DON'T** allow any credentials, API keys, or tokens to be hardcoded
* **CRITICAL:** Secrets MUST flow from environment → Helm --set → Kubernetes Secret → Pod env vars

### 3. Production-Ready from Day One
* **DO** include health checks, resource limits, and monitoring from the start
* **DON'T** defer production concerns to "later" - build them in now
* **RULE:** Every generated artifact must pass production readiness checks

### 4. Technology Stack Assumptions
* **Frontend:** Next.js 15+ (React, TypeScript)
* **Backend:** FastAPI (Python 3.13+)
* **Database:** Neon PostgreSQL (external SaaS)
* **AI:** OpenAI API (external SaaS)
* **Deployment Target:** Minikube (local) → Cloud Kubernetes (production)

## Blueprint Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                    │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                      Helm Chart                        │  │
│  │  ┌──────────────────┐      ┌──────────────────┐      │  │
│  │  │  Frontend Pod    │      │  Backend Pod     │      │  │
│  │  │  ┌────────────┐  │      │  ┌────────────┐  │      │  │
│  │  │  │ Next.js    │  │      │  │  FastAPI   │  │      │  │
│  │  │  │ Container  │  │      │  │  Container │  │      │  │
│  │  │  └────────────┘  │      │  └────────────┘  │      │  │
│  │  │  Port: 3000     │      │  Port: 8000     │      │  │
│  │  │  Non-root: nextjs│      │  Non-root: appuser│     │  │
│  │  └──────────────────┘      └──────────────────┘      │  │
│  │           │                          │                 │  │
│  │  ┌────────▼────────┐      ┌─────────▼────────┐       │  │
│  │  │ Frontend Service│      │ Backend Service  │       │  │
│  │  │ (NodePort 30080)│      │ (ClusterIP 8000) │       │  │
│  │  └─────────────────┘      └──────────────────┘       │  │
│  │           │                          │                 │  │
│  │           │        ┌─────────────────▼──────┐         │  │
│  │           │        │   Kubernetes Secret    │         │  │
│  │           │        │ DATABASE_URL           │         │  │
│  │           │        │ OPENAI_API_KEY         │         │  │
│  │           │        │ BETTER_AUTH_SECRET     │         │  │
│  │           │        └────────────────────────┘         │  │
│  └───────────┼────────────────────────────────────────── ┘  │
│              │                                               │
│     ┌────────▼────────┐                                     │
│     │ External Access │                                     │
│     │ (minikube       │                                     │
│     │  service URL)   │                                     │
│     └─────────────────┘                                     │
└─────────────────────────────────────────────────────────────┘
         │                          │
         │                          │
    ┌────▼──────┐            ┌─────▼──────┐
    │   User    │            │ External   │
    │  Browser  │            │ Services   │
    └───────────┘            │ (Neon,     │
                             │  OpenAI)   │
                             └────────────┘
```

## Complete Blueprint Structure

```
project/
├── frontend/
│   ├── Dockerfile                 # Multi-stage Next.js build
│   ├── .dockerignore              # Exclude node_modules, .next
│   ├── next.config.ts             # Standalone output mode
│   ├── src/
│   │   └── app/
│   │       └── api/
│   │           └── health/
│   │               └── route.ts   # Health check endpoint
│   └── ... (Next.js app)
│
├── backend/
│   ├── Dockerfile                 # Multi-stage FastAPI build
│   ├── .dockerignore              # Exclude .venv, __pycache__
│   ├── pyproject.toml             # Dependencies
│   ├── src/
│   │   ├── main.py                # FastAPI app
│   │   └── routers/
│   │       └── health.py          # Health check endpoint
│   └── ... (FastAPI app)
│
└── k8s/
    └── helm/
        └── todo-app/
            ├── Chart.yaml          # Chart metadata
            ├── values.yaml         # Configuration defaults
            ├── .helmignore         # Exclude dev files
            └── templates/
                ├── _helpers.tpl    # Template functions
                ├── frontend-deployment.yaml
                ├── frontend-service.yaml
                ├── backend-deployment.yaml
                ├── backend-service.yaml
                └── secret.yaml
```

## Implementation Workflow

### Phase A: Containerization

#### A1: Create Frontend Dockerfile
**Location:** `frontend/Dockerfile`

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 --ingroup nodejs nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000
ENV PORT=3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
```

#### A2: Create Backend Dockerfile
**Location:** `backend/Dockerfile`

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim AS builder
WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Stage 2: Runner
FROM python:3.13-slim AS runner
WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini ./

ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### A3: Create .dockerignore Files

**frontend/.dockerignore:**
```
node_modules
.next
.git
.env*
*.log
.DS_Store
coverage
.vscode
.idea
README.md
```

**backend/.dockerignore:**
```
.venv
__pycache__
*.pyc
.pytest_cache
.git
.env*
*.log
.DS_Store
.coverage
.vscode
.idea
README.md
```

#### A4: Create Health Check Endpoints

**frontend/src/app/api/health/route.ts:**
```typescript
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ status: 'healthy', service: 'frontend' })
}
```

**backend/src/routers/health.py:**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}
```

**backend/src/main.py** (add health router):
```python
from fastapi import FastAPI
from routers import health

app = FastAPI()
app.include_router(health.router)
```

### Phase B: Helm Chart Creation

#### B1: Create Chart Metadata
**Location:** `k8s/helm/todo-app/Chart.yaml`

```yaml
apiVersion: v2
name: todo-app
description: AI-Powered Todo Application with Chatbot
type: application
version: 1.0.0
appVersion: "1.0.0"
```

#### B2: Create Default Configuration
**Location:** `k8s/helm/todo-app/values.yaml`

```yaml
frontend:
  image:
    repository: todo-frontend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicaCount: 2
  service:
    type: NodePort
    port: 3000
    nodePort: 30080
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

backend:
  image:
    repository: todo-backend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicaCount: 2
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

secrets:
  databaseUrl: ""
  openaiApiKey: ""
  betterAuthSecret: ""
```

#### B3: Create Deployment Templates
**Location:** `k8s/helm/todo-app/templates/frontend-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app: frontend
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://{{ include "todo-app.fullname" . }}-backend-svc:8000"
        envFrom:
        - secretRef:
            name: {{ include "todo-app.fullname" . }}-secrets
        resources:
          {{- toYaml .Values.frontend.resources | nindent 12 }}
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Location:** `k8s/helm/todo-app/templates/backend-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: {{ include "todo-app.fullname" . }}-secrets
        resources:
          {{- toYaml .Values.backend.resources | nindent 12 }}
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### B4: Create Service Templates
**Location:** `k8s/helm/todo-app/templates/frontend-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend-svc
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
  - port: {{ .Values.frontend.service.port }}
    targetPort: 3000
    nodePort: {{ .Values.frontend.service.nodePort }}
  selector:
    app: frontend
```

**Location:** `k8s/helm/todo-app/templates/backend-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-backend-svc
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.backend.service.type }}
  ports:
  - port: {{ .Values.backend.service.port }}
    targetPort: 8000
  selector:
    app: backend
```

#### B5: Create Secret Template
**Location:** `k8s/helm/todo-app/templates/secret.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-app.fullname" . }}-secrets
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
type: Opaque
stringData:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | quote }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | quote }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | quote }}
```

### Phase C: Deployment Pipeline

#### C1: Build Images
```bash
#!/bin/bash
# deploy.sh - Complete deployment script

set -e

echo "Building Docker images..."
docker build -t todo-frontend:v1.0.0 ./frontend
docker build -t todo-backend:v1.0.0 ./backend

echo "Verifying image sizes..."
docker images | grep todo
```

#### C2: Load into Minikube
```bash
echo "Loading images into Minikube..."
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

echo "Verifying images in Minikube..."
minikube image ls | grep todo
```

#### C3: Deploy with Helm
```bash
echo "Deploying with Helm..."
helm install todo-app ./k8s/helm/todo-app \
  --set secrets.databaseUrl="${DATABASE_URL}" \
  --set secrets.openaiApiKey="${OPENAI_API_KEY}" \
  --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}"

echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend --timeout=120s

echo "Getting service URL..."
minikube service todo-app-frontend-svc --url
```

## Quality Gates Checklist

- [ ] **Dockerfiles**: Multi-stage, non-root, health checks, < size limits
- [ ] **.dockerignore**: Excludes build artifacts
- [ ] **Health endpoints**: Exist in both frontend and backend
- [ ] **Helm Chart**: Passes `helm lint` with zero errors
- [ ] **Deployments**: Have liveness + readiness probes
- [ ] **Services**: Correct types (NodePort/ClusterIP)
- [ ] **Secrets**: Template exists, NO values in values.yaml
- [ ] **Resource limits**: Defined for all containers
- [ ] **Build succeeds**: Both Docker builds complete
- [ ] **Deploy succeeds**: `helm install` completes without errors
- [ ] **Pods running**: `kubectl get pods` shows Running status
- [ ] **Health checks pass**: Liveness/readiness probes succeed
- [ ] **Application accessible**: Frontend URL returns 200 OK

## End-to-End Deployment Commands

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=4096

# 2. Build Docker images
docker build -t todo-frontend:v1.0.0 ./frontend
docker build -t todo-backend:v1.0.0 ./backend

# 3. Load into Minikube
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

# 4. Deploy with Helm
helm install todo-app ./k8s/helm/todo-app \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.openaiApiKey="sk-..." \
  --set secrets.betterAuthSecret="..."

# 5. Verify deployment
kubectl get pods
kubectl get svc

# 6. Access application
minikube service todo-app-frontend-svc --url
```

---

**Remember:** A cloud-native blueprint is more than just code - it's a complete, integrated system that's production-ready from day one!
