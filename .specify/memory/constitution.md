<!--
Sync Impact Report:
- Version change: 1.2.0 (Minor)
- Principles Defined:
    - I. Spec-Driven Discipline: Mandates spec-first workflow and Claude Code usage.
    - II. Architectural Separation: Enforces clear layering (UI/Service/Repository) and dependency inversion.
    - III. Domain-First Modeling: Requires strict Pydantic models, type hinting, and valid state enforcement.
    - IV. Security by Design: Establishes "Hostile Backend" policy, JWT verification, and secure secrets.
    - V. Deterministic AI & Tooling: Defines strict schemas for MCP tools and stateless agent design.
    - VI. Immutable Infrastructure: Treats infrastructure (Helm, Docker) as code with structured logging.
    - VII. Event-Driven Decoupling: Mandates eventual consistency and Dapr abstraction for distributed communication.
    - VIII. Phased Evolution: Mandates sequential development from Phase 1 to Phase 5 as per Hackathon requirements.
    - IX. Test-Driven Development (TDD): Enforces Red-Green-Refactor cycle using pytest.
    - X. Modern Python Tooling: Mandates usage of `uv` for dependency management.
    - XI. The Nine Pillars of AI-Driven Development: Explicitly adopts the nine pillars as guiding architectural philosophy.
- Governance: Established amendment process and versioning rules.
- Templates requiring updates:
    - .specify/templates/plan-template.md (✅ updated - conceptually)
    - .specify/templates/spec-template.md (✅ updated - conceptually)
    - .specify/templates/tasks-template.md (✅ updated - conceptually)
-->

# Todo App - Hackathon II Constitution

## Core Principles

### I. Spec-Driven Discipline
The Specification is the Source of Truth. Implementation code is merely a build artifact of the specification.
- **Workflow:** No implementation code is written without a preceding or concurrent update to the relevant Specification (Spec-Kit Plus).
- **Ambiguity:** If the implementation deviates from the Spec, it is a bug in the implementation. If the Spec is ambiguous, it is a bug in the Spec.
- **Tooling:** All major features and architectural changes must be generated via **Claude Code** based on the Specs to ensure compliance and consistency.
- **ADRs:** Significant architectural decisions must be documented in an Architectural Decision Record (ADR) before implementation.

### II. Architectural Separation
The system must maintain strict separation of concerns to support evolutionary growth from CLI to Cloud-Native.
- **Layering:** Code must be organized into distinct layers:
    - **UI/Interface Layer:** (CLI, Web Frontend, Chatbot) Handles I/O only. Knows nothing of storage.
    - **Service/Domain Layer:** Contains pure business logic. Agnostic to the interface and storage mechanism.
    - **Repository/Data Layer:** Handles persistence (Memory, SQL, etc.). Must implement an Interface/Abstract Base Class to allow swapping backends without touching business logic.
- **Dependency Rule:** Source code dependencies can only point inward. The Service Layer does not depend on the UI or the Database; the UI and Database depend on the Service Layer interfaces.

### III. Domain-First Modeling
Data integrity and valid state are enforced at the domain level, not the UI level.
- **Strict Typing:** Python code must use strictly typed definitions (Python 3.13+ type hints, Pydantic models). `Any` is forbidden unless strictly justified.
- **Validation:** Domain entities (e.g., `Task`) must be self-validating. Invalid states (e.g., empty title) must be rejected by the model/constructor, not just the UI.
- **Entities:** Objects must use structured definitions (e.g., Enums for status, Timezone-aware datetimes for timestamps).

### IV. Security by Design
Security is established through trust boundaries and rigorous validation, not just encryption.
- **Hostile Backend:** The Backend Service must treat the Frontend as "Hostile Territory." Never trust client input.
- **Authentication:** Identity is verified via JWT signature checks at the middleware level before business logic execution.
- **Authorization:** Resource ownership is enforced via extracted token claims (User ID). The request body is never the source of truth for identity.
- **Secrets Management:** Secrets and API keys must never be hardcoded. They are injected via environment variables or secret stores (Dapr/K8s Secrets).

### V. Deterministic AI & Tooling
AI agents must be engineered for reliability and determinism through strict tooling contracts.
- **Strict Schemas:** MCP Tools must be defined with rigid Pydantic schemas. Tool inputs are validated before execution.
- **Stateless Agents:** The AI Agent service is stateless. Context is derived solely from the conversation history stored in the database.
- **Tool-First:** The AI's "intelligence" is constrained and directed by the tools provided. It does not hallucinate actions; it invokes defined tools.

### VI. Immutable Infrastructure
Infrastructure is Code. Deployments must be reproducible and observable.
- **IaC:** Helm charts, Dockerfiles, and Kubernetes manifests are source code. They are versioned, linted, and reviewed.
- **No Drift:** Manual `kubectl` edits to production are forbidden. Changes are made to the codebase/charts and redeployed.
- **Observability:** Applications must emit structured (JSON) logs to facilitate debugging in containerized environments. "Works on my machine" is not an acceptable defense.

### VII. Event-Driven Decoupling
Distributed components communicate asynchronously to ensure scalability and resilience.
- **Eventual Consistency:** Systems should not block waiting for downstream side effects (e.g., notifications). Acknowledge receipt, then process asynchronously.
- **Abstraction:** Direct dependencies on message brokers (e.g., Kafka libraries) are minimized. Use Dapr or similar abstractions to decouple application logic from infrastructure implementation.
- **Idempotency:** Message consumers must handle duplicate events gracefully without corrupting state.

### VIII. Phased Evolution
The project development must follow the strict 5-phase evolution path defined in the Hackathon requirements.
- **Sequential Progression:** Development must proceed sequentially from Phase 1 (Console App) through Phase 5 (Cloud Deployment). Skipping phases is prohibited.
- **Iterative Refinement:** Each phase builds upon the previous one. Code must be refactored, not rewritten, to accommodate new requirements (e.g., migrating from In-Memory to SQLModel in Phase 2).
- **Compliance:** Each phase must meet all defined requirements and deliverables before proceeding to the next.
    - **Phase 1 (Console App):** Completed as a foundational CLI application.
    - **Phase 2 (Web App):** Develop with Python FastAPI, SQLModel (for Neon Serverless PostgreSQL), Next.js 16+ (App Router), Better Auth with JWT, and multi-user API patterns (e.g., `/api/{user_id}/tasks`). Implement a PATCH endpoint for task completion.
    - **Phase 3 (AI Chatbot):** Integrate OpenAI ChatKit for chat UI, Claude Agent SDK for custom agents, and Claude Code MCP SDK for custom tools. Ensure stateless chat service design.
    - **Phase 4 (Cloud-Native Deployment):** Containerize with Docker, deploy locally with Minikube, manage with Helm charts, and integrate AIOps using `kubectl-ai` and `kagent`.
    - **Phase 5 (Event-Driven Microservices):** Implement event streaming with Kafka/Redpanda, leverage Dapr for distributed application building blocks, and deploy to managed Kubernetes services (DigitalOcean DOKS, GKE, AKS) with robust CI/CD pipelines.

### IX. Test-Driven Development (TDD)
Tests define the success criteria before code is written.
- **Red-Green-Refactor:** All features must follow the TDD cycle: Write failing test -> Write minimal code to pass -> Refactor.
- **Framework:** `pytest` is the mandatory testing framework.
- **Coverage:** Tests must cover Unit (Service/Repository layers) and Integration (CLI/API) scenarios.

### X. Modern Python Tooling
The project will utilize modern, efficient Python tooling as mandated.
- **Package Management:** `uv` is the exclusive package manager for all Python dependency resolution, virtual environment management, and project execution.
- **Runtime:** Python 3.13+ is required.

### XI. The Nine Pillars of AI-Driven Development
The project explicitly adopts the Nine Pillars of AI-Driven Development as its architectural philosophy.
1.  **Spec-Driven Development:** Specs are the source of truth.
2.  **Reusable Intelligence:** Agents skills and subagents.
3.  **Cloud-Native AI:** Microservices on Kubernetes.
4.  **Event-Driven Architecture:** Asynchronous communication via Kafka/Dapr.
5.  **AIOps:** AI-assisted operations (kubectl-ai, kagent).
6.  **Security by Design:** Zero trust, JWT, secrets management.
7.  **Deterministic Tooling:** Strict MCP schemas.
8.  **Stateless Architecture:** Scalable, resilient services.
9.  **Immutable Infrastructure:** Infrastructure as Code.

## Governance

This Constitution supersedes all other coding practices. It is the highest authority for architectural and development decisions.

### Amendment Process
- Proposed changes must be submitted via a Pull Request updating this file.
- Changes require justification based on project evolution or new constraints.
- "Hotfixes" to principles are not permitted; principles change only through deliberate consensus.

### Versioning
- **Major:** Fundamental shift in architectural philosophy (e.g., switching from Spec-Driven to Code-First).
- **Minor:** Addition of new principles or significant clarification of existing ones.
- **Patch:** Wording refinements, typo fixes, or non-semantic updates.

### Compliance
- All Pull Requests must be reviewed against these principles.
- Code reviews must explicitly cite violations of these principles (e.g., "Violates Principle II: UI logic found in Service Layer").

**Version**: 1.2.0 | **Ratified**: 2025-12-08 | **Last Amended**: 2025-12-08