---
name: dapr-component-generator
description: Generate Dapr component YAML configurations for Pub/Sub, State, Secrets, Bindings, and Service Invocation. Abstracts infrastructure complexity for Phase 5 microservices.
---

# Dapr Component Generator

## Overview

This skill generates production-ready Dapr component YAML configurations that abstract infrastructure complexity. Dapr provides portable APIs for Pub/Sub, State Management, Secrets, Input/Output Bindings, and Service-to-Service invocation without vendor lock-in.

## When to Use This Skill

- Setting up event-driven microservices with Kafka/Redpanda Pub/Sub
- Configuring distributed state management with PostgreSQL or Redis
- Managing secrets from Kubernetes, Azure Key Vault, or AWS Secrets Manager
- Creating scheduled jobs with Cron bindings for reminders
- Abstracting infrastructure for cloud portability (local → GKE → AKS → OKE)

## Core Dapr Building Blocks

### 1. Pub/Sub Components
- Abstract message brokers (Kafka, Redis, RabbitMQ, NATS)
- Support for topics and subscriptions
- Guaranteed delivery with retries
- Dead letter queues for failed messages

### 2. State Store Components
- Distributed state management
- Support for PostgreSQL, Redis, MongoDB, Cosmos DB
- Strong consistency or eventual consistency options
- Built-in caching and partitioning

### 3. Secret Store Components
- Unified secret retrieval API
- Kubernetes Secrets, Azure Key Vault, AWS Secrets Manager
- Automatic secret rotation support
- No application code changes when switching providers

### 4. Input/Output Bindings
- Trigger microservices on external events
- Cron schedules for periodic tasks
- HTTP webhooks, Kafka topics, Cloud Storage events

### 5. Service Invocation
- Service-to-service calls with automatic retries
- mTLS encryption by default
- Distributed tracing integration

## Usage

### Generate Kafka Pub/Sub Component

```bash
/dapr-component-generator \
  --type=pubsub \
  --provider=kafka \
  --name=kafka-pubsub \
  --brokers=kafka:9092 \
  --output=k8s/dapr-components/
```

### Generate PostgreSQL State Store

```bash
/dapr-component-generator \
  --type=state \
  --provider=postgresql \
  --name=statestore \
  --connection-secret=neon-db-url \
  --output=k8s/dapr-components/
```

### Generate Kubernetes Secret Store

```bash
/dapr-component-generator \
  --type=secretstore \
  --provider=kubernetes \
  --name=kubernetes-secrets \
  --output=k8s/dapr-components/
```

### Generate Cron Binding for Reminders

```bash
/dapr-component-generator \
  --type=binding \
  --provider=cron \
  --name=reminder-scheduler \
  --schedule="@every 1m" \
  --output=k8s/dapr-components/
```

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `--type` | Component type | pubsub, state, binding, secretstore |
| `--provider` | Implementation | kafka, redis, postgresql, kubernetes |
| `--name` | Component name | kafka-pubsub, statestore |
| `--output` | Output directory | k8s/dapr-components/ |
| `--namespace` | Kubernetes namespace | default, production |
| `--brokers` | Kafka broker addresses | kafka:9092 |
| `--schedule` | Cron schedule | @every 1m, */5 * * * * |

## Phase 5 Required Components

### 1. Kafka Pub/Sub Component
- **Purpose**: Event streaming for task events, reminders, notifications
- **Topics**: `task-events`, `reminders`, `task-updates`
- **Consumers**: backend-api, notification-service, recurring-task-service
- **Provider**: Kafka (local) or Redpanda Cloud (production)

### 2. PostgreSQL State Store
- **Purpose**: Distributed state for conversation history
- **Database**: Neon PostgreSQL (existing from Phase 3)
- **Tables**: `dapr_state`, `dapr_metadata`
- **Scopes**: backend-api, notification-service

### 3. Kubernetes Secret Store
- **Purpose**: Centralized secret management
- **Secrets**: database-url, gemini-api-key, openai-api-key, smtp-credentials
- **Scopes**: All services (backend-api, notification-service, frontend)

### 4. Cron Binding for Reminders
- **Purpose**: Check for due reminders every minute
- **Schedule**: `@every 1m`
- **Target Service**: notification-service
- **Endpoint**: `/cron/check-reminders`

## Integration Patterns

### Publishing Events via Dapr HTTP API
No Kafka library needed - just HTTP calls to Dapr sidecar. See [examples.md](examples.md) for complete code.

### Subscribing to Events via FastAPI
Dapr calls your endpoint when events arrive. See [examples.md](examples.md) for subscription setup.

### Saving State via Dapr
Abstract PostgreSQL behind Dapr State API. See [examples.md](examples.md) for state operations.

### Getting Secrets via Dapr
Unified API across all secret providers. See [examples.md](examples.md) for secret retrieval.

## Dapr Component Best Practices

### 1. Use Scopes for Security
- Limit component access to specific app-ids
- Prevents unauthorized service communication
- Example: Only `notification-service` can access email secrets

### 2. Never Store Secrets in YAML
- Always use `secretKeyRef` for sensitive values
- Create Kubernetes secrets separately
- Rotate secrets without changing component config

### 3. Separate Environments with Namespaces
- `development` namespace for local/staging
- `production` namespace for live systems
- Different component configs per environment

### 4. Pin Component Versions
- Specify `version: v1` explicitly
- Prevents breaking changes from auto-upgrades
- Test new versions in staging first

### 5. Use Meaningful Component Names
- `kafka-pubsub` (clear provider)
- `neon-statestore` (clear backend)
- `k8s-secrets` (clear source)

## Provider Options

### Pub/Sub Providers
- `pubsub.kafka` - Apache Kafka / Redpanda
- `pubsub.redis` - Redis Streams
- `pubsub.rabbitmq` - RabbitMQ
- `pubsub.nats` - NATS

### State Store Providers
- `state.postgresql` - PostgreSQL (Neon)
- `state.redis` - Redis
- `state.mongodb` - MongoDB
- `state.cosmosdb` - Azure Cosmos DB

### Secret Store Providers
- `secretstores.kubernetes` - Kubernetes Secrets
- `secretstores.azure.keyvault` - Azure Key Vault
- `secretstores.aws.secretmanager` - AWS Secrets Manager

### Binding Providers
- `bindings.cron` - Scheduled triggers
- `bindings.http` - HTTP webhooks
- `bindings.kafka` - Kafka topics

## Testing Dapr Components

```bash
# Initialize Dapr in Kubernetes
dapr init -k

# Verify components
kubectl get components -n default

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd

# Test Pub/Sub locally
dapr publish --publish-app-id backend-api --pubsub kafka-pubsub --topic task-events --data '{"test":true}'
```

For complete YAML examples and integration code, see [examples.md](examples.md).

## Related Skills

- **kafka-event-schema**: Generate event schemas for Pub/Sub topics
- **microservice-scaffold**: Scaffold Dapr-enabled microservices
- **helm-cloud-chart**: Include Dapr components in Helm charts
- **deployment-blueprint**: Generate Dockerfiles with Dapr sidecars

## Tags

dapr, component, pubsub, state, secrets, bindings, microservices, kubernetes, event-driven, kafka, redis, postgresql
