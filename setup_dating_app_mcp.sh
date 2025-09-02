#!/bin/bash
# 💕 Setting up Dating App specific MCP tools

echo "💕 Setting up Dating App specific MCP tools..."
echo "=============================================="

# Create project-specific MCP config
echo "⚙️  Creating Dating App specific MCP configuration..."

cat > ~/.config/mcp/dating-app-config.json << 'EOF'
{
  "mcpServers": {
    "auth-service": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/DatingApp/auth-service"],
      "env": {
        "SERVICE_NAME": "auth-service",
        "PORT": "5001"
      }
    },
    "messaging-service": {
      "command": "npx", 
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/DatingApp/messaging-service"],
      "env": {
        "SERVICE_NAME": "messaging-service", 
        "PORT": "5007"
      }
    },
    "matchmaking-service": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/DatingApp/matchmaking-service"],
      "env": {
        "SERVICE_NAME": "matchmaking-service",
        "PORT": "5003"
      }
    },
    "swipe-service": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/DatingApp/swipe-service"],
      "env": {
        "SERVICE_NAME": "swipe-service",
        "PORT": "5005"
      }
    },
    "user-service": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/DatingApp/user-service"],
      "env": {
        "SERVICE_NAME": "user-service",
        "PORT": "5002"
      }
    },
    "photo-service": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/DatingApp/photo-service"],
      "env": {
        "SERVICE_NAME": "photo-service",
        "PORT": "5004"
      }
    },
    "flutter-app": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/home/m/development/mobile-apps/flutter/dejtingapp"],
      "env": {
        "APP_TYPE": "flutter",
        "PLATFORM": "mobile"
      }
    },
    "docker-services": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-docker"],
      "env": {
        "COMPOSE_FILE": "/home/m/development/DatingApp/docker-compose.yml",
        "PROJECT_NAME": "dating-app"
      }
    },
    "dating-app-git": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-git", "/home/m/development/DatingApp"],
      "env": {
        "REPO_TYPE": "monorepo",
        "SERVICES": "auth,messaging,matchmaking,swipe,user,photo"
      }
    }
  }
}
EOF

# Create service-specific shortcuts
echo "🔧 Creating service management shortcuts..."

cat > ~/.config/mcp/service-shortcuts.json << 'EOF'
{
  "shortcuts": {
    "start-all": "docker-compose up -d",
    "stop-all": "docker-compose down",
    "logs-auth": "docker-compose logs -f auth-service",
    "logs-messaging": "docker-compose logs -f messaging-service", 
    "logs-matching": "docker-compose logs -f matchmaking-service",
    "restart-messaging": "docker-compose restart messaging-service",
    "db-status": "mysql -e 'SHOW DATABASES;' | grep -E '(dating|auth|messaging)'",
    "test-all": "./run_all_tests.sh",
    "build-all": "docker-compose build",
    "flutter-run": "cd ../mobile-apps/flutter/dejtingapp && flutter run"
  }
}
EOF

# Create MCP testing script
cat > ~/.config/mcp/test_mcp.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing MCP Dating App Configuration..."
echo "=========================================="

# Test each MCP server
echo "📋 Testing MCP servers:"

servers=("auth-service" "messaging-service" "matchmaking-service" "flutter-app" "docker-services")
for server in "${servers[@]}"; do
    echo -n "   Testing $server: "
    if mcp test-connection "$server" 2>/dev/null; then
        echo "✅ OK"
    else
        echo "❌ Failed"
    fi
done

echo ""
echo "🏗️ Service Directory Status:"
services=("auth-service" "messaging-service" "matchmaking-service" "swipe-service" "user-service" "photo-service")
for service in "${services[@]}"; do
    if [ -d "/home/m/development/DatingApp/$service" ]; then
        echo "   ✅ $service - Found"
    else
        echo "   ❌ $service - Missing"
    fi
done

echo ""
echo "📱 Flutter App Status:"
if [ -d "/home/m/development/mobile-apps/flutter/dejtingapp" ]; then
    echo "   ✅ Flutter app - Found"
else
    echo "   ❌ Flutter app - Missing"
fi

echo ""
echo "🐳 Docker Status:"
if docker ps >/dev/null 2>&1; then
    echo "   ✅ Docker - Running"
    docker ps --format "table {{.Names}}\t{{.Status}}" | head -n 6
else
    echo "   ❌ Docker - Not running"
fi

echo ""
echo "💾 Database Status:"
if mysql -e "SHOW DATABASES;" 2>/dev/null | grep -q "dating"; then
    echo "   ✅ Database - Connected"
    mysql -e "SHOW DATABASES;" | grep -E "(dating|auth|messaging)"
else
    echo "   ⚠️  Database - Connection issues"
fi
EOF

chmod +x ~/.config/mcp/test_mcp.sh

echo "✅ Dating app MCP configuration created!"
echo ""
echo "📊 Configuration includes:"
echo "   🔧 7 microservice configurations"
echo "   📱 Flutter app integration"
echo "   🐳 Docker container management"
echo "   🔄 Git repository handling"
echo "   ⚡ Service shortcuts and automation"
echo ""
echo "🧪 Test your setup:"
echo "   ~/.config/mcp/test_mcp.sh"
echo ""
echo "🎯 Your Claude 4 can now handle:"
echo "   ✅ Individual service analysis and debugging"
echo "   ✅ Cross-service architecture optimization"
echo "   ✅ Database schema management"
echo "   ✅ Container orchestration"
echo "   ✅ Mobile app integration testing"
