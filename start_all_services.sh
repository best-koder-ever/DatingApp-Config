#!/bin/bash

# Start all backend services for testing
echo "🚀 Starting all Dating App backend services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to start a service
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    local project_file=$4
    
    echo -e "${YELLOW}Starting $service_name on port $port...${NC}"
    
    cd "$service_path"
    
    # Kill any existing process on the port
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    
    # Start the service in background
    if [ -n "$project_file" ]; then
        nohup dotnet run --project "$project_file" --urls "http://localhost:$port" > "$service_name.log" 2>&1 &
    else
        nohup dotnet run --urls "http://localhost:$port" > "$service_name.log" 2>&1 &
    fi
    
    local pid=$!
    echo "$pid" > "$service_name.pid"
    
    echo -e "${GREEN}$service_name started with PID $pid${NC}"
    
    # Wait a moment for service to start
    sleep 3
    
    # Check if service is responding
    if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name is responding on port $port${NC}"
    else
        echo -e "${YELLOW}⚠️  $service_name may still be starting on port $port${NC}"
    fi
}

# Stop function
stop_all_services() {
    echo -e "${YELLOW}Stopping all services...${NC}"
    
    # Kill processes by PID files
    for service in "AuthService" "UserService" "SwipeService" "MatchmakingService"; do
        if [ -f "${service}.pid" ]; then
            pid=$(cat "${service}.pid")
            kill $pid 2>/dev/null || true
            rm "${service}.pid"
            echo -e "${GREEN}Stopped $service (PID: $pid)${NC}"
        fi
    done
    
    # Kill by port as backup
    for port in 5001 5002 5003 5004; do
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    done
    
    echo -e "${GREEN}All services stopped${NC}"
}

# Handle Ctrl+C
trap stop_all_services EXIT

# Check if MySQL is running (required for some services)
if ! pgrep -x "mysqld" > /dev/null; then
    echo -e "${YELLOW}⚠️  MySQL is not running. Some services may fail to connect to database.${NC}"
    echo -e "${YELLOW}   Consider starting MySQL: sudo systemctl start mysql${NC}"
fi

# Start services
echo "Starting services in dependency order..."

# AuthService (port 5001)
start_service "AuthService" "/home/m/development/DatingApp/auth-service" 5001 "AuthService.csproj"

# UserService (port 5002)  
start_service "UserService" "/home/m/development/DatingApp/user-service/src/UserService" 5002

# SwipeService (port 5003)
start_service "SwipeService" "/home/m/development/DatingApp/swipe-service/src/SwipeService" 5003

# MatchmakingService (port 5004)
start_service "MatchmakingService" "/home/m/development/DatingApp/matchmaking-service" 5004 "MatchmakingService.csproj"

echo ""
echo -e "${GREEN}🎉 All services started!${NC}"
echo ""
echo "Service URLs:"
echo "  AuthService:       http://localhost:5001"
echo "  UserService:       http://localhost:5002" 
echo "  SwipeService:      http://localhost:5003"
echo "  MatchmakingService: http://localhost:5004"
echo ""
echo "Log files:"
echo "  AuthService.log"
echo "  UserService.log"
echo "  SwipeService.log" 
echo "  MatchmakingService.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep script running
wait
