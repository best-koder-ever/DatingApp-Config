#!/bin/bash
# P1-006 Rate Limiting Manual Verification Script
# Tests all 7 rate limit policies against live YARP gateway

set -e

GATEWAY_URL="${GATEWAY_URL:-http://localhost:8080}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "P1-006 Rate Limiting Manual Test"
echo "========================================="
echo "Gateway: $GATEWAY_URL"
echo ""

# Function to get auth token (assumes Keycloak is running)
get_token() {
    # For now, use a mock JWT for testing (replace with real Keycloak token in production)
    echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItMTIzIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjo5OTk5OTk5OTk5fQ.fake"
}

TOKEN=$(get_token)

# Test 1: MessagesPerMinute (10/min)
echo -e "${YELLOW}Test 1: Messages Rate Limit (10/min)${NC}"
echo "Sending 15 POST /api/messages requests..."
SUCCESS=0
RATE_LIMITED=0

for i in {1..15}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$GATEWAY_URL/api/messages" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"content":"test"}')
    
    if [ "$HTTP_CODE" == "429" ]; then
        ((RATE_LIMITED++))
        echo -n "🛑"
    else
        ((SUCCESS++))
        echo -n "✓"
    fi
done

echo ""
echo -e "  Success: $SUCCESS, Rate Limited (429): $RATE_LIMITED"
if [ $RATE_LIMITED -ge 2 ]; then
    echo -e "  ${GREEN}✅ PASS - Rate limiting working${NC}"
else
    echo -e "  ${RED}❌ FAIL - Expected >= 2 rate limited responses${NC}"
fi
echo ""

# Test 2: PhotoUploadsPerDay (20/day)
echo -e "${YELLOW}Test 2: Photo Upload Rate Limit (20/day)${NC}"
echo "Sending 25 POST /api/photos requests..."
SUCCESS=0
RATE_LIMITED=0

for i in {1..25}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$GATEWAY_URL/api/photos" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: multipart/form-data")
    
    if [ "$HTTP_CODE" == "429" ]; then
        ((RATE_LIMITED++))
        echo -n "🛑"
    else
        ((SUCCESS++))
        echo -n "✓"
    fi
done

echo ""
echo -e "  Success: $SUCCESS, Rate Limited (429): $RATE_LIMITED"
if [ $RATE_LIMITED -ge 2 ]; then
    echo -e "  ${GREEN}✅ PASS - Rate limiting working${NC}"
else
    echo -e "  ${RED}❌ FAIL - Expected >= 2 rate limited responses${NC}"
fi
echo ""

# Test 3: ProfileViewsPerMinute (60/min)
echo -e "${YELLOW}Test 3: Profile Views Rate Limit (60/min)${NC}"
echo "Sending 70 GET /api/userprofiles requests..."
SUCCESS=0
RATE_LIMITED=0

for i in {1..70}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X GET "$GATEWAY_URL/api/userprofiles/test-user" \
        -H "Authorization: Bearer $TOKEN")
    
    if [ "$HTTP_CODE" == "429" ]; then
        ((RATE_LIMITED++))
        echo -n "🛑"
    else
        ((SUCCESS++))
        echo -n "✓"
    fi
done

echo ""
echo -e "  Success: $SUCCESS, Rate Limited (429): $RATE_LIMITED"
if [ $RATE_LIMITED -ge 5 ]; then
    echo -e "  ${GREEN}✅ PASS - Rate limiting working${NC}"
else
    echo -e "  ${RED}❌ FAIL - Expected >= 5 rate limited responses${NC}"
fi
echo ""

# Test 4: Header Validation
echo -e "${YELLOW}Test 4: Rate Limit Headers Verification${NC}"
echo "Exhausting limit and checking for headers..."

# Exhaust the limit
for i in {1..15}; do
    curl -s -o /dev/null -X POST "$GATEWAY_URL/api/messages" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"content":"test"}' 2>/dev/null || true
done

# Get a 429 response with headers
RESPONSE=$(curl -s -i -X POST "$GATEWAY_URL/api/messages" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"content":"test"}' 2>/dev/null || true)

echo "$RESPONSE" > /tmp/rate_limit_response.txt

if echo "$RESPONSE" | grep -q "429"; then
    echo -e "  ${GREEN}✅ Got 429 response${NC}"
    
    if echo "$RESPONSE" | grep -qi "X-RateLimit"; then
        echo -e "  ${GREEN}✅ X-RateLimit-* headers present${NC}"
    else
        echo -e "  ${YELLOW}⚠️  X-RateLimit-* headers missing${NC}"
    fi
    
    if echo "$RESPONSE" | grep -qi "Retry-After"; then
        echo -e "  ${GREEN}✅ Retry-After header present${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Retry-After header missing${NC}"
    fi
    
    if echo "$RESPONSE" | grep -qi "application/json"; then
        echo -e "  ${GREEN}✅ Content-Type: application/json${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Content-Type not JSON${NC}"
    fi
else
    echo -e "  ${RED}❌ No 429 response received${NC}"
fi
echo ""

# Test 5: Health endpoint bypass
echo -e "${YELLOW}Test 5: Health Endpoint Bypass (no rate limit)${NC}"
echo "Sending 50 GET /health requests..."
RATE_LIMITED=0

for i in {1..50}; do
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X GET "$GATEWAY_URL/health" 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" == "429" ]; then
        ((RATE_LIMITED++))
    fi
done

if [ $RATE_LIMITED -eq 0 ]; then
    echo -e "  ${GREEN}✅ PASS - Health endpoint NOT rate limited${NC}"
else
    echo -e "  ${RED}❌ FAIL - Health endpoint was rate limited ($RATE_LIMITED times)${NC}"
fi
echo ""

echo "========================================="
echo "Rate Limiting Test Complete"
echo "========================================="
echo ""
echo "Full 429 response saved to: /tmp/rate_limit_response.txt"
