#!/bin/bash

# Quick Start - Backend Only
# Use this when you want to start just the backend services

echo "🚀 Starting Dating App Backend Services..."

cd /home/m/development/DatingApp

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down > /dev/null 2>&1

# Start backend services
echo "Starting backend services..."
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 15

# Show status
echo "✅ Backend services started!"
echo ""
echo "Service URLs:"
echo "  YARP Gateway: http://localhost:8080"
echo "  Auth Service: http://localhost:8081"  
echo "  User Service: http://localhost:8082"
echo "  Matchmaking:  http://localhost:8083"
echo "  Swipe Service: http://localhost:8084"
echo "  Photo Service: http://localhost:5003"
echo ""
echo "To start Flutter app manually:"
echo "  cd /home/m/development/mobile-apps/flutter/dejtingapp"
echo "  flutter run"
echo ""
echo "To run all automated tests:"
echo "  cd /home/m/development/DatingApp/e2e-tests"
echo "  ./run_all_tests.sh"
echo ""
echo "To stop services: docker-compose down"
