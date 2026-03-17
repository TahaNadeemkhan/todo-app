---
name: helm-cloud-chart
description: Generate production-ready Helm charts for cloud Kubernetes deployment (GKE/AKS/OKE) with Ingress, TLS, HPA, PDB, and monitoring integration.
---

# Helm Cloud Chart Generator

## Overview

This skill generates production-ready Helm charts optimized for cloud Kubernetes deployments. It provides complete chart templates for deploying full-stack applications to GKE, AKS, or OKE with best practices for scalability, security, and observability.

## When to Use This Skill

- Deploying Phase 5 todo app to cloud Kubernetes (GKE/AKS/OKE)
- Setting up multi-environment deployments (dev, staging, production)
- Configuring auto-scaling with HPA and Pod Disruption Budgets
- Managing secrets and config maps for cloud environments
- Setting up Ingress with TLS/SSL certificates
- Integrating with cloud-native monitoring (Prometheus/Grafana)

## Core Components Generated

### 1. Chart Structure
- `Chart.yaml` - Chart metadata and versioning
- `values.yaml` - Default configuration values
- `values-production.yaml` - Production overrides
- `.helmignore` - Files to exclude from chart

### 2. Template Files
- `deployment-frontend.yaml` - Next.js frontend deployment
- `deployment-backend.yaml` - FastAPI backend deployment
- `service-frontend.yaml` - Frontend service (LoadBalancer)
- `service-backend.yaml` - Backend service (ClusterIP)
- `ingress.yaml` - Ingress with TLS
- `configmap.yaml` - Application configuration
- `secret.yaml` - Sensitive values (from external secrets)
- `hpa.yaml` - Horizontal Pod Autoscaler
- `pdb.yaml` - Pod Disruption Budget
- `serviceaccount.yaml` - RBAC service account

### 3. Helper Templates
- `_helpers.tpl` - Template helpers and common labels
- Resource naming conventions
- Label and selector management

## Usage

### Generate Complete Helm Chart

```bash
/helm-cloud-chart \
  --app-name=todo-app \
  --frontend=nextjs \
  --backend=fastapi \
  --cloud=gke \
  --output=k8s/helm/
```

### Generate with Custom Values

```bash
/helm-cloud-chart \
  --app-name=todo-app \
  --namespace=production \
  --domain=tasks.example.com \
  --tls=true \
  --monitoring=true \
  --output=k8s/helm/
```

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `--app-name` | Application name | todo-app |
| `--frontend` | Frontend framework | nextjs, react |
| `--backend` | Backend framework | fastapi, express |
| `--cloud` | Target cloud provider | gke, aks, oke |
| `--namespace` | Kubernetes namespace | production, staging |
| `--domain` | Application domain | tasks.example.com |
| `--tls` | Enable TLS/HTTPS | true, false |
| `--monitoring` | Add Prometheus annotations | true, false |
| `--output` | Output directory | k8s/helm/ |

## Phase 5 Deployment Architecture

### Frontend Deployment
- **Image**: Next.js 15+ standalone build
- **Replicas**: 2-3 for HA
- **Resources**: 256Mi memory, 100m CPU
- **Autoscaling**: 2-10 replicas based on CPU
- **Service**: LoadBalancer with external IP
- **Ingress**: HTTPS with Let's Encrypt cert

### Backend Deployment
- **Image**: FastAPI with Python 3.13
- **Replicas**: 2-3 for HA
- **Resources**: 512Mi memory, 250m CPU
- **Autoscaling**: 2-10 replicas based on CPU/memory
- **Service**: ClusterIP (internal only)
- **Health Checks**: Liveness and readiness probes

### Supporting Services
- **PostgreSQL**: Neon serverless (external)
- **Kafka**: Redpanda Cloud or local Kafka (via Dapr)
- **Redis**: Optional for caching/sessions
- **Secrets**: Kubernetes secrets or cloud provider secret manager

## Helm Best Practices

### 1. Values Organization
- Use `values.yaml` for defaults
- Environment-specific overrides in separate files
- Never commit secrets to values files
- Use external secrets operator for sensitive data

### 2. Resource Limits
- Always set resource requests and limits
- Start conservative, scale up based on metrics
- Use VPA (Vertical Pod Autoscaler) to tune

### 3. High Availability
- Minimum 2 replicas for production
- Configure Pod Disruption Budgets (PDB)
- Use pod anti-affinity for spreading across nodes

### 4. Security
- Non-root containers
- Read-only root filesystems where possible
- Network policies to restrict traffic
- Service accounts with minimal permissions

### 5. Monitoring
- Add Prometheus annotations for metrics scraping
- Include health check endpoints
- Configure log aggregation
- Set up alerting for critical metrics

## Deployment Commands

```bash
# Install chart
helm install todo-app ./k8s/helm/todo-app \
  --namespace production \
  --create-namespace \
  --values values-production.yaml

# Upgrade existing release
helm upgrade todo-app ./k8s/helm/todo-app \
  --namespace production \
  --values values-production.yaml

# Rollback to previous version
helm rollback todo-app --namespace production

# Uninstall release
helm uninstall todo-app --namespace production
```

For complete Helm templates and values examples, see [examples.md](examples.md).

## Related Skills

- **deployment-blueprint**: Generate Dockerfiles for images
- **github-actions-cloud**: CI/CD pipelines for Helm deployments
- **dapr-component-generator**: Add Dapr components to chart
- **prometheus-dashboard**: Add monitoring to deployed apps

## Tags

helm, kubernetes, cloud, gke, aks, oke, deployment, charts, ingress, hpa, monitoring
