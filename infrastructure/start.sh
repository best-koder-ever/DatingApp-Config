#!/bin/bash
# Start shared infrastructure containers for local development.

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

REQUIRED_SERVICES=(keycloak-db keycloak mailhog MatchmakingService-db swipe-service-db UserService-db photo-service-db)

pushd "${PROJECT_ROOT}" >/dev/null

echo "🚀 Starting shared infrastructure containers..."
${COMPOSE_CMD} up -d "${REQUIRED_SERVICES[@]}"

echo "\n📊 Container status:"
${COMPOSE_CMD} ps "${REQUIRED_SERVICES[@]}"

KEYCLOAK_CONTAINER=$(${COMPOSE_CMD} ps -q keycloak)

if [ -z "${KEYCLOAK_CONTAINER}" ]; then
    echo "❌ Unable to determine Keycloak container ID." >&2
    exit 1
fi

echo "\n⏳ Waiting for Keycloak to become responsive..."
for i in {1..30}; do
    if curl -sf http://localhost:8090/realms/master >/dev/null 2>&1; then
        KEYCLOAK_READY=1
        break
    fi
    sleep 2
done

if [[ ${KEYCLOAK_READY:-0} -ne 1 ]]; then
    echo "❌ Keycloak did not become ready in time. Check container logs." >&2
    exit 1
fi

REALM_FILE="${PROJECT_ROOT}/config/keycloak/realms/datingapp-realm.json"
TEMP_REALM_PATH="/tmp/datingapp-realm.json"

if [ ! -f "${REALM_FILE}" ]; then
    echo "❌ Realm export not found at ${REALM_FILE}." >&2
    exit 1
fi

docker cp "${REALM_FILE}" "${KEYCLOAK_CONTAINER}:${TEMP_REALM_PATH}" >/dev/null

IMPORT_CMD="/opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin >/dev/null 2>&1 && /opt/keycloak/bin/kcadm.sh get realms/DatingApp >/dev/null 2>&1"

if ! docker exec "${KEYCLOAK_CONTAINER}" bash -c "${IMPORT_CMD}"; then
    echo "🌍 Importing DatingApp realm into Keycloak..."
    docker exec "${KEYCLOAK_CONTAINER}" bash -c "/opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin >/dev/null && /opt/keycloak/bin/kcadm.sh create realms -f ${TEMP_REALM_PATH} >/dev/null"
    echo "✅ DatingApp realm imported."
else
    echo "✅ DatingApp realm already present."
fi

MYSQL_CONTAINER=$(${COMPOSE_CMD} ps -q MatchmakingService-db)
if [ -n "${MYSQL_CONTAINER}" ]; then
    echo "\n🗑️ Resetting MatchmakingService demo data..."
    docker exec "${MYSQL_CONTAINER}" sh -c "mysql -u matchmakingservice_user -pmatchmakingservice_user_password MatchmakingServiceDb -e \"SET FOREIGN_KEY_CHECKS=0; TRUNCATE TABLE MatchScores; TRUNCATE TABLE Matches; TRUNCATE TABLE Messages; TRUNCATE TABLE UserInteractions; SET FOREIGN_KEY_CHECKS=1;\"" >/dev/null && \
    echo "✅ MatchmakingService tables truncated."
else
    echo "⚠️ Could not determine MatchmakingService-db container ID; skipping data reset." >&2
fi

popd >/dev/null

echo "\n✅ Infrastructure ready. Keycloak available on http://localhost:8090, MySQL databases available (see docker-compose.yml for port mappings)."
