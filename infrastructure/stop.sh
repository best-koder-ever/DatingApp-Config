#!/bin/bash
# Stop shared infrastructure containers for local development.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

COMPOSE_CMD="docker compose"
if ! ${COMPOSE_CMD} version >/dev/null 2>&1; then
    if command -v docker-compose >/dev/null 2>&1; then
        COMPOSE_CMD="docker-compose"
    else
        echo "❌ Docker Compose is required. Install Docker Desktop or docker-compose plugin." >&2
        exit 1
    fi
fi

SERVICES=(keycloak keycloak-db mailhog UserService-db MatchmakingService-db swipe-service-db photo-service-db messaging-service-db)

pushd "${PROJECT_ROOT}" >/dev/null

echo "🛑 Stopping infrastructure containers..."
${COMPOSE_CMD} stop "${SERVICES[@]}"

popd >/dev/null

echo "✅ Containers stopped. Use infrastructure/start.sh to bring them back online."
