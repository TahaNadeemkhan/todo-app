# Phase 4: Local Kubernetes Deployment

This phase focuses on containerizing the application and deploying it to a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker Desktop** (or Docker Engine)
*   **Minikube**
*   **Kubectl**
*   **Helm**

## Quick Start Guide

### 1. Start Minikube

Start your local Kubernetes cluster:

```bash
minikube start --cpus=4 --memory=4096 #or use below one
minikube start --driver=docker --cpus=2 --memory=3072 
```

### 2. Build Docker Images

You need to build the Docker images for both the frontend and backend. We'll tag them as `v1.0.0`.

**Backend:**

```bash
cd backend
docker build -t todo-backend:v1.0.0 .
```

**Frontend:**

```bash
cd ../frontend
docker build -t todo-frontend:v1.0.0 .
```

### 3. Load Images into Minikube

Minikube needs to have access to the images you just built.

```bash
minikube image load todo-backend:v1.0.1
minikube image load todo-frontend:v1.0.0
```

### 4. Deploy with Helm

Navigate to the Helm chart directory and install the application. You will need your **Neon Database URL** and **Gemini API Key**.

```bash
cd ../k8s/helm
```

**Install Command:**

Replace the placeholders with your actual values.

```bash
helm install todo-app ./todo-app 
  --set secrets.databaseUrl="postgresql://<user>:<password>@<host>/<dbname>?sslmode=require" 
  --set secrets.geminiApiKey="<YOUR_GEMINI_API_KEY>" 
  --set secrets.betterAuthSecret="<GENERATE_A_RANDOM_SECRET>" 
  --set secrets.betterAuthUrl="http://localhost:3000"
```

*   `betterAuthSecret`: You can generate a random string for this.
*   `betterAuthUrl`: This should match the URL where you access the frontend (likely provided by Minikube later).

### 5. Verify Deployment

Check the status of your deployment:

```bash
kubectl get pods
```

Wait until all pods show `Running` as their status.

### 6. Access the Application

To access the frontend in your browser, run:

```bash
minikube service todo-app-frontend
```

This will open a tunnel and launch your default browser pointing to the Todo App.

## Troubleshooting

*   **Pods stuck in `ImagePullBackOff`:** Ensure you ran the `minikube image load` commands successfully.
*   **Pods stuck in `CrashLoopBackOff`:** Check logs using `kubectl logs <pod-name>`. Often this is due to an incorrect `DATABASE_URL` or missing API keys.
*   **Database Connection Issues:** Ensure your Neon database URL is correct and accessible. If using a local DB, networking is different within Minikube.

## Clean Up

To remove the deployment:

```bash
helm uninstall todo-app
```

To stop Minikube:

```bash
minikube stop
```
