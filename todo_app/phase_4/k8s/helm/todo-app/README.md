# Todo App Helm Chart

Production-ready Helm chart for deploying the AI-Powered Todo Application to Kubernetes (Minikube for Phase 4).

## Prerequisites

- Kubernetes 1.24+
- Helm 3.0+
- Minikube (for local deployment)
- Docker images loaded into Minikube:
  - `todo-frontend:v1.0.0`
  - `todo-backend:v1.0.0`

## Chart Structure

```
todo-app/
├── Chart.yaml                    # Chart metadata
├── values.yaml                   # Default configuration values
├── .helmignore                   # Files to exclude from chart
├── README.md                     # This file
└── templates/
    ├── _helpers.tpl              # Template helper functions
    ├── configmap.yaml            # Non-sensitive configuration
    ├── secret.yaml               # Sensitive data (secrets)
    ├── frontend-deployment.yaml  # Frontend deployment
    ├── frontend-service.yaml     # Frontend service (NodePort)
    ├── backend-deployment.yaml   # Backend deployment
    └── backend-service.yaml      # Backend service (ClusterIP)
```

## Quick Start

### 1. Load Docker Images into Minikube

```bash
# Start Minikube
minikube start --cpus=4 --memory=4096

# Load images (if not already loaded)
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

# Verify images
minikube image ls | grep todo
```

### 2. Install the Chart

```bash
# Navigate to the helm directory
cd /mnt/f/todo-app/todo_app/phase_4/k8s/helm

# Install with required secrets
helm install todo-app ./todo-app \
  --set secrets.databaseUrl="postgresql://user:password@host:5432/database" \
  --set secrets.geminiApiKey="AIzaSyBNJB6NIyJgD-dAKoZY2vJRr0rJA2UjdnE" \
  --set secrets.betterAuthSecret="your-secret-key-here" \
  --set secrets.betterAuthUrl="http://$(minikube ip):30080"
```

### 3. Verify Deployment

```bash
# Check pods status
kubectl get pods

# Check services
kubectl get svc

# Get frontend URL
minikube service todo-app-frontend --url
```

### 4. Access the Application

```bash
# Open in browser
minikube service todo-app-frontend
```

## Configuration

### Required Secrets (MUST be provided via --set)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `secrets.databaseUrl` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `secrets.geminiApiKey` | Google Gemini API key | `AIzaSy...` |
| `secrets.betterAuthSecret` | Better Auth secret key | `your-secret-here` |
| `secrets.betterAuthUrl` | Better Auth URL (frontend URL) | `http://localhost:30080` |

### Common Configuration Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicaCount` | Number of frontend replicas | `2` |
| `backend.replicaCount` | Number of backend replicas | `2` |
| `frontend.service.nodePort` | NodePort for frontend access | `30080` |
| `frontend.resources.limits.memory` | Frontend memory limit | `512Mi` |
| `backend.resources.limits.memory` | Backend memory limit | `256Mi` |

### Example: Custom Configuration

```bash
helm install todo-app ./todo-app \
  --set secrets.databaseUrl="..." \
  --set secrets.geminiApiKey="..." \
  --set secrets.betterAuthSecret="..." \
  --set secrets.betterAuthUrl="..." \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3
```

## Upgrading

```bash
# Upgrade with new configuration
helm upgrade todo-app ./todo-app \
  --set secrets.databaseUrl="..." \
  --set secrets.geminiApiKey="..." \
  --set secrets.betterAuthSecret="..." \
  --set secrets.betterAuthUrl="..." \
  --set frontend.image.tag=v1.1.0

# View upgrade history
helm history todo-app

# Rollback to previous version
helm rollback todo-app
```

## Validation

```bash
# Lint the chart
helm lint ./todo-app

# Dry-run to see generated manifests
helm template todo-app ./todo-app \
  --set secrets.databaseUrl="test" \
  --set secrets.geminiApiKey="test" \
  --set secrets.betterAuthSecret="test" \
  --set secrets.betterAuthUrl="test"

# Install in dry-run mode
helm install todo-app ./todo-app --dry-run --debug \
  --set secrets.databaseUrl="test" \
  --set secrets.geminiApiKey="test" \
  --set secrets.betterAuthSecret="test" \
  --set secrets.betterAuthUrl="test"
```

## Troubleshooting

### Pods not starting (ImagePullBackOff)

```bash
# Verify images are loaded in Minikube
minikube image ls | grep todo

# If missing, load them
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0
```

### Pods crashing (CrashLoopBackOff)

```bash
# Check pod logs
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>

# Common causes:
# - Missing or invalid environment variables
# - Database connection failure
# - Application startup errors
```

### Service not accessible

```bash
# Get service details
kubectl get svc todo-app-frontend

# Get Minikube IP
minikube ip

# Access via NodePort
curl http://$(minikube ip):30080/api/health
```

### Health checks failing

```bash
# Check if health endpoints exist
kubectl exec -it <frontend-pod> -- curl localhost:3000/api/health
kubectl exec -it <backend-pod> -- curl localhost:8000/health
```

## Uninstalling

```bash
# Uninstall the release
helm uninstall todo-app

# Verify resources are removed
kubectl get all
```

## Production Considerations

### For Phase 5 (Cloud Deployment)

When deploying to cloud Kubernetes (GKE/AKS/EKS), make these changes:

1. **Change Service Type**:
   ```yaml
   frontend:
     service:
       type: LoadBalancer  # or use Ingress
   ```

2. **Add Ingress**:
   - Create `templates/ingress.yaml`
   - Configure TLS certificates
   - Set up DNS

3. **Use Container Registry**:
   ```yaml
   frontend:
     image:
       repository: gcr.io/project/todo-frontend
   ```

4. **External Secrets**:
   - Use Kubernetes External Secrets Operator
   - Or cloud-native secret managers (GCP Secret Manager, AWS Secrets Manager)

5. **Add HPA (Horizontal Pod Autoscaler)**:
   ```bash
   kubectl autoscale deployment todo-app-frontend --cpu-percent=80 --min=2 --max=10
   ```

## Health Checks

The chart includes comprehensive health checks:

### Frontend
- **Liveness Probe**: `/api/health` (30s delay, 10s period)
- **Readiness Probe**: `/api/health` (10s delay, 5s period)

### Backend
- **Liveness Probe**: `/health` (30s delay, 10s period)
- **Readiness Probe**: `/health` (10s delay, 5s period)

## Security

- Non-root containers (UID 1000)
- No privilege escalation
- Secrets managed via Kubernetes Secrets
- Resource limits prevent resource exhaustion

## Support

For issues or questions:
- Check pod logs: `kubectl logs <pod-name>`
- Check events: `kubectl get events --sort-by='.lastTimestamp'`
- Describe resources: `kubectl describe <resource> <name>`
