#!/bin/bash

# Enhanced Development Script with CI/CD Status and Health Monitoring
# Usage: ./enhanced_dev_status.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                ${CYAN}Dating App - Enhanced Dev Status${NC}               ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo -e "${BLUE}▶ $1${NC}"
    echo "────────────────────────────────────────────────────────────────"
}

print_success() {
    echo -e "  ${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "  ${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "  ${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "  ${CYAN}ℹ️  $1${NC}"
}

check_service_health() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-""}
    
    if curl -s -f "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        print_success "$service_name (port $port) - Healthy"
        return 0
    else
        print_error "$service_name (port $port) - Unhealthy"
        return 1
    fi
}

check_git_status() {
    local project_dir=$1
    local project_name=$2
    
    if [ -d "$project_dir/.git" ]; then
        cd "$project_dir"
        
        # Check for uncommitted changes
        if [ -n "$(git status --porcelain)" ]; then
            print_warning "$project_name has uncommitted changes"
            # Show brief status
            git status --short | head -5 | while read line; do
                print_info "  $line"
            done
        else
            print_success "$project_name is clean"
        fi
        
        # Check if push is needed
        local ahead=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
        if [ "$ahead" -gt 0 ]; then
            print_warning "$project_name is $ahead commits ahead of remote"
        fi
        
        cd - > /dev/null
    else
        print_warning "$project_name is not a git repository"
    fi
}

check_ci_cd_status() {
    print_section "CI/CD Pipeline Status"
    
    # Check if GitHub Actions workflow exists
    if [ -f ".github/workflows/ci-cd-pipeline.yml" ]; then
        print_success "GitHub Actions workflow configured"
        
        # Get last commit info
        local last_commit=$(git log -1 --pretty=format:"%h - %s (%cr)" 2>/dev/null || echo "No commits")
        print_info "Last commit: $last_commit"
        
        # Check if main branch
        local current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
        if [ "$current_branch" = "main" ]; then
            print_success "On main branch (triggers production pipeline)"
        else
            print_info "On branch: $current_branch"
        fi
    else
        print_warning "No GitHub Actions workflow found"
        print_info "Run: Create .github/workflows/ci-cd-pipeline.yml for automated testing"
    fi
    
    echo ""
}

check_monitoring_status() {
    print_section "Monitoring & Health Checks"
    
    # Check if monitoring stack is running
    if command -v docker-compose &> /dev/null; then
        if [ -f "docker-compose.monitoring.yml" ]; then
            print_success "Monitoring configuration available"
            
            # Check if monitoring services are running
            if docker-compose -f docker-compose.monitoring.yml ps | grep -q "Up"; then
                print_success "Monitoring services are running"
                print_info "Grafana: http://localhost:3000 (admin/dating_app_2025)"
                print_info "Prometheus: http://localhost:9090"
                print_info "Health Dashboard: http://localhost:8090"
            else
                print_warning "Monitoring services not running"
                print_info "Start with: docker-compose -f docker-compose.monitoring.yml up -d"
            fi
        else
            print_warning "Monitoring configuration not found"
        fi
    fi
    
    echo ""
}

check_backend_services() {
    print_section "Backend Services Health"
    
    local services_up=0
    local total_services=6
    
    check_service_health "YARP Gateway" "8080" && ((services_up++))
    check_service_health "Auth Service" "8081" "/health" && ((services_up++))
    check_service_health "User Service" "8082" "/health" && ((services_up++))
    check_service_health "Matchmaking Service" "8083" "/api/matchmaking/health" && ((services_up++))
    check_service_health "Swipe Service" "8084" "/api/swipes/health" && ((services_up++))
    check_service_health "Photo Service" "8085" "/health" && ((services_up++))
    
    echo ""
    if [ $services_up -eq $total_services ]; then
        print_success "All backend services are healthy ($services_up/$total_services)"
    elif [ $services_up -gt 0 ]; then
        print_warning "Partial backend availability ($services_up/$total_services services up)"
    else
        print_error "No backend services are running"
        print_info "Start with: docker-compose up -d"
    fi
    
    echo ""
}

check_flutter_status() {
    print_section "Flutter App Status"
    
    local flutter_dir="/home/m/development/mobile-apps/flutter/dejtingapp"
    
    if [ -d "$flutter_dir" ]; then
        cd "$flutter_dir"
        
        # Check Flutter analyze
        if flutter analyze --no-fatal-infos > /dev/null 2>&1; then
            print_success "Flutter analysis passed"
        else
            print_warning "Flutter analysis found issues"
            print_info "Run: flutter analyze for details"
        fi
        
        # Check if dependencies are up to date
        if [ -f ".dart_tool/package_config.json" ]; then
            print_success "Flutter dependencies are installed"
        else
            print_warning "Flutter dependencies need to be installed"
            print_info "Run: flutter pub get"
        fi
        
        # Check if app is running
        if lsof -i :36349 > /dev/null 2>&1; then
            print_success "Flutter web app is running on port 36349"
        else
            print_info "Flutter app not currently running"
        fi
        
        cd - > /dev/null
    else
        print_error "Flutter directory not found"
    fi
    
    echo ""
}

check_test_status() {
    print_section "Testing Status"
    
    # Check if E2E tests exist and can run
    if [ -d "e2e-tests" ]; then
        print_success "E2E test suite available"
        
        if [ -f "e2e-tests/run_all_tests.sh" ]; then
            print_success "Automated test runner available"
            print_info "Run tests with: cd e2e-tests && ./run_all_tests.sh"
        fi
    else
        print_warning "No E2E tests found"
    fi
    
    # Check Flutter tests
    local flutter_dir="/home/m/development/mobile-apps/flutter/dejtingapp"
    if [ -d "$flutter_dir/test" ]; then
        print_success "Flutter unit tests available"
    else
        print_warning "No Flutter unit tests found"
    fi
    
    # Check .NET tests
    local dotnet_tests_found=0
    for service in auth-service user-service matchmaking-service swipe-service photo-service; do
        if [ -d "$service" ] && find "$service" -name "*Tests.csproj" -o -name "*Test.csproj" | grep -q .; then
            ((dotnet_tests_found++))
        fi
    done
    
    if [ $dotnet_tests_found -gt 0 ]; then
        print_success "Found .NET tests in $dotnet_tests_found services"
    else
        print_warning "No .NET unit tests found"
    fi
    
    echo ""
}

check_git_repositories() {
    print_section "Git Repository Status"
    
    # Main repository
    check_git_status "." "DatingApp (main)"
    
    # Individual services
    for service in auth-service user-service matchmaking-service swipe-service photo-service dejting-yarp TestDataGenerator; do
        if [ -d "$service" ]; then
            check_git_status "$service" "$service"
        fi
    done
    
    # Flutter app
    local flutter_dir="/home/m/development/mobile-apps/flutter/dejtingapp"
    if [ -d "$flutter_dir" ]; then
        check_git_status "$flutter_dir" "Flutter App"
    fi
    
    echo ""
}

show_quick_actions() {
    print_section "Quick Actions"
    
    echo -e "${CYAN}Development:${NC}"
    print_info "Start all services: ./start_dating_app.sh"
    print_info "Run comprehensive tests: cd e2e-tests && ./run_all_tests.sh"
    print_info "Flutter hot reload: cd mobile-apps/flutter/dejtingapp && flutter run -d chrome"
    
    echo ""
    echo -e "${CYAN}Monitoring:${NC}"
    print_info "Start monitoring: docker-compose -f docker-compose.monitoring.yml up -d"
    print_info "View dashboards: http://localhost:3000 (Grafana)"
    print_info "Health dashboard: http://localhost:8090"
    
    echo ""
    echo -e "${CYAN}CI/CD:${NC}"
    print_info "Commit all changes: ./commit_and_push_all.sh"
    print_info "Check build status: View GitHub Actions tab"
    
    echo ""
}

show_system_overview() {
    print_section "System Overview"
    
    # Count various components
    local services_count=$(find . -maxdepth 1 -name "*-service" -type d | wc -l)
    local dockerfile_count=$(find . -name "Dockerfile" | wc -l)
    local test_files=$(find . -name "*test*" -o -name "*Test*" | wc -l)
    
    print_info "Microservices: $services_count"
    print_info "Dockerfiles: $dockerfile_count"
    print_info "Test files: $test_files"
    print_info "Architecture: .NET 8 + Flutter + MySQL + YARP"
    
    echo ""
}

# Main execution
main() {
    print_header
    
    # Navigate to the main directory
    cd /home/m/development/DatingApp
    
    show_system_overview
    check_ci_cd_status
    check_monitoring_status
    check_backend_services
    check_flutter_status
    check_test_status
    check_git_repositories
    show_quick_actions
    
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✨ Enhanced development status check complete! ✨${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
}

# Run the main function
main "$@"
