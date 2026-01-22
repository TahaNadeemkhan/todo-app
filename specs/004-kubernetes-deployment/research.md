# Research: Local Kubernetes Deployment

**Feature**: 004-kubernetes-deployment
**Date**: 2025-12-26
**Purpose**: Resolve technical decisions and best practices for Phase 4 deployment

---

## R1: Docker Multi-Stage Build Strategy

### Decision
Use multi-stage builds with Alpine-based images for both frontend and backend.

### Rationale
- **Size Reduction**: Multi-stage builds eliminate build dependencies from final image
- **Security**: Smaller attack surface with minimal runtime dependencies
- **Speed**: Smaller images = faster pulls in Minikube

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Single-stage build | Simpler | Large images (1GB+), includes build tools | Rejected |
| Multi-stage Alpine | Small (100-300MB), secure | May need Alpine-specific fixes | **Selected** |
| Multi-stage Distroless | Smallest, most secure | No shell for debugging | Considered for production |

### Implementation

**Frontend (Next.js)**:
```
Stage 1: node:20-alpine (deps)
Stage 2: node:20-alpine (build)
Stage 3: node:20-alpine (runner) - standalone output
```

**Backend (FastAPI)**:
```
Stage 1: python:3.13-slim (build with uv)
Stage 2: python:3.13-slim (runtime only)
```

---

## R2: Helm Chart Structure

### Decision
Create a single umbrella Helm chart with subcharts for frontend and backend.

### Rationale
- **Simplicity**: Single `helm install` deploys entire stack
- **Configuration**: Unified `values.yaml` for all components
- **Hackathon Fit**: Easier to demonstrate and grade

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Separate charts | Independent lifecycle | Complex coordination | Rejected |
| Single umbrella chart | Simple deployment, unified config | Tight coupling | **Selected** |
| Kustomize | Native K8s, no Helm | Hackathon requires Helm | Rejected |

### Chart Structure
```
helm/todo-app/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── configmap.yaml
│   └── secret.yaml
```

---

## R3: Kubernetes Service Types

### Decision
- **Frontend**: NodePort (accessible via `minikube service`)
- **Backend**: ClusterIP (internal only, frontend proxies)

### Rationale
- NodePort allows direct browser access without Ingress complexity
- ClusterIP for backend prevents external direct API access
- Simpler than Ingress for local development

### Alternatives Considered

| Option | Frontend | Backend | Decision |
|--------|----------|---------|----------|
| Both NodePort | External | External | Security concern |
| NodePort + ClusterIP | External | Internal | **Selected** |
| Ingress for both | External via Ingress | Internal | Overkill for Minikube |
| LoadBalancer | Works on cloud | N/A locally | Not for Minikube |

---

## R4: Secrets Management Strategy

### Decision
Use Kubernetes Secrets with Helm templating; values provided at install time.

### Rationale
- **Security**: Secrets not in version control
- **Flexibility**: Different values for different environments
- **Simplicity**: Native K8s, no external vault needed

### Implementation
```bash
# Install with secrets
helm install todo-app ./helm/todo-app \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.openaiApiKey="sk-..." \
  --set secrets.betterAuthSecret="..."
```

### Alternatives Considered

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Helm --set values | Simple, no files | Values in shell history | **Selected** |
| External secrets file | Cleaner | File management overhead | Alternative |
| Sealed Secrets | GitOps-ready | Complexity for hackathon | Future enhancement |
| Vault | Enterprise-grade | Overkill | Not needed |

---

## R5: Health Check Implementation

### Decision
- **Backend**: HTTP GET `/health` endpoint returning 200 OK
- **Frontend**: HTTP GET on root `/` or `/api/health`

### Rationale
- Simple HTTP checks are Kubernetes-native
- `/health` is industry standard
- Separates liveness (is running) from readiness (can serve)

### Probe Configuration
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

---

## R6: Resource Limits Strategy

### Decision
Set conservative defaults suitable for Minikube with 8GB RAM allocation.

### Rationale
- Prevents single pod from consuming all Minikube resources
- Allows 2 replicas of each service
- Leaves headroom for system components

### Resource Allocation

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Frontend | 100m | 500m | 128Mi | 512Mi |
| Backend | 100m | 500m | 256Mi | 512Mi |

**Total per replica pair**: 200m CPU, 1GB memory
**With 2 replicas each**: 400m CPU, 2GB memory

---

## R7: AI DevOps Tools Integration

### Decision
Document usage but make optional; provide manual alternatives.

### Rationale
- Tools may not be available on all systems
- Hackathon demonstrates awareness, not dependency
- Manual commands always work

### Tool Usage Examples

**Gordon (Docker AI)**:
```bash
# If available
docker ai "Build optimized image for Next.js app"

# Manual alternative
docker build -t todo-frontend:v1.0.0 -f Dockerfile .
```

**kubectl-ai**:
```bash
# If available
kubectl-ai "Show all pods and their status"

# Manual alternative
kubectl get pods -o wide
```

**kagent**:
```bash
# If available
kagent analyze

# Manual alternative
kubectl top pods && kubectl describe pods
```

---

## R8: Environment Variable Strategy

### Decision
Use ConfigMap for non-sensitive config, Secrets for sensitive data.

### ConfigMap Values
- `NEXT_PUBLIC_API_URL` - Backend API URL for frontend
- `NODE_ENV` - production
- `LOG_LEVEL` - info

### Secret Values
- `DATABASE_URL` - Neon PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `BETTER_AUTH_SECRET` - Auth secret

---

## R9: Image Loading Strategy for Minikube

### Decision
Use `minikube image load` to load locally-built images.

### Rationale
- No registry needed
- Faster than pushing/pulling from remote
- Works offline

### Implementation
```bash
# Build images
docker build -t todo-frontend:v1.0.0 ./frontend
docker build -t todo-backend:v1.0.0 ./backend

# Load into Minikube
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

# Verify
minikube image ls | grep todo
```

### Alternative: Minikube Docker Daemon
```bash
eval $(minikube docker-env)
docker build -t todo-frontend:v1.0.0 ./frontend
# Image available directly in Minikube
```

---

## R10: Bonus - Reusable Skills Design

### Decision
Create Claude Code skills for deployment automation.

### Skill: k8s-deploy
**Purpose**: Deploy any containerized app to Minikube
**Inputs**:
- Application type (frontend/backend/fullstack)
- Framework detected from package.json/requirements.txt
**Outputs**:
- Dockerfile
- Helm chart templates
- Deployment commands

### Skill: deployment-blueprint
**Purpose**: Generate complete deployment configs
**Inputs**:
- Frontend framework (Next.js, React, Vue)
- Backend framework (FastAPI, Express, Django)
- Database type (PostgreSQL, MongoDB, MySQL)
**Outputs**:
- Multi-service Dockerfile templates
- Helm umbrella chart
- Environment configuration templates

---

## Summary of Decisions

| Topic | Decision | Confidence |
|-------|----------|------------|
| Docker builds | Multi-stage Alpine | High |
| Helm structure | Single umbrella chart | High |
| Frontend service | NodePort | High |
| Backend service | ClusterIP | High |
| Secrets | K8s Secrets via Helm | High |
| Health checks | HTTP /health endpoint | High |
| Resources | Conservative limits | Medium |
| AI tools | Optional with alternatives | High |
| Image loading | minikube image load | High |
| Bonus skills | k8s-deploy + blueprint | Medium |

All technical decisions resolved. Ready for Phase 1: Design & Contracts.
