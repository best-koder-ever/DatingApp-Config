#!/bin/bash

# Local Development Startup Script
# Starts all services for local development

echo "🚀 Starting Local Development Environment..."

check_port() {
    local host="$1"
    local port="$2"
    if command -v timeout >/dev/null 2>&1; then
        if timeout 1 bash -c "cat < /dev/null > /dev/tcp/${host}/${port}" >/dev/null 2>&1; then
            return 0
        fi
    else
        if bash -c "cat < /dev/null > /dev/tcp/${host}/${port}" >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

ensure_infrastructure() {
    local missing=0

    if ! check_port localhost 8090; then
        echo "❌ Keycloak (localhost:8090) is not reachable."
        missing=1
    fi

    if ! check_port localhost 3309; then
        echo "❌ Matchmaking MySQL (localhost:3309) is not reachable."
        missing=1
    fi

    if [ "$missing" -eq 1 ]; then
        echo "💡 Please run ./infrastructure/start.sh before launching the services."
        exit 1
    fi
}

ensure_infrastructure

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "dotnet" 2>/dev/null || true

# Wait a moment for processes to clean up
sleep 2

# Check if ports are available
echo "🔍 Checking port availability..."
PORTS=(8080 8081 8082 8083 8085 8086 8087)
for port in "${PORTS[@]}"; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "❌ Port $port is busy - killing processes..."
        pkill -f "$port" 2>/dev/null || true
        sleep 1
    fi
done

# Start AuthService
echo "🔐 Starting AuthService on port 8081..."
cd /home/m/development/DatingApp/AuthService
ASPNETCORE_ENVIRONMENT=Development DEMO_MODE=true ASPNETCORE_URLS=http://+:8081 dotnet run > ../logs/auth-service.log 2>&1 &
AUTH_PID=$!
sleep 2

# Start UserService
echo "👤 Starting UserService on port 8082..."
cd /home/m/development/DatingApp/UserService
ASPNETCORE_ENVIRONMENT=Development DEMO_MODE=true ASPNETCORE_URLS=http://+:8082 dotnet run > ../logs/user-service.log 2>&1 &
USER_PID=$!
sleep 2

# Start MatchmakingService
echo "� Starting MatchmakingService on port 8083..."
cd /home/m/development/DatingApp/MatchmakingService
ASPNETCORE_ENVIRONMENT=Development DEMO_MODE=true ASPNETCORE_URLS=http://+:8083 dotnet run > ../logs/matchmaking-service.log 2>&1 &
MATCHMAKING_PID=$!
sleep 2

# Start PhotoService  
echo "📸 Starting PhotoService on port 8085..."
cd /home/m/development/DatingApp/photo-service
ASPNETCORE_ENVIRONMENT=Development DEMO_MODE=true ASPNETCORE_URLS=http://+:8085 dotnet run > ../logs/photo-service.log 2>&1 &
PHOTO_PID=$!
sleep 2

# Start MessagingService
echo "💬 Starting MessagingService on port 8086..."
cd /home/m/development/DatingApp/messaging-service
ASPNETCORE_ENVIRONMENT=Development DEMO_MODE=true ASPNETCORE_URLS=http://+:8086 dotnet run > ../logs/messaging-service.log 2>&1 &
MESSAGING_PID=$!
sleep 2

# Start SwipeService
echo "👆 Starting SwipeService on port 8087..."
cd /home/m/development/DatingApp/swipe-service
ASPNETCORE_ENVIRONMENT=Development DEMO_MODE=true ASPNETCORE_URLS=http://+:8087 dotnet run --project SwipeService.csproj > ../logs/swipe-service.log 2>&1 &
SWIPE_PID=$!
sleep 2

# Start YARP Gateway
echo "🌐 Starting YARP Gateway on port 8080..."
cd /home/m/development/DatingApp/dejting-yarp/src/dejting-yarp
ASPNETCORE_ENVIRONMENT=Local ASPNETCORE_URLS=http://+:8080 dotnet run > ../../../logs/yarp-gateway.log 2>&1 &
YARP_PID=$!

# Create logs directory if it doesn't exist
mkdir -p /home/m/development/DatingApp/logs


# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 8

# Always run demo seeder for development
echo "🌱 Seeding demo data..."
cd /home/m/development/mobile-apps/flutter/dejtingapp
python3 smart_demo_seeder_fixed.py
cd /home/m/development/DatingApp

# Health checks
echo "🏥 Performing health checks..."
AUTH_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health 2>/dev/null || echo "000")
USER_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8082/health 2>/dev/null || echo "000")
MATCHMAKING_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/health 2>/dev/null || echo "000")
PHOTO_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8085/health 2>/dev/null || echo "000")
MESSAGING_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8086/health 2>/dev/null || echo "000")
MESSAGING_READINESS=$(curl -s http://localhost:8086/health 2>/dev/null || echo "")
SWIPE_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8087/health 2>/dev/null || echo "000")
YARP_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health 2>/dev/null || echo "000")

echo ""
echo "📊 Service Status:"
if [ "$AUTH_HEALTH" = "200" ]; then
    echo "✅ AuthService: Running (PID: $AUTH_PID)"
else
    echo "❌ AuthService: Failed to start (HTTP: $AUTH_HEALTH)"
fi

if [ "$USER_HEALTH" = "200" ]; then
    echo "✅ UserService: Running (PID: $USER_PID)"
else
    echo "❌ UserService: Failed to start (HTTP: $USER_HEALTH)"
fi

if [ "$MATCHMAKING_HEALTH" = "200" ]; then
    echo "✅ MatchmakingService: Running (PID: $MATCHMAKING_PID)"
else
    echo "❌ MatchmakingService: Failed to start (HTTP: $MATCHMAKING_HEALTH)"
fi

if [ "$PHOTO_HEALTH" = "200" ]; then
    echo "✅ PhotoService: Running (PID: $PHOTO_PID)"
else
    echo "❌ PhotoService: Failed to start (HTTP: $PHOTO_HEALTH)"
fi

if [ "$MESSAGING_HEALTH" = "200" ]; then
    READY_MSG="$(echo "$MESSAGING_READINESS" | sed -n 's/.*"status"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
    if [ -z "$READY_MSG" ]; then
        READY_MSG=$(echo "$MESSAGING_READINESS" | tr -d '\n' | cut -c1-120)
    fi
    if [ -n "$READY_MSG" ]; then
        echo "✅ MessagingService: Running (PID: $MESSAGING_PID) – readiness: $READY_MSG"
    else
        echo "✅ MessagingService: Running (PID: $MESSAGING_PID)"
    fi
else
    echo "❌ MessagingService: Failed to start (HTTP: $MESSAGING_HEALTH)"
fi

if [ "$SWIPE_HEALTH" = "200" ]; then
    echo "✅ SwipeService: Running (PID: $SWIPE_PID)"
else
    echo "❌ SwipeService: Failed to start (HTTP: $SWIPE_HEALTH)"
fi

if [ "$YARP_HEALTH" = "200" ]; then
    echo "✅ YARP Gateway: Running (PID: $YARP_PID)"
else
    echo "❌ YARP Gateway: Failed to start (HTTP: $YARP_HEALTH)"
fi

echo ""
echo "📝 Logs:"
echo "   AuthService: tail -f logs/auth-service.log"
echo "   UserService: tail -f logs/user-service.log"
echo "   MatchmakingService: tail -f logs/matchmaking-service.log"
echo "   PhotoService: tail -f logs/photo-service.log"
echo "   MessagingService: tail -f logs/messaging-service.log"
echo "   SwipeService: tail -f logs/swipe-service.log"
echo "   YARP Gateway: tail -f logs/yarp-gateway.log"
echo ""
echo "🛑 To stop: ./dev-stop.sh"
echo "🔄 To restart: ./dev-restart.sh"
echo "📊 To check status: ./dev-status.sh"
echo ""
echo "🎯 Complete Dating App Backend Running!"

echo "💡 All services: 8080(Gateway), 8081(Auth), 8082(User), 8083(Matchmaking), 8085(Photo), 8086(Messaging), 8087(Swipe)"

# Automatically start Flutter app on Chrome for development
echo "📱 Launching Flutter app on Chrome..."
# Kill all Chrome instances to ensure only one is running
pkill -f "chrome" 2>/dev/null || true
sleep 2
cd /home/m/development/mobile-apps/flutter/dejtingapp
./start_flutter.sh &
cd /home/m/development/DatingApp
