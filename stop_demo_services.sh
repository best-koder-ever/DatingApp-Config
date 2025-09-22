#!/bin/bash
# Stop All Demo Services
# Safely stops all running microservices

echo "🛑 Stopping Dating App Demo Services"
echo "===================================="

cd /home/m/development/DatingApp

# Function to stop service by PID file
stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name,,}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping $service_name (PID: $pid)..."
            kill "$pid"
            
            # Wait for graceful shutdown
            local count=0
            while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "   ⚠️  Force killing $service_name..."
                kill -9 "$pid"
            fi
            
            echo "   ✅ $service_name stopped"
        else
            echo "   ℹ️  $service_name was not running"
        fi
        rm -f "$pid_file"
    else
        echo "   ℹ️  No PID file found for $service_name"
    fi
}

echo "🔍 Checking for running services..."

# Stop services by PID files
stop_service "AuthService"
stop_service "UserService"
stop_service "MatchmakingService"

echo ""
echo "🧹 Cleaning up any remaining dotnet processes..."

# Kill any remaining dotnet processes related to our services
pkill -f "dotnet.*auth-service" 2>/dev/null || true
pkill -f "dotnet.*UserService" 2>/dev/null || true
pkill -f "dotnet.*matchmaking-service" 2>/dev/null || true

echo ""
echo "🏥 Checking final status..."

# Check if any services are still running
remaining_processes=$(ps aux | grep -E "(auth-service|UserService|matchmaking-service)" | grep -v grep | wc -l)

if [ "$remaining_processes" -eq 0 ]; then
    echo "✅ All demo services stopped successfully"
else
    echo "⚠️  $remaining_processes processes may still be running"
    echo "🔍 Remaining processes:"
    ps aux | grep -E "(auth-service|UserService|matchmaking-service)" | grep -v grep
fi

echo ""
echo "📋 Service Status:"
echo "   🔐 AuthService:        Stopped"
echo "   👤 UserService:        Stopped"
echo "   💕 MatchmakingService: Stopped"
echo ""
echo "💡 To restart services: ./start_demo_services.sh"
