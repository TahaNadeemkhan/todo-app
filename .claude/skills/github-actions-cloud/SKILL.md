# GitHub Actions Cloud Deployment Pipeline

**Purpose**: Generate GitHub Actions CI/CD workflows for building, testing, and deploying to cloud Kubernetes (AKS/GKE/OKE)

**Trigger Keywords**: github-actions, cicd, pipeline, deployment, workflow, automation, cloud

## Overview

This skill generates production-ready GitHub Actions workflows for:
- Build and test on every push
- Build Docker images and push to registry
- Deploy to Kubernetes cluster (AKS/GKE/OKE)
- Run database migrations
- Rollback on deployment failure
- Notification on success/failure

Perfect for Phase 5 automated cloud deployments.

## Usage

### Generate Full CI/CD Pipeline for Cloud K8s

```bash
/github-actions-cloud \
  --cloud=gke \
  --registry=gcr \
  --helm=true \
  --output=.github/workflows/
```

### Generate for Oracle Cloud (OKE)

```bash
/github-actions-cloud \
  --cloud=oke \
  --registry=ocir \
  --helm=true \
  --output=.github/workflows/
```

## Configuration Options

| Option | Description | Values |
|--------|-------------|--------|
| --cloud | Cloud provider | gke, aks, oke |
| --registry | Container registry | gcr, ecr, acr, ocir, dockerhub |
| --helm | Use Helm for deployment | true, false |
| --output | Output directory | .github/workflows/ |
| --env | Deployment environment | production, staging |

## Generated Artifacts

### 1. Build and Test Workflow

```yaml
# .github/workflows/build-test.yaml
name: Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install UV
        run: pip install uv

      - name: Install dependencies
        run: |
          cd todo_app/phase_5/backend
          uv pip install --system -r pyproject.toml

      - name: Run tests
        run: |
          cd todo_app/phase_5/backend
          pytest tests/ --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd todo_app/phase_5/frontend
          npm ci

      - name: Build
        run: |
          cd todo_app/phase_5/frontend
          npm run build

      - name: Run tests
        run: |
          cd todo_app/phase_5/frontend
          npm test
```

### 2. Build and Push Docker Images

```yaml
# .github/workflows/build-push.yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]
    tags:
      - 'v*.*.*'

env:
  REGISTRY: gcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-push-backend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: _json_key
          password: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./todo_app/phase_5/backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  build-push-frontend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: _json_key
          password: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./todo_app/phase_5/frontend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

### 3. Deploy to Cloud Kubernetes

```yaml
# .github/workflows/deploy-cloud.yaml
name: Deploy to GKE

on:
  workflow_run:
    workflows: ["Build and Push Docker Images"]
    types:
      - completed
    branches: [main]

env:
  GKE_CLUSTER: todo-app-cluster
  GKE_ZONE: us-central1-a
  DEPLOYMENT_NAME: todo-app
  NAMESPACE: production

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2
        with:
          service_account_key: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Install gke-gcloud-auth-plugin
        run: |
          gcloud components install gke-gcloud-auth-plugin

      - name: Get GKE credentials
        run: |
          gcloud container clusters get-credentials ${{ env.GKE_CLUSTER }} \
            --zone ${{ env.GKE_ZONE }}

      - name: Set up Helm
        uses: azure/setup-helm@v4
        with:
          version: '3.13.0'

      - name: Deploy with Helm
        run: |
          helm upgrade --install ${{ env.DEPLOYMENT_NAME }} \
            ./todo_app/phase_5/k8s/helm/todo-app \
            --namespace ${{ env.NAMESPACE }} \
            --create-namespace \
            --set image.frontend.tag=${{ github.sha }} \
            --set image.backend.tag=${{ github.sha }} \
            --set secrets.databaseUrl=${{ secrets.DATABASE_URL }} \
            --set secrets.geminiApiKey=${{ secrets.GEMINI_API_KEY }} \
            --set secrets.betterAuthSecret=${{ secrets.BETTER_AUTH_SECRET }} \
            --set secrets.betterAuthUrl=${{ secrets.BETTER_AUTH_URL }} \
            --wait \
            --timeout 5m

      - name: Run database migrations
        run: |
          kubectl exec -n ${{ env.NAMESPACE }} \
            deployment/todo-app-backend \
            -- alembic upgrade head

      - name: Verify deployment
        run: |
          kubectl rollout status -n ${{ env.NAMESPACE }} \
            deployment/todo-app-frontend
          kubectl rollout status -n ${{ env.NAMESPACE }} \
            deployment/todo-app-backend

      - name: Get service URLs
        run: |
          kubectl get services -n ${{ env.NAMESPACE }}

      - name: Notify on success
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: 'Deployment to GKE succeeded! :rocket:'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

      - name: Rollback on failure
        if: failure()
        run: |
          helm rollback ${{ env.DEPLOYMENT_NAME }} \
            --namespace ${{ env.NAMESPACE }}

      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: 'Deployment to GKE failed and rolled back! :x:'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 4. Oracle Cloud (OKE) Variant

```yaml
# .github/workflows/deploy-oke.yaml
name: Deploy to OKE

on:
  workflow_run:
    workflows: ["Build and Push Docker Images"]
    types:
      - completed
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up OCI CLI
        uses: oracle-actions/configure-oci-cli@v1
        with:
          user-ocid: ${{ secrets.OCI_USER_OCID }}
          tenancy-ocid: ${{ secrets.OCI_TENANCY_OCID }}
          region: ${{ secrets.OCI_REGION }}
          api-key: ${{ secrets.OCI_API_KEY }}
          fingerprint: ${{ secrets.OCI_FINGERPRINT }}

      - name: Get OKE kubeconfig
        run: |
          oci ce cluster create-kubeconfig \
            --cluster-id ${{ secrets.OKE_CLUSTER_ID }} \
            --file $HOME/.kube/config \
            --region ${{ secrets.OCI_REGION }}

      - name: Deploy with Helm
        run: |
          helm upgrade --install todo-app \
            ./k8s/helm/todo-app \
            --namespace production \
            --create-namespace \
            --set image.registry=ocir.io \
            --wait
```

## Required GitHub Secrets

### For GKE (Google Cloud)
```
GCP_PROJECT_ID
GCP_SERVICE_ACCOUNT_KEY
DATABASE_URL
GEMINI_API_KEY
BETTER_AUTH_SECRET
BETTER_AUTH_URL
SLACK_WEBHOOK (optional)
```

### For AKS (Azure)
```
AZURE_CREDENTIALS
ACR_LOGIN_SERVER
ACR_USERNAME
ACR_PASSWORD
DATABASE_URL
...
```

### For OKE (Oracle Cloud)
```
OCI_USER_OCID
OCI_TENANCY_OCID
OCI_REGION
OCI_API_KEY
OCI_FINGERPRINT
OKE_CLUSTER_ID
DATABASE_URL
...
```

## Workflow Best Practices

1. **Branch Protection**: Require CI to pass before merge
2. **Secrets Management**: Store all sensitive data in GitHub Secrets
3. **Docker Caching**: Use GitHub Actions cache for faster builds
4. **Rollback Strategy**: Auto-rollback on deployment failure
5. **Notifications**: Alert team on deployment events
6. **Zero-Downtime**: Use Helm's wait and rollout status

## Testing Locally

```bash
# Install act to run GitHub Actions locally
brew install act

# Run workflow locally
act -j build-test
```

## Related Skills

- **deployment-blueprint**: Generate Dockerfiles and Helm charts
- **helm-cloud-chart**: Generate cloud-ready Helm charts
- **prometheus-dashboard**: Add monitoring to pipelines

## Tags

github-actions, cicd, pipeline, deployment, automation, cloud, kubernetes, gke, aks, oke, helm
