# Beginner's Guide: Running the Todo App (Phase 5)

This guide is designed for beginners to get the application running on your local computer using **Minikube** (a local Kubernetes cluster).

## Prerequisites (What you need to install)

Before you start, make sure you have these tools installed. If not, click the links to download them.

1.  **Docker Desktop** (or Docker Engine) - [Download](https://www.docker.com/products/docker-desktop/)
    *   *Why?* It runs the containers (servers) on your machine.
    *   *Check:* Run `docker --version` in your terminal.

2.  **Minikube** - [Download](https://minikube.sigs.k8s.io/docs/start/)
    *   *Why?* It creates a small Kubernetes cluster inside Docker.
    *   *Check:* Run `minikube version`.

3.  **kubectl** - [Download](https://kubernetes.io/docs/tasks/tools/)
    *   *Why?* It's the command-line tool to talk to Kubernetes.
    *   *Check:* Run `kubectl version --client`.

4.  **Helm** - [Download](https://helm.sh/docs/intro/install/)
    *   *Why?* It's a package manager for Kubernetes (like npm/pip but for apps).
    *   *Check:* Run `helm version`.

5.  **Dapr CLI** - [Download](https://docs.dapr.io/getting-started/install-dapr-cli/)
    *   *Why?* It manages the event-driven communication (Kafka, etc.).
    *   *Check:* Run `dapr --version`.

---

## Step-by-Step Deployment

Open your terminal (PowerShell on Windows, Terminal on Mac/Linux) and run these commands one by one.

### Step 1: Start Minikube
This starts your local cluster.

```bash
minikube start --cpus 4 --memory 8192
minikube start --driver=docker --cpus 2 --memory 4000 #This is working
```

### Step 2: Initialize Dapr
This installs the Dapr system into your cluster.

```bash
dapr init -k
```
*Wait about 1-2 minutes for this to finish.*

### Step 3: Connect Docker to Minikube
This is important! It tells your terminal to use Minikube's internal Docker, so it can see the images we build.

**For Mac/Linux:**
```bash
eval $(minikube docker-env)
```

**For Windows (PowerShell):**
```powershell
minikube -p minikube docker-env | Invoke-Expression
```

### Step 4: Build the Application Images
Now we build the code into containers. Make sure you are in the `todo_app/phase_5` folder.

```bash
# Backend
docker build -t backend-api:latest ./backend

# Frontend
docker build -t frontend:latest ./frontend

# Notification Service
docker build -t notification-service:latest ./services/notification-service

# Recurring Task Service
docker build -t recurring-task-service:latest ./services/recurring-task-service
```

### Step 5: Run the Install Script
We have a script that does all the complex Kubernetes configuration for you.

```bash
cd k8s
chmod +x install.sh  # (Mac/Linux only)
./install.sh
```
*On Windows, you might need to run the commands inside `install.sh` manually if git bash isn't available, or use `kubectl apply` commands directly.*

### Step 6: Access the App
Once the script says "Deployment Complete!", run this command to get the URL:

```bash
minikube service frontend -n todo-app
```

This will open your browser to the Todo App. You can also get the backend API URL:

```bash
minikube service backend-api -n todo-app
```

---

## Testing the Features

1.  **Create a Task**: Click "Add Task".
2.  **Add Tags/Priority**: Use the new dropdowns.
3.  **Recurring Task**: Select "Daily" recurrence. Mark it complete and see if a new one appears (might take a few seconds).
4.  **Reminders**: Set a due date and check if you receive a notification (check logs if no email configured).

## Troubleshooting

- **Pods Pending?** Run `kubectl get pods -n todo-app`. If they are pending, Minikube might need more memory.
- **Dapr Errors?** Ensure `dapr init -k` ran successfully.
- **Services not found?** Ensure you ran `eval $(minikube docker-env)` BEFORE building images.

**To Stop Everything:**
```bash
minikube stop
```

**To Delete Everything (Reset):**
```bash
minikube delete
```
