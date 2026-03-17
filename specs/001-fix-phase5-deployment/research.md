# Research: Fix Phase 5 Deployment

**Created**: 2026-03-06
**Feature**: 001-fix-phase5-deployment

## Key Decisions

### Decision 1: Dapr Python SDK Bypass

- **Decision**: All microservices will communicate with the Dapr sidecar using the direct HTTP API (via `httpx`) instead of the Dapr Python SDK.
- **Rationale**: The `ImportError` related to `dapr.proto.common_v1` on Python 3.13 is a known issue in the SDK. Bypassing it ensures stability across environments.
- **Alternatives considered**:
    - **Fixing the SDK**: Not viable as it requires an upstream fix.
    - **Downgrading Python**: Not preferred as it deviates from the project's target environment.

### Decision 2: Image Tagging Strategy

- **Decision**: All services will be built with the tag `v5.0.2` and loaded into Minikube using `minikube image load`.
- **Rationale**: `v5.0.0` and `v5.0.1` are potentially cached in Minikube's Docker daemon or Kubernetes' internal cache. Using a new tag forces a clean pull/load.
- **Alternatives considered**:
    - **Using `latest`**: Discouraged in Kubernetes for local development due to caching ambiguities.
    - **Image Pruning**: More disruptive and less reliable than tag incrementing.

### Decision 3: Helm Chart Packaging

- **Decision**: The `todo-app` Helm chart will be manually packaged as `todo-app-5.0.0.tgz` before deployment.
- **Rationale**: Helm's automatic packaging during `helm upgrade .` includes the entire parent directory, often exceeding 5MB due to `.venv` and `node_modules`. Manual packaging ensures only necessary files are included.
- **Alternatives considered**:
    - **Fixing `.helmignore`**: Tried, but was unreliable with complex directory nesting in the agent environment.
    - **Increasing Helm Size Limit**: Not an industry-standard solution.

### Decision 4: Initialization Scripting

- **Decision**: A unified `quickstart.md` will document the exact sequence: `minikube delete` -> `minikube start` -> `dapr init -k` -> `kubectl apply -f dapr-components/` -> `kubectl create secret`.
- **Rationale**: Resolves environment volatility where previous Minikube instances left behind stale configurations or missing dependencies.
- **Alternatives considered**:
    - **Manual troubleshooting**: Too slow and error-prone.
