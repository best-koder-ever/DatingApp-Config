#!/bin/bash

# Local Development Restart Script
# Quickly restart all services

echo "🔄 Restarting Local Development Environment..."

# Stop everything first
./dev-stop.sh

echo ""
echo "⏳ Waiting for clean shutdown..."
sleep 3

# Start everything again
./dev-start.sh
