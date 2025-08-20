#!/bin/bash

# Dating App Startup Script
# This script starts the backend services and Flutter app

set -e  # Exit on any error

echo "🚀 Starting Dating App Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    print_error "Flutter is not installed or not in PATH."
    exit 1
fi

# Change to backend directory
BACKEND_DIR="/home/m/development/DatingApp"
FLUTTER_DIR="/home/m/development/mobile-apps/flutter/dejtingapp"

if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FLUTTER_DIR" ]; then
    print_error "Flutter directory not found: $FLUTTER_DIR"
    exit 1
fi

# Step 1: Start backend services
print_status "Starting backend services..."
cd "$BACKEND_DIR"

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down > /dev/null 2>&1 || true

# Start backend services
print_status "Starting Docker Compose services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 10

# Check if YARP gateway is responding
print_status "Checking YARP gateway health..."
RETRY_COUNT=0
MAX_RETRIES=30

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        print_success "YARP gateway is responding!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_warning "YARP gateway might not be fully ready, but continuing..."
fi

# Step 2: Test basic API endpoints
print_status "Testing API endpoints..."

# Test auth service
if curl -s http://localhost:8081 > /dev/null 2>&1; then
    print_success "Auth Service (8081) is responding"
else
    print_warning "Auth Service (8081) might not be ready"
fi

# Test user service
if curl -s http://localhost:8082 > /dev/null 2>&1; then
    print_success "User Service (8082) is responding"
else
    print_warning "User Service (8082) might not be ready"
fi

# Test matchmaking service
if curl -s http://localhost:8083 > /dev/null 2>&1; then
    print_success "Matchmaking Service (8083) is responding"
else
    print_warning "Matchmaking Service (8083) might not be ready"
fi

# Test swipe service
if curl -s http://localhost:8084 > /dev/null 2>&1; then
    print_success "Swipe Service (8084) is responding"
else
    print_warning "Swipe Service (8084) might not be ready"
fi

# Step 3: Check Flutter dependencies
print_status "Checking Flutter app..."
cd "$FLUTTER_DIR"

# Get Flutter dependencies if needed
if [ ! -d "build" ] || [ ! -f ".dart_tool/package_config.json" ]; then
    print_status "Getting Flutter dependencies..."
    flutter pub get
fi

# Run Flutter analyze to check for issues
print_status "Running Flutter analyze..."
if flutter analyze --no-fatal-infos > /dev/null 2>&1; then
    print_success "Flutter analysis passed!"
else
    print_warning "Flutter analysis found some issues, but continuing..."
fi

# Step 4: Start Flutter app
print_status "Starting Flutter app..."
echo ""
print_success "🎉 Backend services are running!"
print_success "📱 Starting Flutter app..."
echo ""
echo "Backend Services URLs:"
echo "  YARP Gateway: http://localhost:8080"
echo "  Auth Service: http://localhost:8081"
echo "  User Service: http://localhost:8082"
echo "  Matchmaking:  http://localhost:8083"
echo "  Swipe Service: http://localhost:8084"
echo ""

# Ask which device to use
echo "Choose target device for Flutter:"
echo "  1) Chrome (Recommended - fast hot reload, DevTools, best for development)"
echo "  2) Android Emulator (for mobile testing only)"
echo "  3) Linux Desktop"
echo "  4) Let Flutter choose"
echo ""
echo "💡 Tip: Use Chrome for development, Android for final testing"
read -p "Enter choice (1-4) [default: 1]: " -n 1 -r
echo ""

FLUTTER_DEVICE=""
case $REPLY in
    2)
        print_status "Starting on Android emulator..."
        print_warning "Android is slower for development. Consider Chrome for faster iterations."
        FLUTTER_DEVICE="-d android"
        ;;
    3)
        print_status "Starting on Linux desktop..."
        FLUTTER_DEVICE="-d linux"
        ;;
    4)
        print_status "Letting Flutter choose device..."
        FLUTTER_DEVICE=""
        ;;
    *)
        print_status "Starting on Chrome (best for development)..."
        FLUTTER_DEVICE="-d chrome"
        ;;
esac

echo ""
echo "Flutter Development Tips:"
echo "  Press 'r' for hot reload"
echo "  Press 'R' for hot restart" 
echo "  Press 'q' to quit"
echo "  Use browser dev tools for debugging (if Chrome)"
echo ""
echo "Press Ctrl+C to stop the Flutter app (backend will keep running)"
echo "To stop backend services, run: cd $BACKEND_DIR && docker-compose down"
echo ""

# Start Flutter with selected device
flutter run --hot $FLUTTER_DEVICE

# Note: The script will pause here while Flutter is running
# When Flutter exits, we can optionally stop the backend

echo ""
read -p "Do you want to stop the backend services? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Stopping backend services..."
    cd "$BACKEND_DIR"
    docker-compose down
    print_success "Backend services stopped."
else
    print_success "Backend services are still running."
    echo "To stop them later, run: cd $BACKEND_DIR && docker-compose down"
fi

print_success "Development session ended. Happy coding! 💙"
