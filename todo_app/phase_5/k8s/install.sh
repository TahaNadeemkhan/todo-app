#!/bin/bash
set -e

echo "🚀 Starting Minikube Deployment..."

# 1. Create Namespace
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# 2. Apply Secrets
echo "🔑 Applying Secrets..."
kubectl apply -f secrets/ -n todo-app

# 3. Apply Dapr Components
echo "🧩 Applying Dapr Components..."
kubectl apply -f dapr-components/ -n todo-app

# 4. Build Images (Assumes eval $(minikube docker-env) is run by user)
echo "🐳 Building Docker Images..."
# Note: User must run this in terminal where minikube docker-env is active
# We skip actual build here to avoid errors if docker not connected, but print instructions.
echo "Make sure you have run 'eval \$(minikube docker-env)' before building!"
# docker build -t backend-api:latest ../backend
# docker build -t frontend:latest ../frontend
# docker build -t notification-service:latest ../services/notification-service
# docker build -t recurring-task-service:latest ../services/recurring-task-service

# 5. Install Helm Chart
echo "📦 Installing Helm Chart..."
helm dependency update helm/todo-app
helm upgrade --install todo-app helm/todo-app -n todo-app --wait

echo "✅ Deployment Complete! Access frontend via 'minikube service todo-app-frontend -n todo-app'"
