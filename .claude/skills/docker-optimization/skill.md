---
name: docker-optimization
description: Optimize Docker image size, layer caching, and build performance. Applies layer ordering, cache mounts, and size reduction techniques for production images.
allowed-tools: Read, Write, Bash, Glob
---

# Docker Optimization Skill

## Context (The Challenge)
Docker images grow quickly without careful layer management. A naive Next.js image can exceed 2GB, while an optimized one stays under 200MB. Build times can take 10+ minutes without proper caching. This skill addresses **size bloat**, **slow builds**, and **inefficient layer caching**.

## 🚨 Critical Rules (Dos and Don'ts)

### 1. Layer Ordering (Cache Efficiency)
* **DO** order instructions from **least to most frequently changing**
* **DO** copy dependency files (package.json, requirements.txt) BEFORE source code
* **DON'T** invalidate cache unnecessarily (e.g., COPY . before dependencies)
* **RULE:** Dependencies change rarely, source code changes often

**❌ Bad (cache busted on every code change):**
```dockerfile
COPY . .
RUN npm install
```

**✅ Good (cache reused unless package.json changes):**
```dockerfile
COPY package*.json ./
RUN npm install
COPY . .
```

### 2. Base Image Selection
* **DO** use Alpine variants when possible (smallest)
* **DO** use Slim variants for Python (Alpine breaks some packages)
* **DON'T** use full images (e.g., `node`, `python`) - 3x larger
* **DO** pin specific versions (e.g., `node:20.10-alpine`, not `node:latest`)

**Size comparison:**
- `node:20` → ~900MB
- `node:20-slim` → ~200MB
- `node:20-alpine` → ~120MB ✅

### 3. Multi-Stage Build Strategy
* **DO** separate build tools from runtime
* **DON'T** include compilers, build tools, or dev dependencies in final stage
* **DO** copy only necessary artifacts between stages
* **CRITICAL:** Final stage should contain ONLY runtime dependencies + app code

### 4. .dockerignore is Mandatory
* **DO** exclude node_modules, .venv, .git, build artifacts
* **DON'T** COPY unnecessary files into Docker context
* **WHY:** Smaller context = faster uploads to Docker daemon

## Optimization Techniques

### Technique 1: Layer Consolidation

**Problem:** Each RUN creates a new layer, increasing size
**Solution:** Chain commands with `&&` to create single layer

**❌ Bad (3 layers):**
```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*
```

**✅ Good (1 layer):**
```dockerfile
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*
```

### Technique 2: Build Cache Mounts (BuildKit)

**Problem:** Package managers re-download on every build
**Solution:** Use cache mounts to persist package manager cache

**Next.js with npm cache:**
```dockerfile
# Enable BuildKit: export DOCKER_BUILDKIT=1
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

**FastAPI with pip cache:**
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

**Build command:**
```bash
DOCKER_BUILDKIT=1 docker build -t app:latest .
```

### Technique 3: Dependency Pruning

**Next.js:** Remove dev dependencies after build
```dockerfile
# Stage 1: Builder (with dev deps)
FROM node:20-alpine AS builder
RUN npm ci  # Installs ALL dependencies
RUN npm run build  # Needs dev dependencies

# Stage 2: Runner (production only)
FROM node:20-alpine AS runner
COPY --from=builder /app/.next/standalone ./  # No dev deps!
```

**FastAPI:** Use `uv` with `--no-dev` flag
```dockerfile
RUN uv sync --frozen --no-dev  # Excludes pytest, black, etc.
```

### Technique 4: Static File Optimization

**Next.js:** Use standalone output mode
```typescript
// next.config.ts
const nextConfig = {
  output: 'standalone',  // Bundles only required dependencies
}
```

**Result:** Reduces image size by ~70% (removes unused Next.js internals)

### Technique 5: Remove Package Manager Files

**After installing dependencies, remove cache:**
```dockerfile
# Alpine (apk)
RUN apk add --no-cache curl  # --no-cache prevents cache storage

# Debian (apt)
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*  # Clean cache

# npm
RUN npm ci && npm cache clean --force

# pip
RUN pip install --no-cache-dir -r requirements.txt
```

## Size Reduction Checklist

**Target Sizes:**
- Next.js Frontend: < 500MB (ideally < 200MB)
- FastAPI Backend: < 300MB (ideally < 150MB)

**Reduction Steps:**

- [ ] **Base image**: Use Alpine or Slim variant
- [ ] **Multi-stage**: Separate builder from runner
- [ ] **Dependencies**: Production only in final stage
- [ ] **Package cache**: Clean after install
- [ ] **.dockerignore**: Exclude node_modules, .venv, .git
- [ ] **Static files**: Next.js standalone mode enabled
- [ ] **Layer count**: Minimize with `&&` chains
- [ ] **BuildKit cache**: Use cache mounts for package managers

## Build Performance Optimization

### Fast Build Strategy

**1. Order layers by change frequency:**
```dockerfile
# Changes rarely → cache friendly
COPY package*.json ./
RUN npm ci

# Changes often → put last
COPY src/ ./src/
RUN npm run build
```

**2. Use .dockerignore to reduce context size:**
```
node_modules
.next
.git
*.log
```

**3. Parallel builds with BuildKit:**
```bash
DOCKER_BUILDKIT=1 docker build --parallel -t app:latest .
```

**4. Cache npm/pip downloads:**
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with cache mounts
docker build -t app:latest .
```

## Quality Gates

Before considering image optimized, verify:

- [ ] **Size check**: `docker images | grep <name>` shows < target size
- [ ] **Layer count**: `docker history <image>` shows minimal layers
- [ ] **Cache test**: Second build completes in < 30 seconds
- [ ] **Runtime test**: Container starts in < 10 seconds
- [ ] **No bloat**: No dev dependencies in final stage
- [ ] **No secrets**: No .env or credentials baked in
- [ ] **Health check**: Passes within start-period

## Diagnostic Commands

```bash
# Check image size
docker images <name>:<tag>

# Inspect layers (find bloat)
docker history <name>:<tag> --no-trunc

# Dive into image (interactive analysis)
dive <name>:<tag>  # Requires: brew install dive

# Compare image sizes
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Build with output to see layer sizes
docker build --no-cache --progress=plain -t <name> . 2>&1 | tee build.log
```

## Common Bloat Sources

### 1. Dev Dependencies
**Problem:** Installing dev packages in production
**Fix:**
```dockerfile
# ❌ Bad
RUN npm install  # Installs everything

# ✅ Good
RUN npm ci --only=production
```

### 2. Build Tools
**Problem:** Keeping compilers in final stage
**Fix:**
```dockerfile
# ❌ Bad (single stage)
FROM python:3.13
RUN apt-get install -y gcc build-essential
RUN pip install -r requirements.txt
# gcc still in final image!

# ✅ Good (multi-stage)
FROM python:3.13 AS builder
RUN apt-get install -y gcc build-essential
RUN pip install -r requirements.txt

FROM python:3.13-slim AS runner
COPY --from=builder /app/.venv /app/.venv
# No gcc!
```

### 3. Logs and Cache
**Problem:** Package manager cache adds 100s of MBs
**Fix:**
```dockerfile
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*  # Clean immediately
```

### 4. Entire Context
**Problem:** No .dockerignore, COPY . includes node_modules
**Fix:**
```
# .dockerignore
node_modules
.next
.git
```

## Example: Before & After

### Before Optimization (1.2GB)
```dockerfile
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
CMD ["npm", "start"]
```

**Issues:**
- Full node image (900MB base)
- Copied entire directory (includes node_modules)
- Installed all dependencies (dev + prod)
- Single stage (build tools in final image)

### After Optimization (180MB)
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

CMD ["node", "server.js"]
```

**Improvements:**
- Alpine base (120MB vs 900MB)
- Multi-stage (no build tools in final)
- Standalone output (minimal dependencies)
- Non-root user (security)
- **Result:** 85% size reduction (1.2GB → 180MB)

## AI DevOps Integration (Mandatory)

Integrating with **Gordon (Docker AI Agent)** is the primary method for optimization:
```bash
# Automated optimization review
gordon analyze Dockerfile --output optimization-plan.md

# Implement Gordon suggestions
gordon optimize --auto-apply

# Verify result
gordon stats todo-backend:v1.0.0
```

Manual analysis is a diagnostic fallback. Gordon's recommendations take precedence for production-grade builds.

---

**Remember:** Every 100MB saved = faster deployments, lower bandwidth costs, and quicker container starts. Optimize early!
