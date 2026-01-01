# Tasks: Local Kubernetes Deployment

**Branch**: `004-phase-4-kubernetes` | **Date**: 2025-12-31
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

## Overview

Implementation tasks for deploying Phase 3 AI Chatbot to local Kubernetes (Minikube) using Docker containerization, Helm charts, and AI DevOps tools.

**Total Tasks**: 36
**Estimated Phases**: 9 (Setup → Foundational → Containerize → Helm → Secrets → Health → Deploy → AI Ops → Polish)

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[US#]**: User story reference (US1-US8)
- All paths relative to `todo_app/phase_4/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create Phase 4 directory structure and copy Phase 3 code

- [X] T001 Create phase_4 directory structure at `todo_app/phase_4/`
- [X] T002 [P] Copy Phase 3 frontend code to `todo_app/phase_4/frontend/`
- [X] T003 [P] Copy Phase 3 backend code to `todo_app/phase_4/backend/`
- [X] T004 Create k8s directory structure at `todo_app/phase_4/k8s/helm/todo-app/`

**Checkpoint ✅**: Phase 4 directory exists with frontend/, backend/, k8s/ subdirectories

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify Phase 3 code works and tools are available

- [X] T005 Verify Phase 3 frontend builds successfully with `npm run build` ✅
- [X] T006 Verify Phase 3 backend runs successfully with `uvicorn` ✅
- [X] T007 [P] Verify Docker/Minikube/Helm/kubectl are installed ✅

---

## Phase 3: AI-Assisted Containerization (US2 & US5)

**Goal**: Create production-grade optimized Docker images

- [X] T008 [P] [US2] Create `.dockerignore` for frontend and backend ✅
- [X] T009 [US2] Create initial multi-stage Dockerfiles ✅
- [X] T010 [US5] Run `gordon analyze frontend/Dockerfile` and apply optimizations ✅
- [X] T011 [US5] Run `gordon analyze backend/Dockerfile` and apply optimizations ✅
- [X] T012 [US2] Build frontend image with `docker build -t todo-frontend:v1.0.0 ./frontend` ✅
- [X] T013 [US2] Build backend image with `docker build -t todo-backend:v1.0.0 ./backend` ✅
- [X] T014 [US5] Run `gordon scanner` for security audit on both images ✅

---

## Phase 4: Helm Chart Development (US3)

**Goal**: Create Helm chart for Kubernetes deployment

- [X] T015 Create generic Helm chart structure and helpers ✅
- [X] T016 Implement deployment templates for frontend and backend ✅
- [X] T017 Implement service templates (NodePort/ClusterIP) ✅
- [X] T018 Validate basic Helm chart with `helm lint` ✅

---

## Phase 5: AI-Optimized Manifests (US3 & US5)

**Goal**: Enhance Kubernetes setup using kubectl-ai

- [X] T019 [US5] Use `kubectl-ai` to generate Horizontal Pod Autoscaler (HPA) manifest ✅
- [X] T020 [US5] Use `kubectl-ai` to generate Pod Disruption Budget (PDB) ✅
- [X] T021 [US5] Add HPA/PDB to Helm templates directory ✅

---

## Phase 6: Configuration & Health (US4 & US6)

**Goal**: Secure storage and automatic recovery

- [X] T022 Create configmap and secret templates ✅
- [X] T023 Update deployments with liveness/readiness probes ✅
- [X] T024 Add resource limits/requests to both deployments ✅

---

## Phase 7: Local Kubernetes Deployment (US1)

**Goal**: Successfully deploy to Minikube

- [X] T025 Start Minikube cluster (CLEAN START) ✅
- [X] T026 Load optimized frontend/backend images into Minikube ✅
- [X] T027 Deploy with Helm (provide secrets via --set flags) ✅
- [X] T028 Verify all pods are Running with `kubectl get pods` ✅

---

## Phase 8: AI-Powered Cluster Review (US5)

**Goal**: Use kagent for automated efficiency audit

- [X] T029 [US5] Run `kagent analyze` to generate cluster efficiency report ✅
- [X] T030 [US5] Apply `kagent` recommendations for resource right-sizing ✅
- [X] T031 Final chatbot functionality test in browser via Minikube URL ✅

---

## Phase 9: Polish & Documentation

- [X] T032 Update project README.md (Vercel ignore added) ✅
- [X] T033 Create DEPLOYMENT.md (Complete guide) ✅
- [X] T034 Create AI-DEVOPS.md (Gordon, kubectl-ai, kagent usage guide) ✅
- [X] T035 Final `helm lint` and cleanup ✅

---

## Notes

- **Parallelism**: T010/T011 can run together.
- **Critical Path**: T010 -> T012 -> T026 -> T027.
- **Commit**: After each Phase Checkpoint.
- **Skills**: k8s-deploy and deployment-blueprint skills created in `.claude/skills/`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
