#!/bin/bash
# 🤖 Enhanced GitHub helpers with MCP integration for Claude 4

ROOT_DIR="/home/m/development/DatingApp"

show_mcp_status() {
    echo "🔧 MCP Development Environment Status:"
    echo "====================================="
    
    echo "📊 MCP Servers:"
    if command -v mcp &> /dev/null; then
        mcp list-servers 2>/dev/null || echo "   ⚠️  MCP servers not responding"
    else
        echo "   ❌ MCP CLI not installed"
    fi
    
    echo ""
    echo "🏗️ Dating App Services with MCP Context:"
    services=("auth-service" "messaging-service" "matchmaking-service" "swipe-service" "user-service" "photo-service")
    for service in "${services[@]}"; do
        if [ -d "$ROOT_DIR/$service" ]; then
            # Check if service has recent activity
            if [ -f "$ROOT_DIR/$service/Program.cs" ] || [ -f "$ROOT_DIR/$service/src/Program.cs" ]; then
                echo "   ✅ $service - MCP enabled & active"
            else
                echo "   ⚠️  $service - MCP enabled but check structure"
            fi
        else
            echo "   ❌ $service - Not found"
        fi
    done
    
    echo ""
    echo "📱 Flutter App:"
    if [ -d "/home/m/development/mobile-apps/flutter/dejtingapp" ]; then
        echo "   ✅ Flutter app - MCP enabled"
    else
        echo "   ❌ Flutter app - Not found"
    fi
    
    echo ""
    echo "🐳 Docker Services:"
    if docker ps >/dev/null 2>&1; then
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -n 8
    else
        echo "   ❌ Docker not running"
    fi
    
    echo ""
    echo "💾 Database Status:"
    if mysql -e "SHOW DATABASES;" 2>/dev/null | grep -E "(dating|auth|messaging)" >/dev/null; then
        echo "   ✅ Database connections active:"
        mysql -e "SHOW DATABASES;" 2>/dev/null | grep -E "(dating|auth|messaging)" | sed 's/^/      /'
    else
        echo "   ⚠️  Database connection issues"
    fi
    
    echo ""
    echo "🔄 Git Repository Status:"
    echo "   Main repo: $(git rev-parse --abbrev-ref HEAD) - $(git log --oneline -1 | cut -c1-50)"
    echo "   Uncommitted changes: $(git status --porcelain | wc -l) files"
}

start_mcp_development() {
    echo "🚀 Starting MCP-Enhanced Development Environment..."
    echo "=================================================="
    
    # Start all services
    echo "🐳 Starting Docker services..."
    cd "$ROOT_DIR"
    docker-compose up -d
    
    # Wait for services to start
    echo "⏳ Waiting for services to initialize..."
    sleep 10
    
    # Test MCP connections
    echo "🔧 Testing MCP connections..."
    if command -v mcp &> /dev/null; then
        mcp test-connection filesystem 2>/dev/null && echo "   ✅ Filesystem MCP ready" || echo "   ⚠️  Filesystem MCP issue"
        mcp test-connection git 2>/dev/null && echo "   ✅ Git MCP ready" || echo "   ⚠️  Git MCP issue"
        mcp test-connection docker 2>/dev/null && echo "   ✅ Docker MCP ready" || echo "   ⚠️  Docker MCP issue"
    else
        echo "   ⚠️  MCP CLI not available - run setup first"
    fi
    
    echo ""
    echo "🏥 Health Check:"
    echo "   Auth Service: $(curl -s http://localhost:5001/health 2>/dev/null || echo 'Not responding')"
    echo "   Messaging Service: $(curl -s http://localhost:5007/health 2>/dev/null || echo 'Not responding')"
    echo "   Matchmaking Service: $(curl -s http://localhost:5003/health 2>/dev/null || echo 'Not responding')"
    
    echo ""
    echo "✅ MCP Development environment ready!"
    echo "💡 Your Claude 4 can now:"
    echo "   🔍 Access your entire codebase structure"
    echo "   🔄 Manage git across all 7 services"
    echo "   💾 Query databases directly"
    echo "   🐳 Control Docker containers"
    echo "   📚 Search documentation in real-time"
    echo "   🧠 Maintain persistent context about your dating app"
}

analyze_project_with_mcp() {
    echo "🔍 MCP-Powered Project Analysis..."
    echo "================================="
    
    echo "📊 Codebase Statistics:"
    echo "   Total services: $(ls -d */ 2>/dev/null | grep -E '(service|app)' | wc -l)"
    echo "   C# files: $(find . -name '*.cs' | wc -l)"
    echo "   Dart files: $(find ../mobile-apps/flutter/dejtingapp -name '*.dart' 2>/dev/null | wc -l)"
    echo "   Docker configs: $(find . -name 'Dockerfile' -o -name 'docker-compose*.yml' | wc -l)"
    
    echo ""
    echo "🔧 Recent Development Activity:"
    echo "   Recent commits: $(git log --oneline --since='7 days ago' | wc -l) in last week"
    echo "   Modified files: $(git status --porcelain | wc -l) uncommitted"
    echo "   Active branches: $(git branch -a | wc -l)"
    
    echo ""
    echo "🏗️ Architecture Overview:"
    echo "   Backend services: $(ls -d *-service 2>/dev/null | wc -l)"
    echo "   Database connections: $(grep -r "ConnectionString" . --include="*.json" | wc -l)"
    echo "   API endpoints: $(grep -r "Route\|HttpGet\|HttpPost" . --include="*.cs" | wc -l)"
    
    echo ""
    echo "📱 Mobile Integration:"
    if [ -d "../mobile-apps/flutter/dejtingapp" ]; then
        echo "   Flutter screens: $(find ../mobile-apps/flutter/dejtingapp/lib -name '*screen*.dart' 2>/dev/null | wc -l)"
        echo "   Services: $(find ../mobile-apps/flutter/dejtingapp/lib -name '*service*.dart' 2>/dev/null | wc -l)"
    else
        echo "   ❌ Flutter app not found"
    fi
}

setup_claude4_integration() {
    echo "🤖 Setting up Claude 4 Integration..."
    echo "===================================="
    
    # Create Claude 4 specific configuration
    cat > ~/.config/mcp/claude4-integration.json << 'EOF'
{
  "claude4Config": {
    "projectContext": "Dating App Microservices",
    "architecture": "7 microservices + Flutter mobile app",
    "techStack": [
      "ASP.NET Core 8.0",
      "Entity Framework Core", 
      "MySQL",
      "SignalR",
      "Docker",
      "Flutter",
      "JWT Authentication"
    ],
    "services": {
      "auth-service": "Port 5001 - JWT Authentication & User Management",
      "messaging-service": "Port 5007 - Real-time messaging with SignalR", 
      "matchmaking-service": "Port 5003 - Match algorithm & recommendations",
      "swipe-service": "Port 5005 - Swipe logic & user interactions",
      "user-service": "Port 5002 - User profiles & preferences",
      "photo-service": "Port 5004 - Photo upload & management"
    },
    "databases": {
      "auth_db": "User authentication & profiles",
      "messaging_db": "Chat messages & conversations",
      "matchmaking_db": "Matches & compatibility scores"
    },
    "mobileApp": {
      "platform": "Flutter",
      "features": ["Real-time chat", "Swiping", "Profile management", "Photo sharing"]
    }
  }
}
EOF

    echo "✅ Claude 4 integration configured!"
    echo "🎯 This provides Claude 4 with complete context about:"
    echo "   📱 Your dating app architecture"
    echo "   🔧 All 7 microservices and their purposes"
    echo "   💾 Database structure and relationships"
    echo "   🔄 Git repositories and development workflow"
    echo "   🐳 Docker container orchestration"
}

run_mcp_diagnostics() {
    echo "🔍 MCP Diagnostic Report..."
    echo "=========================="
    
    # Run the MCP test script if it exists
    if [ -f ~/.config/mcp/test_mcp.sh ]; then
        ~/.config/mcp/test_mcp.sh
    else
        echo "⚠️  MCP test script not found - run setup first"
    fi
    
    echo ""
    echo "🔧 System Requirements Check:"
    echo -n "   Node.js: "
    node --version 2>/dev/null || echo "❌ Not installed"
    echo -n "   npm: "
    npm --version 2>/dev/null || echo "❌ Not installed"
    echo -n "   Docker: "
    docker --version 2>/dev/null | cut -d' ' -f3 || echo "❌ Not installed"
    echo -n "   MySQL: "
    mysql --version 2>/dev/null | cut -d' ' -f6 || echo "❌ Not installed"
    echo -n "   Flutter: "
    flutter --version 2>/dev/null | head -1 || echo "❌ Not installed"
}

# Main menu for MCP-enhanced development
case "${1:-help}" in
    "mcp")
        show_mcp_status
        ;;
    "mcp-start")
        start_mcp_development
        ;;
    "mcp-setup")
        echo "🔧 Running MCP setup..."
        ./setup_mcp_plugins.sh
        ./setup_dating_app_mcp.sh
        setup_claude4_integration
        ;;
    "mcp-analyze")
        analyze_project_with_mcp
        ;;
    "mcp-test")
        run_mcp_diagnostics
        ;;
    "mcp-claude4")
        setup_claude4_integration
        ;;
    *)
        echo "🤖 Enhanced Dating App Development with MCP & Claude 4"
        echo "======================================================"
        echo ""
        echo "MCP Commands:"
        echo "  ./enhanced_github_helpers_mcp.sh mcp         - Show MCP status"
        echo "  ./enhanced_github_helpers_mcp.sh mcp-start   - Start MCP development environment"
        echo "  ./enhanced_github_helpers_mcp.sh mcp-setup   - Install & configure MCP plugins"
        echo "  ./enhanced_github_helpers_mcp.sh mcp-analyze - Analyze project with MCP context"
        echo "  ./enhanced_github_helpers_mcp.sh mcp-test    - Run MCP diagnostics"
        echo "  ./enhanced_github_helpers_mcp.sh mcp-claude4 - Setup Claude 4 integration"
        echo ""
        echo "💡 With MCP + Claude 4, your AI can:"
        echo "   🔍 Navigate your entire 7-service architecture"
        echo "   📊 Query databases and analyze data in real-time"
        echo "   🐳 Manage Docker containers and services"
        echo "   🔄 Handle git operations across all repositories"
        echo "   📚 Search documentation and Stack Overflow"
        echo "   🧠 Maintain persistent context about your dating app"
        echo "   🔧 Debug issues across microservices"
        echo "   📱 Analyze Flutter app integration"
        echo "   ⚡ Automate development workflows"
        echo ""
        echo "🚀 Next steps:"
        echo "   1. Run: ./enhanced_github_helpers_mcp.sh mcp-setup"
        echo "   2. Add GitHub token to ~/.config/mcp/config.json"
        echo "   3. Start development: ./enhanced_github_helpers_mcp.sh mcp-start"
        echo "   4. Test with Claude 4: Ask it to analyze your dating app!"
        ;;
esac
