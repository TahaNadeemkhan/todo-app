---
name: helm-chart-generator
description: Generate production-ready Helm charts for Kubernetes deployments. Creates Chart.yaml, values.yaml, and template manifests for Deployments, Services, ConfigMaps, and Secrets.
allowed-tools: Read, Write, Bash, Glob
---

# Helm Chart Generator Skill

## Context (The Challenge)
Manually writing Kubernetes YAML manifests is error-prone and doesn't scale. Helm provides **templating**, **versioning**, and **configuration management** for Kubernetes applications. This skill automates the creation of complete, production-ready Helm charts following cloud-native best practices.

## 🚨 Critical Rules (Dos and Don'ts)

### 1. Chart Structure is Standard
* **DO** follow the canonical Helm chart structure
* **DON'T** create custom directory layouts
* **STRUCTURE:**
```
chart-name/
├── Chart.yaml          # Metadata
├── values.yaml         # Default configuration
├── .helmignore         # Excluded files
└── templates/
    ├── _helpers.tpl    # Template functions
    ├── deployment.yaml # Pod management
    ├── service.yaml    # Network access
    ├── configmap.yaml  # Non-sensitive config
    └── secret.yaml     # Sensitive data
```

### 2. Secrets Never in values.yaml
* **CRITICAL:** Secrets MUST be passed via `--set` flags, NOT stored in values.yaml
* **DO** define secret placeholders in values.yaml with empty strings
* **DON'T** hardcode credentials, API keys, or database URLs
* **WHY:** values.yaml is version controlled, secrets are not

**❌ Bad (values.yaml):**
```yaml
secrets:
  databaseUrl: "postgresql://user:pass@host/db"  # NEVER!
```

**✅ Good (values.yaml):**
```yaml
secrets:
  databaseUrl: ""  # Provided via --set at deploy time
```

**✅ Good (deployment command):**
```bash
helm install app ./chart --set secrets.databaseUrl="postgresql://..."
```

### 3. Health Checks are Mandatory
* **DO** include liveness and readiness probes in Deployment templates
* **DON'T** skip health checks - Kubernetes requires them for auto-recovery
* **RULE:** Every container must define both probes

### 4. Resource Limits Always
* **DO** define CPU and memory requests/limits for every container
* **DON'T** deploy without resource constraints
* **WHY:** Prevents cluster resource exhaustion

## Helm Chart Components

### Component 1: Chart.yaml (Metadata)

**Purpose:** Define chart name, version, description

**Template:**
```yaml
apiVersion: v2
name: <app-name>
description: <Brief description of the application>
type: application
version: 1.0.0        # Chart version (increment on changes)
appVersion: "1.0.0"   # Application version
```

**Example:**
```yaml
apiVersion: v2
name: todo-app
description: AI-Powered Todo Application with Chatbot
type: application
version: 1.0.0
appVersion: "1.0.0"
```

### Component 2: values.yaml (Default Configuration)

**Purpose:** Define default values that can be overridden at deployment

**Template:**
```yaml
# Frontend configuration
frontend:
  image:
    repository: <frontend-image-name>
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicaCount: 2
  service:
    type: NodePort  # or ClusterIP/LoadBalancer
    port: 3000
    nodePort: 30080  # 30000-32767 range
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

# Backend configuration
backend:
  image:
    repository: <backend-image-name>
    tag: v1.0.0
    pullPolicy: IfNotPresent
  replicaCount: 2
  service:
    type: ClusterIP  # Internal only
    port: 8000
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi

# Secrets (NEVER include actual values)
secrets:
  databaseUrl: ""
  openaiApiKey: ""
  betterAuthSecret: ""
```

### Component 3: _helpers.tpl (Template Functions)

**Purpose:** Reusable template snippets for labels, names, etc.

**Template:**
```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.name" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### Component 4: Deployment Template

**Purpose:** Define Pod management with health checks and resource limits

**Template (frontend-deployment.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app: frontend
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://{{ include "todo-app.fullname" . }}-backend-svc:8000"
        envFrom:
        - secretRef:
            name: {{ include "todo-app.fullname" . }}-secrets
        resources:
          {{- toYaml .Values.frontend.resources | nindent 12 }}
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Template (backend-deployment.yaml):**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: {{ include "todo-app.fullname" . }}-secrets
        resources:
          {{- toYaml .Values.backend.resources | nindent 12 }}
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Component 5: Service Template

**Purpose:** Expose pods for network access

**Template (frontend-service.yaml - NodePort for external access):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend-svc
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
  - port: {{ .Values.frontend.service.port }}
    targetPort: 3000
    nodePort: {{ .Values.frontend.service.nodePort }}
  selector:
    app: frontend
```

**Template (backend-service.yaml - ClusterIP for internal only):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-backend-svc
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
spec:
  type: {{ .Values.backend.service.type }}
  ports:
  - port: {{ .Values.backend.service.port }}
    targetPort: 8000
  selector:
    app: backend
```

### Component 6: Secret Template

**Purpose:** Inject sensitive data from Helm --set flags

**Template (secret.yaml):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "todo-app.fullname" . }}-secrets
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
type: Opaque
stringData:
  DATABASE_URL: {{ .Values.secrets.databaseUrl | quote }}
  OPENAI_API_KEY: {{ .Values.secrets.openaiApiKey | quote }}
  BETTER_AUTH_SECRET: {{ .Values.secrets.betterAuthSecret | quote }}
```

### Component 7: .helmignore

**Purpose:** Exclude files from packaged chart

**Template:**
```
# Development files
.DS_Store
.git/
.gitignore
.idea/
.vscode/

# CI/CD
.travis.yml
.gitlab-ci.yml

# Docs
README.md
NOTES.txt
```

## Implementation Workflow

### Step 1: Create Chart Structure
```bash
cd <project>/k8s/helm
mkdir -p todo-app/templates
cd todo-app
```

### Step 2: Generate Base Files
```bash
# Create Chart.yaml
cat > Chart.yaml <<EOF
apiVersion: v2
name: todo-app
description: AI-Powered Todo Application
type: application
version: 1.0.0
appVersion: "1.0.0"
EOF

# Create values.yaml (use template above)
# Create .helmignore (use template above)
# Create templates/_helpers.tpl (use template above)
```

### Step 3: Create Deployment Templates
```bash
# Create frontend-deployment.yaml (use template above)
# Create backend-deployment.yaml (use template above)
# Create frontend-service.yaml (use template above)
# Create backend-service.yaml (use template above)
# Create secret.yaml (use template above)
```

### Step 4: Validate Chart
```bash
# Lint chart (checks for errors)
helm lint ./todo-app

# Should output: "1 chart(s) linted, 0 chart(s) failed"

# Dry run (generates manifests without deploying)
helm template todo-app ./todo-app

# Preview generated YAML
helm template todo-app ./todo-app --debug
```

### Step 5: Deploy Chart
```bash
# Install with secrets
helm install todo-app ./todo-app \
  --set secrets.databaseUrl="postgresql://user:pass@host/db" \
  --set secrets.openaiApiKey="sk-your-key" \
  --set secrets.betterAuthSecret="your-secret"

# Verify deployment
kubectl get pods
kubectl get svc
```

## Quality Gates Checklist

Before considering chart complete, verify:

- [ ] **Chart.yaml**: Contains name, version, appVersion
- [ ] **values.yaml**: Defines all configurable parameters
- [ ] **_helpers.tpl**: Includes name and label functions
- [ ] **Deployments**: Have health probes and resource limits
- [ ] **Services**: Correct type (NodePort/ClusterIP) and selectors
- [ ] **Secret**: Template exists, NO secrets in values.yaml
- [ ] **.helmignore**: Excludes dev files
- [ ] **Lint passes**: `helm lint` returns zero errors
- [ ] **Template renders**: `helm template` generates valid YAML
- [ ] **Labels match**: Service selectors match Deployment labels

## Common Issues & Fixes

### Issue: "Error: YAML parse error"
**Cause:** Invalid indentation in templates
**Fix:** Use `{{- toYaml .Values.x | nindent N }}` for nested objects

### Issue: "Service has no endpoints"
**Cause:** Service selector doesn't match Pod labels
**Fix:** Verify `selector.app` matches `template.metadata.labels.app`

### Issue: "Secrets not injected"
**Cause:** Forgot --set flags during helm install
**Fix:**
```bash
helm install app ./chart \
  --set secrets.key="value"
```

### Issue: "ImagePullBackOff"
**Cause:** Image not available in cluster
**Fix (Minikube):**
```bash
minikube image load <image>:<tag>
```

## AI DevOps Integration

If **kubectl-ai** is available:
```bash
kubectl-ai "generate helm chart for Next.js and FastAPI app"
kubectl-ai "show me the generated manifests"
```

Manual commands:
```bash
# Validate
helm lint ./chart-name

# Preview
helm template release-name ./chart-name

# Install
helm install release-name ./chart-name --set key=value

# Upgrade
helm upgrade release-name ./chart-name

# Uninstall
helm uninstall release-name
```

---

**Remember:** Helm charts are the declarative definition of your application's desired state. Keep them DRY, parameterized, and version controlled!
