#!/bin/bash

echo "🔄 Restarting Dating App Demo Environment..."

# Kill all existing processes
echo "🛑 Stopping all services..."
pkill -f "dotnet" 2>/dev/null || true
pkill -f "flutter" 2>/dev/null || true
pkill -f "dejtingapp" 2>/dev/null || true

# Wait a moment for processes to stop
sleep 3

# Start AuthService
echo "🔐 Starting AuthService on port 8081..."
cd /home/m/development/DatingApp/AuthService
ASPNETCORE_ENVIRONMENT=Development DEMO_MODE=true ASPNETCORE_URLS=http://localhost:8081 dotnet run > /tmp/auth_service.log 2>&1 &

# Start PhotoService  
echo "📸 Starting PhotoService on port 8085..."
cd /home/m/development/DatingApp/photo-service
ASPNETCORE_ENVIRONMENT=Development DEMO_MODE=true ASPNETCORE_URLS=http://localhost:8085 dotnet run > /tmp/photo_service.log 2>&1 &

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 8

# Check services
echo "🔍 Checking service health..."
auth_status=$(curl -s http://localhost:8081/health | grep -o "Healthy" || echo "Not Ready")
photo_status=$(curl -s http://localhost:8085/health | grep -o "Healthy" || echo "Not Ready")

echo "AuthService: $auth_status"
echo "PhotoService: $photo_status"

if [[ "$auth_status" == "Healthy" && "$photo_status" == "Healthy" ]]; then
    echo "✅ All services ready!"
    echo "🚀 Starting Flutter app..."
    cd /home/m/development/mobile-apps/flutter/dejtingapp
    flutter run -d linux --hot > /tmp/flutter_app.log 2>&1 &
    echo "📱 Flutter app starting in background..."
    echo "🎯 Ready to test photo upload!"
else
    echo "❌ Some services failed to start. Check logs:"
    echo "  - AuthService: /tmp/auth_service.log"
    echo "  - PhotoService: /tmp/photo_service.log"
fi
