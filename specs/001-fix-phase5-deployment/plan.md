# Implementation Plan: Fix Phase 5 Deployment

**Branch**: `001-fix-phase5-deployment` | **Date**: 2026-03-06 | **Spec**: [specs/001-fix-phase5-deployment/spec.md]
**Input**: Feature specification from `/specs/001-fix-phase5-deployment/spec.md`

## Summary

The primary goal is to stabilize the Phase 5 microservices deployment on Minikube by addressing library bugs, environment volatility, and configuration gaps. The technical approach involves:
1.  **Dapr SDK Bypass**: Using `httpx` for direct Dapr HTTP API calls to avoid the `dapr.proto` ImportError.
2.  **Image Tagging & Loading**: Incrementing image tags to `v5.0.2` and using `minikube image load` to ensure fresh deployments.
3.  **Helm Chart Optimization**: Manually packaging the Helm chart into a `.tgz` file to exclude large non-essential files and avoid size limit errors.
4.  **Automated Initialization**: Creating a sequence to reinstall Dapr, apply components, and create missing secrets (`postgres-credentials`, `jwt-secret`) after a Minikube reset.

## Technical Context

**Language/Version**: Python 3.13 (Backend/Services), TypeScript/React (Frontend)
**Primary Dependencies**: FastAPI, Dapr (via HTTP API), Kafka (via Dapr), PostgreSQL (via Dapr)
**Storage**: Neon PostgreSQL (Production), Local PostgreSQL container (Minikube fallback)
**Testing**: pytest (unit/integration)
**Target Platform**: Kubernetes (Minikube local, DOKS/GKE Cloud)
**Project Type**: Web application (Microservices)
**Performance Goals**: Pods reach Running state within 10 minutes; zero startup errors.
**Constraints**: Helm chart < 5MB; Dapr sidecar active for all services.
**Scale/Scope**: 4 services (Backend, Frontend, Notification, Recurring Task) + Dapr infrastructure.

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-phase5-deployment/
├── spec.md              # Requirements and root cause analysis
├── plan.md              # This file
├── research.md          # Decision log and findings
├── data-model.md        # Dapr component and secret definitions
├── quickstart.md        # Step-by-step recovery and deployment guide
└── tasks.md             # Implementation tasks (Phase 2)
```

### Source Code (repository root)

```text
todo_app/phase_5/
├── backend/             # Python FastAPI service
│   ├── src/             # Source code
│   └── Dockerfile       # Rebuild with v5.0.2
├── frontend/            # React frontend
│   └── Dockerfile       # Rebuild with v5.0.2
├── services/
│   ├── notification-service/
│   │   ├── src/
│   │   └── Dockerfile   # Rebuild with v5.0.2
│   └── recurring-task-service/
│       ├── src/
│       └── Dockerfile   # Rebuild with v5.0.2
└── k8s/
    ├── dapr-components/ # YAML for PubSub, StateStore
    └── helm/
        └── todo-app/    # Helm chart to be packaged as .tgz
```

**Structure Decision**: Option 2: Web application (Microservices). The structure is already established in `todo_app/phase_5/`. The plan focuses on the deployment of these existing services.
