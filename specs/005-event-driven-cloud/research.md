# Phase 0 Research: Event-Driven Cloud Deployment

**Feature**: 005-event-driven-cloud
**Created**: 2026-01-04
**Status**: Complete

## Purpose

This document captures the technical research and resolution of unknowns identified during the planning phase for Phase 5: Event-Driven Cloud Deployment.

## Research Questions & Resolutions

### 1. Kafka vs Managed Kafka Services

**Question**: Should we use self-hosted Kafka (local) vs managed Kafka services (Confluent Cloud, Redpanda Cloud) for production?

**Research Findings**:
- **Local (Minikube)**: Kafka in KRaft mode (Zookeeper-free) is production-ready since Kafka 3.3+
  - Simpler deployment for local development
  - No external dependencies
  - Resource requirements: ~1GB RAM minimum per broker
- **Cloud (Production)**: Managed services recommended for production
  - **Confluent Cloud**: Industry leader, full Kafka ecosystem, higher cost
  - **Redpanda Cloud**: Kafka-compatible, higher performance, lower cost, simpler ops
  - **Recommendation**: Redpanda Cloud for better performance/cost ratio

**Decision**:
- Local: Kafka in KRaft mode via Bitnami Helm chart
- Production: Redpanda Cloud (Kafka-compatible API)

**References**:
- Kafka KRaft: https://kafka.apache.org/documentation/#kraft
- Redpanda Cloud: https://redpanda.com/redpanda-cloud

---

### 2. Dapr Building Blocks Selection

**Question**: Which Dapr building blocks are required for Phase 5, and how should they be configured?

**Research Findings**:
Dapr provides 10+ building blocks. For Phase 5, we need:

1. **Pub/Sub** (REQUIRED - Priority 1)
   - Component: `pubsub.kafka` or `pubsub.redpanda`
   - Purpose: Abstract Kafka for event streaming
   - Configuration: Topic creation, partition strategy, consumer groups

2. **State Management** (REQUIRED - Priority 1)
   - Component: `state.postgresql`
   - Purpose: Conversation/session state for chatbot
   - Configuration: Connection string, table prefix, TTL for sessions

3. **Secrets** (REQUIRED - Priority 1)
   - Component: `secretstores.kubernetes.secrets`
   - Purpose: Database credentials, Kafka credentials, API keys
   - Configuration: Namespace scoping, secret references

4. **Bindings** (REQUIRED - Priority 2)
   - Component: `bindings.cron`
   - Purpose: Scheduled reminder checks (alternative to Jobs API)
   - Configuration: Cron expressions for reminder intervals

5. **Service Invocation** (REQUIRED - Priority 2)
   - Built-in mTLS
   - Purpose: Frontend-to-backend, microservice-to-microservice calls
   - Configuration: App IDs, namespaces, retries, circuit breakers

**Decision**: All 5 building blocks will be implemented with Helm-based component YAML files.

**References**:
- Dapr Docs: https://docs.dapr.io/developing-applications/building-blocks/

---

### 3. Microservices Deployment Strategy

**Question**: Should microservices run as separate deployments or combined with main backend?

**Research Findings**:
- **Separate Deployments** (Recommended):
  - Independent scaling (e.g., scale Notification Service separately)
  - Fault isolation (Recurring Task Service failure doesn't crash API)
  - Clear ownership and observability
  - Cons: More Kubernetes manifests, higher minimum resource usage

- **Monolith with Workers** (Alternative):
  - Single deployment with Celery/RQ workers
  - Simpler initial setup
  - Cons: Violates microservices pattern, harder to scale independently

**Decision**: Separate deployments for:
1. **Backend API** (main FastAPI app)
2. **Notification Service** (consumer: reminders → notifications)
3. **Recurring Task Service** (consumer: task.completed → task.created)

Each service runs in its own pod with Dapr sidecar.

---

### 4. Event Schema Versioning

**Question**: How should we handle Kafka event schema evolution?

**Research Findings**:
- **Avro with Schema Registry** (Industry Standard):
  - Strong typing, backward/forward compatibility
  - Requires Confluent Schema Registry
  - Adds complexity

- **JSON with Versioned Events** (Simpler):
  - Include `schema_version` field in each event
  - Use event type naming: `task.created.v1`, `task.created.v2`
  - Consumers check version and handle accordingly
  - Pros: Simpler, human-readable, no extra infrastructure
  - Cons: Less enforcement, manual compatibility checks

**Decision**: JSON with versioned events for Phase 5 simplicity. Migrate to Avro if/when schema complexity increases.

**Event Structure**:
```json
{
  "event_id": "uuid",
  "event_type": "task.created.v1",
  "schema_version": "1.0",
  "timestamp": "ISO8601",
  "data": { ... }
}
```

---

### 5. Kubernetes Cluster Selection

**Question**: Which managed Kubernetes service should we target for cloud deployment?

**Research Findings**:
- **Google GKE**:
  - Pros: Autopilot mode (managed nodes), best integration with Google Cloud services
  - Cons: More expensive, vendor lock-in

- **Azure AKS**:
  - Pros: Good integration with Azure services, competitive pricing
  - Cons: Regional availability varies

- **Oracle OKE**:
  - Pros: Lowest cost, good for hackathon/demo
  - Cons: Smaller ecosystem, fewer managed add-ons

- **DigitalOcean DOKS**:
  - Pros: Simplest setup, lowest cost, flat pricing
  - Cons: Limited to specific regions, fewer enterprise features

**Decision**: Primary target: **DigitalOcean DOKS** for cost and simplicity. Helm charts will be portable to GKE/AKS/OKE with minimal changes.

---

### 6. CI/CD Pipeline Strategy

**Question**: What should the GitHub Actions workflow automate?

**Research Findings**:
Best practices for Kubernetes CI/CD:

1. **Build Phase**:
   - Run tests (pytest, Next.js tests)
   - Build Docker images (multi-stage)
   - Push to registry (Docker Hub, GHCR, or cloud registry)
   - Tag with git commit SHA and `latest`

2. **Deploy Phase**:
   - Helm lint and template validation
   - Deploy to staging (auto)
   - Deploy to production (manual approval gate)
   - Health checks and rollback on failure

3. **Triggers**:
   - Push to `main`: Deploy to staging
   - Manual dispatch: Deploy to production
   - PR: Run tests only

**Decision**: Implement 2-stage pipeline (test → build → deploy) with manual production gate.

---

### 7. Observability Stack

**Question**: How should we implement monitoring, metrics, and tracing for Phase 5?

**Research Findings**:
- **Prometheus + Grafana** (Industry Standard):
  - Prometheus: Metrics scraping from `/metrics` endpoints
  - Grafana: Dashboards for visualization
  - AlertManager: Alert rules and notifications

- **OpenTelemetry + Jaeger** (Distributed Tracing):
  - OpenTelemetry SDK for Python (FastAPI) and Node.js (Next.js)
  - Jaeger for trace collection and visualization
  - Correlate requests across microservices

- **Structured Logging**:
  - Python: `structlog` for JSON logs
  - Forward logs to stdout (captured by Kubernetes)
  - Optional: Loki for centralized log aggregation

**Decision**:
- **Metrics**: Prometheus + Grafana (required for SC-024, SC-025)
- **Tracing**: OpenTelemetry + Jaeger (optional nice-to-have)
- **Logging**: Structured JSON logs to stdout (captured by `kubectl logs`)

**Metrics to Expose**:
- API: Request rate, latency (p50/p95/p99), error rate
- Kafka: Message publish rate, consumer lag, processing time
- Dapr: Service invocation success/failure, state store latency

---

### 8. Database Migration Strategy for New Tables

**Question**: How should we add new database tables (reminders, recurring patterns, notifications) without breaking existing Phase 2/3 deployments?

**Research Findings**:
- **Alembic Migrations** (Already in use):
  - Create new migration: `alembic revision --autogenerate -m "add_recurring_reminders"`
  - Alembic generates DDL for new tables
  - Run `alembic upgrade head` during deployment

- **Backward Compatibility**:
  - New tables are additive (don't modify existing `tasks`, `conversations`, `messages`)
  - Phase 5 code checks for table existence before querying (defensive)

- **Rollback Safety**:
  - Each migration includes `downgrade()` method
  - Test rollback: `alembic downgrade -1`

**Decision**: Use Alembic for all schema changes. Create migrations for:
1. `task_recurrence` table (recurrence pattern, next_due_at)
2. `task_reminders` table (reminder config per task)
3. `notifications` table (notification log with status)

---

### 9. Helm Chart Structure

**Question**: Should we use a monorepo Helm chart or separate charts per service?

**Research Findings**:
- **Monorepo (Umbrella Chart)** (Recommended for Phase 5):
  - Single `helm install todo-app ./helm/todo-app`
  - Subcharts for: backend, frontend, notification-service, recurring-task-service, postgres, kafka (optional)
  - Pros: Single deployment command, shared values, easier version coordination
  - Cons: Larger chart, all-or-nothing upgrades

- **Separate Charts** (Better for production at scale):
  - One chart per microservice
  - Independent versioning and deployment
  - Pros: Granular updates, clearer ownership
  - Cons: More complex initial setup, requires dependency management

**Decision**: Monorepo umbrella chart for Phase 5 simplicity. Structure:
```
helm/todo-app/
├── Chart.yaml
├── values.yaml
├── charts/
│   ├── backend/
│   ├── frontend/
│   ├── notification-service/
│   └── recurring-task-service/
└── templates/
    ├── configmap.yaml
    ├── secret.yaml
    ├── ingress.yaml
    └── dapr-components/
```

---

### 10. Testing Strategy for Event-Driven Architecture

**Question**: How should we test Kafka producers, consumers, and event handlers?

**Research Findings**:
- **Unit Tests** (Service Layer):
  - Mock Kafka producer/consumer
  - Test event serialization/deserialization
  - Test business logic in event handlers

- **Integration Tests** (Kafka + Services):
  - Use `testcontainers-python` for ephemeral Kafka
  - Publish test event → consume → assert side effects
  - Test idempotency (publish same event twice)

- **Contract Tests** (Event Schemas):
  - Define JSON schemas for each event type
  - Validate events against schema before publish
  - Consumers validate events on receive

- **End-to-End Tests** (Full Flow):
  - Create task → assert `task.created` event published
  - Complete recurring task → assert next occurrence created
  - Trigger reminder → assert notification sent

**Decision**: Implement all 4 levels:
1. Unit: pytest for event handlers (mock Kafka)
2. Integration: testcontainers for Kafka tests
3. Contract: JSON Schema validation
4. E2E: pytest fixtures for full workflows

**Test Coverage Target**: 80% (per SC-026)

---

## Technology Stack Summary

Based on research, the confirmed technology stack for Phase 5:

### Core Application
- **Backend**: Python 3.13+, FastAPI 0.115+, SQLModel 0.0.22+, Pydantic 2.9+
- **Frontend**: Next.js 15+, React 19+, TypeScript 5.6+
- **Database**: Neon Serverless PostgreSQL 16+
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Migrations**: Alembic 1.13+

### Event-Driven Architecture
- **Local Kafka**: Bitnami Kafka Helm chart (KRaft mode)
- **Production Kafka**: Redpanda Cloud (Kafka-compatible)
- **Event Schema**: JSON with versioned event types
- **Dapr**: v1.14+ (Pub/Sub, State, Secrets, Bindings, Service Invocation)

### Microservices
1. **Backend API** (existing, extended)
2. **Notification Service** (new - Python 3.13+, FastAPI, Dapr)
3. **Recurring Task Service** (new - Python 3.13+, FastAPI, Dapr)

### Containerization & Orchestration
- **Docker**: Multi-stage builds (node:20-alpine, python:3.13-slim)
- **Local K8s**: Minikube v1.33+ with Dapr
- **Cloud K8s**: DigitalOcean DOKS (primary), portable to GKE/AKS/OKE
- **Package Manager**: Helm 3.15+

### CI/CD
- **Platform**: GitHub Actions
- **Stages**: Test → Build → Push → Deploy (staging/production)
- **Registry**: GitHub Container Registry (ghcr.io)
- **Deployment**: Helm upgrade with health checks

### Observability
- **Metrics**: Prometheus 2.54+ (scraping), Grafana 11+ (dashboards)
- **Tracing**: OpenTelemetry + Jaeger (optional)
- **Logging**: Structured JSON (structlog) → stdout → kubectl logs
- **Alerts**: Prometheus AlertManager (critical: API errors, consumer lag)

### Development Tools
- **Package Manager**: uv 0.5+ (Python dependency management)
- **Testing**: pytest 8.3+, pytest-asyncio, testcontainers-python
- **Linting**: ruff 0.7+ (Python), eslint 9+ (TypeScript)
- **Type Checking**: mypy 1.13+ (Python), TypeScript compiler

---

## Assumptions Validated

1. ✅ **Existing codebase**: Phases 1-4 are complete and functional
2. ✅ **Database schema**: Can be extended with Alembic migrations
3. ✅ **Neon PostgreSQL**: Supports required connection pooling and extensions
4. ✅ **Dapr compatibility**: Works with existing FastAPI and Next.js stack
5. ✅ **Kafka topics**: Can be created programmatically or via Dapr component YAML
6. ✅ **Kubernetes resources**: Minikube and DOKS provide sufficient resources for demo

---

## Open Questions (if any)

None at this time. All critical technical decisions have been researched and documented.

---

## Next Steps

- ✅ Phase 0 Research: Complete
- ⏭️ Phase 1 Design: Create data-model.md, contracts/, quickstart.md
- ⏭️ Phase 2 Tasks: Generate tasks.md from this plan
