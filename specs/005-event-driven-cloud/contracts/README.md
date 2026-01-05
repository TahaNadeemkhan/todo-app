# API Contracts: Event-Driven Cloud Deployment

**Feature**: 005-event-driven-cloud
**Created**: 2026-01-04

## Overview

This directory contains API contract specifications for Phase 5. Contracts define the interfaces between:
1. **Frontend ↔ Backend API** (HTTP/REST)
2. **Backend ↔ Microservices** (Dapr Service Invocation)
3. **Services ↔ Kafka** (Event Pub/Sub via Dapr)

## Contract Files

- `backend-api.md` - Backend REST API endpoints (extended from Phase 2/3)
- `notification-service.md` - Notification Service API (Dapr invocation + Kafka)
- `recurring-task-service.md` - Recurring Task Service API (Dapr invocation + Kafka)
- `kafka-events.md` - Kafka event schemas and topic specifications
- `dapr-components.md` - Dapr component configurations

## Contract Principles

All contracts follow these principles from the Constitution (Section IV: Security by Design):

1. **Hostile Backend Assumption**: Backend treats frontend as hostile territory
2. **JWT Authentication**: User identity verified via JWT signature at middleware
3. **Resource Ownership**: User ID extracted from JWT claims, not request body
4. **Input Validation**: Pydantic models validate all inputs before business logic
5. **Idempotency**: Event consumers handle duplicate events gracefully

## Versioning

- API endpoints: `/api/v1/...` (versioned in URL path)
- Kafka events: `<event-type>.v1` (versioned in event_type field)
- Contracts are immutable once deployed; changes require new version

## Testing

- **Contract Tests**: Validate request/response schemas match contracts
- **Integration Tests**: Test actual HTTP/Dapr/Kafka communication
- **E2E Tests**: Test full workflows across multiple services
