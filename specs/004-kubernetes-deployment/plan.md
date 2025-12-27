# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-kubernetes-deployment` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-kubernetes-deployment/spec.md`

---

## Summary

Deploy the Phase 3 AI-powered Todo Chatbot application to a local Kubernetes cluster (Minikube) using containerization, Helm charts, and AI-assisted DevOps tools. The implementation includes:

1. **Dockerization**: Multi-stage builds for Next.js frontend and FastAPI backend
2. **Helm Charts**: Single umbrella chart managing all Kubernetes resources
3. **Minikube Deployment**: Local K8s cluster with NodePort access
4. **AI DevOps**: Documentation for Gordon, kubectl-ai, and kagent usage
5. **Bonus**: Reusable deployment skills for Claude Code

---

## Technical Context

**Language/Version**:
- Frontend: Node.js 20 (Next.js 15+)
- Backend: Python 3.13+ (FastAPI)
- Infrastructure: YAML (Kubernetes manifests), Go templates (Helm)

**Primary Dependencies**:
- Docker 20.10+
- Minikube 1.30+
- Helm 3.12+
- kubectl 1.28+

**Storage**: External Neon PostgreSQL (no local database in K8s)

**Testing**:
- `helm lint` for chart validation
- `kubectl` commands for deployment verification
- Health check endpoints for runtime validation

**Target Platform**: Local Kubernetes (Minikube on Linux/WSL2)

**Project Type**: Web application (frontend + backend) with infrastructure-as-code

**Performance Goals**:
- Pod startup < 30 seconds
- Health check response < 5 seconds
- Image size: Frontend < 500MB, Backend < 300MB

**Constraints**:
- Minikube: 4GB RAM, 4 CPUs minimum
- No cloud dependencies (local deployment only)
- Secrets via Helm --set (not committed to git)

**Scale/Scope**:
- 2 replicas per service (default)
- Single Minikube cluster
- ~20 Kubernetes resources total

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Check ✅

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Discipline | ✅ PASS | Spec written before implementation |
| II. Architectural Separation | ✅ PASS | Frontend/Backend remain separate services |
| III. Domain-First Modeling | ✅ N/A | No new domain models (infrastructure phase) |
| IV. Security by Design | ✅ PASS | Secrets via K8s Secrets, non-root containers |
| V. Deterministic AI & Tooling | ✅ N/A | No new AI tools in this phase |
| VI. Immutable Infrastructure | ✅ PASS | Helm charts as IaC, no manual kubectl edits |
| VII. Event-Driven Decoupling | ✅ N/A | Deferred to Phase 5 |
| VIII. Phased Evolution | ✅ PASS | Phase 4 follows Phase 3 completion |
| IX. Test-Driven Development | ⚠️ PARTIAL | Infrastructure testing via validation commands |
| X. Modern Python Tooling | ✅ PASS | Using uv in Dockerfile |
| XI. Nine Pillars | ✅ PASS | Cloud-Native AI, AIOps, Immutable Infrastructure |

### Post-Design Re-Check ✅

All constitution principles validated after Phase 1 design completion.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-kubernetes-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation plan)
├── research.md          # Technical research and decisions
├── data-model.md        # Kubernetes resource entities
├── quickstart.md        # Deployment quick start guide
├── contracts/           # Interface contracts
│   └── README.md        # Helm and Docker contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Implementation tasks (created by /sp.tasks)
```

### Source Code (repository root)

```text
todo_app/phase_4/
├── frontend/                    # Next.js application (from Phase 3)
│   ├── Dockerfile              # 🆕 Multi-stage build
│   ├── .dockerignore           # 🆕 Exclude unnecessary files
│   ├── package.json
│   ├── next.config.js
│   └── src/
│       ├── app/
│       ├── components/
│       └── lib/
│
├── backend/                     # FastAPI application (from Phase 3)
│   ├── Dockerfile              # 🆕 Multi-stage build
│   ├── .dockerignore           # 🆕 Exclude unnecessary files
│   ├── pyproject.toml
│   └── src/
│       ├── main.py
│       ├── models/
│       ├── routers/
│       └── services/
│
└── k8s/                        # 🆕 Kubernetes configuration
    └── helm/
        └── todo-app/
            ├── Chart.yaml           # Chart metadata
            ├── values.yaml          # Default configuration
            ├── .helmignore          # Exclude files from chart
            └── templates/
                ├── _helpers.tpl     # Template helpers
                ├── frontend-deployment.yaml
                ├── frontend-service.yaml
                ├── backend-deployment.yaml
                ├── backend-service.yaml
                ├── configmap.yaml
                └── secret.yaml
```

**Structure Decision**: Web application structure with added `k8s/` directory for Kubernetes infrastructure. Phase 4 code lives in `todo_app/phase_4/` to maintain phase separation while reusing Phase 3 application code.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    default namespace                    │ │
│  │                                                         │ │
│  │  ┌─────────────┐         ┌─────────────┐              │ │
│  │  │  ConfigMap  │         │   Secret    │              │ │
│  │  │ todo-config │         │ todo-secrets│              │ │
│  │  └──────┬──────┘         └──────┬──────┘              │ │
│  │         │                       │                      │ │
│  │         └───────────┬───────────┘                      │ │
│  │                     │                                  │ │
│  │         ┌───────────┴───────────┐                      │ │
│  │         ▼                       ▼                      │ │
│  │  ┌─────────────┐         ┌─────────────┐              │ │
│  │  │ Deployment  │         │ Deployment  │              │ │
│  │  │  frontend   │         │   backend   │              │ │
│  │  │ replicas: 2 │         │ replicas: 2 │              │ │
│  │  └──────┬──────┘         └──────┬──────┘              │ │
│  │         │                       │                      │ │
│  │         ▼                       ▼                      │ │
│  │  ┌─────────────┐         ┌─────────────┐              │ │
│  │  │   Service   │ ──────▶ │   Service   │              │ │
│  │  │  NodePort   │         │  ClusterIP  │              │ │
│  │  │   :30080    │         │   :8000     │              │ │
│  │  └──────┬──────┘         └─────────────┘              │ │
│  │         │                                              │ │
│  └─────────┼──────────────────────────────────────────────┘ │
│            │                                                 │
└────────────┼─────────────────────────────────────────────────┘
             │
             ▼
      ┌─────────────┐
      │   Browser   │
      │ localhost:  │
      │   30080     │
      └─────────────┘
             │
             ▼
      ┌─────────────┐
      │  Neon DB    │
      │ (External)  │
      └─────────────┘
```

---

## Implementation Phases

### Phase A: Containerization
1. Create frontend Dockerfile (multi-stage, Node 20 Alpine)
2. Create backend Dockerfile (multi-stage, Python 3.13 slim)
3. Add .dockerignore files
4. Verify builds locally

### Phase B: Helm Chart Development
1. Initialize Helm chart structure
2. Create deployment templates
3. Create service templates
4. Create configmap and secret templates
5. Configure values.yaml with defaults
6. Validate with helm lint

### Phase C: Minikube Deployment
1. Start Minikube cluster
2. Build and load Docker images
3. Deploy with helm install
4. Verify pod status
5. Test application access

### Phase D: Documentation & AI Tools
1. Document Gordon usage
2. Document kubectl-ai usage
3. Document kagent usage
4. Create troubleshooting guide

### Phase E: Bonus Features (Optional)
1. Create k8s-deploy skill
2. Create deployment-blueprint skill
3. Test skills on sample project

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Docker base images | Alpine/Slim | Smaller size, security |
| Helm structure | Single umbrella chart | Simpler deployment |
| Frontend service | NodePort | Direct Minikube access |
| Backend service | ClusterIP | Internal only |
| Secrets handling | Helm --set | Not in version control |
| Image loading | minikube image load | No registry needed |

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Image too large | Multi-stage builds, Alpine base |
| Secrets exposed | K8s Secrets, never in git |
| Minikube resources | Document minimum requirements |
| AI tools unavailable | Provide manual alternatives |

---

## Complexity Tracking

> No constitution violations requiring justification.

All design decisions align with constitution principles. Infrastructure-as-Code via Helm charts satisfies Principle VI (Immutable Infrastructure).

---

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Execute tasks using Claude Code
3. Verify deployment with checklist
4. Create demo video (<90 seconds)
5. Submit for hackathon review

---

## Related Documents

- [spec.md](./spec.md) - Feature specification
- [research.md](./research.md) - Technical research
- [data-model.md](./data-model.md) - Kubernetes entities
- [quickstart.md](./quickstart.md) - Deployment guide
- [contracts/README.md](./contracts/README.md) - Interface contracts
