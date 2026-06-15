#!/usr/bin/env bash
# Health-check all DatingApp services. Exits 0 if all healthy, 1 otherwise.
set -euo pipefail

BASE_URL="${1:-http://localhost}"
TIMEOUT="${2:-5}"
FAIL=0

check() {
  local port="$1" name="$2"
  local url="${BASE_URL}:${port}/health"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")
  if [ "$code" = "200" ]; then
    echo "  ✓ $name (:$port) — $code"
  else
    echo "  ✗ $name (:$port) — $code"
    FAIL=1
  fi
}

echo "=== DatingApp Health Check @ $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
check 8080 "YARP Gateway"
check 8082 "UserService"
check 8083 "MatchmakingService"
check 8085 "PhotoService"
check 8086 "MessagingService"
check 8087 "SwipeService"
check 8088 "SafetyService"
check 8090 "Keycloak"
check 8089 "BotService (optional)"

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "✅ All services healthy"
else
  echo "❌ Some services unhealthy"
fi
exit $FAIL
