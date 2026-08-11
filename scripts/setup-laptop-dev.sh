#!/usr/bin/env bash
# Setup local development environment on a laptop.
# Only runs Keycloak + shared DBs (via infrastructure/start.sh) and a few services.
# Does NOT run all 8 services — use .devcontainer or remote for full stack.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 Setting up local dev environment..."
echo ""

# 1. Install prerequisites if missing
command -v dotnet >/dev/null 2>&1 || {
    echo "Installing .NET SDK 8.0..."
    wget -q https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O /tmp/ms-prod.deb
    sudo dpkg -i /tmp/ms-prod.deb
    sudo apt update && sudo apt install -y dotnet-sdk-8.0
}

command -v flutter >/dev/null 2>&1 || {
    echo "⚠ Flutter not found. Install manually: https://flutter.dev/docs/get-started/install/linux"
}

command -v docker >/dev/null 2>&1 || {
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    echo "⚠ Log out and back in for Docker group to take effect."
}

# 2. Start shared infrastructure (Keycloak + MySQL)
echo "Starting shared infrastructure..."
bash infrastructure/start.sh 2>/dev/null || {
    echo "⚠ infrastructure/start.sh not found. Using docker compose for Keycloak only."
    docker compose -f docker-compose.yml up -d keycloak keycloak-db 2>/dev/null || true
}

# 3. Verify Keycloak is ready
echo "⏳ Waiting for Keycloak..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8090/health/ready >/dev/null 2>&1; then
        echo "✓ Keycloak ready (:8090)"
        break
    fi
    sleep 2
done

# 4. Set up Flutter (if present)
if [ -d "mobile-apps/flutter/dejtingapp" ]; then
    echo ""
    echo "📱 Setting up Flutter..."
    cd mobile-apps/flutter/dejtingapp
    flutter pub get 2>/dev/null || echo "⚠ Flutter not available, skipping pub get"
    cd "$SCRIPT_DIR"
fi

echo ""
echo "✅ Local dev environment ready."
echo ""
echo "   Next steps:"
echo "   1. Start a service: cd <service-dir> && dotnet run"
echo "   2. Or run all: ./dev-start.sh"
echo "   3. Flutter: cd mobile-apps/flutter/dejtingapp && flutter run"
echo "   4. Tests: python3 api_tests.py"
