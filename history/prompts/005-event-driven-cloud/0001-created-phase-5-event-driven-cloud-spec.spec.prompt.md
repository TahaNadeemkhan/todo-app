---
id: 0001
title: Created Phase 5 Event-Driven Cloud Spec
stage: spec
date: 2026-01-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: 005-event-driven-cloud
branch: 005-event-driven-cloud
user: TahaNadeemKhan
command: /sp.specify
labels: ["phase-5", "event-driven-architecture", "kafka", "dapr", "microservices", "kubernetes", "cloud-deployment", "specification"]
links:
  spec: specs/005-event-driven-cloud/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-event-driven-cloud/spec.md
  - specs/005-event-driven-cloud/checklists/requirements.md
tests:
  - none
---

## Prompt

Phase 5: Advanced Cloud Deployment with Event-Driven Architecture

## Overview
Phase 5 extends the todo application with advanced features, event-driven architecture using Kafka, distributed runtime with Dapr, and production Kubernetes deployment on cloud platforms (GKE/AKS/OKE).

## Part A: Advanced Features

### Recurring Tasks
- Users can create tasks that repeat on a schedule (daily, weekly, monthly)
- When a recurring task is completed, automatically create the next occurrence
- Support recurrence patterns: daily, weekly (specific days), monthly (specific date)
- Track recurrence chain and allow stopping recurrence

### Due Dates & Reminders
- Users can set due dates and times for tasks
- System sends reminders before tasks are due (configurable: 1 hour, 1 day, 1 week before)
- Support multiple reminder channels: email, push notifications
- Mark reminders as sent/failed with delivery status

### Intermediate Features
- **Priorities**: High, Medium, Low priority levels
- **Tags**: Multi-tag support for categorization
- **Search**: Full-text search across task titles and descriptions
- **Filter**: Filter by priority, tags, due date, completion status
- **Sort**: Sort by due date, priority, created date, alphabetical

### Event-Driven Architecture
- Implement Kafka topics for task events, reminders, notifications
- Publish events for all task CRUD operations
- Build microservices that consume and publish events
- Ensure event idempotency and reliable delivery

### Dapr Integration
- Use Dapr Pub/Sub for Kafka abstraction
- Use Dapr State Store for conversation/session state
- Use Dapr Secrets for configuration management
- Use Dapr Jobs API or Bindings for scheduled reminders
- Use Dapr Service Invocation for frontend-backend communication

## Part B: Local Deployment (Minikube)

### Minikube Setup
- Deploy complete application to Minikube
- Run Kafka locally (KRaft mode or with Zookeeper)
- Install Dapr on Minikube with all components

### Full Dapr Components
1. **Pub/Sub**: kafka-pubsub component for event streaming
2. **State Management**: PostgreSQL state store
3. **Bindings**: Cron binding for reminder scheduler
4. **Secrets**: Kubernetes secrets component
5. **Service Invocation**: mTLS-enabled service-to-service calls

### Docker Images
- Multi-stage Dockerfiles for frontend (Next.js) and backend (FastAPI)
- Optimize image size with layer caching
- Non-root containers with security best practices
- Health check endpoints

### Helm Charts
- Create Helm chart for local deployment
- ConfigMaps for environment-specific configuration
- Secrets management for sensitive data
- Service definitions and pod specifications

## Part C: Cloud Deployment (GKE/AKS/OKE)

### Cloud Kubernetes
- Deploy to one of: Google GKE, Azure AKS, Oracle OKE
- Configure Ingress with TLS/SSL certificates
- Set up Horizontal Pod Autoscaler (HPA)
- Configure Pod Disruption Budgets (PDB)

### Managed Kafka
- Use Confluent Cloud or Redpanda Cloud
- Configure Dapr to connect to managed Kafka
- Set up topics with proper retention policies
- Configure partitioning for scalability

### CI/CD Pipeline
- GitHub Actions workflow for build, test, deploy
- Automated Docker image builds and registry push
- Helm-based deployment automation
- Deployment approval gates for production

### Monitoring & Logging
- Prometheus metrics collection
- Grafana dashboards for visualization
- Alert rules for critical issues
- Distributed tracing with OpenTelemetry/Jaeger
- Centralized logging

## Microservices Architecture

### Notification Service
- **Purpose**: Send email and push notifications for reminders
- **Consumes**: `reminders` topic (event: `reminder.due`)
- **Produces**: `notifications` topic (events: `notification.sent`, `notification.failed`)
- **Database**: Notification log table
- **External Services**: SMTP server, Firebase Cloud Messaging
- **Deployment**: Separate pod with Dapr sidecar

### Recurring Task Service
- **Purpose**: Generate next task occurrence when recurring task is completed
- **Consumes**: `task-events` topic (event: `task.completed` with has_recurrence=true)
- **Produces**: `task-events` topic (event: `task.created`)
- **Business Logic**: Parse recurrence pattern, calculate next due date, clone task
- **Deployment**: Separate pod with Dapr sidecar

### Backend API (Extended)
- **Purpose**: Main CRUD API for tasks
- **Publishes to**: `task-events` topic for all CRUD operations
- **Consumes from**: `task-updates` topic for real-time sync
- **Database**: PostgreSQL with SQLModel ORM
- **Endpoints**: /api/v1/tasks, /api/v1/reminders, /api/v1/notifications

## Kafka Event Schemas

### task.created
```json
{
  "event_id": "uuid",
  "event_type": "task.created",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string",
  "due_at": "ISO8601",
  "priority": "high|medium|low",
  "tags": ["string"],
  "has_recurrence": "boolean",
  "recurrence_pattern": "daily|weekly|monthly",
  "created_at": "ISO8601"
}
```

### task.completed
```json
{
  "event_id": "uuid",
  "event_type": "task.completed",
  "task_id": "uuid",
  "user_id": "uuid",
  "completed_at": "ISO8601",
  "has_recurrence": "boolean",
  "recurrence_pattern": "daily|weekly|monthly"
}
```

### reminder.due
```json
{
  "event_id": "uuid",
  "event_type": "reminder.due",
  "task_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "due_at": "ISO8601",
  "reminder_channels": ["email", "push"]
}
```

### notification.sent / notification.failed
```json
{
  "event_id": "uuid",
  "event_type": "notification.sent|notification.failed",
  "notification_id": "int",
  "user_id": "uuid",
  "channel": "email|push",
  "message": "string",
  "sent_at": "ISO8601",
  "error": "string (if failed)"
}
```

## Technology Stack
- **Backend**: Python 3.13+, FastAPI, SQLModel, Alembic
- **Frontend**: Next.js 15+, TypeScript 5+, React
- **Database**: Neon Serverless PostgreSQL
- **Event Streaming**: Kafka (local) / Confluent Cloud or Redpanda Cloud (production)
- **Distributed Runtime**: Dapr
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes (Minikube local, GKE/AKS/OKE cloud)
- **Package Management**: Helm
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana, OpenTelemetry
- **Secret Management**: Kubernetes Secrets + External Secrets Operator

## Success Criteria
- All advanced features (recurring tasks, reminders, priorities, tags, search, filter, sort) are fully functional
- Event-driven architecture with Kafka is implemented and tested
- All 5 Dapr building blocks are integrated and working
- Notification Service and Recurring Task Service are deployed and processing events
- Application successfully deploys to Minikube with all components
- Application successfully deploys to cloud Kubernetes (GKE/AKS/OKE)
- CI/CD pipeline automates build, test, and deploy
- Monitoring dashboards show metrics and alerts are configured
- All microservices are containerized with optimized Docker images
- TDD approach with comprehensive unit and integration tests
- Documentation includes setup, deployment, and troubleshooting guides

## Acceptance Criteria
1. Recurring tasks can be created with daily/weekly/monthly patterns
2. Completed recurring tasks automatically generate next occurrence
3. Users can set due dates and receive reminders via email/push
4. Tasks can be tagged, prioritized, searched, filtered, and sorted
5. All task operations publish events to Kafka
6. Notification Service consumes reminder events and sends notifications
7. Recurring Task Service consumes completion events and creates new tasks
8. All Dapr components are configured and functional
9. Application runs on Minikube with local Kafka and Dapr
10. Application deploys to cloud with managed Kafka and cloud resources
11. GitHub Actions pipeline builds, tests, and deploys automatically
12. Prometheus metrics are exposed and Grafana dashboards visualize them
13. All services pass health checks and have proper resource limits
14. TDD tests cover event handlers, repositories, and business logic

## Points: 300
## Due Date: January 18, 2026

## Response snapshot

Created comprehensive Phase 5 specification with 13 prioritized user stories (P1-P3), 98 functional requirements, and 30 measurable success criteria. Specification covers three parts: Advanced Features (recurring tasks, reminders, priorities, tags, search/filter/sort, event-driven architecture, microservices), Local Deployment (Minikube with Dapr), and Cloud Deployment (GKE/AKS/OKE with CI/CD and monitoring). All quality checks passed - no implementation details, technology-agnostic success criteria, testable requirements, comprehensive edge cases, and clear scope boundaries.

## Outcome

- ✅ Impact: Complete Phase 5 specification ready for planning with 13 independently testable user stories covering event-driven microservices architecture and cloud-native deployment
- 🧪 Tests: Quality validation checklist created - all 14 criteria passed (no clarifications needed, all requirements testable, measurable success criteria)
- 📁 Files: Created specs/005-event-driven-cloud/spec.md (554 lines) and checklists/requirements.md with comprehensive validation results
- 🔁 Next prompts: Run `/sp.clarify` to refine requirements with stakeholders, or `/sp.plan` to design technical architecture and implementation strategy
- 🧠 Reflection: Prioritized user stories (P1: 8 critical stories, P2: 4 important, P3: 2 nice-to-have) enable incremental delivery, with clear MVP path through P1 stories

## Evaluation notes (flywheel)

- Failure modes observed: Initial bash script failure due to CRLF line endings (Windows environment issue). Fixed using `sed -i 's/\r$//'` command. Script then executed successfully.
- Graders run and results (PASS/FAIL): PASS - All 14 quality checklist items passed: no implementation details, technology-agnostic success criteria, testable requirements, comprehensive acceptance scenarios (71 total), edge cases documented (10), clear scope boundaries (16 out-of-scope items), dependencies (12) and assumptions (15) identified
- Prompt variant (if applicable): Standard /sp.specify workflow with SDD approach
- Next experiment (smallest change to try): Consider adding pre-commit hook to automatically convert line endings to LF for all bash scripts in .specify/ directory to prevent future CRLF issues
