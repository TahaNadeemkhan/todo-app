# ADR-0001: Phase 5 Infrastructure: Redpanda and PostgreSQL with Dapr

- **Status:** Accepted
- **Date:** 2026-01-05
- **Feature:** 005-event-driven-cloud
- **Context:** Implementing Phase 5 event-driven microservices requires a robust message broker and reliable state store. The user requested a modern approach using Redpanda for Kafka-compatible event streaming and PostgreSQL for the Dapr state store to optimize for Hackathon performance and bonus criteria.

## Decision

We will use the following infrastructure cluster for Phase 5:
- **Event Streaming (Kafka)**: **Redpanda Cloud** (production) and Redpanda Bitnami image (local). Chosen for its C++ high-performance architecture, Kafka-compatibility without Zookeeper complexity, and modern observability features.
- **State Store**: **Neon Serverless PostgreSQL**. Reused via the Dapr State Store building block for consistent persistence across microservices.
- **Abstraction Layer**: **Dapr (Distributed Application Runtime)**. All microservices MUST use Dapr building blocks (Pub/Sub, State, Secrets, Bindings) to ensure deployment portability across Minikube and secondary Cloud K8s (DOKS/GKE).

## Consequences

### Positive

- **Modern Stack Bonus**: Using Redpanda and Dapr aligns with high-end hackathon criteria (+100 potential bonus points).
- **Reduced Complexity**: Redpanda simplifies local development by removing Zookeeper overhead.
- **Infrastructure Portability**: Dapr allows switching from local PostgreSQL/Kafka to cloud-managed versions via YAML configuration without touching application code.
- **High Performance**: Redpanda provides low-latency streaming essential for real-time task sync.

### Negative

- **Resource Usage**: Running Dapr sidecars and Redpanda containers locally requires significant RAM (Recommended: 16GB+ RAM environment).
- **Learning Curve**: Team must gain proficiency in Dapr component configuration and event-driven patterns.

## Alternatives Considered

- **Alternative A (Standard Kafka)**: Using standard Apache Kafka (Bitnami). Rejected in favor of Redpanda's single-binary simplicity and performance.
- **Alternative B (Redis State Store)**: Using Redis for state. Rejected as PostgreSQL (Neon) is already the primary data source and provides stronger persistence guarantees for task state.

## References

- Feature Spec: [specs/005-event-driven-cloud/spec.md](specs/005-event-driven-cloud/spec.md)
- Implementation Plan: [specs/005-event-driven-cloud/plan.md](specs/005-event-driven-cloud/plan.md)
- Related ADRs: none
- Evaluator Evidence: none
