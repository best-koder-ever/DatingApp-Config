#!/bin/bash
# Recreate the dev Keycloak container with Tailscale Funnel hostname overrides.
# JWTs issued will have iss=https://fastdev.tail45c6a7.ts.net/auth/realms/DatingApp
# which is what tester-distributed APKs need.
#
# Run this AFTER ./infrastructure/start.sh whenever you want the tunnel-aware
# Keycloak config. To revert to plain dev mode, just run ./infrastructure/start.sh
# again (it will recreate via docker-compose with default env).
#
# Reads credentials from ../.env (KC_DB_USERNAME, KC_DB_PASSWORD,
# KEYCLOAK_ADMIN_USER, KEYCLOAK_ADMIN_PASSWORD).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NET=datingapp_app-network
NAME=datingapp-keycloak-1
TUNNEL_HOST=${TUNNEL_HOST:-fastdev.tail45c6a7.ts.net}

if [[ ! -f "$ROOT/.env" ]]; then
  echo "X Missing $ROOT/.env — required for Keycloak credentials." >&2
  exit 1
fi
# shellcheck disable=SC1091
set -a; source "$ROOT/.env"; set +a

if ! docker network inspect "$NET" >/dev/null 2>&1; then
  echo "X Docker network '$NET' not found. Run ./infrastructure/start.sh first." >&2
  exit 1
fi

if docker ps -a --format '{{.Names}}' | grep -q "^${NAME}$"; then
  echo "==> Removing existing keycloak container..."
  docker stop "$NAME" >/dev/null 2>&1 || true
  docker rm "$NAME" >/dev/null
fi

echo "==> Starting keycloak with tunnel hostname=https://${TUNNEL_HOST}/auth ..."
docker run -d \
  --name "$NAME" \
  --network "$NET" \
  --network-alias keycloak \
  -p 8090:8080 \
  --env-file "$ROOT/.env" \
  -e KC_DB=postgres \
  -e KC_DB_URL=jdbc:postgresql://keycloak-db:5432/keycloak \
  -e KC_HOSTNAME="https://${TUNNEL_HOST}/auth" \
  -e KC_HOSTNAME_STRICT=false \
  -e KC_HOSTNAME_STRICT_BACKCHANNEL=false \
  -e KC_PROXY_HEADERS=xforwarded \
  -e KC_HTTP_ENABLED=true \
  quay.io/keycloak/keycloak:25.0.0 \
  start-dev --features=token-exchange >/dev/null

echo "==> Waiting for keycloak to become ready..."
for i in $(seq 1 90); do
  if curl -sf http://localhost:8090/realms/master/.well-known/openid-configuration >/dev/null 2>&1; then
    echo "  ready after ${i}s"
    break
  fi
  sleep 1
done

ISS=$(curl -sS "https://${TUNNEL_HOST}/auth/realms/DatingApp/.well-known/openid-configuration" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('issuer','?'))" 2>/dev/null || echo '?')
echo "==> Tunnel issuer: $ISS"
if [ "$ISS" = "https://${TUNNEL_HOST}/auth/realms/DatingApp" ]; then
  echo "==> OK — Keycloak is tunnel-aware. APK build can now authenticate testers."
else
  echo "==> WARNING — Unexpected issuer; check 'docker logs ${NAME}'."
  exit 2
fi
