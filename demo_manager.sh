#!/bin/bash
# Demo Environment Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "🎭 Dating App Demo Environment Manager"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"  
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if demo environment is running
check_demo_status() {
    print_status "Checking demo environment status..."
    
    if docker-compose -f environments/demo/docker-compose.simple.yml ps | grep -q "Up"; then
        print_success "Demo environment is running"
        docker-compose -f environments/demo/docker-compose.simple.yml ps
        return 0
    else
        print_warning "Demo environment is not running"
        return 1
    fi
}

# Function to start demo environment
start_demo() {
    print_status "Starting demo environment..."
    
    cd "${PROJECT_ROOT}"
    
    # Build all services first
    print_status "Building services..."
    docker-compose -f environments/demo/docker-compose.simple.yml build
    
    # Start the environment
    print_status "Starting containers..."
    docker-compose -f environments/demo/docker-compose.simple.yml up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Generate demo data
    print_status "Generating demo data..."
    cd TestDataGenerator
    dotnet run --project TestDataGenerator.csproj -- --environment demo --create-users 50 --api
    
    print_success "Demo environment started successfully!"
    print_status "Demo URLs:"
    echo "  🌐 YARP Gateway: http://localhost:5000"
    echo "  🔐 Auth Service: http://localhost:5001"  
    echo "  👤 User Service: http://localhost:5002"
    echo "  💕 Matchmaking: http://localhost:5003"
    echo "  📱 Flutter App: Connect to http://localhost:5000"
}

# Function to stop demo environment
stop_demo() {
    print_status "Stopping demo environment..."
    
    cd "${PROJECT_ROOT}"
    docker-compose -f environments/demo/docker-compose.simple.yml down
    
    print_success "Demo environment stopped"
}

# Function to reset demo data
reset_demo_data() {
    print_status "Resetting demo data..."
    
    cd "${PROJECT_ROOT}"
    
    # Stop containers
    docker-compose -f environments/demo/docker-compose.simple.yml down
    
    # Remove demo database volume
    docker volume rm "demo_mysql_data" 2>/dev/null || true
    
    # Restart environment
    start_demo
    
    print_success "Demo data reset complete!"
}

# Function to run automated demo journey
run_demo_journey() {
    print_status "Running automated demo journey..."
    
    # Ensure demo is running
    if ! check_demo_status > /dev/null 2>&1; then
        print_status "Demo not running, starting it first..."
        start_demo
    fi
    
    cd "${PROJECT_ROOT}/TestDataGenerator"
    
    # Run demo scenarios
    print_status "Executing demo scenarios..."
    dotnet run --project TestDataGenerator.csproj -- --environment demo --run-scenarios
    
    print_success "Demo journey completed!"
    print_status "You can now:"
    echo "  📱 Open Flutter app and login as demo users"
    echo "  👥 Users: demo.alice@example.com, demo.bob@example.com (password: Demo123!)"
    echo "  🔍 See pre-created matches and conversations"
}

# Function to show demo user credentials
show_demo_users() {
    print_status "Demo User Credentials:"
    echo "========================"
    echo "👩 Alice Johnson: demo.alice@example.com | Demo123!"
    echo "👨 Bob Martinez:  demo.bob@example.com   | Demo123!"  
    echo "🧑 Charlie Chen:  demo.charlie@example.com | Demo123!"
    echo "👩 Diana Park:    demo.diana@example.com  | Demo123!"
    echo "👩 Eve Thompson:  demo.eve@example.com    | Demo123!"
    echo ""
    echo "📝 All demo users are pre-matched with interesting conversations!"
}

# Function to open demo in browser
open_demo() {
    print_status "Opening demo environment..."
    
    # Check if demo is running
    if ! check_demo_status > /dev/null 2>&1; then
        print_error "Demo environment is not running. Please start it first with: $0 start"
        exit 1
    fi
    
    # Open browser to demo gateway
    if command -v xdg-open > /dev/null; then
        xdg-open "http://localhost:5000"
    elif command -v open > /dev/null; then
        open "http://localhost:5000"
    else
        print_status "Please open http://localhost:5000 in your browser"
    fi
}

# Main script logic
case "${1:-}" in
    "start")
        start_demo
        ;;
    "stop") 
        stop_demo
        ;;
    "status")
        check_demo_status
        ;;
    "reset")
        reset_demo_data
        ;;
    "journey")
        run_demo_journey
        ;;
    "users")
        show_demo_users
        ;;
    "open")
        open_demo
        ;;
    "logs")
        cd "${PROJECT_ROOT}"
        docker-compose -f environments/demo/docker-compose.simple.yml logs -f
        ;;
    *)
        echo "Usage: $0 {start|stop|status|reset|journey|users|open|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start demo environment with generated data"
        echo "  stop    - Stop demo environment"  
        echo "  status  - Check if demo is running"
        echo "  reset   - Reset demo data and restart"
        echo "  journey - Run automated demo user journey"
        echo "  users   - Show demo user credentials"
        echo "  open    - Open demo in browser"
        echo "  logs    - Follow demo environment logs"
        exit 1
        ;;
esac
