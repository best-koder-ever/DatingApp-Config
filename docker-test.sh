#!/bin/bash

# Docker Validation Script
# Tests the existing Docker setup to ensure it works for periodic validation

echo "🐳 Testing Existing Docker Setup"
echo "================================="

# Stop any local services first
echo "🛑 Stopping local development services..."
./dev-stop.sh > /dev/null 2>&1

echo ""
echo "🧹 Cleaning up existing Docker containers..."
docker-compose down > /dev/null 2>&1

echo ""
echo "🔍 Validating docker-compose configuration..."
if docker-compose config --quiet; then
    echo "✅ docker-compose.yml is valid"
else
    echo "❌ docker-compose.yml has configuration errors"
    exit 1
fi

echo ""
echo "📊 Current Docker images:"
docker images | grep -E "(auth-service|photo-service|yarp)" | head -5

echo ""
echo "🚀 Testing Docker build (auth-service only)..."
echo "   This may take a few minutes..."

# Test building just AuthService
if docker-compose build auth-service; then
    echo "✅ AuthService Docker build successful"
else
    echo "❌ AuthService Docker build failed"
    exit 1
fi

echo ""
echo "🧪 Testing container startup (auth-service only)..."

# Start just AuthService with its database
if docker-compose up -d AuthService-db; then
    echo "✅ AuthService database started"
else
    echo "❌ AuthService database failed to start"
    exit 1
fi

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 10

if docker-compose up -d auth-service; then
    echo "✅ AuthService container started"
else
    echo "❌ AuthService container failed to start"
    exit 1
fi

# Wait for service to start
echo "⏳ Waiting for AuthService to initialize..."
sleep 15

# Test health endpoint
echo "🏥 Testing AuthService health..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health 2>/dev/null || echo "000")

if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ AuthService is healthy (HTTP 200)"
else
    echo "❌ AuthService health check failed (HTTP $HEALTH_STATUS)"
fi

echo ""
echo "📋 Docker Container Status:"
docker-compose ps

echo ""
echo "📝 AuthService Logs (last 10 lines):"
docker-compose logs --tail=10 auth-service

echo ""
echo "🧹 Cleaning up test containers..."
docker-compose down

echo ""
if [ "$HEALTH_STATUS" = "200" ]; then
    echo "🎉 Docker Setup Validation: SUCCESS"
    echo "   ✅ Configuration valid"
    echo "   ✅ Images build successfully"
    echo "   ✅ Containers start and run"
    echo "   ✅ Services respond to health checks"
    echo ""
    echo "🔄 Full Docker environment is ready for periodic testing!"
else
    echo "❌ Docker Setup Validation: FAILED"
    echo "   Check logs above for issues"
    exit 1
fi
