# Tasks: Local Kubernetes Deployment

**Branch**: `004-kubernetes-deployment` | **Date**: 2025-12-26
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

## Overview

Implementation tasks for deploying Phase 3 AI Chatbot to local Kubernetes (Minikube) using Docker containerization and Helm charts.

**Total Tasks**: 35
**Estimated Phases**: 9 (Setup → Foundational → 6 User Stories → Polish)

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US#]**: User story reference (US1-US8)
- All paths relative to `todo_app/phase_4/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create Phase 4 directory structure and copy Phase 3 code

- [ ] T001 Create phase_4 directory structure at `todo_app/phase_4/`
- [ ] T002 [P] Copy Phase 3 frontend code to `todo_app/phase_4/frontend/`
- [ ] T003 [P] Copy Phase 3 backend code to `todo_app/phase_4/backend/`
- [ ] T004 Create k8s directory structure at `todo_app/phase_4/k8s/helm/todo-app/`

**Checkpoint ✅**: Phase 4 directory exists with frontend/, backend/, k8s/ subdirectories

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify Phase 3 code works and tools are available

**⚠️ CRITICAL**: No containerization can begin until this phase is complete

- [ ] T005 Verify Phase 3 frontend builds successfully with `npm run build`
- [ ] T006 Verify Phase 3 backend runs successfully with `uvicorn`
- [ ] T007 [P] Verify Docker is installed and running with `docker --version`
- [ ] T008 [P] Verify Minikube is available with `minikube version`
- [ ] T009 [P] Verify Helm is installed with `helm version`
- [ ] T010 [P] Verify kubectl is configured with `kubectl version`

**Checkpoint ✅**: All tools verified, Phase 3 code builds successfully

---

## Phase 3: User Story 2 - Containerize Applications (Priority: P1) 🎯 MVP

**Goal**: Create production-ready Docker images for frontend and backend

**Independent Test**: Run `docker build` and verify images are under size limits

**Why First?**: Containers MUST exist before Kubernetes deployment (US2 blocks US1)

### Implementation for US2

- [ ] T011 [P] [US2] Create `.dockerignore` for frontend at `todo_app/phase_4/frontend/.dockerignore`
- [ ] T012 [P] [US2] Create `.dockerignore` for backend at `todo_app/phase_4/backend/.dockerignore`
- [ ] T013 [US2] Create multi-stage Dockerfile for frontend at `todo_app/phase_4/frontend/Dockerfile`
  - Stage 1: deps (node:20-alpine)
  - Stage 2: builder (npm run build)
  - Stage 3: runner (standalone output, non-root user)
- [ ] T014 [US2] Create multi-stage Dockerfile for backend at `todo_app/phase_4/backend/Dockerfile`
  - Stage 1: builder (python:3.13-slim with uv)
  - Stage 2: runner (minimal runtime, non-root user)
- [ ] T015 [US2] Build frontend image with `docker build -t todo-frontend:v1.0.0 ./frontend`
- [ ] T016 [US2] Build backend image with `docker build -t todo-backend:v1.0.0 ./backend`
- [ ] T017 [US2] Verify frontend image size is under 500MB with `docker images`
- [ ] T018 [US2] Verify backend image size is under 300MB with `docker images`
- [ ] T019 [US2] Test frontend container locally with `docker run -p 3000:3000 todo-frontend:v1.0.0`
- [ ] T020 [US2] Test backend container locally with `docker run -p 8000:8000 todo-backend:v1.0.0`

**Checkpoint ✅**: Both Docker images built, tested locally, sizes within limits

---

## Phase 4: User Story 3 - Helm Charts (Priority: P1)

**Goal**: Create Helm chart to manage Kubernetes deployment configuration

**Independent Test**: Run `helm lint` and `helm template` to validate chart

### Implementation for US3

- [ ] T021 [US3] Create Chart.yaml at `todo_app/phase_4/k8s/helm/todo-app/Chart.yaml`
- [ ] T022 [US3] Create values.yaml with defaults at `todo_app/phase_4/k8s/helm/todo-app/values.yaml`
- [ ] T023 [US3] Create .helmignore at `todo_app/phase_4/k8s/helm/todo-app/.helmignore`
- [ ] T024 [US3] Create _helpers.tpl at `todo_app/phase_4/k8s/helm/todo-app/templates/_helpers.tpl`
- [ ] T025 [P] [US3] Create frontend-deployment.yaml at `todo_app/phase_4/k8s/helm/todo-app/templates/frontend-deployment.yaml`
- [ ] T026 [P] [US3] Create backend-deployment.yaml at `todo_app/phase_4/k8s/helm/todo-app/templates/backend-deployment.yaml`
- [ ] T027 [P] [US3] Create frontend-service.yaml (NodePort) at `todo_app/phase_4/k8s/helm/todo-app/templates/frontend-service.yaml`
- [ ] T028 [P] [US3] Create backend-service.yaml (ClusterIP) at `todo_app/phase_4/k8s/helm/todo-app/templates/backend-service.yaml`
- [ ] T029 [US3] Validate Helm chart with `helm lint ./k8s/helm/todo-app`
- [ ] T030 [US3] Generate manifests with `helm template todo-app ./k8s/helm/todo-app`

**Checkpoint ✅**: Helm chart passes lint, generates valid Kubernetes YAML

---

## Phase 5: User Story 4 - Secrets Management (Priority: P2)

**Goal**: Secure storage for database credentials and API keys

**Independent Test**: Deploy with secrets and verify env vars are injected (not hardcoded)

### Implementation for US4

- [ ] T031 [P] [US4] Create configmap.yaml at `todo_app/phase_4/k8s/helm/todo-app/templates/configmap.yaml`
- [ ] T032 [P] [US4] Create secret.yaml at `todo_app/phase_4/k8s/helm/todo-app/templates/secret.yaml`
- [ ] T033 [US4] Update values.yaml with secrets placeholders (databaseUrl, openaiApiKey, betterAuthSecret)
- [ ] T034 [US4] Update deployments to reference secrets via envFrom

**Checkpoint ✅**: Secrets template created, deployments reference secrets correctly

---

## Phase 6: User Story 6 - Health Monitoring (Priority: P2)

**Goal**: Add liveness and readiness probes for automatic recovery

**Independent Test**: Kill pod and verify auto-restart, check health endpoints

### Implementation for US6

- [ ] T035 [US6] Add health endpoint to backend at `todo_app/phase_4/backend/src/routers/health.py` (if not exists)
- [ ] T036 [US6] Update backend-deployment.yaml with liveness/readiness probes
- [ ] T037 [US6] Update frontend-deployment.yaml with readiness probe
- [ ] T038 [US6] Add resource limits/requests to both deployments

**Checkpoint ✅**: Health probes configured, resource limits set

---

## Phase 7: User Story 1 - Deploy to Kubernetes (Priority: P1)

**Goal**: Successfully deploy application to Minikube cluster

**Independent Test**: Access application via `minikube service` URL

**Note**: This phase executes the deployment - depends on US2, US3, US4, US6

### Implementation for US1

- [ ] T039 [US1] Start Minikube cluster with `minikube start --cpus=4 --memory=4096`
- [ ] T040 [US1] Load frontend image into Minikube with `minikube image load todo-frontend:v1.0.0`
- [ ] T041 [US1] Load backend image into Minikube with `minikube image load todo-backend:v1.0.0`
- [ ] T042 [US1] Deploy with Helm (provide secrets via --set flags)
- [ ] T043 [US1] Verify all pods are Running with `kubectl get pods`
- [ ] T044 [US1] Get frontend URL with `minikube service todo-frontend-svc --url`
- [ ] T045 [US1] Test chatbot functionality in browser
- [ ] T046 [US1] Verify backend health endpoint with `kubectl exec`

**Checkpoint ✅**: Application deployed, accessible via browser, chatbot works

---

## Phase 8: User Story 5 - AI DevOps Documentation (Priority: P2)

**Goal**: Document AI-assisted DevOps tools usage

**Independent Test**: Documentation includes working examples

### Implementation for US5

- [ ] T047 [P] [US5] Create AI-DEVOPS.md at `todo_app/phase_4/AI-DEVOPS.md`
- [ ] T048 [US5] Document Gordon usage examples for Docker operations
- [ ] T049 [US5] Document kubectl-ai usage examples for K8s queries
- [ ] T050 [US5] Document kagent usage examples for cluster analysis
- [ ] T051 [US5] Add manual command alternatives for each AI tool

**Checkpoint ✅**: AI DevOps documentation complete with examples

---

## Phase 9: User Story 7 & 8 - Bonus Skills (Priority: P3) 🎁

**Goal**: Create reusable Claude Code skills for deployment

**Independent Test**: Invoke skill and verify it generates correct artifacts

### Implementation for US7 & US8

- [ ] T052 [P] [US7] Create k8s-deploy skill at `.claude/skills/k8s-deploy.md`
- [ ] T053 [P] [US8] Create deployment-blueprint skill at `.claude/skills/deployment-blueprint.md`
- [ ] T054 [US7] Test k8s-deploy skill generates Dockerfile template
- [ ] T055 [US8] Test deployment-blueprint skill generates Helm chart for Next.js+FastAPI

**Checkpoint ✅**: Both bonus skills created and tested

---

## Phase 10: Polish & Documentation

**Purpose**: Final cleanup and documentation

- [ ] T056 [P] Update project README.md with Phase 4 deployment instructions
- [ ] T057 [P] Create DEPLOYMENT.md with complete deployment guide at `todo_app/phase_4/DEPLOYMENT.md`
- [ ] T058 Verify quickstart.md steps work end-to-end
- [ ] T059 Run final `helm lint` and fix any warnings
- [ ] T060 Create <90 second demo video script

**Checkpoint ✅**: Documentation complete, deployment reproducible

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL
    ↓
Phase 3 (US2: Docker) ← BLOCKS US1
    ↓
Phase 4 (US3: Helm) ← BLOCKS US1
    ↓
Phase 5 (US4: Secrets) ← BLOCKS US1
    ↓
Phase 6 (US6: Health) ← BLOCKS US1
    ↓
Phase 7 (US1: Deploy) ← CORE DELIVERABLE
    ↓
Phase 8 (US5: AI Docs) ← Can parallel with Phase 9
    ↓
Phase 9 (US7/8: Bonus) ← Optional
    ↓
Phase 10 (Polish)
```

### Critical Path

```
T001 → T005/T006 → T013/T014 → T021/T022 → T031/T032 → T035/T036 → T039-T046
```

### Parallel Opportunities

**Phase 1 (Setup)**:
```
T002 (copy frontend) ║ T003 (copy backend) - different directories
```

**Phase 2 (Foundational)**:
```
T007 (docker) ║ T008 (minikube) ║ T009 (helm) ║ T010 (kubectl)
```

**Phase 3 (Docker)**:
```
T011 (.dockerignore frontend) ║ T012 (.dockerignore backend)
T015 (build frontend) ║ T016 (build backend) - after Dockerfiles done
```

**Phase 4 (Helm)**:
```
T025 (frontend-deployment) ║ T026 (backend-deployment)
T027 (frontend-service) ║ T028 (backend-service)
```

**Phase 5 (Secrets)**:
```
T031 (configmap) ║ T032 (secret)
```

---

## Implementation Strategy

### MVP First (Phases 1-7)

1. ✅ Setup + Foundational (T001-T010)
2. ✅ Containerize (T011-T020)
3. ✅ Helm Charts (T021-T030)
4. ✅ Secrets (T031-T034)
5. ✅ Health Probes (T035-T038)
6. ✅ **DEPLOY** (T039-T046) → **MVP COMPLETE**
7. 🎯 Test chatbot in Kubernetes

### Bonus Points (Phases 8-9)

8. AI DevOps Docs (T047-T051) → +Hackathon points
9. Reusable Skills (T052-T055) → +200 bonus points

### Final (Phase 10)

10. Polish & Documentation (T056-T060) → Demo ready

---

## Task Summary by User Story

| User Story | Tasks | Priority | Status |
|------------|-------|----------|--------|
| US2: Containerize | T011-T020 (10) | P1 | Core |
| US3: Helm Charts | T021-T030 (10) | P1 | Core |
| US4: Secrets | T031-T034 (4) | P2 | Core |
| US6: Health | T035-T038 (4) | P2 | Core |
| US1: Deploy | T039-T046 (8) | P1 | Core |
| US5: AI Docs | T047-T051 (5) | P2 | Enhancement |
| US7/8: Skills | T052-T055 (4) | P3 | Bonus |
| Setup/Polish | T001-T010, T056-T060 (15) | - | Infrastructure |

**Total**: 60 tasks

---

## Notes

- All tasks are atomic and independently completable
- [P] marks tasks that can run in parallel
- Commit after each checkpoint
- Run `helm lint` after any chart changes
- Run `kubectl get pods` to verify deployment status
- Demo video should show: build → deploy → access → chatbot working
