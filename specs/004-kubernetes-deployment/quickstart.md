# Quickstart: Local Kubernetes Deployment

**Feature**: 004-kubernetes-deployment
**Date**: 2025-12-26
**Time to Complete**: ~30 minutes

---

## Prerequisites

### Required Tools

| Tool | Version | Install Command |
|------|---------|-----------------|
| Docker | 20.10+ | [docker.com](https://docs.docker.com/get-docker/) |
| Minikube | 1.30+ | `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube` |
| kubectl | 1.28+ | `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo install kubectl /usr/local/bin/kubectl` |
| Helm | 3.12+ | `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \| bash` |

### Required Credentials

Ensure you have these from Phase 3:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `BETTER_AUTH_SECRET` - Better Auth secret

### System Requirements

- **RAM**: 8GB minimum (4GB for Minikube)
- **CPU**: 4 cores minimum (2 for Minikube)
- **Disk**: 20GB free space

---

## Quick Deploy (5 Steps)

### Step 1: Start Minikube

```bash
# Start with recommended resources
minikube start --driver=docker --cpus=4 --memory=4096

# Verify
minikube status
```

### Step 2: Build Docker Images

```bash
cd todo_app/phase_4

# Build frontend
docker build -t todo-frontend:v1.0.0 ./frontend

# Build backend
docker build -t todo-backend:v1.0.0 ./backend
```

### Step 3: Load Images into Minikube

```bash
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

# Verify images loaded
minikube image ls | grep todo
```

### Step 4: Deploy with Helm

```bash
# Navigate to helm chart
cd k8s/helm

# Install (replace placeholders with your actual values)
helm install todo-app ./todo-app \
  --set secrets.databaseUrl="postgresql://user:pass@host/db" \
  --set secrets.openaiApiKey="sk-your-key" \
  --set secrets.betterAuthSecret="your-secret"
```

### Step 5: Access Application

```bash
# Get the URL
minikube service todo-frontend-svc --url

# Open in browser or curl
curl $(minikube service todo-frontend-svc --url)
```

---

## Verification Checklist

```bash
# Check all pods are running
kubectl get pods

# Expected output:
# NAME                            READY   STATUS    RESTARTS   AGE
# todo-frontend-xxx-xxx           1/1     Running   0          1m
# todo-backend-xxx-xxx            1/1     Running   0          1m

# Check services
kubectl get svc

# Expected output:
# NAME                TYPE        CLUSTER-IP      PORT(S)          AGE
# todo-frontend-svc   NodePort    10.x.x.x        3000:30080/TCP   1m
# todo-backend-svc    ClusterIP   10.x.x.x        8000/TCP         1m

# Check backend health
kubectl exec -it $(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}') -- curl localhost:8000/health
```

---

## Common Commands

### View Logs

```bash
# Frontend logs
kubectl logs -l app=frontend -f

# Backend logs
kubectl logs -l app=backend -f
```

### Restart Deployment

```bash
kubectl rollout restart deployment todo-frontend
kubectl rollout restart deployment todo-backend
```

### Scale Replicas

```bash
kubectl scale deployment todo-frontend --replicas=3
kubectl scale deployment todo-backend --replicas=3
```

### Update Deployment

```bash
helm upgrade todo-app ./todo-app --set frontend.replicaCount=3
```

### Uninstall

```bash
helm uninstall todo-app
```

### Stop Minikube

```bash
minikube stop
```

---

## AI-Assisted Commands (Optional)

If you have AI tools installed:

### Gordon (Docker AI)

```bash
# Build with AI assistance
docker ai "build production image for Next.js in ./frontend"
```

### kubectl-ai

```bash
# Query with natural language
kubectl-ai "show me all pods and their resource usage"
kubectl-ai "why is the backend pod failing?"
```

### kagent

```bash
# Analyze cluster
kagent analyze
```

---

## Troubleshooting

### Pod not starting (Pending)

```bash
# Check events
kubectl describe pod <pod-name>

# Common causes:
# - Insufficient resources → Increase Minikube resources
# - Image not found → Run minikube image load
```

### CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> --previous

# Common causes:
# - Missing env vars → Check secrets/configmap
# - Database connection → Verify DATABASE_URL
```

### Service not accessible

```bash
# Check service
kubectl describe svc todo-frontend-svc

# Try port-forward as alternative
kubectl port-forward svc/todo-frontend-svc 3000:3000
```

### Images not found in Minikube

```bash
# Re-load images
minikube image load todo-frontend:v1.0.0 --overwrite

# Or use Minikube's Docker daemon
eval $(minikube docker-env)
docker build -t todo-frontend:v1.0.0 ./frontend
```

---

## Next Steps

1. **Test chatbot functionality** - Create tasks via chat interface
2. **Monitor resources** - `kubectl top pods`
3. **Review logs** - Check for errors or warnings
4. **Create demo video** - Record <90 second walkthrough
5. **Document in README** - Update project documentation

---

## File Structure After Deployment

```
todo_app/phase_4/
├── frontend/
│   ├── Dockerfile           # Multi-stage build
│   └── ...                  # Phase 3 code
├── backend/
│   ├── Dockerfile           # Multi-stage build
│   └── ...                  # Phase 3 code
└── k8s/
    └── helm/
        └── todo-app/
            ├── Chart.yaml
            ├── values.yaml
            └── templates/
                ├── frontend-deployment.yaml
                ├── frontend-service.yaml
                ├── backend-deployment.yaml
                ├── backend-service.yaml
                ├── configmap.yaml
                └── secret.yaml
```
