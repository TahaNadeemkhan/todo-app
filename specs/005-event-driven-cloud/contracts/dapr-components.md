# Dapr Components Configuration

**Feature**: 005-event-driven-cloud
**Created**: 2026-01-04

## Overview

This document specifies the Dapr component configurations for Phase 5. Dapr components are deployed as Kubernetes CRDs and provide building blocks for distributed application development.

## Component 1: Pub/Sub (Kafka)

**File**: `k8s/dapr-components/pubsub.yaml`

**Purpose**: Abstract Kafka for event pub/sub across services

**Type**: `pubsub.kafka`

**Local (Minikube) Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Kafka broker addresses (Bitnami Kafka Helm release)
    - name: brokers
      value: "kafka-0.kafka-headless.default.svc.cluster.local:9092"
    - name: authType
      value: "none"  # No auth for local Kafka
    - name: maxMessageBytes
      value: "1048576"  # 1MB max message size
    - name: consumerID
      value: "{APP_ID}"  # Dapr automatically replaces with app-id
```

**Production (Redpanda Cloud) Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "seed-12345.cloud.redpanda.com:9092"
    - name: authType
      value: "certificate"
    - name: caCert
      secretKeyRef:
        name: redpanda-ca-cert
        key: ca.crt
    - name: clientCert
      secretKeyRef:
        name: redpanda-client-cert
        key: tls.crt
    - name: clientKey
      secretKeyRef:
        name: redpanda-client-cert
        key: tls.key
    - name: maxMessageBytes
      value: "1048576"
```

**Scopes**: All services (backend-api, notification-service, recurring-task-service)

---

## Component 2: State Store (PostgreSQL)

**File**: `k8s/dapr-components/statestore.yaml`

**Purpose**: Store chatbot conversation state (Phase 3 requirement extended to Phase 5)

**Type**: `state.postgresql`

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-credentials
        key: connectionString
    - name: tableName
      value: "dapr_state"
    - name: metadataTableName
      value: "dapr_metadata"
    - name: keyPrefix
      value: "app"
    - name: timeoutInSeconds
      value: "30"
    - name: maxIdleTimeoutInSeconds
      value: "300"
```

**Secret** (`postgres-credentials`):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-credentials
  namespace: default
type: Opaque
stringData:
  connectionString: "host=neon-db-host port=5432 user=app_user dbname=todo_db password=<PASSWORD> sslmode=require"
```

**Database Tables** (automatically created by Dapr):
```sql
CREATE TABLE dapr_state (
  key VARCHAR(255) PRIMARY KEY,
  value JSONB NOT NULL,
  isbinary BOOLEAN NOT NULL,
  insertdate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updatedate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dapr_metadata (
  key VARCHAR(255) PRIMARY KEY,
  value TEXT NOT NULL
);
```

**Scopes**: backend-api (for chatbot conversation state)

---

## Component 3: Secrets (Kubernetes Secrets)

**File**: `k8s/dapr-components/secrets.yaml`

**Purpose**: Provide secure access to secrets without hardcoding in code

**Type**: `secretstores.kubernetes`

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
    - name: vaultKubeMountPath
      value: "kubernetes"
    - name: defaultNamespace
      value: "default"
```

**Scopes**: All services

**Secrets Managed**:
1. **PostgreSQL Connection String** (`postgres-credentials`)
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: postgres-credentials
   type: Opaque
   stringData:
     connectionString: "postgres://user:password@host:5432/todo_db"
   ```

2. **SMTP Credentials** (`smtp-credentials`)
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: smtp-credentials
   type: Opaque
   stringData:
     SMTP_HOST: "smtp.gmail.com"
     SMTP_PORT: "587"
     SMTP_USERNAME: "app@example.com"
     SMTP_PASSWORD: "<PASSWORD>"
     SMTP_FROM_EMAIL: "noreply@todo-app.example.com"
   ```

3. **Firebase Cloud Messaging Credentials** (`fcm-credentials`)
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: fcm-credentials
   type: Opaque
   stringData:
     FCM_SERVER_KEY: "<SERVER_KEY>"
     FCM_PROJECT_ID: "<PROJECT_ID>"
   ```

4. **JWT Secret** (`jwt-secret`)
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: jwt-secret
   type: Opaque
   stringData:
     JWT_SECRET: "<SECRET>"
   ```

5. **Redpanda Cloud Certificates** (production only)
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: redpanda-ca-cert
   type: Opaque
   data:
     ca.crt: <base64-encoded-cert>
   ---
   apiVersion: v1
   kind: Secret
   metadata:
     name: redpanda-client-cert
   type: kubernetes.io/tls
   data:
     tls.crt: <base64-encoded-cert>
     tls.key: <base64-encoded-key>
   ```

**Usage in Code**:
```python
from dapr.clients import DaprClient

with DaprClient() as client:
    secret = client.get_secret(
        store_name="kubernetes-secrets",
        key="smtp-credentials",
        metadata={"namespace": "default"}
    )
    smtp_password = secret.secret["SMTP_PASSWORD"]
```

---

## Component 4: Bindings (Cron for Reminder Scheduler)

**File**: `k8s/dapr-components/bindings.yaml`

**Purpose**: Trigger reminder scheduler job every minute to check for due reminders

**Type**: `bindings.cron`

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-scheduler
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/1 * * * *"  # Every 1 minute
    - name: direction
      value: "input"  # Only input (trigger), not output
```

**Scopes**: backend-api

**Handler Endpoint** (Backend API):
```python
from fastapi import FastAPI, Request
from dapr.ext.fastapi import DaprActor

app = FastAPI()

@app.post("/cron/reminder-scheduler")
async def reminder_scheduler_handler(request: Request):
    """Triggered every minute by Dapr Cron binding."""
    # Find tasks with unsent reminders due within next minute
    tasks = find_tasks_needing_reminders(db, now=datetime.utcnow())

    for task in tasks:
        for reminder in task.reminders:
            if not reminder.sent_at:
                # Publish reminder.due event to Kafka
                await publish_reminder_due_event(task, reminder)
                # Mark reminder as sent
                reminder.sent_at = datetime.utcnow()
                db.commit()

    return {"status": "ok", "reminders_sent": len(tasks)}
```

**Alternative**: Dapr Jobs API (alpha feature in Dapr 1.14+)
- More flexible than Cron bindings
- Supports distributed job scheduling
- Requires Dapr 1.14+ with Jobs API enabled

---

## Component 5: Service Invocation (Built-in)

**Purpose**: Secure mTLS-enabled service-to-service communication

**Type**: Built-in Dapr feature (no component YAML needed)

**Configuration** (Per-Service):

Each service deployment must have Dapr annotations:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-api"
        dapr.io/app-port: "8000"
        dapr.io/app-protocol: "http"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9090"
        dapr.io/log-level: "info"
    spec:
      containers:
        - name: backend-api
          image: ghcr.io/your-org/backend-api:latest
          ports:
            - containerPort: 8000
```

**Service IDs**:
- `backend-api` (Backend API)
- `notification-service` (Notification Service)
- `recurring-task-service` (Recurring Task Service)

**mTLS Configuration** (automatic):
- Dapr automatically enables mTLS between services
- Certificates managed by Dapr Sentry service
- No manual certificate management needed

**Usage**:

**Python (DaprClient)**:
```python
from dapr.clients import DaprClient

with DaprClient() as client:
    response = client.invoke_method(
        app_id="backend-api",
        method_name="/api/v1/users/123/tasks",
        http_verb="POST",
        data=json.dumps({"title": "New task"}),
        headers={"Content-Type": "application/json"}
    )
```

**curl (via Dapr sidecar)**:
```bash
curl http://localhost:3500/v1.0/invoke/backend-api/method/api/v1/users/123/tasks \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"title": "New task"}'
```

**Retry Policy** (default):
- Max retries: 3
- Backoff: Exponential (1s, 2s, 4s)
- Timeout: 60s

**Circuit Breaker** (optional - requires Resiliency configuration):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: backend-api-resiliency
spec:
  policies:
    circuitBreakers:
      backend-api-cb:
        maxRequests: 5
        interval: 5s
        timeout: 60s
        trip: consecutiveFailures > 3
  targets:
    apps:
      backend-api:
        circuitBreaker: backend-api-cb
```

---

## Dapr Configuration (Global)

**File**: `k8s/dapr-components/configuration.yaml`

**Purpose**: Global Dapr runtime configuration

**Configuration**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: daprconfig
  namespace: default
spec:
  # Tracing (OpenTelemetry)
  tracing:
    samplingRate: "1"  # 100% sampling in dev, 10% in prod
    otel:
      endpointAddress: "jaeger-collector.default.svc.cluster.local:4317"
      isSecure: false
      protocol: grpc

  # Metrics (Prometheus)
  metric:
    enabled: true

  # mTLS
  mtls:
    enabled: true
    workloadCertTTL: "24h"
    allowedClockSkew: "15m"

  # Access Control (allow all for now)
  accessControl:
    defaultAction: allow
    trustDomain: "public"

  # API Logging
  api:
    logging:
      enabled: true
      obfuscateURLs: false

  # Secrets
  secrets:
    scopes:
      - storeName: kubernetes-secrets
        defaultAccess: allow
```

---

## Deployment Order

When deploying Dapr components, follow this order:

1. **Install Dapr** on Kubernetes cluster:
   ```bash
   dapr init -k --enable-mtls=true --enable-ha=false
   ```

2. **Deploy Secrets** (Kubernetes Secrets):
   ```bash
   kubectl apply -f k8s/secrets/
   ```

3. **Deploy Dapr Components**:
   ```bash
   kubectl apply -f k8s/dapr-components/
   ```

4. **Deploy Application Services**:
   ```bash
   helm install todo-app ./helm/todo-app
   ```

5. **Verify Dapr Components**:
   ```bash
   dapr components -k
   ```

   Expected output:
   ```
   NAMESPACE  NAME                  TYPE                         VERSION  SCOPES
   default    kafka-pubsub          pubsub.kafka                 v1       backend-api, notification-service, recurring-task-service
   default    statestore            state.postgresql             v1       backend-api
   default    kubernetes-secrets    secretstores.kubernetes      v1       backend-api, notification-service, recurring-task-service
   default    reminder-scheduler    bindings.cron                v1       backend-api
   ```

---

## Testing Dapr Components

### Test Pub/Sub

**Publish Test Event**:
```bash
dapr publish --publish-app-id backend-api --pubsub kafka-pubsub --topic task-events --data '{"event_id":"test","event_type":"task.created.v1","schema_version":"1.0","timestamp":"2026-01-04T12:00:00Z","data":{"task_id":"test","user_id":"test","title":"Test"}}'
```

**Subscribe and Consume**:
```bash
dapr run --app-id test-consumer --dapr-http-port 3500 -- python -m http.server 8080
curl http://localhost:3500/v1.0/subscribe
```

### Test State Store

**Set State**:
```bash
dapr invoke --app-id backend-api --method /v1.0/state/statestore --verb POST --data '[{"key":"test-key","value":"test-value"}]'
```

**Get State**:
```bash
dapr invoke --app-id backend-api --method /v1.0/state/statestore/test-key --verb GET
```

### Test Secrets

**Get Secret**:
```bash
dapr invoke --app-id backend-api --method /v1.0/secrets/kubernetes-secrets/smtp-credentials --verb GET
```

### Test Service Invocation

**Invoke Backend API**:
```bash
dapr invoke --app-id backend-api --method /health --verb GET
```

---

## Monitoring Dapr

**Dapr Dashboard**:
```bash
dapr dashboard -k
```

Access at: `http://localhost:8080`

**Prometheus Metrics**:
- Dapr sidecars expose metrics on port `9090`
- Prometheus scrapes: `http://pod-ip:9090/metrics`

**Key Metrics**:
- `dapr_http_server_request_count` (HTTP requests per service)
- `dapr_grpc_io_server_completed_rpcs` (gRPC calls)
- `dapr_component_pubsub_ingress_count` (Pub/Sub messages received)
- `dapr_component_pubsub_egress_count` (Pub/Sub messages published)
- `dapr_runtime_service_invocation_req_sent_total` (Service invocation calls)

---

## Security Considerations

1. **mTLS**: Always enabled in production for service-to-service communication
2. **Secrets**: Never commit secrets to Git; use Kubernetes Secrets or External Secrets Operator
3. **RBAC**: Restrict Dapr component access using Kubernetes RBAC and Dapr scopes
4. **Network Policies**: Limit pod-to-pod communication to only required services
5. **Certificate Rotation**: Dapr Sentry automatically rotates certificates every 24h
