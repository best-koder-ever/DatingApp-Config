#!/bin/bash

# Local Development Logs Script
# Shows live logs from all services

echo "📝 Live Logs - Local Development Environment"
echo "Press Ctrl+C to stop"
echo "============================================"

# Create logs directory if it doesn't exist
mkdir -p logs

# Create log files if they don't exist
touch logs/auth-service.log
touch logs/user-service.log
touch logs/matchmaking-service.log
touch logs/photo-service.log
touch logs/messaging-service.log
touch logs/swipe-service.log
touch logs/yarp-gateway.log

# Follow logs from all services
tail -f logs/auth-service.log logs/user-service.log logs/matchmaking-service.log logs/photo-service.log logs/messaging-service.log logs/swipe-service.log logs/yarp-gateway.log
