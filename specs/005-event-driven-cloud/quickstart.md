# Quickstart Guide: Phase 5 - Event-Driven Cloud Deployment

**Feature**: 005-event-driven-cloud
**Created**: 2026-01-04
**Estimated Setup Time**: 60-90 minutes

## Prerequisites

### Required Tools

1. **Docker Desktop** (latest)
   - Install: https://www.docker.com/products/docker-desktop
   - Required for: Building container images, running local Kafka

2. **Minikube** (v1.33+)
   - Install: `brew install minikube` (macOS) or https://minikube.sigs.k8s.io/docs/start/
   - Required for: Local Kubernetes cluster

3. **Helm** (v3.15+)
   - Install: `brew install helm` (macOS) or https://helm.sh/docs/intro/install/
   - Required for: Kubernetes package management

4. **Dapr CLI** (v1.14+)
   - Install: `brew install dapr/tap/dapr-cli` (macOS) or https://docs.dapr.io/getting-started/install-dapr-cli/
   - Required for: Dapr installation and management

5. **kubectl** (v1.30+)
   - Install: `brew install kubectl` (macOS) or https://kubernetes.io/docs/tasks/tools/
   - Required for: Kubernetes cluster management

6. **Python** (3.13+)
   - Install: `brew install python@3.13` (macOS) or https://www.python.org/downloads/
   - Required for: Backend API and microservices

7. **uv** (0.5+)
   - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Required for: Python dependency management

8. **Node.js** (20+)
   - Install: `brew install node` (macOS) or https://nodejs.org/
   - Required for: Frontend (Next.js)

### Optional Tools

9. **k9s** (nice-to-have)
   - Install: `brew install k9s` (macOS)
   - Required for: Terminal-based Kubernetes dashboard

10. **Lens** (nice-to-have)
    - Install: https://k8slens.dev/
    - Required for: GUI-based Kubernetes dashboard

---

## Part 1: Local Development Setup (Minikube)

### Step 1: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g --kubernetes-version=v1.30.0

# Enable Ingress addon (for HTTP routing)
minikube addons enable ingress

# Verify cluster is running
kubectl cluster-info
```

Expected output:
```
Kubernetes control plane is running at https://127.0.0.1:xxxxx
CoreDNS is running at https://127.0.0.1:xxxxx/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

---

### Step 2: Install Dapr on Minikube

```bash
# Initialize Dapr on Kubernetes
dapr init -k --enable-mtls=true --enable-ha=false --wait

# Verify Dapr installation
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
dapr-sidecar-injector  dapr-system  True     Running  1         1.14.0   15s  2026-01-04 12:00.00
dapr-sentry            dapr-system  True     Running  1         1.14.0   15s  2026-01-04 12:00.00
dapr-operator          dapr-system  True     Running  1         1.14.0   15s  2026-01-04 12:00.00
dapr-placement         dapr-system  True     Running  1         1.14.0   15s  2026-01-04 12:00.00
```

---

### Step 3: Install Kafka (Bitnami Helm Chart)

```bash
# Add Bitnami Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install Kafka in KRaft mode (no Zookeeper)
helm install kafka bitnami/kafka \
  --set kraft.enabled=true \
  --set listeners.client.protocol=PLAINTEXT \
  --set controller.replicaCount=1 \
  --set broker.replicaCount=1 \
  --set persistence.size=5Gi \
  --wait

# Verify Kafka is running
kubectl get pods | grep kafka
```

Expected output:
```
kafka-controller-0   1/1     Running   0          2m
```

**Create Kafka Topics**:
```bash
# Get Kafka pod name
KAFKA_POD=$(kubectl get pods -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

# Create topics
kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic task-events --partitions 3 --replication-factor 1

kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic reminders --partitions 2 --replication-factor 1

kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic notifications --partitions 2 --replication-factor 1

# Verify topics
kubectl exec -it $KAFKA_POD -- kafka-topics.sh \
  --bootstrap-server localhost:9092 --list
```

---

### Step 4: Setup PostgreSQL (Neon Serverless)

**Option A: Use Existing Neon Database** (from Phase 2/3)

```bash
# Export connection string
export DATABASE_URL="postgresql://user:password@neon-host:5432/todo_db?sslmode=require"
```

**Option B: Use Local PostgreSQL** (for offline development)

```bash
# Install PostgreSQL via Helm
helm install postgres bitnami/postgresql \
  --set auth.postgresPassword=postgres \
  --set auth.database=todo_db \
  --wait

# Get PostgreSQL password
export POSTGRES_PASSWORD=$(kubectl get secret postgres-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)

# Port-forward to access locally
kubectl port-forward svc/postgres-postgresql 5432:5432 &

# Create database
PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U postgres -d postgres -c "CREATE DATABASE todo_db;"
```

**Run Alembic Migrations** (from Phase 5 backend):

```bash
cd todo_app/phase_5/backend

# Install dependencies
uv sync

# Run migrations
uv run alembic upgrade head
```

---

### Step 5: Create Kubernetes Secrets

```bash
# Create namespace (if not exists)
kubectl create namespace default || true

# PostgreSQL credentials
kubectl create secret generic postgres-credentials \
  --from-literal=connectionString="$DATABASE_URL" \
  --dry-run=client -o yaml | kubectl apply -f -

# SMTP credentials (use Gmail App Password or similar)
kubectl create secret generic smtp-credentials \
  --from-literal=SMTP_HOST="smtp.gmail.com" \
  --from-literal=SMTP_PORT="587" \
  --from-literal=SMTP_USERNAME="your-email@gmail.com" \
  --from-literal=SMTP_PASSWORD="your-app-password" \
  --from-literal=SMTP_FROM_EMAIL="noreply@todo-app.local" \
  --dry-run=client -o yaml | kubectl apply -f -

# FCM credentials (placeholder - optional for Phase 5)
kubectl create secret generic fcm-credentials \
  --from-literal=FCM_SERVER_KEY="placeholder" \
  --from-literal=FCM_PROJECT_ID="placeholder" \
  --dry-run=client -o yaml | kubectl apply -f -

# JWT secret
kubectl create secret generic jwt-secret \
  --from-literal=JWT_SECRET="your-secret-key-here-change-in-production" \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

### Step 6: Build Docker Images

```bash
# Build Backend API
cd todo_app/phase_5/backend
docker build -t backend-api:latest .

# Build Frontend
cd ../frontend
docker build -t frontend:latest .

# Build Notification Service
cd ../services/notification-service
docker build -t notification-service:latest .

# Build Recurring Task Service
cd ../services/recurring-task-service
docker build -t recurring-task-service:latest .

# Load images into Minikube
minikube image load backend-api:latest
minikube image load frontend:latest
minikube image load notification-service:latest
minikube image load recurring-task-service:latest
```

---

### Step 7: Deploy Dapr Components

```bash
cd todo_app/phase_5/k8s/dapr-components

# Apply Dapr components
kubectl apply -f pubsub.yaml
kubectl apply -f statestore.yaml
kubectl apply -f secrets.yaml
kubectl apply -f bindings.yaml
kubectl apply -f configuration.yaml

# Verify components
dapr components -k
```

---

### Step 8: Deploy Application with Helm

```bash
cd todo_app/phase_5/k8s/helm

# Install Helm chart
helm install todo-app ./todo-app \
  --set image.repository=local \
  --set image.tag=latest \
  --set image.pullPolicy=Never \
  --wait

# Verify deployments
kubectl get pods
```

Expected output:
```
NAME                                      READY   STATUS    RESTARTS   AGE
backend-api-xxxx                          2/2     Running   0          30s
frontend-xxxx                             2/2     Running   0          30s
notification-service-xxxx                 2/2     Running   0          30s
recurring-task-service-xxxx               2/2     Running   0          30s
```

Note: `2/2` means app container + Dapr sidecar

---

### Step 9: Access the Application

**Option A: Port Forwarding** (simplest)

```bash
# Port-forward frontend
kubectl port-forward svc/frontend 3000:3000 &

# Port-forward backend
kubectl port-forward svc/backend-api 8000:8000 &

# Access frontend
open http://localhost:3000

# Access backend API docs
open http://localhost:8000/docs
```

**Option B: Minikube Service** (uses NodePort)

```bash
# Get frontend URL
minikube service frontend --url

# Get backend URL
minikube service backend-api --url
```

---

### Step 10: Verify Functionality

**Test 1: Create Task with Recurrence**

```bash
# Get auth token (use existing Phase 2/3 user)
# Assume you have a user with email=test@example.com

curl -X POST http://localhost:8000/api/v1/users/{user_id}/tasks \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Weekly groceries",
    "priority": "high",
    "tags": ["shopping"],
    "due_at": "2026-01-05T18:00:00Z",
    "recurrence": {
      "pattern": "weekly",
      "interval": 1,
      "days_of_week": [0, 3, 5]
    },
    "reminders": [
      {"remind_before": "PT1H", "channels": ["email"]}
    ]
  }'
```

**Test 2: Complete Recurring Task**

```bash
# Complete the task
curl -X PATCH http://localhost:8000/api/v1/users/{user_id}/tasks/{task_id}/complete \
  -H "Authorization: Bearer <JWT_TOKEN>"

# Wait 5 seconds, then list tasks (should see new occurrence)
curl http://localhost:8000/api/v1/users/{user_id}/tasks \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

**Test 3: Check Kafka Events**

```bash
# Consume task-events topic
kubectl exec -it $KAFKA_POD -- kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic task-events \
  --from-beginning \
  --max-messages 10
```

Expected: See `task.created.v1` and `task.completed.v1` events

**Test 4: Check Notification Logs**

```bash
# Check notification service logs
kubectl logs -l app=notification-service -c notification-service --tail=50

# Should see: "Processed reminder.due event" (if reminder time passed)
```

---

## Part 2: Cloud Deployment (DigitalOcean DOKS)

### Prerequisites

1. **DigitalOcean Account** with billing enabled
2. **doctl CLI** installed: `brew install doctl`
3. **GitHub Container Registry** access

---

### Step 1: Create DOKS Cluster

```bash
# Authenticate
doctl auth init

# Create cluster (2 nodes, 2 vCPU, 4GB RAM each)
doctl kubernetes cluster create todo-app-cluster \
  --region nyc1 \
  --version 1.30.0-do.0 \
  --count 2 \
  --size s-2vcpu-4gb \
  --wait

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-app-cluster

# Verify connection
kubectl cluster-info
```

---

### Step 2: Install Dapr on DOKS

```bash
# Install Dapr with high availability
dapr init -k --enable-mtls=true --enable-ha=true --wait

# Verify
dapr status -k
```

---

### Step 3: Setup Redpanda Cloud (Managed Kafka)

1. Sign up at https://redpanda.com/try-redpanda
2. Create a cluster (free tier: 10GB storage, 100MB/s throughput)
3. Create topics: `task-events`, `reminders`, `notifications`
4. Download client certificates (ca.crt, tls.crt, tls.key)
5. Create Kubernetes secrets:

```bash
# Create CA certificate secret
kubectl create secret generic redpanda-ca-cert \
  --from-file=ca.crt=path/to/ca.crt

# Create client certificate secret
kubectl create secret tls redpanda-client-cert \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

---

### Step 4: Build and Push Docker Images

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Tag and push images
docker tag backend-api:latest ghcr.io/your-org/backend-api:v1.0.0
docker tag frontend:latest ghcr.io/your-org/frontend:v1.0.0
docker tag notification-service:latest ghcr.io/your-org/notification-service:v1.0.0
docker tag recurring-task-service:latest ghcr.io/your-org/recurring-task-service:v1.0.0

docker push ghcr.io/your-org/backend-api:v1.0.0
docker push ghcr.io/your-org/frontend:v1.0.0
docker push ghcr.io/your-org/notification-service:v1.0.0
docker push ghcr.io/your-org/recurring-task-service:v1.0.0
```

---

### Step 5: Deploy with Helm (Production)

```bash
cd todo_app/phase_5/k8s/helm

# Create production values file
cat > values-production.yaml <<EOF
image:
  repository: ghcr.io/your-org
  tag: v1.0.0
  pullPolicy: Always

kafka:
  external: true
  brokers: "seed-12345.cloud.redpanda.com:9092"

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: todo-app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: todo-app-tls
      hosts:
        - todo-app.example.com

resources:
  backend:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
EOF

# Deploy
helm upgrade --install todo-app ./todo-app \
  -f values-production.yaml \
  --wait
```

---

### Step 6: Setup Ingress and TLS

```bash
# Install cert-manager (for TLS certificates)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=Available --timeout=300s deployment/cert-manager -n cert-manager

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF

# Wait for certificate issuance (takes 1-2 minutes)
kubectl describe certificate todo-app-tls
```

---

### Step 7: Setup Monitoring (Prometheus + Grafana)

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --wait

# Port-forward Grafana
kubectl port-forward svc/monitoring-grafana 3001:80 &

# Get Grafana admin password
kubectl get secret monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d

# Access Grafana
open http://localhost:3001
# Login: admin / <password>
```

**Import Dapr Dashboards**:
1. Go to Dashboards → Import
2. Use dashboard ID: `19558` (Dapr Dashboard)
3. Select Prometheus data source

---

### Step 8: Setup CI/CD (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to DOKS

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push images
        run: |
          docker build -t ghcr.io/${{ github.repository }}/backend-api:${{ github.sha }} todo_app/phase_5/backend
          docker build -t ghcr.io/${{ github.repository }}/frontend:${{ github.sha }} todo_app/phase_5/frontend
          docker push ghcr.io/${{ github.repository }}/backend-api:${{ github.sha }}
          docker push ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Setup kubeconfig
        run: doctl kubernetes cluster kubeconfig save todo-app-cluster

      - name: Deploy with Helm
        run: |
          helm upgrade --install todo-app ./todo_app/phase_5/k8s/helm/todo-app \
            --set image.tag=${{ github.sha }} \
            --wait
```

---

## Part 3: Troubleshooting

### Issue: Pods not starting

```bash
# Check pod status
kubectl get pods

# Describe pod (shows events)
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name> -c <container-name>

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd
```

### Issue: Kafka connection failed

```bash
# Check Kafka pods
kubectl get pods -l app.kubernetes.io/name=kafka

# Test Kafka connectivity from backend pod
kubectl exec -it <backend-pod> -c backend-api -- \
  nc -zv kafka-0.kafka-headless.default.svc.cluster.local 9092
```

### Issue: Database connection failed

```bash
# Test PostgreSQL connectivity
kubectl run -it --rm debug --image=postgres:16 --restart=Never -- \
  psql -h <neon-host> -U <user> -d todo_db -c "SELECT 1;"
```

### Issue: Dapr component not working

```bash
# List components
dapr components -k

# Check component configuration
kubectl get component kafka-pubsub -o yaml

# Check Dapr logs
kubectl logs -n dapr-system -l app=dapr-operator
```

---

## Part 4: Performance Tuning

### Backend API Scaling

```bash
# Horizontal Pod Autoscaler
kubectl autoscale deployment backend-api --cpu-percent=70 --min=2 --max=10

# Check HPA status
kubectl get hpa
```

### Kafka Consumer Lag Monitoring

```bash
# Check consumer group lag
kubectl exec -it $KAFKA_POD -- kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --group recurring-task-service \
  --describe
```

### Database Connection Pooling

Configure in backend `config.py`:
```python
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## Part 5: Testing

### Run Unit Tests

```bash
cd todo_app/phase_5/backend
uv run pytest tests/unit/ -v
```

### Run Integration Tests

```bash
# Start testcontainers (Kafka + PostgreSQL)
uv run pytest tests/integration/ -v
```

### Run E2E Tests

```bash
# Requires running Minikube cluster
cd todo_app/phase_5/e2e
uv run pytest tests/ -v
```

---

## Next Steps

1. **Review Architecture**: Read `specs/005-event-driven-cloud/plan.md`
2. **Review Contracts**: Read `specs/005-event-driven-cloud/contracts/`
3. **Start Implementation**: Run `/sp.tasks` to generate task breakdown
4. **Deploy to Cloud**: Follow Part 2 for production deployment
5. **Monitor Performance**: Setup Grafana dashboards and alerts

---

## Additional Resources

- **Dapr Docs**: https://docs.dapr.io/
- **Kafka Docs**: https://kafka.apache.org/documentation/
- **Redpanda Cloud**: https://docs.redpanda.com/
- **Helm Docs**: https://helm.sh/docs/
- **DigitalOcean DOKS**: https://docs.digitalocean.com/products/kubernetes/
- **Prometheus**: https://prometheus.io/docs/
- **Grafana**: https://grafana.com/docs/

---

**Estimated Costs** (Production on DOKS):
- **DOKS Cluster**: $48/month (2 nodes × $24/mo)
- **Redpanda Cloud**: Free tier (10GB)
- **Neon PostgreSQL**: Free tier (3GB)
- **Total**: ~$48/month

**Scaling Costs** (with HPA at max 10 pods):
- **DOKS Cluster**: ~$240/month (10 nodes × $24/mo)
