# Deployment Blueprint Skill

**Purpose**: Generate complete deployment blueprints for full-stack applications on cloud-native platforms

**Trigger Keywords**: deployment, blueprint, infrastructure, IaC, cloud-native, docker, kubernetes, helm, architecture

## Overview

This skill generates comprehensive deployment blueprints that include:
- Multi-stage Dockerfiles (frontend + backend)
- Helm charts for Kubernetes orchestration
- Docker Compose for local development
- CI/CD pipeline configurations
- Infrastructure specifications

## Usage

### Generate Full Deployment Blueprint

```bash
# Generate for a Next.js + FastAPI application
/deployment-blueprint \
  --frontend=nextjs \
  --backend=fastapi \
  --output=./infrastructure \
  --cloud=aws
```

### Configuration Options

| Option | Description | Values |
|--------|-------------|--------|
| --frontend | Frontend framework | nextjs, react, vue |
| --backend | Backend framework | fastapi, express, spring |
| --output | Output directory | path |
| --cloud | Target cloud provider | aws, gcp, azure, local |
| --registry | Container registry | dockerhub, ecr, gcr |

## Generated Artifacts

### 1. Dockerfiles

**Frontend (Next.js)**
- Multi-stage build (deps → builder → runner)
- Node.js 20 Alpine base
- Standalone output optimization
- Non-root user for security

**Backend (FastAPI)**
- Multi-stage build (builder → runner)
- Python 3.13 slim base
- uv for fast dependency installation
- Health checks included

### 2. Helm Chart Structure

```
helm/
└── <app-name>/
    ├── Chart.yaml
    ├── values.yaml
    ├── .helmignore
    └── templates/
        ├── _helpers.tpl
        ├── deployment-frontend.yaml
        ├── deployment-backend.yaml
        ├── service-frontend.yaml
        ├── service-backend.yaml
        ├── configmap.yaml
        ├── secret.yaml
        ├── hpa.yaml
        └── pdb.yaml
```

### 3. Docker Compose (Local Dev)

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
```

### 4. Kubernetes Resources

**Deployments**
- Configured with replicas, resources, health checks
- Environment variables from ConfigMaps/Secrets
- Volume mounts for static assets

**Services**
- Frontend: NodePort (local) or LoadBalancer (cloud)
- Backend: ClusterIP (internal only)

**HPA**
- Auto-scaling based on CPU utilization
- Configurable min/max replicas

**PDB**
- Ensures minimum availability during disruptions

## Best Practices

1. **Immutable Infrastructure**: Rebuild images for each deployment
2. **Security**: Non-root users, read-only filesystems where possible
3. **Observability**: Health checks, resource limits, logging
4. **Scalability**: HPA configured with appropriate thresholds
5. **Secrets Management**: Never commit secrets to git

## Cloud Provider Specifics

### AWS
- Use ECR for container registry
- ALB for load balancing
- RDS for managed databases
- Secrets Manager for secrets

### GCP
- Use Artifact Registry
- Cloud Load Balancing
- Cloud SQL
- Secret Manager

### Local (Minikube/k3d)
- Use local registry or image loading
- NodePort for external access
- SQLite or local PostgreSQL

## Integration

This skill works with:
- **docker-build**: For building images
- **docker-optimization**: For image size reduction
- **k8s-deploy**: For actual deployment execution
- **helm-chart-generator**: For chart customization

---

**Tags**: deployment, infrastructure, IaC, cloud, kubernetes, docker, blueprint, architecture
