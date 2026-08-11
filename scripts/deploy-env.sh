#!/usr/bin/env bash
# Deploy a DatingApp environment profile.
# Usage: ./scripts/deploy-env.sh <dev|test|prod> [image-tag]
set -euo pipefail

ENV="${1:-}"
TAG="${2:-latest}"

if [ -z "$ENV" ] || [[ ! "$ENV" =~ ^(dev|test|prod)$ ]]; then
  echo "Usage: $0 <dev|test|prod> [image-tag]"
  echo "  dev  — deploy to dev environment (ports 8080-8099)"
  echo "  test — deploy to test environment (ports 9080-9099)"
  echo "  prod — deploy to production (internal ports only)"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

export IMAGE_TAG="$TAG"

case "$ENV" in
  dev)
    echo "🚀 Deploying DEV environment (tag=$TAG)..."
    docker compose -f docker-compose.yml -f infra/docker-compose.prod.yml --env-file infra/.env.dev pull 2>/dev/null || true
    docker compose -f docker-compose.yml --env-file infra/.env.dev up -d --remove-orphans
    ;;
  test)
    echo "🚀 Deploying TEST environment (tag=$TAG)..."
    # Test uses staging overlay with different ports
    docker compose -f docker-compose.yml -f docker-compose.staging.yml --env-file infra/.env.test pull 2>/dev/null || true
    docker compose -f docker-compose.yml -f docker-compose.staging.yml --env-file infra/.env.test up -d --remove-orphans
    # Override ports: prefix all host ports with 9
    # This is handled by setting ASPNETCORE_HTTP_PORTS in .env.test
    ;;
  prod)
    echo "🚀 Deploying PRODUCTION (tag=$TAG)..."
    docker compose -f docker-compose.yml -f infra/docker-compose.prod.yml --env-file infra/.env.prod pull 2>/dev/null || true
    docker compose -f docker-compose.yml -f infra/docker-compose.prod.yml --env-file infra/.env.prod up -d --remove-orphans
    ;;
esac

echo ""
echo "⏳ Waiting for services to become healthy..."
sleep 5
bash "$SCRIPT_DIR/scripts/health-check.sh" "http://localhost" 10

echo ""
echo "✅ Deploy to $ENV complete (tag=$TAG)"
