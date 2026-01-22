#!/bin/bash

# Todo App Helm Chart Installation Script
# This script helps install the Todo App Helm chart with proper secret handling

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
RELEASE_NAME="todo-app"
NAMESPACE="default"
CHART_PATH="./todo-app"

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        print_error "Helm is not installed. Please install Helm 3.0+ first."
        exit 1
    fi

    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi

    # Check if minikube is running (optional)
    if command -v minikube &> /dev/null; then
        if minikube status | grep -q "Running"; then
            print_info "Minikube is running"
            MINIKUBE_IP=$(minikube ip)
        else
            print_warning "Minikube is not running. Start it with: minikube start"
        fi
    fi

    print_info "Prerequisites check passed ✓"
}

# Function to validate chart
validate_chart() {
    print_info "Validating Helm chart..."

    if [ ! -d "$CHART_PATH" ]; then
        print_error "Chart directory not found: $CHART_PATH"
        exit 1
    fi

    helm lint "$CHART_PATH"
    print_info "Chart validation passed ✓"
}

# Function to load Docker images into Minikube
load_images() {
    if command -v minikube &> /dev/null && minikube status | grep -q "Running"; then
        print_info "Loading Docker images into Minikube..."

        # Check if images exist locally
        if docker images | grep -q "todo-frontend.*v1.0.0"; then
            print_info "Loading todo-frontend:v1.0.0..."
            minikube image load todo-frontend:v1.0.0
        else
            print_warning "Image todo-frontend:v1.0.0 not found. Please build it first."
        fi

        if docker images | grep -q "todo-backend.*v1.0.0"; then
            print_info "Loading todo-backend:v1.0.0..."
            minikube image load todo-backend:v1.0.0
        else
            print_warning "Image todo-backend:v1.0.0 not found. Please build it first."
        fi

        print_info "Images loaded ✓"
    fi
}

# Function to prompt for secrets
prompt_for_secrets() {
    print_info "Please provide the required secrets:"
    echo ""

    # Database URL
    if [ -z "$DATABASE_URL" ]; then
        read -p "Database URL (postgresql://...): " DATABASE_URL
        if [ -z "$DATABASE_URL" ]; then
            print_error "Database URL is required"
            exit 1
        fi
    fi

    # Gemini API Key
    if [ -z "$GEMINI_API_KEY" ]; then
        read -p "Gemini API Key (AIzaSy...): " GEMINI_API_KEY
        if [ -z "$GEMINI_API_KEY" ]; then
            print_error "Gemini API Key is required"
            exit 1
        fi
    fi

    # Better Auth Secret
    if [ -z "$BETTER_AUTH_SECRET" ]; then
        read -p "Better Auth Secret: " BETTER_AUTH_SECRET
        if [ -z "$BETTER_AUTH_SECRET" ]; then
            print_error "Better Auth Secret is required"
            exit 1
        fi
    fi

    # Better Auth URL
    if [ -z "$BETTER_AUTH_URL" ]; then
        if [ -n "$MINIKUBE_IP" ]; then
            BETTER_AUTH_URL="http://${MINIKUBE_IP}:30080"
            print_info "Using default Better Auth URL: $BETTER_AUTH_URL"
        else
            read -p "Better Auth URL (http://...): " BETTER_AUTH_URL
            if [ -z "$BETTER_AUTH_URL" ]; then
                print_error "Better Auth URL is required"
                exit 1
            fi
        fi
    fi

    echo ""
}

# Function to install or upgrade chart
install_chart() {
    print_info "Installing Helm chart..."

    # Check if release already exists
    if helm list -n "$NAMESPACE" | grep -q "^$RELEASE_NAME"; then
        print_warning "Release '$RELEASE_NAME' already exists. Upgrading..."
        helm upgrade "$RELEASE_NAME" "$CHART_PATH" \
            --namespace "$NAMESPACE" \
            --set "secrets.databaseUrl=$DATABASE_URL" \
            --set "secrets.geminiApiKey=$GEMINI_API_KEY" \
            --set "secrets.betterAuthSecret=$BETTER_AUTH_SECRET" \
            --set "secrets.betterAuthUrl=$BETTER_AUTH_URL" \
            "$@"
    else
        helm install "$RELEASE_NAME" "$CHART_PATH" \
            --namespace "$NAMESPACE" \
            --set "secrets.databaseUrl=$DATABASE_URL" \
            --set "secrets.geminiApiKey=$GEMINI_API_KEY" \
            --set "secrets.betterAuthSecret=$BETTER_AUTH_SECRET" \
            --set "secrets.betterAuthUrl=$BETTER_AUTH_URL" \
            "$@"
    fi

    print_info "Chart installed successfully ✓"
}

# Function to wait for pods
wait_for_pods() {
    print_info "Waiting for pods to be ready..."

    kubectl wait --for=condition=ready pod \
        -l app.kubernetes.io/instance="$RELEASE_NAME" \
        -n "$NAMESPACE" \
        --timeout=300s || print_warning "Some pods may still be starting"

    print_info "Pods status:"
    kubectl get pods -l app.kubernetes.io/instance="$RELEASE_NAME" -n "$NAMESPACE"
}

# Function to display access information
display_access_info() {
    echo ""
    print_info "=========================================="
    print_info "  Todo App Deployment Successful!"
    print_info "=========================================="
    echo ""

    if command -v minikube &> /dev/null && minikube status | grep -q "Running"; then
        print_info "Access the application at:"
        FRONTEND_URL=$(minikube service "$RELEASE_NAME-frontend" --url -n "$NAMESPACE" 2>/dev/null || echo "http://${MINIKUBE_IP}:30080")
        echo "  $FRONTEND_URL"
        echo ""
        print_info "To open in browser:"
        echo "  minikube service $RELEASE_NAME-frontend -n $NAMESPACE"
    else
        print_info "Frontend NodePort: 30080"
        print_info "Get your cluster IP and access: http://<cluster-ip>:30080"
    fi

    echo ""
    print_info "Useful commands:"
    echo "  View pods:        kubectl get pods -n $NAMESPACE"
    echo "  View logs:        kubectl logs -f deployment/$RELEASE_NAME-frontend -n $NAMESPACE"
    echo "  View services:    kubectl get svc -n $NAMESPACE"
    echo "  Helm status:      helm status $RELEASE_NAME -n $NAMESPACE"
    echo ""
}

# Main execution
main() {
    echo ""
    print_info "Todo App Helm Chart Installer"
    echo ""

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --release-name)
                RELEASE_NAME="$2"
                shift 2
                ;;
            --namespace)
                NAMESPACE="$2"
                shift 2
                ;;
            --chart-path)
                CHART_PATH="$2"
                shift 2
                ;;
            --skip-images)
                SKIP_IMAGES=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --release-name NAME    Release name (default: todo-app)"
                echo "  --namespace NS         Kubernetes namespace (default: default)"
                echo "  --chart-path PATH      Path to chart (default: ./todo-app)"
                echo "  --skip-images          Skip loading images into Minikube"
                echo "  --help                 Show this help message"
                echo ""
                echo "Environment variables:"
                echo "  DATABASE_URL           PostgreSQL connection string"
                echo "  GEMINI_API_KEY         Gemini API key"
                echo "  BETTER_AUTH_SECRET     Better Auth secret"
                echo "  BETTER_AUTH_URL        Better Auth URL"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Execute installation steps
    check_prerequisites
    validate_chart

    if [ "$SKIP_IMAGES" != "true" ]; then
        load_images
    fi

    prompt_for_secrets
    install_chart
    wait_for_pods
    display_access_info
}

# Run main function
main "$@"
