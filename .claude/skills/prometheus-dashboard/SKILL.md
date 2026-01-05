---
name: prometheus-dashboard
description: Generate Prometheus metrics, Grafana dashboards, and alerting rules for monitoring Phase 5 microservices in Kubernetes.
---

# Prometheus & Grafana Dashboard Generator

## Overview

This skill generates complete monitoring stack configurations including Prometheus scrape configs, Grafana dashboards, and alerting rules for Phase 5 event-driven microservices deployed on cloud Kubernetes.

## When to Use This Skill

- Setting up observability for cloud-deployed microservices
- Creating custom Grafana dashboards for task metrics
- Configuring alerts for critical service health
- Monitoring Kafka/Dapr event throughput
- Tracking API latency, error rates, and resource usage
- Fulfilling Phase 5 monitoring requirements

## Core Components Generated

### 1. Prometheus Configuration
- Service discovery for Kubernetes pods
- Scrape configs with proper annotations
- Recording rules for aggregations
- Alert rules for SLO violations

### 2. Grafana Dashboards
- Application metrics dashboard (requests, latency, errors)
- Infrastructure dashboard (CPU, memory, disk)
- Kafka/Dapr event metrics dashboard
- Custom business metrics (tasks created, completed, etc.)

### 3. Alert Rules
- High error rate alerts
- Latency SLO violations
- Resource exhaustion warnings
- Service down alerts
- Database connection failures

## Usage

### Generate Complete Monitoring Stack

```bash
/prometheus-dashboard \
  --app-name=todo-app \
  --services=backend-api,notification-service,recurring-task-service \
  --cloud=gke \
  --output=k8s/monitoring/
```

### Generate Custom Dashboard

```bash
/prometheus-dashboard \
  --type=dashboard \
  --metrics=task_created_total,task_completed_total,reminder_sent_total \
  --output=grafana/dashboards/
```

## Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `--app-name` | Application name | todo-app |
| `--services` | Microservices to monitor | backend-api,notification-service |
| `--type` | Config type | all, prometheus, grafana, alerts |
| `--metrics` | Custom metrics to include | task_created_total,api_latency |
| `--cloud` | Cloud provider | gke, aks, oke |
| `--output` | Output directory | k8s/monitoring/ |

## Phase 5 Monitoring Strategy

### Application Metrics
- **Task Operations**: task_created_total, task_completed_total, task_deleted_total
- **API Performance**: http_request_duration_seconds, http_requests_total
- **Event Processing**: kafka_messages_consumed_total, dapr_events_published_total
- **Notification Delivery**: notification_sent_total, notification_failed_total

### Infrastructure Metrics
- **Resource Usage**: container_cpu_usage, container_memory_usage
- **Pod Health**: kube_pod_status_ready, kube_pod_restarts_total
- **Network**: container_network_receive_bytes, container_network_transmit_bytes

### Business Metrics
- **User Engagement**: active_users_total, tasks_per_user
- **System Health**: database_connections_active, cache_hit_ratio
- **SLO Tracking**: api_availability_percent, p95_latency_seconds

## Key Dashboards

### 1. Application Overview Dashboard
- Request rate, error rate, duration (RED metrics)
- Top endpoints by traffic and latency
- Error breakdown by type and endpoint
- Active users and sessions

### 2. Infrastructure Dashboard
- CPU and memory usage per pod
- Pod restart count
- Network I/O
- Disk usage

### 3. Event-Driven Dashboard
- Kafka topic lag
- Dapr Pub/Sub throughput
- Event processing latency
- Dead letter queue size

### 4. Business Metrics Dashboard
- Tasks created per hour/day
- Task completion rate
- Reminder delivery success rate
- User activity heatmap

## Alert Rules Best Practices

### Critical Alerts (Page immediately)
- Service completely down
- Database unreachable
- Error rate > 10%
- P95 latency > 1 second

### Warning Alerts (Investigate within hours)
- Pod restarts > 3 in 10 minutes
- Memory usage > 80%
- Kafka consumer lag > 1000 messages
- API availability < 99.5%

For complete Prometheus configs, Grafana dashboard JSON, and alert rule examples, see [examples.md](examples.md).

## Related Skills

- **helm-cloud-chart**: Add Prometheus annotations to Helm charts
- **microservice-scaffold**: Include metrics endpoints in microservices
- **github-actions-cloud**: Deploy monitoring stack via CI/CD
- **dapr-component-generator**: Monitor Dapr components

## Tags

prometheus, grafana, monitoring, observability, alerts, metrics, kubernetes, dashboards, slo
