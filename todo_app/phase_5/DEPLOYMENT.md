# Deployment Guide

This guide covers deployment for Phase 5: Event-Driven Cloud Architecture.

## 1. Local Development (Minikube)

### Prerequisites
- Docker Desktop
- Minikube
- Helm
- kubectl
- Dapr CLI

### Steps

1.  **Start Minikube**:
    ```bash
    minikube start --cpus 4 --memory 8192
    eval $(minikube docker-env)
    ```

2.  **Initialize Dapr**:
    ```bash
    dapr init -k
    ```

3.  **Build Images**:
    ```bash
    docker build -t backend-api:latest ./backend
    docker build -t frontend:latest ./frontend
    docker build -t notification-service:latest ./services/notification-service
    docker build -t recurring-task-service:latest ./services/recurring-task-service
    ```

4.  **Run Install Script**:
    ```bash
    cd k8s
    chmod +x install.sh
    ./install.sh
    ```

5.  **Access Application**:
    ```bash
    minikube service frontend -n todo-app
    ```

## 2. Cloud Deployment (DigitalOcean / GKE / AKS)

### Prerequisites
- Cloud Kubernetes Cluster (DOKS, GKE, AKS)
- Container Registry (GHCR, Docker Hub)
- Managed Kafka (Redpanda Cloud)
- Managed PostgreSQL (Neon)
- Domain Name (configured DNS)

### Steps

1.  **Push Images to Registry**:
    ```bash
    # Login
    docker login ghcr.io
    
    # Tag
    docker tag backend-api:latest ghcr.io/user/backend-api:latest
    # ... repeat for all images ...
    
    # Push
    docker push ghcr.io/user/backend-api:latest
    # ...
    ```

2.  **Configure Secrets**:
    Update `k8s/secrets/*.yaml` with production credentials:
    - `postgres-credentials.yaml`: Neon DB connection string
    - `jwt-secret.yaml`: Secure random key
    - `smtp-credentials.yaml`: SMTP/Brevo keys
    - `fcm-credentials.yaml`: Firebase keys (optional)

    Apply secrets:
    ```bash
    kubectl create namespace todo-app
    kubectl apply -f k8s/secrets/ -n todo-app
    ```

3.  **Configure Dapr for Redpanda**:
    Edit `k8s/dapr-components/pubsub-kafka.yaml` to use SASL auth and Redpanda brokers.

4.  **Install Cert-Manager & Nginx Ingress**:
    ```bash
    helm repo add jetstack https://charts.jetstack.io
    helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --version v1.12.0 --set installCRDs=true
    
    helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
    helm install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace
    ```

5.  **Deploy Application**:
    Update `k8s/helm/todo-app/values-production.yaml` with your image repository and hosts.
    
    ```bash
    helm upgrade --install todo-app k8s/helm/todo-app -f k8s/helm/todo-app/values-production.yaml -n todo-app
    ```

6.  **Verify**:
    Check pods and logs:
    ```bash
    kubectl get pods -n todo-app
    ```
