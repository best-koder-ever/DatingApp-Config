#!/usr/bin/env bash
# dev-web-start.sh — build the Flutter web bundle and serve it via nginx.
#
# Idempotent. Use this on the "little machine" (or any dev host) when
# you want a browser-accessible DatingApp demo:
#
#   $ ./dev-web-start.sh                 # default gateway (localhost:8080)
#   $ WEB_LAN_ORIGIN=http://1.2.3.4:9000 ./dev-web-start.sh
#
# The script:
#   1. Builds the Flutter web release (or skips it if the build is fresh).
#   2. Brings up the `web` (nginx) container via docker compose.
#   3. Starts the rest of the backend stack via ./dev-start.sh.
#   4. Prints the URL to open in a browser.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

WEB_DIR="$SCRIPT_DIR/mobile-apps/flutter/dejtingapp"
BUILD_DIR="$SCRIPT_DIR/build/web"

# ----- 1. Build Flutter web -----
if [ ! -d "$WEB_DIR" ] || [ ! -f "$WEB_DIR/pubspec.yaml" ]; then
  echo "❌ Flutter app not found at $WEB_DIR"
  echo "   Set WEB_DIR=/path/to/dejtingapp and re-run."
  exit 1
fi

if [ ! -d "$BUILD_DIR" ] || [ -z "$(ls -A "$BUILD_DIR" 2>/dev/null)" ]; then
  echo "🔨 Building Flutter web release..."
  (cd "$WEB_DIR" && flutter build web --release)
else
  echo "✅ Reusing existing build/web (delete to force rebuild)"
fi

# ----- 2. Start backend + web -----
echo "🚀 Starting docker compose stack..."
docker compose up -d --build web

# Boot the rest of the services (Keycloak, MySQL, dotnet services)
# — the existing script handles this idempotently.
if [ -x "$SCRIPT_DIR/dev-start.sh" ]; then
  "$SCRIPT_DIR/dev-start.sh" || echo "⚠️  dev-start.sh exited non-zero (continuing)"
else
  echo "⚠️  dev-start.sh not found; run it manually for the backend services."
fi

# ----- 3. Print URL -----
LAN_IP="$(hostname -I 2>/dev/null | awk '{print $1}' || true)"
echo ""
echo "=================================================="
echo "  Flutter web dev build is live."
echo ""
if [ -n "$LAN_IP" ]; then
  echo "  Open on this machine:  http://localhost:9000"
  echo "  Open from your phone:  http://$LAN_IP:9000"
  echo "  Dev dashboard:         http://localhost:9100"
else
  echo "  Open:                  http://localhost:9000"
fi
echo "=================================================="
echo "  Useful commands:"
echo "    docker compose logs -f web"
echo "    docker compose restart web"
echo "    ./dev-stop.sh && docker compose down"
echo "=================================================="
