# Quickstart: Phase 5 Recovery and Deployment

**Feature**: 001-fix-phase5-deployment
**Date**: 2026-03-06

## Prerequisites

- Minikube, Docker, Helm, Dapr CLI installed.

## Recovery Sequence (Minikube Reset)

If your environment is messy or pods are failing, perform this fresh start:

1.  **Delete Cluster**:
    ```bash
    minikube delete
    ```

2.  **Start Cluster**:
    ```bash
    minikube start --driver=docker --cpus=2 --memory=3072
    ```

3.  **Install Dapr**:
    ```bash
    dapr init -k
    ```

4.  **Create Secrets**:
    Replace placeholder values with real ones.
    ```bash
    kubectl create secret opaque postgres-credentials --from-literal=connectionString="postgresql://user:password@todo-app-postgresql:5432/todo_db"
    kubectl create secret opaque jwt-secret --from-literal=secret_key="supersecretkey"
    kubectl create secret opaque gemini-api-key --from-literal=api_key="your-key"
    ```

5.  **Apply Dapr Components**:
    ```bash
    kubectl apply -f todo_app/phase_5/k8s/dapr-components/
    ```

## Build & Deploy Strategy (v5.0.2)

1.  **Build Images**:
    Execute from service root directories.
    ```bash
    docker build -t todo-backend:v5.0.2 .
    docker build -t notification-service:v5.0.2 .
    docker build -t recurring-task-service:v5.0.2 .
    docker build -t todo-frontend:v5.0.2 .
    ```

2.  **Load into Minikube**:
    ```bash
    minikube image load todo-backend:v5.0.2
    minikube image load notification-service:v5.0.2
    minikube image load recurring-task-service:v5.0.2
    minikube image load todo-frontend:v5.0.2
    ```

3.  **Package & Deploy Helm Chart**:
    ```bash
    cd todo_app/phase_5/k8s/helm/todo-app
    helm package .
    helm upgrade --install todo-app todo-app-5.0.0.tgz --set backend.image.tag=v5.0.2 --set notificationService.image.tag=v5.0.2 --set recurringTaskService.image.tag=v5.0.2 --set frontend.image.tag=v5.0.2
    ```

## Verification

- **Pod Check**: `kubectl get pods` (Wait until all are Running).
- **Log Check**: `kubectl logs -l app=backend-api` (Confirm no ImportErrors).
