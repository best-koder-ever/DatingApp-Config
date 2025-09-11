#!/bin/bash
# Environment Management Script for Dating App
# Usage: ./manage-env.sh [demo|dev|staging] [up|down|ps|logs|health]

set -e

ENV=$1
ACTION=$2

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Validate environment
case $ENV in
    "demo")
        COMPOSE_FILE="environments/demo/docker-compose.demo.yml"
        ENV_FILE="environments/demo/.env.demo"
        ;;
    "dev"|"development")
        COMPOSE_FILE="environments/development/docker-compose.dev.yml"
        ENV_FILE="environments/development/.env.dev"
        ;;
    "staging")
        COMPOSE_FILE="environments/staging/docker-compose.staging.yml"
        ENV_FILE="environments/staging/.env.staging"
        ;;
    *)
        print_error "Invalid environment. Use: demo, dev, or staging"
        echo "Usage: $0 [demo|dev|staging] [up|down|ps|logs|health]"
        exit 1
        ;;
esac

# Check if files exist
if [[ ! -f "$COMPOSE_FILE" ]]; then
    print_error "Compose file not found: $COMPOSE_FILE"
    exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
    print_error "Environment file not found: $ENV_FILE"
    exit 1
fi

# Load environment variables
set -a
source "$ENV_FILE"
set +a

print_status "Using environment: $ENV_NAME"
print_status "Compose file: $COMPOSE_FILE"
print_status "Environment file: $ENV_FILE"

# Execute action
case $ACTION in
    "up")
        print_status "Starting $ENV_NAME environment..."
        docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d
        print_success "$ENV_NAME environment started!"
        ;;
    "down")
        print_status "Stopping $ENV_NAME environment..."
        docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" down
        print_success "$ENV_NAME environment stopped!"
        ;;
    "ps"|"status")
        print_status "Status of $ENV_NAME environment:"
        docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps
        ;;
    "logs")
        SERVICE=$3
        if [[ -n "$SERVICE" ]]; then
            print_status "Showing logs for $SERVICE in $ENV_NAME environment:"
            docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs -f "$SERVICE"
        else
            print_status "Showing logs for $ENV_NAME environment:"
            docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs -f
        fi
        ;;
    "health")
        print_status "Checking health of $ENV_NAME environment..."
        echo ""
        
        # Check each service health
        print_status "Testing Auth Service (port $AUTH_PORT)..."
        if curl -s -f "http://localhost:$AUTH_PORT/health" > /dev/null 2>&1; then
            print_success "Auth Service: Healthy"
        else
            print_warning "Auth Service: No response or unhealthy"
        fi
        
        print_status "Testing User Service (port $USER_PORT)..."
        if curl -s -f "http://localhost:$USER_PORT/health" > /dev/null 2>&1; then
            print_success "User Service: Healthy"
        else
            print_warning "User Service: No response or unhealthy"
        fi
        
        print_status "Testing Matchmaking Service (port $MATCHMAKING_PORT)..."
        if curl -s -f "http://localhost:$MATCHMAKING_PORT/api/matchmaking/health" > /dev/null 2>&1; then
            print_success "Matchmaking Service: Healthy"
        else
            print_warning "Matchmaking Service: No response or unhealthy"
        fi
        
        if [[ -n "$GATEWAY_PORT" ]]; then
            print_status "Testing Gateway (port $GATEWAY_PORT)..."
            if curl -s -f "http://localhost:$GATEWAY_PORT/health" > /dev/null 2>&1; then
                print_success "Gateway: Healthy"
            else
                print_warning "Gateway: No response or unhealthy"
            fi
        fi
        
        print_status "Testing Database (port $DB_PORT)..."
        if nc -z localhost "$DB_PORT" 2>/dev/null; then
            print_success "Database: Accessible"
        else
            print_warning "Database: Not accessible"
        fi
        ;;
    "restart")
        SERVICE=$3
        if [[ -n "$SERVICE" ]]; then
            print_status "Restarting $SERVICE in $ENV_NAME environment..."
            docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" restart "$SERVICE"
            print_success "$SERVICE restarted!"
        else
            print_status "Restarting $ENV_NAME environment..."
            docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" restart
            print_success "$ENV_NAME environment restarted!"
        fi
        ;;
    "build")
        print_status "Building $ENV_NAME environment..."
        docker-compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" build
        print_success "$ENV_NAME environment built!"
        ;;
    *)
        print_error "Invalid action. Use: up, down, ps, logs, health, restart, build"
        echo "Usage: $0 [demo|dev|staging] [up|down|ps|logs|health|restart|build] [service-name]"
        exit 1
        ;;
esac
