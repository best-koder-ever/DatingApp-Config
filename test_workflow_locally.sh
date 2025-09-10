#!/bin/bash
# 🧪 Local GitHub Actions Testing with act
# This script allows testing workflows locally before pushing

echo "🧪 LOCAL GITHUB ACTIONS TESTING"
echo "================================"

# Add act to PATH
export PATH="$HOME/bin:$PATH"

# Function to test a specific job
test_job() {
    local job_name=$1
    local service_name=${2:-"AuthService"}
    
    echo "🔍 Testing job: $job_name with service: $service_name"
    echo "=============================================="
    
    # Run act with the specific job
    act -j "$job_name" \
        --matrix service:"$service_name" \
        --env GITHUB_TOKEN="fake-token" \
        --platform ubuntu-latest=catthehacker/ubuntu:act-latest \
        --verbose
}

# Function to test just the build steps locally (without act)
test_build_locally() {
    echo "🔧 TESTING BUILDS LOCALLY (without containers)"
    echo "=============================================="
    
    services=("AuthService" "UserService" "MatchmakingService" "swipe-service" "photo-service")
    projects=("AuthService.csproj" "UserService.csproj" "MatchmakingService.csproj" "swipe-service.csproj" "PhotoService.csproj")
    
    for i in "${!services[@]}"; do
        service="${services[$i]}"
        project="${projects[$i]}"
        
        echo ""
        echo "🔍 Testing $service..."
        echo "Project: $project"
        
        if [ -d "$service" ]; then
            cd "$service"
            
            echo "  📦 Restoring packages..."
            if dotnet restore "$project" --verbosity minimal; then
                echo "  ✅ Restore successful"
                
                echo "  🔨 Building project..."
                if dotnet build "$project" --no-restore --verbosity minimal; then
                    echo "  ✅ Build successful"
                else
                    echo "  ❌ Build failed"
                fi
            else
                echo "  ❌ Restore failed"
            fi
            
            cd ..
        else
            echo "  ❌ Service directory not found: $service"
        fi
    done
}

# Function to show available options
show_menu() {
    echo ""
    echo "USAGE: $0 [option]"
    echo ""
    echo "Options:"
    echo "  build-local    - Test all service builds locally (fastest)"
    echo "  test-dotnet    - Test .NET job with act (slower, more accurate)"
    echo "  test-docker    - Test Docker build job with act"
    echo "  test-auth      - Test just AuthService with act"
    echo "  test-photo     - Test just photo-service with act"
    echo "  list-jobs      - List all available jobs in workflow"
    echo "  help           - Show this help"
}

# Function to list jobs
list_jobs() {
    echo "📋 Available jobs in workflow:"
    echo "============================="
    ~/bin/act --list 2>/dev/null || echo "Run from repository root with .github/workflows/"
}

# Main logic
case "${1:-help}" in
    "build-local"|"local"|"l")
        test_build_locally
        ;;
    "test-dotnet"|"dotnet"|"d")
        test_job "dotnet-tests" "AuthService"
        ;;
    "test-docker"|"docker")
        test_job "docker-build" "AuthService"
        ;;
    "test-auth"|"auth")
        test_job "dotnet-tests" "AuthService"
        ;;
    "test-photo"|"photo")
        test_job "dotnet-tests" "photo-service"
        ;;
    "list-jobs"|"list")
        list_jobs
        ;;
    "help"|"h"|*)
        show_menu
        ;;
esac

echo ""
echo "💡 TIP: Start with 'build-local' for fastest feedback!"
echo "🐳 Use act jobs for full GitHub Actions simulation"
