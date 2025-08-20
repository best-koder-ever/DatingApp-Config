#!/bin/bash

# Dating App Setup Validation - Chrome Optimized
# Quick check that everything is properly configured

echo "🧪 Dating App Development Setup Validation"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

echo ""
echo "📂 Checking Project Structure..."

# Check main directories
if [ -d "/home/m/development/DatingApp" ]; then
    success "Main project directory exists"
else
    error "Main project directory missing"
fi

if [ -d "/home/m/development/mobile-apps/flutter/dejtingapp" ]; then
    success "Flutter app directory exists"
else
    error "Flutter app directory missing"
fi

echo ""
echo "🔧 Checking Scripts..."

# Check startup scripts
if [ -x "/home/m/development/DatingApp/start_dating_app.sh" ]; then
    success "Main startup script is executable"
else
    error "Main startup script missing or not executable"
fi

if [ -x "/home/m/development/DatingApp/start_backend.sh" ]; then
    success "Backend startup script is executable"
else
    error "Backend startup script missing or not executable"
fi

if [ -x "/home/m/development/DatingApp/e2e-tests/run_all_tests.sh" ]; then
    success "Test runner script is executable"
else
    error "Test runner script missing or not executable"
fi

echo ""
echo "🧪 Checking Test Setup..."

if [ -f "/home/m/development/DatingApp/e2e-tests/test_login_enhanced.py" ]; then
    success "Enhanced E2E test exists"
else
    error "Enhanced E2E test missing"
fi

if [ -f "/home/m/development/DatingApp/e2e-tests/README.md" ]; then
    success "Testing documentation exists"
else
    warning "Testing documentation missing"
fi

echo ""
echo "🐳 Checking Docker Setup..."

if command -v docker &> /dev/null; then
    success "Docker is installed"
    if command -v docker-compose &> /dev/null; then
        success "Docker Compose is available"
    else
        error "Docker Compose not found"
    fi
else
    error "Docker not installed"
fi

if [ -f "/home/m/development/DatingApp/docker-compose.yml" ]; then
    success "Docker Compose configuration exists"
else
    error "Docker Compose configuration missing"
fi

echo ""
echo "📱 Checking Flutter Setup..."

if command -v flutter &> /dev/null; then
    success "Flutter is installed"
    
    # Check Flutter web support
    cd /home/m/development/mobile-apps/flutter/dejtingapp 2>/dev/null
    if flutter devices 2>/dev/null | grep -q "Chrome"; then
        success "Flutter web (Chrome) support detected"
    else
        warning "Flutter web support may not be enabled"
    fi
else
    error "Flutter not installed"
fi

echo ""
echo "🌐 Checking Development Files..."

if [ -f "/home/m/development/DatingApp/CHROME_DEVELOPMENT.md" ]; then
    success "Chrome development guide exists"
else
    warning "Chrome development guide missing"
fi

echo ""
echo "🎯 Quick Chrome Readiness Check..."

echo "To start development:"
echo "  1. cd /home/m/development/DatingApp"
echo "  2. ./start_dating_app.sh"
echo "  3. Choose option 1 (Chrome)"
echo ""
echo "To run tests:"
echo "  1. cd /home/m/development/DatingApp/e2e-tests" 
echo "  2. ./run_all_tests.sh"
echo ""
echo "Development URLs:"
echo "  🌐 Flutter App: http://localhost:36349"
echo "  🔌 Backend API: http://localhost:8080"
echo ""

success "Chrome-optimized setup validation complete!"
echo ""
echo "💡 See CHROME_DEVELOPMENT.md for quick start guide"
echo "📚 See e2e-tests/README.md for testing details"
