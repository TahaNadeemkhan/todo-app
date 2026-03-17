# Feature Specification: Fix Phase 5 Deployment

**Feature Branch**: `001-fix-phase5-deployment`  
**Created**: 2026-03-06  
**Status**: Draft  
**Input**: User description: "the issue is looking so messy I want u to create an excellent specification in which all the common pitfalls should be mentioned all the problems that are occuring should be mentioned and their best of the best solution should be mentioned. Search the whole issue carefully and list all of them and how to tackle them all"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stable Local Microservices Deployment (Priority: P1)

As a developer, I want to deploy the Phase 5 microservices architecture (Backend, Notification, Recurring Task, Frontend) on a local Minikube cluster so that I can verify the end-to-end functionality of the event-driven system.

**Why this priority**: This is the core requirement for Phase 5. Without a stable deployment, no other features or tests can be validated.

**Independent Test**: Can be fully tested by running a deployment script and verifying that all pods (Backend, Notification, Recurring Task, Frontend, Dapr sidecars) reach the `Running` state and can communicate.

**Acceptance Scenarios**:

1. **Given** a fresh Minikube cluster, **When** the deployment process is executed, **Then** all services must be running with their respective Dapr sidecars.
2. **Given** the microservices are deployed, **When** a task is created via the Backend, **Then** the Notification service should receive the event and the Recurring Task service should process it.

---

### User Story 2 - Resilient Environment Recovery (Priority: P2)

As a developer, I want a repeatable process to recover the deployment environment after a Minikube reset or deletion, ensuring all dependencies (Dapr, Secrets, Images) are correctly restored.

**Why this priority**: Minikube is often restarted or deleted during development. A manual or brittle recovery process significantly slows down development.

**Independent Test**: Delete the Minikube cluster, then run the recovery/deployment process and verify all services return to a functional state.

**Acceptance Scenarios**:

1. **Given** a deleted Minikube cluster, **When** the initialization script is run, **Then** Dapr must be installed, CRDs applied, and necessary secrets (Postgres, JWT) created.
2. **Given** images were built previously, **When** they are loaded into the new Minikube instance, **Then** Kubernetes must be able to pull them without `ImagePullBackOff` errors.

---

### User Story 3 - Robust Event Processing (Priority: P3)

As a system, I want to process events reliably between services without being blocked by library-level bugs (like the Dapr Python SDK issue).

**Why this priority**: Reliability is key in an event-driven architecture. Using direct HTTP APIs instead of buggy SDKs ensures the system remains stable.

**Independent Test**: Verify that the Backend can publish events to Kafka via the Dapr HTTP API and that the Notification service can consume them.

**Acceptance Scenarios**:

1. **Given** a Backend service using the Dapr HTTP API, **When** it publishes a "task-created" event, **Then** the Dapr sidecar must successfully forward it to the Kafka pubsub component.

---

### Edge Cases

- **Image Tag Collision**: What happens when a new image is built with the same tag? The system must ensure the latest version is used (e.g., using `v5.0.2` or forcing a reload).
- **Missing Secrets**: How does the system handle missing `postgres-credentials`? The pods should wait or fail gracefully with a clear error message (FR-005).
- **Network Timeouts**: How does the system handle slow image pulls or Dapr initialization? The Helm deployment should have adequate timeouts (e.g., 10m).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST bypass the buggy Dapr Python SDK (specifically the `dapr.proto` import issue) by using the Dapr HTTP API for event publishing and service invocation.
- **FR-002**: System MUST ensure that all local Docker images (Backend, Frontend, Services) are correctly loaded into the Minikube Docker daemon before deployment.
- **FR-003**: System MUST provide a mechanism (e.g., `.helmignore` or pre-packaging) to exclude large non-essential files (like `.venv`, `node_modules`) from the Helm chart to stay under the 5MB size limit.
- **FR-004**: System MUST automatically initialize Dapr and apply its CRDs and components after a Minikube cluster reset.
- **FR-005**: System MUST ensure all required Kubernetes Secrets (`postgres-credentials`, `jwt-secret`, `gemini-api-key`) are present before starting the microservices.
- **FR-006**: System MUST use unique image tags (e.g., incrementing from `v5.0.1` to `v5.0.2`) or a reliable image loading strategy to avoid stale image issues in Minikube.
- **FR-007**: System MUST use absolute paths or well-defined relative paths for Helm charts and configuration files to avoid agent-level path resolution errors.

### Pitfalls & Problems Identified (Root Cause Analysis)

| Problem | Root Cause | Best Solution |
|---------|------------|---------------|
| `ImportError: cannot import name 'common_v1' from 'dapr.proto'` | Bug in Dapr Python SDK (specifically on Python 3.13) | Bypass SDK; use `httpx` to call Dapr HTTP API directly. |
| `ErrImageNeverPull` / `ImagePullBackOff` | Minikube not finding local images; stale tags in K8s cache. | Use `minikube image load` and increment image tags (e.g., `v5.0.2`). |
| `chart file... is larger than the maximum file size 5242880` | Helm packaging the entire project (including `.venv`) into the chart. | Add a `.helmignore` file or package the chart as a `.tgz` manually. |
| `CreateContainerConfigError` | Missing Kubernetes Secrets (e.g., `postgres-credentials`). | Ensure `postgresql.enabled=true` in Helm or create secrets manually before deployment. |
| `unrecognized format "int32"` during `dapr init` | Dapr version mismatch or transient K8s API warnings. | Can often be ignored, but ensure Dapr is fully initialized before applying components. |

### Key Entities *(include if feature involves data)*

- **Dapr Component**: Represents the infrastructure abstraction (PubSub, StateStore) used by microservices.
- **Kubernetes Secret**: Stores sensitive configuration (DB strings, API keys) required by the containers.
- **Helm Release**: The packaged deployment of the entire application on the cluster.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 4 primary microservice pods (Backend, Frontend, Notification, Recurring Task) reach the `Running` state within 10 minutes of deployment.
- **SC-002**: Zero `ImportError` or `ModuleNotFoundError` messages related to Dapr in the pod logs.
- **SC-003**: Successfully publish and consume a test event between Backend and Notification service via Kafka.
- **SC-004**: The deployment process can be completed from a "Minikube deleted" state to "All pods running" using a single sequence of commands.
- **SC-005**: Helm chart package size remains under 500KB.
