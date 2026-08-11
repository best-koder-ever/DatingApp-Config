#!/usr/bin/env bash
set -euo pipefail

# DatingApp Staging — stop all services
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ENV_FILE=".env.staging"
COMPOSE_CMD="docker compose -f docker-compose.yml -f docker-compose.staging.yml --env-file $ENV_FILE"

echo "🛑 Stopping DatingApp staging..."
$COMPOSE_CMD down

echo "✅ All staging services stopped."
echo "   Data volumes preserved. To remove: $COMPOSE_CMD down -v"
