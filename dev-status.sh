#!/bin/bash

# Local Development Status Script
# Shows current status of all services

echo "📊 Local Development Environment Status"
echo "========================================"

# Check running processes
echo ""
echo "🔍 Running .NET Processes:"
DOTNET_PROCESSES=$(ps aux | grep -E "(AuthService|PhotoService|UserService|MatchmakingService|MessagingService|SwipeService|dejting-yarp)" | grep -v grep)
if [ -z "$DOTNET_PROCESSES" ]; then
    echo "   No services running"
else
    echo "$DOTNET_PROCESSES" | while read line; do
        echo "   $line"
    done
fi

echo ""
echo "🌐 Port Status:"
# Check all service ports
PORTS=(8080 8081 8082 8083 8085 8086 8087)
SERVICE_NAMES=("YARP Gateway" "AuthService" "UserService" "MatchmakingService" "PhotoService" "MessagingService" "SwipeService")

for i in "${!PORTS[@]}"; do
    port=${PORTS[$i]}
    service=${SERVICE_NAMES[$i]}
    if lsof -i :$port >/dev/null 2>&1; then
        PROCESS=$(lsof -i :$port | tail -n 1 | awk '{print $1}')
        echo "   Port $port ($service): ✅ In use by $PROCESS"
    else
        echo "   Port $port ($service): ❌ Available"
    fi
done

echo ""
echo "🏥 Health Checks:"
# Health check for all services
SERVICES=(8080 8081 8082 8083 8085 8086 8087)
SERVICE_NAMES=("YARP Gateway" "AuthService" "UserService" "MatchmakingService" "PhotoService" "MessagingService" "SwipeService")

for i in "${!SERVICES[@]}"; do
    port=${SERVICES[$i]}
    service=${SERVICE_NAMES[$i]}
    HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null || echo "000")
    if [ "$HEALTH" = "200" ]; then
        echo "   $service: ✅ Healthy (HTTP 200)"
    elif [ "$HEALTH" = "000" ]; then
        echo "   $service: ❌ Unreachable"
    else
        echo "   $service: ⚠️  HTTP $HEALTH"
    fi
done

echo ""
echo "📝 Log Files:"
LOG_FILES=("auth-service.log" "user-service.log" "matchmaking-service.log" "photo-service.log" "messaging-service.log" "swipe-service.log" "yarp-gateway.log")
SERVICE_NAMES=("AuthService" "UserService" "MatchmakingService" "PhotoService" "MessagingService" "SwipeService" "YARP Gateway")

for i in "${!LOG_FILES[@]}"; do
    logfile=${LOG_FILES[$i]}
    service=${SERVICE_NAMES[$i]}
    if [ -f "logs/$logfile" ]; then
        LOG_SIZE=$(wc -l < "logs/$logfile")
        echo "   $service: logs/$logfile ($LOG_SIZE lines)"
    else
        echo "   $service: No log file"
    fi
done

echo ""
echo "🎮 Commands:"
echo "   ./dev-start.sh   - Start all services"
echo "   ./dev-stop.sh    - Stop all services"
echo "   ./dev-restart.sh - Restart all services"
echo "   ./dev-logs.sh    - View live logs"
