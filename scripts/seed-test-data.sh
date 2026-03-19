#!/bin/bash
# seed-test-data.sh - Atomic test data seeding script
# 
# Real product approach:
# - One command loads everything across all services
# - Idempotent (safe to re-run)
# - Validates services are healthy before seeding
# - Provides clear feedback on success/failure
#
# Usage:
#   ./scripts/seed-test-data.sh minimal       # Load minimal test set (5 users)
#   ./scripts/seed-test-data.sh standard      # Load standard test set (50 users)
#   ./scripts/seed-test-data.sh --validate    # Validate fixtures without loading

set -euo pipefail  # Exit on error, undefined vars, pipe failures

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FIXTURE_SET="${1:-minimal}"

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Validate fixture set
if [[ ! "$FIXTURE_SET" =~ ^(minimal|standard|load|demo|--validate)$ ]]; then
    log_error "Invalid fixture set: $FIXTURE_SET"
    echo "Usage: $0 {minimal|standard|load|demo|--validate}"
    exit 1
fi

# Check if services are running
log_info "Checking service health..."

check_service() {
    local name=$1
    local url=$2
    
    # Special case for Keycloak (returns 302 redirect, which is OK)
    if [[ "$name" == "Keycloak" ]]; then
        if curl -sf "$url" > /dev/null 2>&1 || \
           curl -s -o /dev/null -w "%{http_code}" "$url" | grep -qE "^(200|302|404)$"; then
            log_info "  ✓ $name is healthy"
            return 0
        else
            log_error "  ✗ $name is NOT responding at $url"
            return 1
        fi
    fi
    
    if curl -sf "$url/health" > /dev/null 2>&1 || \
       curl -sf "$url/api/health" > /dev/null 2>&1; then
        log_info "  ✓ $name is healthy"
        return 0
    else
        log_error "  ✗ $name is NOT responding at $url"
        return 1
    fi
}

# Check all required services
SERVICES_OK=true
check_service "Keycloak" "http://localhost:8090" || SERVICES_OK=false
check_service "UserService" "http://localhost:8082" || SERVICES_OK=false
check_service "SwipeService" "http://localhost:8087" || SERVICES_OK=false
check_service "MatchmakingService" "http://localhost:8083" || SERVICES_OK=false
check_service "MessagingService" "http://localhost:8086" || SERVICES_OK=false

if [ "$SERVICES_OK" = false ]; then
    log_error "Some services are not running!"
    log_warn "Start services with: ./dev-start.sh"
    exit 1
fi

log_info "All services healthy ✓"

# Activate Python venv if it exists
if [ -d "$PROJECT_DIR/.venv" ]; then
    log_info "Activating Python virtual environment..."
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.venv/bin/activate"
fi

# Check if fixture_loader.py has required dependencies
if ! python3 -c "import requests" 2>/dev/null; then
    log_warn "Missing Python dependency: requests"
    log_info "Installing: pip install requests"
    pip install requests
fi

# Run fixture loader
log_info "================================================================"
log_info "Loading fixtures: $FIXTURE_SET"
log_info "================================================================"

if [ "$FIXTURE_SET" = "--validate" ]; then
    python3 "$SCRIPT_DIR/fixture_loader.py" validate --set minimal
    exit $?
fi

# Load fixtures
if python3 "$SCRIPT_DIR/fixture_loader.py" load --set "$FIXTURE_SET" --env demo; then
    log_info "================================================================"
    log_info "✓ Test data loaded successfully!"
    log_info "================================================================"
    log_info ""
    log_info "Available test users (auth: impersonation, no password needed):"
    log_info "  alice@test.se    - 28F, Photographer, Stockholm"
    log_info "  bob@test.se      - 32M, Musician, Göteborg"
    log_info "  charlie@test.se  - 30M, Fitness Coach, Malmö"
    log_info "  diana@test.se    - 27F, Graphic Designer, Linköping"
    log_info "  erik@test.se     - 35M, Civil Engineer, Uppsala"
    log_info ""
    log_info "Pre-configured relationships:"
    log_info "  alice ↔ bob      - Matched (2 messages in history)"
    log_info "  bob ↔ charlie    - Matched"
    log_info "  alice → charlie  - Left swipe (no match)"
    log_info ""
    log_info "Next steps:"
    log_info "  1. Run integration tests: cd mobile-apps/flutter/dejtingapp && flutter test integration_test/"
    log_info "  2. Test API manually: curl -H 'Authorization: Bearer \$TOKEN' http://localhost:8001/api/..."
    log_info "  3. View in app: flutter run -d chrome"
    exit 0
else
    log_error "================================================================"
    log_error "✗ Fixture loading failed!"
    log_error "================================================================"
    log_error ""
    log_error "Troubleshooting:"
    log_error "  1. Check service logs: ls -lh logs/"
    log_error "  2. Verify Keycloak: http://localhost:8080 (admin/admin)"
    log_error "  3. Check database: docker ps | grep mysql"
    log_error "  4. Re-run with verbose: python3 scripts/fixture_loader.py load --set minimal"
    exit 1
fi
