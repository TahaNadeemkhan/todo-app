---
name: docker-build
description: Generate production-ready multi-stage Dockerfiles for Next.js, FastAPI, and other frameworks. Creates optimized, secure, non-root containers with health checks.
allowed-tools: Read, Write, Bash, Glob
---

# Docker Build Skill

## Context (The Challenge)
Production Docker images must balance **size**, **security**, and **performance**. Single-stage builds create bloated images with unnecessary build tools. Multi-stage builds separate build-time from runtime dependencies, resulting in smaller, more secure containers.

## 🚨 Critical Rules (Dos and Don'ts)

### 1. Multi-Stage Builds are MANDATORY
* **DO** create minimum 3 stages: deps → builder → runner
* **DON'T** use single-stage Dockerfiles for production
* **DO** copy only necessary artifacts between stages
* **CRITICAL:** Final stage must be minimal (Alpine or Slim variants)

### 2. Security First
* **DO** run containers as non-root user (UID 1001)
* **DON'T** use `latest` tags - pin specific versions (e.g., `node:20.10-alpine`)
* **DO** create dedicated system users with minimal permissions
* **DON'T** include secrets, .env files, or credentials in images

### 3. Size Optimization
* **Target:** Frontend < 500MB, Backend < 300MB
* **DO** use Alpine (`-alpine`) or Slim (`-slim`) base images
* **DON'T** install dev dependencies in production stage
* **DO** leverage .dockerignore to exclude build artifacts
* **DO** order instructions from least to most frequently changing

### 4. Health Checks are Required
* **DO** add HEALTHCHECK instruction to every Dockerfile
* **Frontend:** Check `/api/health` or root endpoint
* **Backend:** Check `/health` or `/healthz` endpoint
* **DON'T** skip health checks - Kubernetes requires them

## Framework-Specific Templates

### Next.js 15+ (Frontend)

**Key Requirements:**
- Standalone output mode enabled in `next.config.ts`
- Static files copied to production stage
- Non-root user `nextjs:nodejs`
- Health check on port 3000

**Template:**
```dockerfile
# Stage 1: Dependencies (production only)
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder (with dev dependencies)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Requires next.config.ts: output: 'standalone'
RUN npm run build

# Stage 3: Runner (minimal production)
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 --ingroup nodejs nextjs

# Copy built artifacts
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

**Required next.config.ts:**
```typescript
const nextConfig = {
  output: 'standalone', // CRITICAL for Docker
}
export default nextConfig
```

### FastAPI (Backend)

**Key Requirements:**
- Use `uv` for fast dependency installation
- Copy only .venv, src/, alembic/ to runtime
- Non-root user `appuser:appgroup`
- Health check on port 8000

**Template:**
```dockerfile
# Stage 1: Builder (install dependencies)
FROM python:3.13-slim AS builder
WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev packages)
RUN uv sync --frozen --no-dev

# Stage 2: Runner (minimal runtime)
FROM python:3.13-slim AS runner
WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser

# Copy dependencies from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appgroup src/ ./src/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini ./

# Set environment
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Implementation Workflow

### Step 1: Create .dockerignore
**Purpose:** Exclude build artifacts and dev files from Docker context

**Next.js .dockerignore:**
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

**FastAPI .dockerignore:**
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

### Step 2: Build Image
```bash
# Frontend
docker build -t <app>-frontend:v1.0.0 -f frontend/Dockerfile frontend/

# Backend
docker build -t <app>-backend:v1.0.0 -f backend/Dockerfile backend/
```

### Step 3: Verify Image
```bash
# Check size
docker images | grep <app>

# Expected:
# frontend: < 500MB
# backend:  < 300MB

# Test run
docker run -p 3000:3000 <app>-frontend:v1.0.0
docker run -p 8000:8000 <app>-backend:v1.0.0

# Verify health check
docker inspect <app>-frontend:v1.0.0 | grep -A 10 Healthcheck
```

## Quality Gates Checklist

Before marking Dockerfile complete, verify:

- [ ] **Multi-stage**: Minimum 2 stages (builder + runner)
- [ ] **Base image**: Alpine or Slim variant with pinned version
- [ ] **Non-root**: Container runs as dedicated user (not root)
- [ ] **Size**: Frontend < 500MB, Backend < 300MB
- [ ] **Health check**: HEALTHCHECK instruction present
- [ ] **.dockerignore**: Excludes node_modules/.venv/build artifacts
- [ ] **No secrets**: No .env files or API keys in image
- [ ] **Build success**: `docker build` completes without errors
- [ ] **Runtime test**: Container starts and responds to health check

## Common Issues & Fixes

### Issue: "Cannot find module"
**Cause:** Missing files in COPY instruction
**Fix:** Verify WORKDIR and COPY paths, check .dockerignore

### Issue: Image too large (> 500MB)
**Cause:** Dev dependencies or large base image
**Fix:**
- Use Alpine base images
- Ensure `npm ci --only=production` in deps stage
- Verify .dockerignore excludes node_modules

### Issue: Permission denied
**Cause:** Files not owned by non-root user
**Fix:** Use `--chown` flag in COPY commands:
```dockerfile
COPY --from=builder --chown=nextjs:nodejs /app/.next ./
```

### Issue: Health check fails
**Cause:** Endpoint doesn't exist or port mismatch
**Fix:**
- Create `/api/health` route in Next.js
- Create `/health` endpoint in FastAPI
- Verify EXPOSE port matches health check port

## AI DevOps Integration (Optional)

If **Gordon (Docker AI)** is available:
```bash
docker ai "build production image for Next.js app in ./frontend"
docker ai "optimize image size for FastAPI backend"
docker ai "explain why this Dockerfile is failing"
```

Manual alternative:
```bash
docker build -t <name>:<tag> -f <path>/Dockerfile <context>/
docker images | grep <name>
docker run -p <port>:<port> <name>:<tag>
```

## Example: Complete Implementation

**File structure:**
```
project/
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── next.config.ts (output: 'standalone')
│   └── ... (Next.js app)
└── backend/
    ├── Dockerfile
    ├── .dockerignore
    ├── pyproject.toml
    └── src/
        └── main.py
```

**Build commands:**
```bash
# Build both images
docker build -t todo-frontend:v1.0.0 ./frontend
docker build -t todo-backend:v1.0.0 ./backend

# Verify sizes
docker images | grep todo

# Test locally
docker run -d -p 3000:3000 --name frontend todo-frontend:v1.0.0
docker run -d -p 8000:8000 --name backend todo-backend:v1.0.0

# Check health
docker ps  # Should show "healthy" status after health check interval

# View logs
docker logs frontend
docker logs backend

# Cleanup
docker stop frontend backend
docker rm frontend backend
```

---

**Remember:** Every Dockerfile must be production-ready from day one. Multi-stage builds, non-root users, and health checks are non-negotiable for Kubernetes deployment.
