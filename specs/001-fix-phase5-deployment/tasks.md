# Tasks: Fix Phase 5 Deployment

**Input**: Design documents from `/specs/001-fix-phase5-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment initialization and basic cluster setup

- [ ] T001 Delete existing Minikube cluster and start fresh with `minikube delete && minikube start --driver=docker --cpus=2 --memory=3072`
- [ ] T002 Initialize Dapr in the Kubernetes cluster with `dapr init -k`
- [ ] T003 [P] Verify Dapr control plane status with `dapr status -k`
- [ ] T004 Apply Dapr components from `todo_app/phase_5/k8s/dapr-components/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and image preparation that MUST be complete before ANY user story can be implemented

- [ ] T005 Create `postgres-credentials` secret with connection string in `kubectl`
- [ ] T006 Create `jwt-secret` and `gemini-api-key` secrets in `kubectl`
- [ ] T007 [P] Update image tags to `v5.0.2` in `todo_app/phase_5/k8s/helm/todo-app/values.yaml`
- [ ] T008 [P] Build `todo-backend:v5.0.2` image in `todo_app/phase_5/backend/`
- [ ] T009 [P] Build `notification-service:v5.0.2` image in `todo_app/phase_5/services/notification-service/`
- [ ] T010 [P] Build `recurring-task-service:v5.0.2` image in `todo_app/phase_5/services/recurring-task-service/`
- [ ] T011 [P] Build `todo-frontend:v5.0.2` image in `todo_app/phase_5/frontend/`
- [ ] T012 [P] Load all `v5.0.2` images into Minikube using `minikube image load`

**Checkpoint**: Foundation ready - Environment is prepared with Dapr, Secrets, and Images.

---

## Phase 3: User Story 1 - Stable Local Microservices Deployment (Priority: P1) 🎯 MVP

**Goal**: Successfully deploy the microservices architecture on Minikube.

**Independent Test**: Verify all pods reach the `Running` state using `kubectl get pods`.

- [ ] T013 [US1] Package the Helm chart into a `.tgz` file in `todo_app/phase_5/k8s/helm/todo-app/`
- [ ] T014 [US1] Deploy the application using `helm upgrade --install todo-app [path-to-tgz]` with explicit tag overrides.
- [ ] T015 [US1] Verify backend pod logs for successful startup in `kubectl logs -l app=backend-api`
- [ ] T016 [US1] Verify frontend accessibility via Minikube service or port-forward.

**Checkpoint**: User Story 1 is functional; the app is deployed and running.

---

## Phase 4: User Story 2 - Resilient Environment Recovery (Priority: P2)

**Goal**: Ensure the environment can be recovered from a total reset.

**Independent Test**: Perform a `minikube delete`, then re-run the deployment sequence from `quickstart.md` and verify success.

- [ ] T017 [US2] Validate the recovery sequence documented in `specs/001-fix-phase5-deployment/quickstart.md`
- [ ] T018 [US2] Refine the Helm chart `templates/` if any pathing or dependency issues are found during recovery.

**Checkpoint**: Environment recovery is documented and verified.

---

## Phase 5: User Story 3 - Robust Event Processing (Priority: P3)

**Goal**: Implement the Dapr HTTP API bypass to avoid SDK bugs.

**Independent Test**: Verify event publishing from Backend and consumption in Notification service without ImportErrors.

- [ ] T019 [P] [US3] Verify `KafkaService` in `todo_app/phase_5/backend/src/services/kafka_service.py` uses `httpx` for direct Dapr HTTP publishing.
- [ ] T020 [P] [US3] Update `NotificationHandler` in `todo_app/phase_5/services/notification-service/src/handlers/notification_handler.py` to use direct HTTP for state/binding calls if applicable.
- [ ] T021 [US3] Re-build and re-load images for any code changes made during the bypass implementation.
- [ ] T022 [US3] Perform an end-to-end event flow test (e.g., create a task and check notification logs).

**Checkpoint**: System is resilient to Dapr Python SDK bugs.

---

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T023 [P] Clean up any temporary `.tgz` files or build artifacts in the `k8s/helm/` directory.
- [ ] T024 [P] Update `CLAUDE.md` or `GEMINI.md` project context if deployment patterns have changed.
- [ ] T025 Final validation of all success criteria (SC-001 to SC-005) from `spec.md`.

---

## Dependencies & Execution Order

1.  **Phase 1 (Setup)**: Blocks Phase 2.
2.  **Phase 2 (Foundational)**: Blocks US1.
3.  **Phase 3 (US1)**: Blocks US2 and US3 (system must be running to test recovery and event flow).
4.  **Phase 4 (US2)** and **Phase 5 (US3)**: Can proceed in parallel after US1 is stable.

## Parallel Execution Examples

```bash
# Phase 2 Parallel Builds
Task T008: Build backend
Task T009: Build notification
Task T010: Build recurring-task
Task T011: Build frontend
```

---

## Implementation Strategy

1.  **MVP**: Complete Phases 1, 2, and 3 to get the app running in Minikube.
2.  **Incremental**: Once US1 is stable, proceed to US2 (Recovery) and US3 (SDK Bypass) to ensure long-term stability.
