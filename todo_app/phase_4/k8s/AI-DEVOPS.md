# AI DevOps Tools Guide

This guide explains how to use AI-powered tools for Kubernetes deployment optimization.

## Tools Overview

| Tool | Purpose | Install |
|------|---------|---------|
| Gordon | Docker image optimization | `npm install -g gordon-ai` |
| kubectl-ai | K8s manifest generation | `brew install kubectl-ai` |
| kagent | Cluster efficiency analysis | `brew install kagent` |

---

## Gordon - Docker Optimization

### Analyze Dockerfile

```bash
# Analyze frontend Dockerfile
gordon analyze ./frontend/Dockerfile

# Analyze backend Dockerfile
gordon analyze ./backend/Dockerfile
```

### Security Scan

```bash
# Scan image for vulnerabilities
gordon scanner --image todo-frontend:v1.0.0
gordon scanner --image todo-backend:v1.0.0
```

### Optimize Dockerfile

```bash
# Get optimization recommendations
gordon optimize ./frontend/Dockerfile --output=./frontend/Dockerfile.optimized
```

---

## kubectl-ai - Kubernetes Manifests

### Generate HPA (Horizontal Pod Autoscaler)

```bash
kubectl ai "create horizontal pod autoscaler for frontend deployment with min 2 and max 5 replicas"
```

### Generate PDB (Pod Disruption Budget)

```bash
kubectl ai "create pod disruption budget for frontend with min available 1"
```

### Generate Complete Deployment

```bash
kubectl ai "create deployment for nextjs app with 2 replicas, nodeport service on port 3000"
```

---

## kagent - Cluster Analysis

### Analyze Cluster

```bash
# Run efficiency analysis
kagent analyze --cluster minikube

# Generate report
kagent analyze --cluster minikube --output report.md
```

### Resource Right-Sizing

```bash
# Get recommendations
kagent recommend --cluster minikube

# Apply recommendations automatically
kagent apply --cluster minikube --recommendations
```

### Cost Estimation

```bash
kagent cost --cluster minikube --provider=aws
```

---

## Usage in This Project

### Phase 3: Containerization

```bash
# Build images
gordon optimize ./frontend/Dockerfile > ./frontend/Dockerfile
gordon optimize ./backend/Dockerfile > ./backend/Dockerfile

# Build
docker build -t todo-frontend:v1.0.0 ./frontend
docker build -t todo-backend:v1.0.0 ./backend

# Scan
gordon scanner --image todo-frontend:v1.0.0
gordon scanner --image todo-backend:v1.0.0
```

### Phase 5: K8s Manifests

```bash
# Generate HPA
kubectl ai "create horizontal pod autoscaler for todo-app-frontend with min 2 max 5 replicas cpu target 80%"

# Generate PDB
kubectl ai "create pod disruption budget for todo-app-frontend min available 1"
```

### Phase 8: Cluster Review

```bash
# Analyze
kagent analyze --cluster minikube

# Get recommendations
kagent recommend --cluster minikube
```

---

## Best Practices

1. **Run gordon scanner** before production deployment
2. **Use kubectl-ai** for complex manifest generation
3. **Run kagent** weekly for cluster optimization
4. **Review AI suggestions** before applying
5. **Version control** generated manifests

---

## Troubleshooting

### Gordon not working?

```bash
# Check installation
gordon --version

# Reinstall
npm uninstall -g gordon-ai
npm install -g gordon-ai
```

### kubectl-ai permission denied?

```bash
# Make executable
chmod +x $(which kubectl-ai)

# Add to PATH
export PATH="$PATH:$(dirname $(which kubectl-ai))"
```

### kagent cluster not found?

```bash
# Check kubeconfig
kubectl config view

# Set cluster context
kubectl config use-context minikube
```

---

## Alternatives

If these tools are not available:
- **DockerScan**: `docker scan <image>`
- **Kubernetes Generator**: Use Helm templates (included in this project)
- **Kubernetes Dashboard**: Web UI for cluster analysis
