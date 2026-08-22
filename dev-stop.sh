#!/bin/bash

# Local Development Stop Script
# Stops all local development services

echo "🛑 Stopping Local Development Environment..."

# Kill dotnet processes
echo "🧹 Stopping .NET services..."
pkill -f "dotnet run" 2>/dev/null || true
pkill -f "AuthService" 2>/dev/null || true  
pkill -f "PhotoService" 2>/dev/null || true
pkill -f "UserService" 2>/dev/null || true
pkill -f "MatchmakingService" 2>/dev/null || true
pkill -f "MessagingService" 2>/dev/null || true
pkill -f "SwipeService" 2>/dev/null || true
pkill -f "dejting-yarp" 2>/dev/null || true

# Stop Whisper feedback transcription watcher
pkill -f "process-feedback.py" 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Check if processes are still running
REMAINING=$(ps aux | grep -E "(AuthService|PhotoService|UserService|MatchmakingService|MessagingService|SwipeService|dejting-yarp)" | grep -v grep | wc -l)

if [ "$REMAINING" -eq 0 ]; then
    echo "✅ All services stopped successfully"
else
    echo "⚠️  Some processes may still be running:"
    ps aux | grep -E "(AuthService|PhotoService|UserService|MatchmakingService|MessagingService|SwipeService|dejting-yarp)" | grep -v grep
    echo ""
    echo "🔧 Force killing remaining processes..."
    pkill -f "dotnet" 2>/dev/null || true
fi

# Clear port bindings
echo "🔓 Releasing ports 8080, 8081, 8082, 8083, 8085, 8086, 8087..."

# Show final status
echo ""
echo "📊 Port Status:"
PORTS=(8080 8081 8082 8083 8085 8086 8087)
for port in "${PORTS[@]}"; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo "⚠️  Port $port still in use"
    else
        echo "✅ Port $port available"
    fi
done

echo ""
echo "🎯 Local development environment stopped!"
echo "🚀 To restart: ./dev-start.sh"
