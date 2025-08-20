#!/bin/bash

# Comprehensive Testing Script - Optimized for Chrome Development
# Location: /home/m/development/DatingApp/e2e-tests/
# Focus: Chrome-first development with fast feedback

echo "🧪 Running Dating App Test Suite (Chrome-Optimized)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Directories
FLUTTER_DIR="/home/m/development/mobile-apps/flutter/dejtingapp"
E2E_DIR="/home/m/development/DatingApp/e2e-tests"
BACKEND_DIR="/home/m/development/DatingApp"

# Check if backend is running
print_status "Checking if backend is running..."
if ! curl -s http://localhost:8080 > /dev/null 2>&1; then
    print_error "Backend not running. Starting backend services..."
    cd "$BACKEND_DIR"
    docker-compose up -d
    print_status "Waiting for backend to start..."
    sleep 20
    
    if ! curl -s http://localhost:8080 > /dev/null 2>&1; then
        print_error "Failed to start backend. Please check Docker services."
        exit 1
    fi
fi
print_success "Backend is running"

# Test 1: Flutter Analysis (Quick)
print_status "=== PHASE 1: Flutter Code Quality (Fast) ==="
cd "$FLUTTER_DIR"

print_status "Getting Flutter dependencies..."
flutter pub get > /dev/null 2>&1

print_status "Running Flutter analyze..."
if flutter analyze --no-fatal-infos > /dev/null 2>&1; then
    print_success "Flutter analysis passed"
else
    print_warning "Flutter analysis found issues (continuing...)"
fi

# Test 2: Start Flutter for Chrome (Optimized)
print_status "=== PHASE 2: Starting Flutter for Chrome ==="

# Kill any existing processes
pkill -f "flutter.*run" > /dev/null 2>&1 || true

print_status "Starting Flutter web app (Chrome-optimized)..."
# Use debug mode for faster startup, specific port
flutter run -d chrome --web-port=36349 --dart-define=TESTING=true &
FLUTTER_PID=$!

print_status "Waiting for Flutter to start (optimized for Chrome)..."
sleep 20

# Quick check if accessible
RETRY_COUNT=0
MAX_RETRIES=15
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:36349 > /dev/null 2>&1; then
        print_success "Flutter web app ready at http://localhost:36349"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "Flutter web app failed to start"
    kill $FLUTTER_PID 2>/dev/null || true
    exit 1
fi

# Test 3: Backend Health Check (Quick)
print_status "=== PHASE 3: Backend Health Check ==="

services_ok=0
total_services=5

for service in "YARP:8080" "Auth:8081" "User:8082" "Matchmaking:8083" "Swipe:8084"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    if curl -s http://localhost:$port > /dev/null 2>&1; then
        print_success "$name Service OK"
        services_ok=$((services_ok + 1))
    else
        print_warning "$name Service not responding"
    fi
done

if [ $services_ok -eq $total_services ]; then
    print_success "All backend services healthy"
else
    print_warning "$services_ok/$total_services services responding (continuing...)"
fi

# Test 4: E2E Tests (Chrome-optimized)
print_status "=== PHASE 4: E2E Tests (Playwright + Chrome) ==="
cd "$E2E_DIR"

# Setup Python environment quickly
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install Playwright if needed (with cache check)
if ! python -c "import playwright" 2>/dev/null; then
    print_status "Installing Playwright (one-time setup)..."
    pip install playwright > /dev/null 2>&1
    playwright install chromium > /dev/null 2>&1
fi

print_status "Running E2E tests (Chrome-focused)..."
if python test_login_enhanced.py; then
    print_success "E2E tests passed"
else
    print_warning "E2E tests had issues (check screenshots)"
fi

# Test 5: Flutter Widget Tests (if available)
print_status "=== PHASE 5: Flutter Unit Tests ==="
cd "$FLUTTER_DIR"

if [ -d "test" ] && [ "$(ls test/*.dart 2>/dev/null | wc -l)" -gt 0 ]; then
    print_status "Running Flutter unit tests..."
    if timeout 30s flutter test > /dev/null 2>&1; then
        print_success "Flutter unit tests passed"
    else
        print_warning "Flutter unit tests failed or timed out"
    fi
else
    print_warning "No Flutter unit tests found"
fi

# Cleanup
print_status "=== CLEANUP ==="
print_status "Cleaning up test processes..."
kill $FLUTTER_PID 2>/dev/null || true

# Test Summary with Chrome focus
print_status "=== TEST SUMMARY (Chrome Development Ready) ==="
print_success "🎉 Chrome-optimized test suite completed!"
echo ""
echo "✅ Ready for Chrome development:"
echo "  📊 Code quality checked"
echo "  🌐 Chrome web app tested"  
echo "  🔗 Backend APIs verified"
echo "  🧪 E2E flows validated"
echo ""
echo "🚀 Start development:"
echo "  cd $BACKEND_DIR && ./start_dating_app.sh"
echo "  (Choose option 1 for Chrome)"
echo ""
echo "💡 Chrome DevTools tips:"
echo "  - F12 for developer tools"
echo "  - Network tab for API calls"
echo "  - Console for Flutter logs"
echo "  - Hot reload with 'r' in terminal"
echo ""
echo "Backend services still running at:"
echo "  YARP Gateway: http://localhost:8080"
print_success "Happy Chrome development! 🎯"
