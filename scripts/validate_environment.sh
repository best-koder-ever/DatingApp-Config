#!/bin/bash

# 🔍 Environment Validation Script
# Validates that all services are properly configured and running

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Dating App Environment Validation${NC}"
echo "=================================="

# Function to check if port is available
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✅ Port $port is in use by $service${NC}"
        return 0
    else
        echo -e "${RED}❌ Port $port is not in use (expected for $service)${NC}"
        return 1
    fi
}

# Function to check service health
check_service_health() {
    local url=$1
    local service=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null || echo "000")
    
    if [ "$response" -eq 200 ]; then
        echo -e "${GREEN}✅ $service health check passed ($url)${NC}"
        return 0
    else
        echo -e "${RED}❌ $service health check failed ($url) - HTTP $response${NC}"
        return 1
    fi
}

# Function to check docker container status
check_container() {
    local container=$1
    local status=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep $container | awk '{print $2}' || echo "")
    
    if [[ "$status" == "Up" ]]; then
        echo -e "${GREEN}✅ Container $container is running${NC}"
        return 0
    else
        echo -e "${RED}❌ Container $container is not running${NC}"
        return 1
    fi
}

# Function to check appsettings files in container
check_appsettings() {
    local container=$1
    local environment=$2
    local file_count=$(docker exec $container ls /app/appsettings*.json 2>/dev/null | wc -l || echo "0")
    
    if [ "$file_count" -gt 1 ]; then
        echo -e "${GREEN}✅ $container has environment-specific appsettings${NC}"
        docker exec $container ls -la /app/appsettings*.json 2>/dev/null | sed 's/^/    /'
        return 0
    else
        echo -e "${YELLOW}⚠️  $container only has default appsettings.json${NC}"
        return 1
    fi
}

# Function to check port mapping consistency
check_port_mapping() {
    local container=$1
    local expected_internal=$2
    local expected_external=$3
    
    local mapping=$(docker port $container 2>/dev/null | grep "$expected_internal/tcp" || echo "")
    
    if [[ "$mapping" == *":$expected_external"* ]]; then
        echo -e "${GREEN}✅ $container port mapping correct: $expected_external→$expected_internal${NC}"
        return 0
    else
        echo -e "${RED}❌ $container port mapping incorrect. Expected: $expected_external→$expected_internal${NC}"
        echo "    Actual: $mapping"
        return 1
    fi
}

echo ""
echo -e "${BLUE}📋 Checking Docker Containers...${NC}"
echo "--------------------------------"

CONTAINERS=("dating-auth-demo" "dating-user-demo" "dating-matchmaking-demo" "dating-mysql-demo" "dating-yarp-demo")
CONTAINER_CHECKS=0
CONTAINER_FAILURES=0

for container in "${CONTAINERS[@]}"; do
    if check_container $container; then
        ((CONTAINER_CHECKS++))
    else
        ((CONTAINER_FAILURES++))
    fi
done

echo ""
echo -e "${BLUE}🔌 Checking Port Mappings...${NC}"
echo "----------------------------"

PORT_CHECKS=0
PORT_FAILURES=0

# Check port mappings (external→internal)
if check_port_mapping "dating-auth-demo" "80" "8081"; then ((PORT_CHECKS++)); else ((PORT_FAILURES++)); fi
if check_port_mapping "dating-user-demo" "80" "8082"; then ((PORT_CHECKS++)); else ((PORT_FAILURES++)); fi
if check_port_mapping "dating-matchmaking-demo" "80" "8083"; then ((PORT_CHECKS++)); else ((PORT_FAILURES++)); fi
if check_port_mapping "dating-mysql-demo" "3306" "3307"; then ((PORT_CHECKS++)); else ((PORT_FAILURES++)); fi
if check_port_mapping "dating-yarp-demo" "80" "8080"; then ((PORT_CHECKS++)); else ((PORT_FAILURES++)); fi

echo ""
echo -e "${BLUE}🏥 Checking Service Health...${NC}"
echo "-----------------------------"

HEALTH_CHECKS=0
HEALTH_FAILURES=0

# Check service health endpoints
if check_service_health "http://localhost:8081/health" "Auth Service"; then ((HEALTH_CHECKS++)); else ((HEALTH_FAILURES++)); fi
if check_service_health "http://localhost:8082/health" "User Service"; then ((HEALTH_CHECKS++)); else ((HEALTH_FAILURES++)); fi
if check_service_health "http://localhost:8083/health" "Matchmaking Service"; then ((HEALTH_CHECKS++)); else ((HEALTH_FAILURES++)); fi

echo ""
echo -e "${BLUE}⚙️  Checking Configuration Files...${NC}"
echo "----------------------------------"

CONFIG_CHECKS=0
CONFIG_WARNINGS=0

# Check appsettings files in containers
if check_appsettings "dating-auth-demo" "Demo"; then ((CONFIG_CHECKS++)); else ((CONFIG_WARNINGS++)); fi
if check_appsettings "dating-user-demo" "Demo"; then ((CONFIG_CHECKS++)); else ((CONFIG_WARNINGS++)); fi
if check_appsettings "dating-matchmaking-demo" "Demo"; then ((CONFIG_CHECKS++)); else ((CONFIG_WARNINGS++)); fi

echo ""
echo -e "${BLUE}🗄️  Checking Database Connectivity...${NC}"
echo "------------------------------------"

DB_CHECKS=0
DB_FAILURES=0

# Check database is accessible
if docker exec dating-mysql-demo mysql -u root -p"demo_root_password" -e "SHOW DATABASES;" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ MySQL database is accessible${NC}"
    ((DB_CHECKS++))
else
    echo -e "${RED}❌ MySQL database is not accessible${NC}"
    ((DB_FAILURES++))
fi

# Check each service database exists
for db in "auth_service_demo" "user_service_demo" "matchmaking_service_demo"; do
    if docker exec dating-mysql-demo mysql -u root -p"demo_root_password" -e "USE $db; SELECT 1;" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Database $db exists and is accessible${NC}"
        ((DB_CHECKS++))
    else
        echo -e "${RED}❌ Database $db is not accessible${NC}"
        ((DB_FAILURES++))
    fi
done

echo ""
echo -e "${BLUE}📊 Summary${NC}"
echo "==========="
echo -e "Containers: ${GREEN}$CONTAINER_CHECKS passed${NC}, ${RED}$CONTAINER_FAILURES failed${NC}"
echo -e "Port Mappings: ${GREEN}$PORT_CHECKS passed${NC}, ${RED}$PORT_FAILURES failed${NC}"
echo -e "Health Checks: ${GREEN}$HEALTH_CHECKS passed${NC}, ${RED}$HEALTH_FAILURES failed${NC}"
echo -e "Configuration: ${GREEN}$CONFIG_CHECKS passed${NC}, ${YELLOW}$CONFIG_WARNINGS warnings${NC}"
echo -e "Database: ${GREEN}$DB_CHECKS passed${NC}, ${RED}$DB_FAILURES failed${NC}"

TOTAL_FAILURES=$((CONTAINER_FAILURES + PORT_FAILURES + HEALTH_FAILURES + DB_FAILURES))

if [ $TOTAL_FAILURES -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All critical checks passed! Environment is healthy.${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ $TOTAL_FAILURES critical issues found. Please resolve before proceeding.${NC}"
    exit 1
fi
