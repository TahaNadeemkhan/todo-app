# Todo App Helm Chart - Quick Start Guide

## Prerequisites

```bash
# Ensure you have these installed
helm version      # Should be v3.0+
kubectl version   # Should match your cluster version
minikube version  # For local deployment
```

## 1. Start Minikube

```bash
minikube start --cpus=4 --memory=4096
minikube status
```

## 2. Build and Load Docker Images

```bash
# Navigate to phase 4 directory
cd /mnt/f/todo-app/todo_app/phase_4

# Build images (if not already built)
docker build -t todo-frontend:v1.0.0 ./frontend
docker build -t todo-backend:v1.0.0 ./backend

# Load images into Minikube
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

# Verify images are loaded
minikube image ls | grep todo
```

## 3. Validate Helm Chart

```bash
cd /mnt/f/todo-app/todo_app/phase_4/k8s/helm

# Lint the chart
helm lint ./todo-app

# Dry-run to preview manifests
helm template todo-app ./todo-app \
  --set secrets.databaseUrl="test" \
  --set secrets.geminiApiKey="test" \
  --set secrets.betterAuthSecret="test" \
  --set secrets.betterAuthUrl="test"
```

## 4. Install Using Script (Recommended)

```bash
# Interactive installation with prompts
./install.sh

# Or with environment variables
DATABASE_URL="postgresql://user:pass@host:5432/db" \
GEMINI_API_KEY="AIzaSyBNJB6NIyJgD-dAKoZY2vJRr0rJA2UjdnE" \
BETTER_AUTH_SECRET="your-secret-here" \
BETTER_AUTH_URL="http://$(minikube ip):30080" \
./install.sh
```

## 5. Manual Installation

```bash
# Get Minikube IP
export MINIKUBE_IP=$(minikube ip)

# Install with Helm
helm install todo-app ./todo-app \
  --set secrets.databaseUrl="postgresql://user:password@host.neon.tech:5432/database?sslmode=require" \
  --set secrets.geminiApiKey="AIzaSyBNJB6NIyJgD-dAKoZY2vJRr0rJA2UjdnE" \
  --set secrets.betterAuthSecret="your-secret-key-here" \
  --set secrets.betterAuthUrl="http://${MINIKUBE_IP}:30080"
```

## 6. Verify Deployment

```bash
# Check release status
helm status todo-app

# Watch pods come up
kubectl get pods -w

# Check all resources
kubectl get all

# Check services
kubectl get svc
```

## 7. Access the Application

```bash
# Get the URL
minikube service todo-app-frontend --url

# Or open in browser directly
minikube service todo-app-frontend
```

## Common Commands

### Check Application Health

```bash
# Frontend health
kubectl exec -it deployment/todo-app-frontend -- curl localhost:3000/api/health

# Backend health
kubectl exec -it deployment/todo-app-backend -- curl localhost:8000/health
```

### View Logs

```bash
# Frontend logs (real-time)
kubectl logs -f deployment/todo-app-frontend

# Backend logs (real-time)
kubectl logs -f deployment/todo-app-backend

# All logs from both
kubectl logs -f -l app.kubernetes.io/instance=todo-app
```

### Scale Replicas

```bash
# Scale frontend
helm upgrade todo-app ./todo-app \
  --reuse-values \
  --set frontend.replicaCount=3

# Scale backend
helm upgrade todo-app ./todo-app \
  --reuse-values \
  --set backend.replicaCount=3

# Or use kubectl
kubectl scale deployment todo-app-frontend --replicas=3
kubectl scale deployment todo-app-backend --replicas=3
```

### Update Application

```bash
# Build new image version
docker build -t todo-frontend:v1.1.0 ./frontend
minikube image load todo-frontend:v1.1.0

# Upgrade release with new image
helm upgrade todo-app ./todo-app \
  --reuse-values \
  --set frontend.image.tag=v1.1.0
```

### Debug Issues

```bash
# Describe a pod
kubectl describe pod <pod-name>

# Get events
kubectl get events --sort-by='.lastTimestamp'

# Check logs from crashed pod
kubectl logs <pod-name> --previous

# Execute shell in pod
kubectl exec -it <pod-name> -- /bin/sh
```

### Rollback

```bash
# View release history
helm history todo-app

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app 2
```

### Clean Up

```bash
# Uninstall release
helm uninstall todo-app

# Verify cleanup
kubectl get all

# If needed, manually delete resources
kubectl delete all -l app.kubernetes.io/instance=todo-app
```

## Troubleshooting

### Issue: ImagePullBackOff

```bash
# Check if images are in Minikube
minikube image ls | grep todo

# If missing, load them
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0
```

### Issue: CrashLoopBackOff

```bash
# Check pod logs
kubectl logs <pod-name>

# Common causes:
# 1. Invalid DATABASE_URL
# 2. Missing GEMINI_API_KEY
# 3. Database connection timeout
# 4. Application startup errors
```

### Issue: Pods Pending

```bash
# Check resource availability
kubectl describe node minikube

# Check pod events
kubectl describe pod <pod-name>

# May need to increase Minikube resources
minikube stop
minikube start --cpus=4 --memory=8192
```

### Issue: Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints

# Check service details
kubectl describe svc todo-app-frontend

# Verify Minikube tunnel (if needed)
minikube tunnel
```

## Configuration Examples

### Development Configuration

```bash
helm install todo-app ./todo-app \
  --set global.environment=dev \
  --set frontend.replicaCount=1 \
  --set backend.replicaCount=1 \
  --set frontend.resources.requests.cpu=50m \
  --set backend.resources.requests.cpu=50m \
  --set secrets.databaseUrl="..." \
  --set secrets.geminiApiKey="..." \
  --set secrets.betterAuthSecret="..." \
  --set secrets.betterAuthUrl="..."
```

### Production-like Configuration

```bash
helm install todo-app ./todo-app \
  --set global.environment=production \
  --set frontend.replicaCount=3 \
  --set backend.replicaCount=3 \
  --set frontend.resources.limits.memory=1Gi \
  --set backend.resources.limits.memory=512Mi \
  --set secrets.databaseUrl="..." \
  --set secrets.geminiApiKey="..." \
  --set secrets.betterAuthSecret="..." \
  --set secrets.betterAuthUrl="..."
```

## Next Steps

1. **Phase 5**: Deploy to cloud Kubernetes (GKE/AKS/EKS)
2. **Add Ingress**: Configure external access with TLS
3. **Add Monitoring**: Integrate Prometheus and Grafana
4. **Add Autoscaling**: Configure HPA for automatic scaling
5. **Add CI/CD**: Automate deployments with GitHub Actions

## Resources

- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Project README](/mnt/f/todo-app/README.md)
