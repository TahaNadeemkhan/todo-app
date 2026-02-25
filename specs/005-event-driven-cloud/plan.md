# Implementation Plan: Event-Driven Cloud Deployment

**Branch**: `005-event-driven-cloud` | **Date**: 2026-01-04 | **Spec**: [spec.md](./spec.md)

## Summary

Phase 5 transforms the todo application into a cloud-native, event-driven distributed system with Kafka for asynchronous communication, Dapr for portable microservices, and production Kubernetes deployment. The implementation adds advanced features (recurring tasks, reminders, priorities, tags, search/filter/sort), two new microservices (Notification Service, Recurring Task Service), and comprehensive observability with Prometheus and Grafana.

**Technical Approach**:
- **Event-Driven Architecture**: Kafka topics for task lifecycle events, reminders, and notifications
- **Microservices**: Backend API extended + 2 new services consuming/publishing events
- **Dapr Building Blocks**: Pub/Sub, State Store, Secrets, Bindings, Service Invocation
- **Containerization**: Multi-stage Dockerfiles optimized for production
- **Orchestration**: Minikube (local) → DigitalOcean DOKS (cloud)
- **Observability**: Prometheus metrics, Grafana dashboards, structured logging
- **CI/CD**: GitHub Actions for automated build, test, deploy

---

## Technical Context

**Language/Version**: Python 3.13+ (backend/microservices), Node.js 20+ (frontend)

**Primary Dependencies**:
- Backend: FastAPI 0.115+, SQLModel 0.0.22+, Alembic 1.13+, Dapr Python SDK 1.14+
- Frontend: Next.js 15+, React 19+, TypeScript 5.6+
- Kafka: Bitnami Kafka (local), Redpanda Cloud (production)
- Observability: Prometheus 2.54+, Grafana 11+, OpenTelemetry (optional)

**Storage**:
- Database: Neon Serverless PostgreSQL 16+ (existing from Phase 2/3, extended)
- State Store: PostgreSQL via Dapr (conversation/session state)
- Event Streaming: Kafka topics (task-events, reminders, notifications)

**Testing**: pytest 8.3+ (unit, integration, contract, E2E), testcontainers-python 4.9+

**Target Platform**:
- Local: Minikube v1.33+ on Linux/macOS/Windows
- Cloud: DigitalOcean DOKS 1.30+ (portable to GKE/AKS/OKE)

**Project Type**: Web application + microservices (backend, frontend, 2 event-driven services)

**Performance Goals**:
- API latency: P95 < 200ms (per SC-017)
- Task creation with events: < 5 seconds end-to-end (per SC-001)
- Notification delivery: Within 1 minute of reminder time (per SC-002)
- Concurrent users: 1000 without degradation (per SC-016)
- Kafka consumer lag: < 1000 messages under normal load

**Constraints**:
- Backward compatibility with Phase 2/3 APIs (no breaking changes)
- Idempotent event consumers (handle duplicate Kafka messages)
- Database migration safety (additive schema changes only)
- Resource limits: Backend (500m CPU, 512Mi RAM), Microservices (200m CPU, 256Mi RAM)

**Scale/Scope**:
- **Users**: 10,000 (design target)
- **Tasks**: 1M+ (with proper database indexing)
- **Events**: 100K+ per day (Kafka throughput)
- **Services**: 4 (Backend API, Frontend, Notification Service, Recurring Task Service)
- **Code**: ~15K LOC new (backend extensions, microservices, Helm charts)

---

## Constitution Check

### ✅ All Principles Compliant

**I. Spec-Driven Discipline**: ✅
- Specification created first (`spec.md`)
- Plan follows from spec (`plan.md`, `research.md`, `data-model.md`, contracts)
- Tasks will be generated from plan (`/sp.tasks`)

**II. Architectural Separation**: ✅
- **UI Layer**: Next.js frontend (existing, unchanged architecture)
- **Service Layer**: Backend API + Microservices (pure business logic)
- **Repository Layer**: SQLModel repositories (existing pattern extended)
- Dependencies flow inward (UI → Service → Repository)

**III. Domain-First Modeling**: ✅
- Strict typing: All Pydantic models use Python 3.13+ type hints
- Self-validating entities: Task, TaskRecurrence, TaskReminder, Notification models
- Enums for status: TaskStatus, Priority, RecurrencePattern, NotificationChannel

**IV. Security by Design**: ✅
- Hostile Backend: JWT verification at middleware (existing from Phase 2/3)
- Resource Ownership: User ID from JWT claims, not request body
- Secrets Management: Kubernetes Secrets via Dapr (no hardcoded credentials)
- Input Validation: Pydantic schemas for all API requests and Kafka events

**V. Deterministic AI & Tooling**: ✅
- MCP Tools: Existing from Phase 3 (ChatKit integration)
- Stateless Agents: Conversation state in Dapr State Store (PostgreSQL-backed)
- Event Schemas: JSON Schema validation for all Kafka events

**VI. Immutable Infrastructure**: ✅
- IaC: Helm charts, Dockerfiles, Kubernetes manifests versioned in Git
- No manual `kubectl` edits: All changes via Helm upgrades
- Structured Logging: JSON logs to stdout (captured by Kubernetes)

**VII. Event-Driven Decoupling**: ✅
- Eventual Consistency: Task completion → event → recurring task created asynchronously
- Dapr Abstraction: Pub/Sub component hides Kafka implementation details
- Idempotency: Event log table prevents duplicate processing

**VIII. Phased Evolution**: ✅
- Sequential: Phase 1 (CLI) → Phase 2 (Web) → Phase 3 (Chatbot) → Phase 4 (Kubernetes) → **Phase 5 (Event-Driven Cloud)**
- Iterative Refinement: Extends existing codebase (no rewrite)
- Compliance: Meets all Phase 5 hackathon requirements

**IX. Test-Driven Development (TDD)**: ✅
- Red-Green-Refactor: Will be enforced during implementation
- pytest: Unit, integration, contract, E2E tests planned
- Coverage: 80% target (per SC-026)

**X. Modern Python Tooling**: ✅
- Package Manager: `uv 0.5+` for all Python projects
- Runtime: Python 3.13+

**XI. The Nine Pillars**: ✅
1. Spec-Driven Development: ✅ This plan
2. Reusable Intelligence: ✅ Phase 5 agent skills planned
3. Cloud-Native AI: ✅ Microservices on Kubernetes
4. Event-Driven Architecture: ✅ Kafka + Dapr Pub/Sub
5. AIOps: ✅ (Phase 4 requirement, continuing in Phase 5)
6. Security by Design: ✅ JWT, mTLS, secrets management
7. Deterministic Tooling: ✅ JSON Schema validation
8. Stateless Architecture: ✅ Microservices with Dapr
9. Immutable Infrastructure: ✅ Helm + Docker

### No Violations - Proceed to Implementation

---

## Project Structure

### Documentation (this feature)

```text
specs/005-event-driven-cloud/
├── spec.md                      # ✅ Feature specification (554 lines)
├── plan.md                      # ✅ This file (implementation plan)
├── research.md                  # ✅ Phase 0 research (10 technical decisions)
├── data-model.md                # ✅ Phase 1 data model (entities, events, migrations)
├── quickstart.md                # ✅ Phase 1 setup guide (local + cloud)
├── contracts/                   # ✅ Phase 1 API contracts
│   ├── README.md
│   ├── backend-api.md           # Backend REST API (extended)
│   ├── notification-service.md   # Notification microservice contract
│   ├── recurring-task-service.md # Recurring task microservice contract
│   ├── kafka-events.md          # Event schemas and topic specs
│   └── dapr-components.md       # Dapr component configurations
├── checklists/
│   └── requirements.md          # ✅ Specification quality validation (14/14 passed)
└── tasks.md                     # ⏭️ Phase 2 (generated by /sp.tasks)
```

### Source Code (repository root)

Phase 5 extends existing Phase 2/3/4 structure with new microservices and Kubernetes manifests:

```text
todo_app/
├── phase_1/                     # Existing (console app)
├── phase_2/                     # Existing (web app)
├── phase_3/                     # Existing (AI chatbot)
├── phase_4/                     # Existing (Kubernetes with Helm)
└── phase_5/                     # NEW - Event-driven cloud deployment
    ├── backend/                 # Extended from Phase 3
    │   ├── src/
    │   │   ├── api/
    │   │   │   └── routes/
    │   │   │       ├── tasks.py           # EXTENDED: priorities, tags, due dates, recurrence
    │   │   │       ├── notifications.py   # NEW: notification history API
    │   │   │       └── reminders.py       # NEW: reminder management API
    │   │   ├── models/                    # EXTENDED: new SQLModel entities
    │   │   │   ├── task.py                # EXTENDED: priority, tags, due_at, recurrence_id
    │   │   │   ├── task_recurrence.py     # NEW
    │   │   │   ├── task_reminder.py       # NEW
    │   │   │   └── notification.py        # NEW
    │   │   ├── repositories/              # EXTENDED: new repositories
    │   │   │   ├── task_repository.py     # EXTENDED: filter by priority, tags, due date
    │   │   │   ├── recurrence_repository.py # NEW
    │   │   │   └── notification_repository.py # NEW
    │   │   ├── services/                  # EXTENDED: new business logic
    │   │   │   ├── task_service.py        # EXTENDED: create with recurrence/reminders
    │   │   │   ├── kafka_service.py       # NEW: publish events to Kafka via Dapr
    │   │   │   └── reminder_scheduler.py  # NEW: cron job to publish reminder events
    │   │   └── schemas/                   # EXTENDED: Pydantic schemas
    │   │       ├── task_schemas.py        # EXTENDED: TaskCreate with recurrence
    │   │       ├── recurrence_schemas.py  # NEW
    │   │       └── event_schemas.py       # NEW: Kafka event schemas
    │   ├── alembic/
    │   │   └── versions/
    │   │       ├── add_phase5_task_fields.py        # NEW migration
    │   │       ├── create_task_recurrences.py       # NEW migration
    │   │       ├── create_task_reminders.py         # NEW migration
    │   │       └── create_notifications.py          # NEW migration
    │   ├── tests/
    │   │   ├── unit/                      # NEW: unit tests for Phase 5 features
    │   │   ├── integration/               # NEW: Kafka integration tests
    │   │   ├── contract/                  # NEW: event schema validation tests
    │   │   └── e2e/                       # NEW: end-to-end workflows
    │   ├── Dockerfile                     # EXTENDED: multi-stage build
    │   └── pyproject.toml                 # EXTENDED: new dependencies
    │
    ├── frontend/                          # Extended from Phase 3
    │   ├── src/
    │   │   ├── app/
    │   │   │   ├── (authenticated)/
    │   │   │   │   ├── tasks/             # EXTENDED: priority filter, tags, search
    │   │   │   │   ├── today/             # EXTENDED: due date filtering
    │   │   │   │   └── notifications/     # NEW: notification history page
    │   │   │   └── api/
    │   │   ├── components/
    │   │   │   ├── task-item.tsx          # EXTENDED: show priority, tags, due date
    │   │   │   ├── add-task-dialog.tsx    # EXTENDED: recurrence, reminders UI
    │   │   │   ├── priority-badge.tsx     # NEW
    │   │   │   └── recurrence-config.tsx  # NEW
    │   │   └── lib/
    │   │       └── api.ts                 # EXTENDED: new API endpoints
    │   ├── Dockerfile                     # EXTENDED: multi-stage build
    │   └── package.json                   # EXTENDED: new dependencies
    │
    ├── services/                          # NEW: microservices
    │   ├── notification-service/
    │   │   ├── src/
    │   │   │   ├── main.py                # FastAPI + Dapr consumer
    │   │   │   ├── consumers/
    │   │   │   │   └── reminder_consumer.py
    │   │   │   ├── producers/
    │   │   │   │   └── notification_producer.py
    │   │   │   ├── handlers/
    │   │   │   │   ├── email_handler.py   # SMTP integration
    │   │   │   │   └── push_handler.py    # FCM integration
    │   │   │   ├── models/
    │   │   │   │   └── notification.py
    │   │   │   └── schemas/
    │   │   │       └── event_schemas.py
    │   │   ├── tests/
    │   │   ├── Dockerfile
    │   │   └── pyproject.toml
    │   │
    │   └── recurring-task-service/
    │       ├── src/
    │       │   ├── main.py                # FastAPI + Dapr consumer
    │       │   ├── consumers/
    │       │   │   └── task_completed_consumer.py
    │       │   ├── handlers/
    │       │   │   └── recurrence_handler.py
    │       │   ├── calculators/           # Recurrence date calculation
    │       │   │   ├── daily.py
    │       │   │   ├── weekly.py
    │       │   │   └── monthly.py
    │       │   ├── models/
    │       │   │   ├── task.py
    │       │   │   └── recurrence.py
    │       │   └── schemas/
    │       │       └── event_schemas.py
    │       ├── tests/
    │       ├── Dockerfile
    │       └── pyproject.toml
    │
    └── k8s/                               # NEW/EXTENDED: Kubernetes manifests
        ├── dapr-components/               # NEW: Dapr component YAMLs
        │   ├── pubsub.yaml                # Kafka Pub/Sub component
        │   ├── statestore.yaml            # PostgreSQL State Store component
        │   ├── secrets.yaml               # Kubernetes Secrets component
        │   ├── bindings.yaml              # Cron binding for reminders
        │   └── configuration.yaml         # Dapr global config
        │
        ├── secrets/                       # NEW: Kubernetes Secret manifests
        │   ├── postgres-credentials.yaml
        │   ├── smtp-credentials.yaml
        │   ├── fcm-credentials.yaml
        │   └── jwt-secret.yaml
        │
        └── helm/                          # EXTENDED: Helm charts
            └── todo-app/
                ├── Chart.yaml             # EXTENDED: version bump to 5.0.0
                ├── values.yaml            # EXTENDED: new services, Kafka config
                ├── values-production.yaml # NEW: production overrides
                ├── charts/                # NEW: subcharts
                │   ├── notification-service/
                │   └── recurring-task-service/
                └── templates/
                    ├── backend-deployment.yaml         # EXTENDED: Dapr annotations
                    ├── frontend-deployment.yaml        # EXTENDED: Dapr annotations
                    ├── notification-service-deployment.yaml  # NEW
                    ├── recurring-task-service-deployment.yaml # NEW
                    ├── ingress.yaml                    # EXTENDED: TLS, rate limiting
                    ├── hpa.yaml                        # EXTENDED: all services
                    ├── pdb.yaml                        # EXTENDED: all services
                    ├── servicemonitor.yaml             # NEW: Prometheus scraping
                    └── dashboards/                     # NEW: Grafana dashboards
                        ├── overview.json
                        └── kafka.json
```

**Structure Decision**: Web application architecture with microservices. Phase 5 extends existing Phase 2/3/4 codebase with:
1. **Backend Extensions**: New models, repositories, services for Phase 5 features
2. **Two New Microservices**: Notification Service + Recurring Task Service (independent deployments with Dapr)
3. **Kubernetes Manifests**: Dapr components, Helm charts, monitoring configs

---

## Complexity Tracking

No violations detected. All architectural decisions align with Constitution principles.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Cloud Platform (DOKS)                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                         Ingress (TLS)                             │  │
│  │              https://todo-app.example.com                         │  │
│  └────────────────────────┬──────────────────────────────────────────┘  │
│                           │                                              │
│         ┌─────────────────┴─────────────────┐                           │
│         │                                   │                           │
│  ┌──────▼────────┐                  ┌───────▼──────┐                    │
│  │   Frontend    │                  │ Backend API  │                    │
│  │   (Next.js)   │◄─────Dapr───────►│  (FastAPI)   │                    │
│  │               │  Service         │              │                    │
│  │  Pods: 2-10   │  Invocation      │  Pods: 2-10  │                    │
│  └───────────────┘                  └───────┬──────┘                    │
│                                             │                           │
│                                             │ Publishes Events          │
│                                             │                           │
│                        ┌────────────────────▼─────────────┐             │
│                        │   Kafka (Redpanda Cloud)         │             │
│                        │                                  │             │
│                        │  Topics:                         │             │
│                        │  - task-events (3 partitions)    │             │
│                        │  - reminders (2 partitions)      │             │
│                        │  - notifications (2 partitions)  │             │
│                        └──────┬─────────────┬─────────────┘             │
│                               │             │                           │
│                Consumes       │             │    Consumes               │
│                               │             │                           │
│             ┌─────────────────▼──┐     ┌────▼──────────────────┐        │
│             │  Notification      │     │ Recurring Task        │        │
│             │  Service           │     │ Service               │        │
│             │  (FastAPI + Dapr)  │     │ (FastAPI + Dapr)      │        │
│             │                    │     │                       │        │
│             │  Pods: 2           │     │  Pods: 1              │        │
│             └──────┬─────────────┘     └────┬──────────────────┘        │
│                    │                        │                           │
│         Sends      │                        │ Creates New Tasks         │
│         Email/Push │                        │ (via Dapr Invocation)     │
│                    │                        │                           │
│              ┌─────▼────────────────────────▼────┐                      │
│              │  Neon PostgreSQL                  │                      │
│              │  (Serverless)                     │                      │
│              │                                   │                      │
│              │  Tables:                          │                      │
│              │  - tasks (extended)               │                      │
│              │  - task_recurrences (new)         │                      │
│              │  - task_reminders (new)           │                      │
│              │  - notifications (new)            │                      │
│              │  - dapr_state (Dapr state store)  │                      │
│              └───────────────────────────────────┘                      │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                   Observability Stack                             │  │
│  │                                                                   │  │
│  │  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │  │
│  │  │  Prometheus  │──────►│   Grafana    │      │    Jaeger    │   │  │
│  │  │  (Metrics)   │      │ (Dashboards) │      │  (Tracing)   │   │  │
│  │  └──────────────┘      └──────────────┘      └──────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 0: Research ✅ COMPLETE
- ✅ Kafka vs managed Kafka (Redpanda Cloud selected)
- ✅ Dapr building blocks (all 5 defined)
- ✅ Microservices deployment strategy (separate pods)
- ✅ Event schema versioning (JSON with versions)
- ✅ Kubernetes cluster selection (DOKS primary)
- ✅ CI/CD pipeline strategy (GitHub Actions)
- ✅ Observability stack (Prometheus + Grafana)
- ✅ Database migration strategy (Alembic)
- ✅ Helm chart structure (monorepo umbrella chart)
- ✅ Testing strategy (4 levels: unit, integration, contract, E2E)

**Output**: `research.md` (10 technical decisions documented)

---

### Phase 1: Design ✅ COMPLETE
- ✅ Data model defined (4 new entities, 6 event schemas)
- ✅ API contracts specified (Backend REST, 2 microservices, Kafka, Dapr)
- ✅ Quickstart guide created (local + cloud deployment steps)

**Output**:
- `data-model.md` (entities, relationships, migrations, event schemas)
- `contracts/` directory (5 contract documents)
- `quickstart.md` (60-90 min setup guide)

---

### Phase 2: Task Generation ⏭️ NEXT
- Generate tasks.md from this plan using `/sp.tasks` command
- Break down implementation into testable, ordered tasks
- Assign priorities and dependencies
- Define acceptance criteria per task

**Output**: `tasks.md` (to be generated)

---

### Phase 3: Implementation ⏭️ FUTURE
- Follow TDD Red-Green-Refactor cycle
- Implement tasks in dependency order
- Create unit tests before implementation
- Run integration tests after each service
- Document ADRs for significant decisions

**Output**: Working Phase 5 codebase

---

### Phase 4: Deployment ⏭️ FUTURE
- Build and push Docker images to GHCR
- Deploy to Minikube for testing
- Deploy to DOKS for production
- Configure monitoring and alerts
- Run E2E tests on deployed system

**Output**: Live Phase 5 application

---

## Key Architectural Decisions

### ADR-001: Event-Driven Architecture with Kafka
**Decision**: Use Kafka for asynchronous communication between services
**Alternatives Considered**: RabbitMQ, Redis Pub/Sub, Direct HTTP calls
**Rationale**:
- Kafka provides durable, ordered, partitioned event streams
- Industry-standard for event-driven architectures at scale
- Dapr Pub/Sub component provides abstraction layer
- Redpanda Cloud offers Kafka-compatible managed service

**Trade-offs**:
- ✅ Pros: Scalable, reliable, eventually consistent
- ❌ Cons: Complexity (requires consumer idempotency, event schema management)

---

### ADR-002: Dapr for Distributed Application Building Blocks
**Decision**: Use Dapr for Pub/Sub, State, Secrets, Bindings, Service Invocation
**Alternatives Considered**: Direct Kafka client, raw Kubernetes features
**Rationale**:
- Dapr abstracts infrastructure (can swap Kafka for RabbitMQ without code changes)
- Built-in mTLS for service-to-service calls
- Simplifies microservice development (no boilerplate for common patterns)

**Trade-offs**:
- ✅ Pros: Portable, less boilerplate, built-in observability
- ❌ Cons: Additional sidecar overhead (~50MB RAM per pod)

---

### ADR-003: Separate Microservices for Event Consumers
**Decision**: Deploy Notification Service and Recurring Task Service as independent deployments
**Alternatives Considered**: Monolith with background workers (Celery)
**Rationale**:
- Independent scaling (notification spikes don't affect task creation)
- Fault isolation (recurring task service failure doesn't crash API)
- Clear ownership and observability per service

**Trade-offs**:
- ✅ Pros: Scalable, resilient, clear boundaries
- ❌ Cons: More Kubernetes manifests, higher minimum resource usage

---

### ADR-004: PostgreSQL for State Store (via Dapr)
**Decision**: Use existing Neon PostgreSQL as Dapr State Store backend
**Alternatives Considered**: Redis, Cosmos DB, DynamoDB
**Rationale**:
- Reuse existing database (no new infrastructure)
- ACID guarantees for conversation state
- Simple backup/restore with existing database

**Trade-offs**:
- ✅ Pros: Consistent, durable, no new dependencies
- ❌ Cons: Slightly higher latency than Redis (acceptable for chatbot state)

---

### ADR-005: JSON Event Schemas with Versioning
**Decision**: Use JSON with versioned event types (e.g., `task.created.v1`)
**Alternatives Considered**: Avro with Schema Registry
**Rationale**:
- Simpler for Phase 5 scope (no Schema Registry infrastructure)
- Human-readable events (easier debugging)
- JSON Schema validation provides type safety

**Trade-offs**:
- ✅ Pros: Simple, readable, no extra infrastructure
- ❌ Cons: Less strict enforcement than Avro (manual compatibility checks)

---

## Testing Strategy

### Level 1: Unit Tests (pytest)
**Scope**: Individual functions and classes in isolation

**Examples**:
- `test_calculate_next_weekly_recurrence()`
- `test_task_creation_with_invalid_due_date()`
- `test_event_schema_validation()`

**Mocks**: Kafka producer/consumer, database, external services (SMTP, FCM)

**Coverage Target**: 80% (per SC-026)

---

### Level 2: Integration Tests (pytest + testcontainers)
**Scope**: Services interacting with real dependencies

**Examples**:
- Publish `task.completed` event → Recurring Task Service consumes → creates new task
- Backend API publishes event → Kafka stores → Notification Service consumes

**Dependencies**: Kafka (testcontainers), PostgreSQL (testcontainers)

**Coverage Target**: Happy paths + critical error scenarios

---

### Level 3: Contract Tests (JSON Schema)
**Scope**: Event schema validation

**Examples**:
- Validate `task.created.v1` event against JSON Schema
- Validate Backend API request/response schemas

**Tools**: `jsonschema` library, `pytest-jsonschema`

**Coverage Target**: All event types + API endpoints

---

### Level 4: End-to-End Tests (pytest)
**Scope**: Complete workflows across all services

**Examples**:
- User creates recurring task → completes it → next occurrence appears
- Task due date approaches → reminder sent → notification delivered

**Environment**: Running Minikube cluster (or staging DOKS)

**Coverage Target**: All P1 user stories (8 critical scenarios)

---

## Deployment Strategy

### Local (Minikube)
1. **Prerequisites**: Docker Desktop, Minikube, Helm, Dapr CLI, kubectl
2. **Setup**: Start Minikube → Install Dapr → Install Kafka (Bitnami Helm)
3. **Secrets**: Create Kubernetes Secrets for DB, SMTP, FCM
4. **Build**: Multi-stage Dockerfiles → Load images to Minikube
5. **Deploy**: Helm install → Verify pods running → Port-forward services
6. **Test**: Run E2E tests, manual verification

**Estimated Time**: 60-90 minutes (per quickstart.md)

---

### Cloud (DigitalOcean DOKS)
1. **Prerequisites**: DOKS cluster, doctl CLI, GitHub Container Registry
2. **Setup**: Create DOKS cluster → Install Dapr (HA mode) → Setup Redpanda Cloud
3. **Secrets**: Create Kubernetes Secrets + Redpanda TLS certificates
4. **Build**: Docker build → Push to GHCR
5. **Deploy**: Helm install with production values → Configure Ingress + TLS
6. **Monitor**: Install Prometheus + Grafana → Import Dapr dashboards
7. **CI/CD**: GitHub Actions workflow for automated deployments

**Estimated Time**: 120-180 minutes (per quickstart.md)

---

## Monitoring and Observability

### Metrics (Prometheus)
**Exposed by all services on `/metrics` endpoint**

**Key Metrics**:
- `tasks_created_total{priority, has_recurrence}`
- `http_request_duration_seconds{method, status, quantile}`
- `kafka_messages_published_total{topic, event_type}`
- `kafka_consumer_lag{topic, group}`
- `notifications_sent_total{channel, status}`

**Alerts** (via Prometheus AlertManager):
- API error rate > 5% for 5 minutes
- Kafka consumer lag > 5000 messages
- Database connection pool exhausted

---

### Dashboards (Grafana)
**Dashboards**:
1. **Overview**: Request rate, latency, error rate, CPU/memory per service
2. **Kafka**: Producer throughput, consumer lag, partition distribution
3. **Dapr**: Service invocation success rate, Pub/Sub message flow
4. **Database**: Query latency, connection pool usage

**Import IDs**: Dapr dashboard `19558`, Kafka dashboard `7589`

---

### Tracing (Optional - OpenTelemetry + Jaeger)
**Scope**: Distributed tracing across services

**Spans**:
- HTTP request → Backend API
- Backend API → Kafka publish
- Kafka → Notification Service consumer
- Notification Service → SMTP send

**Configuration**: Dapr automatically injects trace context

---

## Security Considerations

### Authentication & Authorization
- **JWT Verification**: Backend API middleware validates JWT signature (existing from Phase 2/3)
- **Resource Ownership**: User ID extracted from JWT claims, enforced at repository layer
- **mTLS**: Dapr sidecars use mTLS for service-to-service communication (automatic)

### Secrets Management
- **Kubernetes Secrets**: Database credentials, SMTP password, FCM keys
- **Dapr Secrets Component**: Services access secrets via Dapr API (no direct K8s access)
- **No Hardcoded Secrets**: All sensitive data injected via environment variables

### Network Security
- **Ingress**: TLS/SSL certificates via cert-manager (Let's Encrypt)
- **Network Policies**: (Optional) Limit pod-to-pod communication to required services
- **RBAC**: Kubernetes Role-Based Access Control for Dapr components

### Input Validation
- **Pydantic Schemas**: All API requests validated before processing
- **JSON Schema**: All Kafka events validated before consumption
- **SQL Injection**: SQLModel ORM prevents SQL injection (parameterized queries)

---

## Performance Optimization

### Database Indexing
- `(user_id, status)` composite index (existing)
- `(user_id, due_at)` composite index (NEW - for reminder queries)
- `(user_id, priority)` composite index (NEW - for filtering)

### Kafka Partitioning
- Partition key: `user_id` (ensures per-user ordering)
- 3 partitions for `task-events` (allows 3 parallel consumers)

### Caching
- **Not required for Phase 5** (PostgreSQL query performance sufficient)
- Future enhancement: Redis cache for frequently accessed tasks

### Horizontal Pod Autoscaler (HPA)
- Backend API: 2-10 replicas based on CPU (70% threshold)
- Frontend: 2-10 replicas based on CPU
- Microservices: Fixed replicas (Notification: 2, Recurring Task: 1)

---

## Risks and Mitigation

### Risk 1: Kafka Consumer Lag
**Scenario**: High event volume → consumer can't keep up → lag increases

**Mitigation**:
- Monitor consumer lag metric (alert if > 5000 messages)
- Increase consumer replicas (for Notification Service)
- Increase Kafka partitions (for task-events topic)

---

### Risk 2: Duplicate Event Processing
**Scenario**: Kafka redelivers message → consumer processes twice → duplicate tasks created

**Mitigation**:
- Implement idempotency via event log table (`event_id` deduplication)
- Enforce in tests: Publish duplicate event → assert no duplicate side effects

---

### Risk 3: Database Migration Failure
**Scenario**: Alembic migration fails → rollback required → potential data loss

**Mitigation**:
- Test migrations on staging environment first
- Use additive migrations only (no column drops)
- Implement rollback in migration `downgrade()` method

---

### Risk 4: SMTP/FCM Service Unavailable
**Scenario**: External notification service down → reminders not sent

**Mitigation**:
- Store failed notifications in database with `status=failed`
- Implement retry logic with exponential backoff
- Alert on high failure rate (> 10%)

---

## Next Steps

1. ✅ **Phase 0 Research**: Complete (research.md)
2. ✅ **Phase 1 Design**: Complete (data-model.md, contracts/, quickstart.md)
3. ⏭️ **Phase 2 Task Generation**: Run `/sp.tasks` to break down implementation
4. ⏭️ **Phase 3 Implementation**: Follow TDD cycle, implement tasks
5. ⏭️ **Phase 4 Deployment**: Deploy to Minikube, then DOKS
6. ⏭️ **Phase 5 Monitoring**: Setup Grafana dashboards, configure alerts
7. ⏭️ **Documentation**: Update README, create ADRs, record PHR

---

## References

- **Specification**: [spec.md](./spec.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Quickstart**: [quickstart.md](./quickstart.md)
- **Contracts**: [contracts/](./contracts/)
- **Constitution**: [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md)

---

**Plan Status**: ✅ COMPLETE - Ready for `/sp.tasks`
**Created**: 2026-01-04
**Last Updated**: 2026-01-04
