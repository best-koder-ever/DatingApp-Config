#!/usr/bin/env bash
set -euo pipefail

# DatingApp Staging — start all services behind YARP + Tailscale Funnel
# Usage: ./staging-start.sh
#
# Prerequisites:
#   1. Install Tailscale: curl -fsSL https://tailscale.com/install.sh | sh
#   2. Enable Funnel:     sudo tailscale funnel 8080
#   3. Copy .env.staging and set TUNNEL_HOST to your Tailscale hostname
#   4. Import Keycloak realm (first run only — see below)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE=".env.staging"
COMPOSE_CMD="docker compose -f docker-compose.yml -f docker-compose.staging.yml --env-file $ENV_FILE"

# --- Pre-flight checks ---
if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ Missing $ENV_FILE — copy from .env.staging.example and set TUNNEL_HOST"
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"
if [[ "${TUNNEL_HOST:-}" == "CHANGE_ME.ts.net" || -z "${TUNNEL_HOST:-}" ]]; then
  echo "❌ Set TUNNEL_HOST in $ENV_FILE to your Tailscale hostname"
  echo "   Run: tailscale status | head -1"
  exit 1
fi

echo "🚀 Starting DatingApp staging → https://$TUNNEL_HOST"
echo "   Compose: docker-compose.yml + docker-compose.staging.yml"
echo "   Env:     $ENV_FILE"
echo ""

# --- Build & start ---
echo "📦 Building images..."
$COMPOSE_CMD build --parallel

echo "🔼 Starting services..."
$COMPOSE_CMD up -d

# --- Health checks ---
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

check_service() {
  local name="$1"
  local url="$2"
  if curl -sf "$url" > /dev/null 2>&1; then
    echo "  ✅ $name"
  else
    echo "  ⏳ $name (still starting...)"
  fi
}

check_service "Keycloak" "http://localhost:8090/auth/health"
check_service "YARP Gateway" "http://localhost:8080/health"

echo ""
echo "📊 Service status:"
$COMPOSE_CMD ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "═══════════════════════════════════════════════════"
echo "  DatingApp Staging is running!"
echo ""
echo "  🌐 Gateway:  https://$TUNNEL_HOST"
echo "  🔐 Keycloak: https://$TUNNEL_HOST/auth"
echo "  📱 Flutter:   flutter run --dart-define=ENVIRONMENT=staging \\"
echo "                  --dart-define=STAGING_HOST=$TUNNEL_HOST"
echo ""
echo "  First run? Import the Keycloak realm:"
echo "    Open https://$TUNNEL_HOST/auth/admin"
echo "    Login: admin / admin"
echo "    Import: config/keycloak/realms/datingapp-realm.json"
echo ""
echo "  Stop: ./staging-stop.sh"
echo "═══════════════════════════════════════════════════"
