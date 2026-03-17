# Data Model & Infrastructure: Fix Phase 5 Deployment

**Created**: 2026-03-06
**Feature**: 001-fix-phase5-deployment

## Dapr Components

### Kafka PubSub (`kafka-pubsub`)

- **Kind**: `Component` (`pubsub.kafka`)
- **Metadata**:
    - `brokers`: `todo-app-kafka.default.svc.cluster.local:9092`
    - `authType`: `none` (development)

### PostgreSQL StateStore (`statestore`)

- **Kind**: `Component` (`state.postgresql`)
- **Metadata**:
    - `connectionString`: `SecretKeyRef: postgres-credentials/connectionString`

## Kubernetes Secrets

### `postgres-credentials`

- **Type**: `Opaque`
- **Keys**:
    - `connectionString`: Full PostgreSQL connection URL.

### `jwt-secret`

- **Type**: `Opaque`
- **Keys**:
    - `secret_key`: Secure key for JWT signing.

### `gemini-api-key`

- **Type**: `Opaque`
- **Keys**:
    - `api_key`: Google Gemini API key.

## Internal Service Communication (Dapr HTTP API)

### Event Publishing

- **Method**: `POST`
- **URL**: `http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}`
- **Payload**:
    ```json
    {
      "event_id": "uuid",
      "event_type": "type",
      "data": { ... }
    }
    ```

### Service Invocation (Future)

- **Method**: `POST/GET`
- **URL**: `http://localhost:3500/v1.0/invoke/{app_id}/method/{method_name}`
