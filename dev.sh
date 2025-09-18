#!/bin/bash

# Development environment management script for Cookbook

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[COOKBOOK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if docker and docker compose are available
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available"
        exit 1
    fi
}

# Function to start development environment
start_dev() {
    print_status "Starting cookbook development environment..."
    print_status "This will:"
    print_status "  - Mount source code for live reload"
    print_status "  - Frontend (Vite dev server) with HMR on port 3000"
    print_status "  - Backend (Uvicorn) with auto-reload on port 8000"
    print_status "  - PostgreSQL database on port 5432"
    print_status "  - Redis cache on port 6379"

    # Stop any existing containers
    docker compose -f docker-compose.dev.yml down

    # Build development images
    print_status "Building development images..."
    docker compose -f docker-compose.dev.yml build

    # Start development environment
    print_status "Starting containers..."
    docker compose -f docker-compose.dev.yml up -d

    print_status "Development environment started!"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend API: http://localhost:8000"
    print_status "API Docs: http://localhost:8000/docs"
    print_status "Database: postgresql://postgres:password@localhost:5432/cookbook"
    print_status "Redis: redis://localhost:6379/0"
    print_status ""
    print_status "To view logs: ./dev.sh logs"
    print_status "To stop: ./dev.sh stop"
}

# Function to stop development environment
stop_dev() {
    print_status "Stopping cookbook development environment..."
    docker compose -f docker-compose.dev.yml down
    print_status "Development environment stopped!"
}

# Function to restart development environment
restart_dev() {
    print_status "Restarting cookbook development environment..."
    stop_dev
    start_dev
}

# Function to show logs
show_logs() {
    service=${2:-""}
    if [ -n "$service" ]; then
        docker compose -f docker-compose.dev.yml logs -f "$service"
    else
        docker compose -f docker-compose.dev.yml logs -f
    fi
}

# Function to start production environment
start_prod() {
    print_status "Starting cookbook production environment..."
    print_status "This will use pre-built images without source mounting"

    # Stop development environment if running
    docker compose -f docker-compose.yml -f docker-compose.dev.yml down 2>/dev/null || true

    # Start production environment
    docker compose up -d

    print_status "Production environment started!"
    print_status "Application: http://localhost"
    print_status "API: http://localhost/api"
}

# Function to stop production environment
stop_prod() {
    print_status "Stopping cookbook production environment..."
    docker compose down
    print_status "Production environment stopped!"
}

# Function to build frontend
build_frontend() {
    print_status "Building frontend..."
    cd frontend
    npm run build
    cd ..
    print_status "Frontend built successfully!"
}

# Function to run tests
run_tests() {
    print_status "Running tests in development environment..."

    # Backend tests
    print_status "Running backend tests..."
    docker compose -f docker-compose.dev.yml exec backend python -m pytest

    # Frontend tests
    print_status "Running frontend tests..."
    docker compose -f docker-compose.dev.yml exec frontend npm run test
}

# Function to run linting
run_lint() {
    print_status "Running linting..."

    # Backend linting
    print_status "Running backend linting..."
    docker compose -f docker-compose.dev.yml exec backend ruff check --fix --unsafe-fixes --preview
    docker compose -f docker-compose.dev.yml exec backend black .
    docker compose -f docker-compose.dev.yml exec backend mypy .

    # Frontend linting (if available)
    print_status "Running frontend linting..."
    docker compose -f docker-compose.dev.yml exec frontend npm run lint || true
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    docker compose -f docker-compose.dev.yml exec backend alembic upgrade head
    print_status "Database migrations completed!"
}

# Function to create new migration
create_migration() {
    if [ -z "$2" ]; then
        print_error "Please provide a migration message"
        print_error "Usage: ./dev.sh migrate 'Add new recipe fields'"
        exit 1
    fi

    migration_message="$2"
    print_status "Creating new migration: $migration_message"
    docker compose -f docker-compose.dev.yml exec backend alembic revision --autogenerate -m "$migration_message"
    print_status "Migration created successfully!"
}

# Function to shell into containers
shell() {
    service=${2:-"backend"}
    print_status "Opening shell in $service container..."
    docker compose -f docker-compose.dev.yml exec "$service" /bin/bash
}

# Function to show help
show_help() {
    echo "Cookbook Development Environment Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start, dev          Start development environment with live reload"
    echo "  stop               Stop development environment"
    echo "  restart            Restart development environment"
    echo "  logs [service]     Show logs (optionally for specific service)"
    echo "  prod               Start production environment"
    echo "  prod-stop          Stop production environment"
    echo "  build              Build frontend"
    echo "  test               Run all tests"
    echo "  lint               Run linting and formatting"
    echo "  migrate            Run database migrations"
    echo "  migration 'msg'    Create new migration with message"
    echo "  shell [service]    Open shell in container (default: backend)"
    echo "  help               Show this help message"
    echo ""
    echo "Development URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  Database: postgresql://postgres:password@localhost:5432/cookbook"
    echo ""
    echo "Production URLs:"
    echo "  Application: http://localhost"
    echo "  API: http://localhost/api"
    echo ""
    echo "Available services for logs/shell:"
    echo "  backend, frontend, db, redis"
}

# Main script logic
check_dependencies

case "${1:-help}" in
    "start"|"dev")
        start_dev
        ;;
    "stop")
        stop_dev
        ;;
    "restart")
        restart_dev
        ;;
    "logs")
        show_logs "$@"
        ;;
    "prod")
        start_prod
        ;;
    "prod-stop")
        stop_prod
        ;;
    "build")
        build_frontend
        ;;
    "test")
        run_tests
        ;;
    "lint")
        run_lint
        ;;
    "migrate")
        run_migrations
        ;;
    "migration")
        create_migration "$@"
        ;;
    "shell")
        shell "$@"
        ;;
    "help"|*)
        show_help
        ;;
esac