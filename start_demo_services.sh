#!/bin/bash
# Start All Services with Demo Mode
# Launches all microservices with demo endpoints enabled

echo "🚀 Starting Dating App Services with Demo Mode"
echo "=============================================="

# Set demo mode environment variable
export DEMO_MODE=true

# Navigate to main project directory
cd /home/m/development/DatingApp

echo "📱 Demo Mode Environment: $DEMO_MODE"
echo ""

# Function to start service in background
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    
    echo "🔧 Starting $service_name on port $port..."
    cd "$service_path"
    
    # Build and run the service
    dotnet run --urls="http://localhost:$port" > "../logs/${service_name,,}.log" 2>&1 &
    local pid=$!
    echo "$pid" > "../logs/${service_name,,}.pid"
    
    echo "   ✅ $service_name started (PID: $pid)"
    cd ..
}

# Create logs directory
mkdir -p logs

echo "🏗️  Building and starting microservices..."
echo ""

# Start AuthService (port 8081)
start_service "AuthService" "AuthService" 8081

# Wait a moment between services
sleep 2

# Start UserService (port 8082)  
start_service "UserService" "UserService" 8082

# Wait a moment between services
sleep 2

# Start MatchmakingService (port 8083)
start_service "MatchmakingService" "MatchmakingService" 8083

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 10

echo ""
echo "🏥 Checking service health..."

# Check if services are responding
check_service() {
    local service_name=$1
    local url=$2
    
    if curl -s "$url" > /dev/null 2>&1; then
        echo "   ✅ $service_name: Healthy"
        return 0
    else
        echo "   ❌ $service_name: Not responding"
        return 1
    fi
}

# Check demo health endpoints
all_healthy=true

if ! check_service "AuthService Demo" "http://localhost:8081/api/demo/health"; then
    all_healthy=false
fi

if ! check_service "UserService Demo" "http://localhost:8082/api/demo/health"; then
    all_healthy=false
fi

if ! check_service "MatchmakingService Demo" "http://localhost:8083/api/demo/health"; then
    all_healthy=false
fi

echo ""

if [ "$all_healthy" = true ]; then
    echo "🎉 All services started successfully with demo mode!"
    echo ""
    echo "📋 Available Demo Endpoints:"
    echo "   🔐 AuthService Demo:        http://localhost:8081/api/demo/health"
    echo "   👤 UserService Demo:        http://localhost:8082/api/demo/health"
    echo "   💕 MatchmakingService Demo: http://localhost:8083/api/demo/health"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Run the Flutter app demo system: cd mobile-apps/flutter/dejtingapp && python3 accurate_demo.py"
    echo "   2. Use option 9 to test backend demo endpoints"
    echo "   3. Use options 1-8 for Flutter UI automation testing"
    echo ""
    echo "🛑 To stop all services: pkill -f dotnet"
else
    echo "⚠️  Some services failed to start properly"
    echo "🔍 Check log files in logs/ directory for details"
    echo ""
    echo "📋 Log Files:"
    echo "   • logs/authservice.log"
    echo "   • logs/userservice.log" 
    echo "   • logs/matchmakingservice.log"
fi

echo ""
echo "📊 Service Status Summary:"
echo "   📋 AuthService:        PID $(cat logs/authservice.pid 2>/dev/null || echo 'N/A')"
echo "   📋 UserService:        PID $(cat logs/userservice.pid 2>/dev/null || echo 'N/A')"
echo "   📋 MatchmakingService: PID $(cat logs/matchmakingservice.pid 2>/dev/null || echo 'N/A')"
echo ""
echo "💡 Use 'ps aux | grep dotnet' to see running services"
echo "🛑 Use 'pkill -f dotnet' to stop all services"
