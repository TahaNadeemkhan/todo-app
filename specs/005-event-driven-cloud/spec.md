# Feature Specification: Phase 5 - Event-Driven Cloud Deployment

**Feature Branch**: `005-event-driven-cloud`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "Phase 5: Advanced Cloud Deployment with Event-Driven Architecture"

**Points**: 300
**Due Date**: January 18, 2026

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recurring Tasks (Priority: P1)

Users can create tasks that automatically repeat on a defined schedule (daily, weekly, monthly), and when a recurring task is completed, the system automatically generates the next occurrence based on the recurrence pattern.

**Why this priority**: Core advanced feature that delivers immediate user value. Users can set up recurring tasks once instead of manually recreating them, saving significant time and reducing cognitive load. This is the foundation for automation and a key differentiator from basic todo apps.

**Independent Test**: Can be fully tested by creating a recurring task, marking it complete, and verifying the next occurrence is automatically created with the correct due date. Delivers standalone value without requiring other Phase 5 features.

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they enable recurrence and select "daily", **Then** the task is saved with a daily recurrence pattern
2. **Given** a task with daily recurrence is marked complete, **When** the system processes the completion, **Then** a new task with the same title and description is created with tomorrow's date
3. **Given** a task with weekly recurrence (every Monday), **When** it is completed on Monday, **Then** the next occurrence is created for the following Monday
4. **Given** a task with monthly recurrence (15th of each month), **When** completed, **Then** the next task is created for the 15th of the next month
5. **Given** a user views a recurring task, **When** they choose to stop recurrence, **Then** future occurrences are no longer generated
6. **Given** a recurring task chain exists, **When** a user views the task, **Then** they can see the recurrence pattern and history of completed occurrences

---

### User Story 2 - Due Dates & Reminders (Priority: P1)

Users can set due dates and times for tasks, and receive timely reminders before tasks are due through their preferred notification channels (email, push notifications).

**Why this priority**: Critical for task completion and user engagement. Without reminders, users may forget about tasks, reducing the app's value. This directly addresses the pain point of missed deadlines and forgotten tasks.

**Independent Test**: Can be fully tested by creating a task with a due date, setting a reminder for "1 hour before", and verifying the reminder is sent via the selected channel (email or push). Delivers standalone value for time-sensitive task management.

**Acceptance Scenarios**:

1. **Given** a user is creating a task, **When** they set a due date and time, **Then** the task is saved with the specified due date
2. **Given** a task has a due date, **When** the user enables reminders, **Then** they can choose when to be reminded (1 hour, 1 day, 1 week before)
3. **Given** a task has a reminder set for "1 hour before" at 2:00 PM, **When** the system time reaches 1:00 PM, **Then** a reminder notification is sent to the user
4. **Given** a user has selected email as their reminder channel, **When** a reminder is due, **Then** an email is sent to their registered email address
5. **Given** a user has selected push notifications, **When** a reminder is due, **Then** a push notification is delivered to their device
6. **Given** a reminder is sent, **When** the system logs the delivery, **Then** the delivery status (sent/failed) is recorded
7. **Given** a reminder fails to send, **When** the system detects the failure, **Then** the error is logged and optionally retried based on the failure type

---

### User Story 3 - Task Organization with Priorities and Tags (Priority: P2)

Users can assign priority levels (High, Medium, Low) to tasks and organize them using multiple custom tags, enabling better task categorization and focus on what matters most.

**Why this priority**: Enhances task management effectiveness by allowing users to prioritize and categorize work. Essential for users managing multiple projects or contexts, but can be delivered after basic recurring tasks and reminders.

**Independent Test**: Can be fully tested by creating tasks with different priorities, adding multiple tags, and verifying tasks can be organized by these attributes. Delivers standalone value for task organization without requiring other features.

**Acceptance Scenarios**:

1. **Given** a user is creating a task, **When** they select a priority level, **Then** the task is saved with priority set to High, Medium, or Low
2. **Given** a user is creating a task, **When** they add tags, **Then** multiple tags can be assigned to a single task
3. **Given** tasks exist with different priorities, **When** the user views their task list, **Then** high-priority tasks are visually distinguished (color, icon, or badge)
4. **Given** tasks have been tagged, **When** the user clicks on a tag, **Then** all tasks with that tag are shown
5. **Given** a user has created custom tags, **When** creating a new task, **Then** existing tags are suggested for reuse

---

### User Story 4 - Advanced Search and Filtering (Priority: P2)

Users can quickly find tasks using full-text search across titles and descriptions, and filter tasks by priority, tags, due date, and completion status to focus on relevant work.

**Why this priority**: Critical for users with large task lists (>50 tasks). Without search and filtering, finding specific tasks becomes time-consuming. Delivers high value for power users but isn't essential for basic functionality.

**Independent Test**: Can be fully tested by creating 20+ tasks with various attributes, performing searches and applying filters, and verifying correct results are returned. Delivers standalone value for task discovery.

**Acceptance Scenarios**:

1. **Given** 50 tasks exist in the system, **When** a user searches for "meeting", **Then** all tasks with "meeting" in the title or description are displayed
2. **Given** tasks have various priorities, **When** the user filters by "High priority", **Then** only high-priority tasks are shown
3. **Given** tasks have different tags, **When** the user filters by tag "work", **Then** only tasks tagged with "work" are displayed
4. **Given** tasks have due dates, **When** the user filters by "Due this week", **Then** only tasks with due dates in the next 7 days are shown
5. **Given** both completed and incomplete tasks exist, **When** the user filters by "Completed", **Then** only completed tasks are shown
6. **Given** multiple filters are applied (priority + tag + due date), **When** the user views results, **Then** tasks matching ALL filters are displayed
7. **Given** a search query returns results, **When** the user clears the search, **Then** all tasks are displayed again

---

### User Story 5 - Flexible Task Sorting (Priority: P3)

Users can sort their task list by different criteria (due date, priority, created date, alphabetical) to view tasks in the order that best suits their workflow.

**Why this priority**: Enhances user experience and workflow efficiency but is less critical than search/filter. Users can still manage tasks effectively with default sorting. Nice-to-have feature for personalization.

**Independent Test**: Can be fully tested by creating tasks with various attributes and verifying each sort option reorders the list correctly. Delivers standalone value for task organization preferences.

**Acceptance Scenarios**:

1. **Given** tasks have different due dates, **When** the user sorts by "Due date", **Then** tasks are ordered from earliest to latest due date
2. **Given** tasks have different priorities, **When** the user sorts by "Priority", **Then** tasks are ordered High → Medium → Low
3. **Given** tasks were created at different times, **When** the user sorts by "Created date", **Then** tasks are ordered from newest to oldest (or vice versa based on preference)
4. **Given** tasks have different titles, **When** the user sorts by "Alphabetical", **Then** tasks are ordered A-Z by title
5. **Given** a sort preference is selected, **When** the user refreshes the page, **Then** the sort preference is remembered

---

### User Story 6 - Event-Driven Architecture with Real-Time Sync (Priority: P1)

The system publishes events for all task operations (create, update, complete, delete) to enable real-time synchronization across multiple devices, asynchronous processing by microservices, and future integrations.

**Why this priority**: Foundational architecture that enables microservices, scalability, and real-time collaboration. Required for notification and recurring task services to function. Critical for Part B and C deployment requirements.

**Independent Test**: Can be fully tested by performing task operations and verifying events are published to Kafka topics, consumed by services, and state updates propagate in real-time. Delivers value by enabling multi-device sync.

**Acceptance Scenarios**:

1. **Given** a user creates a task, **When** the task is saved, **Then** a "task.created" event is published to the "task-events" topic
2. **Given** a user updates a task, **When** the update is saved, **Then** a "task.updated" event is published with the changed fields
3. **Given** a user completes a task, **When** marked complete, **Then** a "task.completed" event is published
4. **Given** a user deletes a task, **When** the deletion is confirmed, **Then** a "task.deleted" event is published
5. **Given** a task event is published, **When** multiple consumers listen to the topic, **Then** each consumer receives the event independently
6. **Given** a user has the app open on two devices, **When** a task is created on device A, **Then** device B receives the update in real-time (within 2 seconds)
7. **Given** events are published, **When** processed by consumers, **Then** each consumer handles the event idempotently (duplicate events do not cause errors)

---

### User Story 7 - Notification Microservice (Priority: P1)

A dedicated microservice consumes reminder events and sends notifications via email and push notifications, tracking delivery status and handling failures gracefully.

**Why this priority**: Core microservice required for reminder functionality. Demonstrates event-driven architecture in action. Essential for Part A and validates the microservices approach before scaling to cloud.

**Independent Test**: Can be fully tested by triggering a reminder event, verifying the notification service consumes it, sends the notification, and logs the delivery status. Delivers standalone value for reliable reminder delivery.

**Acceptance Scenarios**:

1. **Given** a reminder event is published to the "reminders" topic, **When** the notification service consumes it, **Then** the event is processed and a notification is prepared
2. **Given** a reminder specifies email channel, **When** the notification is sent, **Then** an email is delivered to the user's registered address via SMTP
3. **Given** a reminder specifies push channel, **When** the notification is sent, **Then** a push notification is delivered via Firebase Cloud Messaging
4. **Given** a notification is sent successfully, **When** the service logs the delivery, **Then** a "notification.sent" event is published with timestamp and channel
5. **Given** a notification fails to send, **When** the error is caught, **Then** a "notification.failed" event is published with error details
6. **Given** multiple reminder events arrive simultaneously, **When** the service processes them, **Then** all notifications are sent without loss or duplication
7. **Given** the notification service crashes during processing, **When** it restarts, **Then** unprocessed events are consumed and processed (at-least-once delivery)

---

### User Story 8 - Recurring Task Microservice (Priority: P1)

A dedicated microservice listens for task completion events and automatically generates the next occurrence for recurring tasks based on their recurrence pattern.

**Why this priority**: Core microservice required for recurring task functionality. Separates concerns by handling recurrence logic asynchronously. Essential for demonstrating event-driven microservices pattern.

**Independent Test**: Can be fully tested by completing a recurring task, verifying the service consumes the event, calculates the next due date, and creates the new task occurrence. Delivers standalone value for automated task recurrence.

**Acceptance Scenarios**:

1. **Given** a task with daily recurrence is completed, **When** the "task.completed" event is consumed, **Then** the service creates a new task with tomorrow's due date
2. **Given** a task with weekly recurrence (every Monday) is completed, **When** processed, **Then** the next occurrence is created for the following Monday
3. **Given** a task with monthly recurrence (15th) is completed, **When** processed, **Then** the next task is created for the 15th of the next month
4. **Given** a recurring task has a recurrence pattern, **When** the next occurrence is created, **Then** the recurrence pattern is copied to the new task
5. **Given** a new task occurrence is created, **When** saved, **Then** a "task.created" event is published
6. **Given** recurrence has been stopped on a task, **When** a completion event is received, **Then** no new occurrence is created
7. **Given** the recurring task service processes an event, **When** a duplicate event arrives, **Then** it is ignored (idempotent processing)

---

### User Story 9 - Dapr Integration for Portable Microservices (Priority: P1)

All microservices use Dapr (Distributed Application Runtime) building blocks to abstract infrastructure, ensuring portability across local (Minikube) and cloud (GKE/AKS/OKE) environments.

**Why this priority**: Architectural foundation that enables deployment flexibility and reduces vendor lock-in. Required for Part B (Minikube) and Part C (cloud) deployment. Validates the portable microservices approach.

**Independent Test**: Can be fully tested by deploying to Minikube and cloud, verifying services communicate via Dapr APIs without code changes. Delivers value by simplifying infrastructure abstraction.

**Acceptance Scenarios**:

1. **Given** the backend API publishes events, **When** using Dapr Pub/Sub, **Then** events are sent to Kafka without using Kafka-specific libraries
2. **Given** services need to retrieve secrets, **When** using Dapr Secrets API, **Then** secrets are fetched from Kubernetes Secrets (or cloud secret stores) without environment-specific code
3. **Given** services need to save state, **When** using Dapr State Store, **Then** state is persisted to PostgreSQL without database-specific code
4. **Given** the notification service needs scheduled reminders, **When** using Dapr Jobs API or Bindings, **Then** reminders are triggered on schedule without cron-specific code
5. **Given** the frontend calls the backend, **When** using Dapr Service Invocation, **Then** requests are secured with mTLS automatically
6. **Given** a service is deployed to Minikube, **When** the same Docker image is deployed to GKE, **Then** the service functions identically using different Dapr component configurations

---

### User Story 10 - Local Kubernetes Deployment with Minikube (Priority: P2)

The complete application (frontend, backend, Kafka, PostgreSQL, microservices) can be deployed to Minikube for local development and testing, with all Dapr components configured.

**Why this priority**: Essential for local development workflow and validating the complete stack before cloud deployment. Enables developers to test end-to-end without cloud costs. Required for Part B.

**Independent Test**: Can be fully tested by running `helm install` on Minikube and verifying all services start, communicate, and process events correctly. Delivers standalone value for local development.

**Acceptance Scenarios**:

1. **Given** Minikube is running, **When** the Helm chart is installed, **Then** all pods (frontend, backend, notification service, recurring task service) start successfully
2. **Given** Kafka is deployed locally, **When** services publish events, **Then** events are consumed by the appropriate services
3. **Given** Dapr is installed on Minikube, **When** services use Dapr components, **Then** Pub/Sub, State, Secrets, and Service Invocation work correctly
4. **Given** the application is running on Minikube, **When** a user accesses the frontend, **Then** they can create tasks, set reminders, and see real-time updates
5. **Given** all services are deployed, **When** a recurring task is completed, **Then** the recurring task service generates the next occurrence
6. **Given** a reminder is due, **When** the notification service processes it, **Then** the notification is sent (mock email/push for local testing)

---

### User Story 11 - Cloud Kubernetes Deployment (GKE/AKS/OKE) (Priority: P2)

The application can be deployed to a production-grade cloud Kubernetes cluster (Google GKE, Azure AKS, or Oracle OKE) with Ingress, TLS, autoscaling, and managed Kafka.

**Why this priority**: Required for Part C and production readiness. Demonstrates cloud-native architecture at scale. Enables real-world usage and validates the complete deployment pipeline.

**Independent Test**: Can be fully tested by deploying to a cloud K8s cluster and verifying the application handles production load with autoscaling, TLS, and monitoring. Delivers value for production deployment.

**Acceptance Scenarios**:

1. **Given** a cloud Kubernetes cluster exists (GKE/AKS/OKE), **When** the Helm chart is deployed with production values, **Then** all services start with proper resource limits and health checks
2. **Given** the application is deployed, **When** users access the public URL, **Then** traffic is routed via Ingress with TLS/SSL certificate
3. **Given** load increases, **When** CPU usage exceeds 70%, **Then** Horizontal Pod Autoscaler (HPA) scales up replicas automatically
4. **Given** managed Kafka (Confluent/Redpanda Cloud) is configured, **When** services publish events, **Then** events are reliably delivered across topics
5. **Given** services are running in production, **When** a pod is terminated, **Then** Pod Disruption Budget (PDB) ensures minimum replicas remain available
6. **Given** the application is deployed, **When** monitoring is configured, **Then** Prometheus metrics are collected and Grafana dashboards visualize system health

---

### User Story 12 - CI/CD Pipeline with GitHub Actions (Priority: P2)

Every commit to the main branch triggers an automated pipeline that builds Docker images, runs tests, pushes to a container registry, and deploys to Kubernetes (staging/production).

**Why this priority**: Essential for continuous delivery and reducing deployment friction. Enables rapid iteration and reduces human error. Required for Part C and professional development workflow.

**Independent Test**: Can be fully tested by pushing a code change and verifying the pipeline builds, tests, and deploys automatically. Delivers value by automating the entire deployment process.

**Acceptance Scenarios**:

1. **Given** a developer pushes code to the main branch, **When** GitHub Actions runs, **Then** all tests are executed and must pass before proceeding
2. **Given** tests pass, **When** the build step runs, **Then** Docker images are built for frontend and backend with the commit SHA as tag
3. **Given** Docker images are built, **When** the push step runs, **Then** images are pushed to a container registry (Docker Hub, GCR, ACR, OCIR)
4. **Given** images are pushed, **When** the deploy step runs, **Then** Helm upgrades the Kubernetes release with the new images
5. **Given** deployment completes, **When** health checks run, **Then** the pipeline verifies all pods are healthy before marking success
6. **Given** deployment fails, **When** rollback is triggered, **Then** the previous Helm release is restored automatically
7. **Given** deployment to production, **When** an approval gate is configured, **Then** deployment waits for manual approval before proceeding

---

### User Story 13 - Observability with Prometheus and Grafana (Priority: P3)

The application exposes metrics for monitoring, with Prometheus collecting metrics and Grafana dashboards visualizing system health, performance, and business metrics.

**Why this priority**: Critical for production operations but not required for basic functionality. Enables proactive issue detection and performance optimization. Nice-to-have for initial deployment, essential for long-term operations.

**Independent Test**: Can be fully tested by deploying monitoring stack, generating load, and verifying metrics are collected and visualized in Grafana. Delivers value for operational visibility.

**Acceptance Scenarios**:

1. **Given** services expose `/metrics` endpoints, **When** Prometheus scrapes them, **Then** metrics are collected every 15 seconds
2. **Given** metrics are collected, **When** a Grafana dashboard is configured, **Then** request rate, error rate, and latency (RED metrics) are visualized
3. **Given** business metrics are tracked, **When** viewing the Grafana dashboard, **Then** tasks created, completed, and reminder delivery rates are shown
4. **Given** alert rules are configured, **When** error rate exceeds 5%, **Then** an alert is triggered and sent to the configured notification channel
5. **Given** distributed tracing is enabled, **When** a request spans multiple services, **Then** the full trace is captured and visualizable in Jaeger
6. **Given** a service experiences high latency, **When** viewing traces, **Then** the slowest operation in the request chain is identified

---

### Edge Cases

- **What happens when a recurring task's next occurrence conflicts with an existing task?**: The system creates the new occurrence regardless, allowing users to manually merge or delete if needed. Future enhancement could detect and suggest merging.

- **How does the system handle reminders for tasks with past due dates?**: Reminders for past dates are not sent. If a task's due date is in the past and a reminder is configured, the system skips sending the reminder and logs a warning.

- **What happens when the notification service is down and reminder events accumulate?**: Events are retained in Kafka (default 7-day retention). When the service restarts, it consumes backlogged events and sends reminders (though some may be late). Dead letter queue handles events that fail after retry attempts.

- **How does the system handle time zones for due dates and reminders?**: All due dates and times are stored in UTC in the database. The frontend converts to the user's local time zone for display. Reminders are sent based on UTC time.

- **What happens if a user deletes a recurring task mid-chain?**: The specific task instance is deleted. The recurrence pattern is removed to prevent future occurrences. Past completed instances remain in history.

- **How does the system handle duplicate events in Kafka?**: All event consumers implement idempotent processing using event_id as a deduplication key. Duplicate events are detected and ignored.

- **What happens when a user creates a monthly recurring task on the 31st?**: For months with fewer than 31 days, the task is created on the last day of that month (e.g., February 28/29).

- **How does the system handle failures when creating the next recurring task occurrence?**: The recurring task service logs the error and publishes a "task.creation.failed" event. The system may retry based on the error type. The user is notified via the UI if recurrence stops due to repeated failures.

- **What happens when Kafka is temporarily unavailable?**: The backend API retains events in memory (up to 1000 events) and attempts to publish when Kafka reconnects. If the buffer fills, new operations return a 503 error to prevent data loss.

- **How does the system handle concurrent updates to the same task?**: The database enforces optimistic locking using a version field. The second update fails with a 409 conflict error, prompting the user to refresh and retry.

## Requirements *(mandatory)*

### Functional Requirements

#### Part A: Advanced Features

**Recurring Tasks**

- **FR-001**: System MUST allow users to create tasks with recurrence patterns (daily, weekly, monthly)
- **FR-002**: System MUST support weekly recurrence with specific day selection (e.g., every Monday and Wednesday)
- **FR-003**: System MUST support monthly recurrence with specific date selection (e.g., 15th of every month)
- **FR-004**: System MUST automatically create the next task occurrence when a recurring task is marked complete
- **FR-005**: System MUST preserve task title, description, priority, and tags when creating recurring task occurrences
- **FR-006**: System MUST allow users to stop recurrence on a recurring task, preventing future occurrences
- **FR-007**: System MUST display recurrence pattern information on recurring tasks
- **FR-008**: System MUST handle edge cases for monthly recurrence (e.g., 31st when month has 30 days)

**Due Dates & Reminders**

- **FR-009**: System MUST allow users to set due dates and times for tasks with date/time picker
- **FR-010**: System MUST allow users to configure reminder timing (1 hour, 1 day, 1 week before due date)
- **FR-011**: System MUST support multiple reminder channels: email and push notifications
- **FR-012**: System MUST send reminders at the configured time before the due date
- **FR-013**: System MUST log reminder delivery status (sent, failed) with timestamp and error details
- **FR-014**: System MUST not send reminders for tasks with due dates in the past
- **FR-015**: System MUST retry failed reminder notifications according to a retry policy
- **FR-016**: System MUST allow users to select their preferred reminder channel(s) per task
- **FR-017**: System MUST store all timestamps in UTC and convert to user's local timezone for display

**Priorities, Tags, Search, Filter, Sort**

- **FR-018**: System MUST allow users to assign priority levels (High, Medium, Low) to tasks
- **FR-019**: System MUST visually distinguish high-priority tasks in the UI (color, icon, or badge)
- **FR-020**: System MUST allow users to add multiple tags to a single task
- **FR-021**: System MUST suggest existing tags when adding tags to a task (autocomplete)
- **FR-022**: System MUST provide full-text search across task titles and descriptions
- **FR-023**: System MUST allow filtering tasks by priority level
- **FR-024**: System MUST allow filtering tasks by one or more tags
- **FR-025**: System MUST allow filtering tasks by due date ranges (today, this week, this month, overdue)
- **FR-026**: System MUST allow filtering tasks by completion status (active, completed)
- **FR-027**: System MUST allow combining multiple filters simultaneously (AND logic)
- **FR-028**: System MUST allow sorting tasks by due date (ascending/descending)
- **FR-029**: System MUST allow sorting tasks by priority (High → Medium → Low)
- **FR-030**: System MUST allow sorting tasks by created date (newest/oldest first)
- **FR-031**: System MUST allow sorting tasks alphabetically by title (A-Z or Z-A)
- **FR-032**: System MUST persist user's sort and filter preferences across sessions

#### Event-Driven Architecture

- **FR-033**: System MUST publish a "task.created" event to Kafka when a task is created
- **FR-034**: System MUST publish a "task.updated" event to Kafka when a task is modified
- **FR-035**: System MUST publish a "task.completed" event to Kafka when a task is marked complete
- **FR-036**: System MUST publish a "task.deleted" event to Kafka when a task is deleted
- **FR-037**: System MUST publish a "reminder.due" event to Kafka when a reminder should be sent
- **FR-038**: System MUST include event_id (UUID) in all events for deduplication
- **FR-039**: System MUST include user_id in all events for multi-tenancy
- **FR-040**: System MUST include timestamp in all events (ISO 8601 format)
- **FR-041**: System MUST use JSON format for all event payloads
- **FR-042**: System MUST configure Kafka topics with appropriate partitioning and replication
- **FR-043**: System MUST implement idempotent event consumers using event_id for deduplication
- **FR-044**: System MUST handle Kafka unavailability gracefully with retry and fallback mechanisms

#### Microservices

**Notification Service**

- **FR-045**: Notification service MUST consume events from the "reminders" Kafka topic
- **FR-046**: Notification service MUST send email notifications via SMTP
- **FR-047**: Notification service MUST send push notifications via Firebase Cloud Messaging
- **FR-048**: Notification service MUST log all notifications to a database table (user_id, type, message, sent_at, status)
- **FR-049**: Notification service MUST publish "notification.sent" events when notifications succeed
- **FR-050**: Notification service MUST publish "notification.failed" events when notifications fail
- **FR-051**: Notification service MUST implement retry logic for transient failures
- **FR-052**: Notification service MUST process events idempotently to avoid duplicate notifications

**Recurring Task Service**

- **FR-053**: Recurring task service MUST consume "task.completed" events from the "task-events" topic
- **FR-054**: Recurring task service MUST filter for tasks with has_recurrence=true
- **FR-055**: Recurring task service MUST calculate the next due date based on recurrence pattern (daily, weekly, monthly)
- **FR-056**: Recurring task service MUST create a new task with the calculated due date
- **FR-057**: Recurring task service MUST copy title, description, priority, tags, and recurrence pattern to the new task
- **FR-058**: Recurring task service MUST publish "task.created" event for the new occurrence
- **FR-059**: Recurring task service MUST not create new occurrences if recurrence has been stopped
- **FR-060**: Recurring task service MUST process events idempotently to avoid duplicate task creation

#### Dapr Integration

- **FR-061**: All services MUST use Dapr Pub/Sub API for publishing and subscribing to Kafka events
- **FR-062**: All services MUST use Dapr Secrets API for retrieving configuration secrets
- **FR-063**: Services requiring state MUST use Dapr State Store API for persistence
- **FR-064**: Services MUST use Dapr Service Invocation for inter-service communication
- **FR-065**: System MUST configure Dapr Jobs API or Bindings for scheduled reminder checks
- **FR-066**: All Dapr components MUST be configurable via YAML files
- **FR-067**: Dapr components MUST be scoped to appropriate services to limit access

#### Part B: Local Deployment (Minikube)

- **FR-068**: Application MUST provide a Helm chart for deployment to Minikube
- **FR-069**: Helm chart MUST deploy frontend, backend, notification service, and recurring task service
- **FR-070**: Helm chart MUST deploy Kafka locally (KRaft mode or with Zookeeper)
- **FR-071**: Helm chart MUST configure Dapr components (Pub/Sub, State, Secrets, Bindings, Service Invocation)
- **FR-072**: All services MUST have health check endpoints (/health or /healthz)
- **FR-073**: All services MUST have readiness and liveness probes configured
- **FR-074**: ConfigMaps MUST be used for non-sensitive configuration
- **FR-075**: Kubernetes Secrets MUST be used for sensitive data (DB credentials, SMTP passwords)
- **FR-076**: Services MUST have resource requests and limits defined

#### Part C: Cloud Deployment (GKE/AKS/OKE)

- **FR-077**: Application MUST deploy to at least one cloud Kubernetes platform (GKE, AKS, or OKE)
- **FR-078**: Helm chart MUST support production values for cloud deployment
- **FR-079**: Ingress MUST be configured with TLS/SSL certificates for HTTPS access
- **FR-080**: Horizontal Pod Autoscaler (HPA) MUST be configured for frontend and backend services
- **FR-081**: Pod Disruption Budgets (PDB) MUST be configured to ensure minimum availability during updates
- **FR-082**: System MUST use managed Kafka (Confluent Cloud or Redpanda Cloud) in production
- **FR-083**: Dapr components MUST be configured to connect to cloud-managed services (Kafka, secrets)
- **FR-084**: GitHub Actions workflow MUST build Docker images on commit to main branch
- **FR-085**: GitHub Actions workflow MUST run tests before building images
- **FR-086**: GitHub Actions workflow MUST push Docker images to a container registry with commit SHA tags
- **FR-087**: GitHub Actions workflow MUST deploy to Kubernetes using Helm upgrade
- **FR-088**: GitHub Actions workflow MUST verify deployment health after upgrade
- **FR-089**: GitHub Actions workflow MUST support rollback on deployment failure
- **FR-090**: System MUST expose Prometheus metrics from all services (/metrics endpoint)
- **FR-091**: Grafana dashboards MUST be provided for application and infrastructure monitoring
- **FR-092**: Alert rules MUST be configured for critical issues (service down, high error rate, high latency)
- **FR-093**: Distributed tracing MUST be enabled using OpenTelemetry or Jaeger

#### Docker & Containerization

- **FR-094**: All services MUST have multi-stage Dockerfiles for optimized image size
- **FR-095**: Docker images MUST use non-root users for security
- **FR-096**: Docker images MUST include health check instructions
- **FR-097**: Frontend Docker image MUST use Next.js standalone output for minimal size
- **FR-098**: Backend Docker image MUST use Python 3.13+ slim base image

### Key Entities

- **Task**: Represents a todo item with attributes including id (UUID), title, description, due_at (timestamp), priority (enum: high/medium/low), tags (array), has_recurrence (boolean), recurrence_pattern (string), completed (boolean), user_id (UUID), created_at, updated_at
- **Reminder**: Represents a scheduled reminder with attributes including id, task_id, user_id, reminder_time (timestamp), channels (array: email/push), status (enum: pending/sent/failed)
- **Notification**: Log of sent notifications with attributes including id, user_id, type (enum: email/push), message, sent_at (timestamp), delivery_status (enum: sent/failed), error_message
- **RecurrencePattern**: Defines how tasks repeat with attributes including pattern_type (enum: daily/weekly/monthly), day_of_week (for weekly), day_of_month (for monthly), enabled (boolean)
- **KafkaEvent**: Base structure for all events with attributes including event_id (UUID), event_type (string), timestamp (ISO 8601), user_id (UUID), payload (JSON)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Part A: Advanced Features**

- **SC-001**: Users can create a recurring task and mark it complete, with the next occurrence automatically created within 5 seconds
- **SC-002**: Users receive reminder notifications via their selected channel (email or push) within 1 minute of the scheduled reminder time
- **SC-003**: 95% of reminder notifications are successfully delivered (sent status logged)
- **SC-004**: Users can search across 100+ tasks and receive results in under 1 second
- **SC-005**: Users can apply multiple filters simultaneously and see filtered results in under 500ms
- **SC-006**: Task organization features (priorities, tags, search, filter, sort) reduce average time to find a specific task by 60% compared to linear scanning

**Part B & C: Event-Driven Architecture and Microservices**

- **SC-007**: All task CRUD operations publish events to Kafka within 100ms of the operation
- **SC-008**: Microservices consume and process events within 2 seconds of event publication
- **SC-009**: 99.9% of events are processed successfully (no data loss)
- **SC-010**: System handles duplicate events gracefully with idempotent processing (no duplicate tasks or notifications created)
- **SC-011**: When a user completes a recurring task on one device, the next occurrence appears on all devices within 3 seconds (real-time sync)

**Part B: Local Deployment**

- **SC-012**: Complete application deploys to Minikube in under 5 minutes using a single `helm install` command
- **SC-013**: All services (frontend, backend, notification, recurring task, Kafka) start successfully on Minikube with health checks passing
- **SC-014**: Local deployment consumes less than 4GB RAM to support development on standard laptops
- **SC-015**: Developers can test end-to-end functionality locally (create task, set reminder, receive notification) without external dependencies

**Part C: Cloud Deployment**

- **SC-016**: Application deploys to cloud Kubernetes (GKE/AKS/OKE) and handles 1000 concurrent users without degradation
- **SC-017**: Frontend serves pages with P95 response time under 200ms
- **SC-018**: Backend API endpoints respond with P95 latency under 150ms
- **SC-019**: Horizontal Pod Autoscaler scales services from 2 to 10 replicas when CPU exceeds 70%
- **SC-020**: Zero-downtime deployments with Pod Disruption Budgets ensuring at least 1 replica remains available
- **SC-021**: TLS/SSL certificates are configured and all traffic is served over HTTPS
- **SC-022**: GitHub Actions CI/CD pipeline completes (build, test, deploy) in under 10 minutes
- **SC-023**: Prometheus collects metrics from all services every 15 seconds
- **SC-024**: Grafana dashboards visualize request rate, error rate, and latency for all services
- **SC-025**: Alerts trigger within 1 minute when error rate exceeds 5% or service is down

**Quality and Testing**

- **SC-026**: Unit test coverage for backend services exceeds 80%
- **SC-027**: Integration tests validate event flow from publication to consumption for all event types
- **SC-028**: End-to-end tests verify complete user journeys (create recurring task → complete → next occurrence created)
- **SC-029**: All Docker images are under 200MB (frontend) and 150MB (backend) after optimization
- **SC-030**: Documentation enables a new developer to deploy locally within 15 minutes following the README

## Assumptions

1. **Kafka Availability**: Assumes Kafka (local or cloud-managed) is available and properly configured. The application will handle temporary Kafka unavailability with retry logic and buffering.

2. **Email/Push Infrastructure**: Assumes SMTP server credentials and Firebase Cloud Messaging setup are provided via configuration. For local testing, mock implementations or development services (e.g., Mailtrap) can be used.

3. **User Authentication**: Assumes user authentication and authorization are already implemented (from Phase 2/3). User IDs are included in all events and API requests for multi-tenancy.

4. **Database**: Assumes Neon Serverless PostgreSQL is the primary database. New tables for reminders and notifications will be added via Alembic migrations.

5. **Cloud Platform**: Assumes users have access to at least one cloud Kubernetes platform (GKE, AKS, or OKE) with permissions to create clusters, configure Ingress, and manage resources.

6. **Container Registry**: Assumes access to a container registry (Docker Hub, GCR, ACR, OCIR) for storing Docker images.

7. **Domain and TLS**: For production deployment, assumes a domain name is available for Ingress and TLS certificates can be obtained (via Let's Encrypt or cloud provider).

8. **Monitoring Tools**: Assumes Prometheus and Grafana can be deployed to the Kubernetes cluster or are available as managed services.

9. **Time Zones**: Assumes users will set their time zone preference in their profile (defaulting to UTC if not set). All server-side timestamps are stored in UTC.

10. **Event Ordering**: Assumes Kafka partitioning by user_id ensures events for the same user are processed in order.

11. **Recurrence Patterns**: Initial implementation supports three patterns (daily, weekly, monthly). More complex patterns (e.g., "every other week", "last Friday of the month") are out of scope for Phase 5.

12. **Notification Channels**: Email and push notifications are supported. SMS and other channels are out of scope.

13. **Multi-Region**: Single-region deployment is assumed. Multi-region, geo-distributed deployment is out of scope.

14. **Cost**: Assumes users accept cloud costs for managed Kafka, Kubernetes cluster, and associated resources. Local Minikube deployment is free for development.

15. **Test-Driven Development**: Assumes TDD approach with tests written before or alongside implementation, achieving the success criteria for test coverage.

## Dependencies

- **Phase 2/3 Codebase**: Builds on existing frontend (Next.js), backend (FastAPI), and database (PostgreSQL with SQLModel)
- **Authentication System**: Requires Better Auth or equivalent from Phase 2/3 for user_id in events
- **Kafka**: Requires Apache Kafka (local) or managed Kafka (Confluent Cloud, Redpanda Cloud)
- **Dapr**: Requires Dapr runtime installed on Kubernetes (Minikube or cloud)
- **Kubernetes**: Requires Minikube for local development and GKE/AKS/OKE for cloud deployment
- **Helm**: Requires Helm 3.x for packaging and deploying to Kubernetes
- **Docker**: Requires Docker for building container images
- **GitHub Actions**: Requires GitHub repository with Actions enabled for CI/CD
- **SMTP Server**: Requires SMTP credentials for email notifications (e.g., Gmail, SendGrid, AWS SES)
- **Firebase Cloud Messaging**: Requires Firebase project and FCM credentials for push notifications
- **Monitoring Stack**: Requires Prometheus and Grafana for observability

## Out of Scope

- **Multi-language Support**: UI translations for languages other than English
- **Offline Mode**: Progressive Web App (PWA) with offline task management
- **Collaboration Features**: Sharing tasks with other users, team workspaces
- **Advanced Recurrence Patterns**: Complex patterns like "every other Tuesday" or "last Friday of the month"
- **Calendar Integration**: Sync with Google Calendar, Outlook, etc.
- **AI Features**: Smart task suggestions, priority recommendations
- **Mobile Native Apps**: iOS/Android native apps (web app is mobile-responsive)
- **Voice Commands**: Voice-based task creation or management
- **File Attachments**: Attaching files or images to tasks
- **Subtasks**: Hierarchical task breakdown with subtasks
- **Time Tracking**: Logging time spent on tasks
- **Multi-Region Deployment**: Geo-distributed deployment across multiple cloud regions
- **SMS Notifications**: SMS as a reminder channel (only email and push supported)
- **Custom Recurrence Patterns**: User-defined complex recurrence logic
- **Backup and Restore**: Automated backup of task data (relies on cloud provider database backups)

## Notes

This specification focuses on **WHAT** the system should do from a user and business perspective, intentionally avoiding **HOW** to implement it. The planning phase (`/sp.plan`) will address the technical architecture, design decisions, and implementation strategy.

The three-part structure (Part A: Advanced Features, Part B: Local Deployment, Part C: Cloud Deployment) aligns with the hackathon requirements and allows for phased development and validation:

1. **Part A** can be developed and tested with the existing Phase 3 stack before containerization
2. **Part B** validates the complete stack locally on Minikube before cloud deployment
3. **Part C** extends the deployment to production cloud platforms with CI/CD and monitoring

All user stories are prioritized (P1, P2, P3) and independently testable, enabling incremental delivery and validation at each stage.
