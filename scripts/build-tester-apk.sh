#!/usr/bin/env bash
# build-tester-apk.sh — zero-cost tester APK build pointed at your laptop via Tailscale Funnel.
#
# Prereqs (one-time):
#   1. Tailscale Funnel already serving https://<TUNNEL_HOST>/ → http://127.0.0.1:8080
#        sudo tailscale funnel 8080
#   2. dev-start.sh running on this laptop.
#   3. Keycloak restarted with hostname override so issued credentials use the tunnel URL:
#        KC_HOSTNAME=<TUNNEL_HOST> KC_HOSTNAME_PATH=/auth KC_PROXY=edge KC_HOSTNAME_STRICT=false \
#          ./infrastructure/start.sh
#      (without this, PKCE credentials have issuer=http://localhost:8090 and the phone fails)
#
# What this script does:
#   - Reads TUNNEL_HOST from .env.staging
#   - Builds a release APK with the tunnel as base URL + feedback FAB enabled
#   - Prints the install command for adb / a URL for the tester

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FLUTTER_DIR="${FLUTTER_DIR:-/home/m/development/mobile-apps/flutter/dejtingapp}"

if [[ ! -f "$ROOT/.env.staging" ]]; then
  echo "❌ Missing $ROOT/.env.staging (set TUNNEL_HOST=fastdev.tail45c6a7.ts.net)"
  exit 1
fi
# shellcheck disable=SC1091
source "$ROOT/.env.staging"
if [[ -z "${TUNNEL_HOST:-}" || "$TUNNEL_HOST" == "CHANGE_ME.ts.net" ]]; then
  echo "❌ TUNNEL_HOST not configured in .env.staging"
  exit 1
fi

echo "🌐 Tunnel: https://$TUNNEL_HOST"

# Sanity: tunnel reachable + YARP responding through it?
if ! curl -fsS --max-time 5 "https://$TUNNEL_HOST/health" >/dev/null 2>&1; then
  echo "⚠️  https://$TUNNEL_HOST/health is not responding."
  echo "   Check: tailscale funnel status   &&   curl http://127.0.0.1:8080/health"
fi

cd "$FLUTTER_DIR"
echo "📦 flutter pub get…"
flutter pub get >/dev/null

echo "🔨 Building release APK against the tunnel…"
flutter build apk --release \
  --dart-define=ENVIRONMENT=staging \
  --dart-define=STAGING_HOST="$TUNNEL_HOST" \
  --dart-define=STAGING_SCHEME=https \
  --dart-define=DEJTING_FEEDBACK_VISIBLE=true

APK="$FLUTTER_DIR/build/app/outputs/flutter-apk/app-release.apk"
if [[ ! -f "$APK" ]]; then
  echo "❌ APK not produced at $APK"
  exit 1
fi

SIZE=$(du -h "$APK" | cut -f1)
echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ APK ready: $APK ($SIZE)"
echo ""
echo "  Install via USB:        adb install -r '$APK'"
echo "  Or copy to phone:       scp '$APK' phone:/sdcard/Download/"
echo ""
echo "  Tester opens APK → logs in via https://$TUNNEL_HOST/auth"
echo "  Feedback FAB visible (mic icon, draggable).  Voice memos POST to"
echo "  https://$TUNNEL_HOST/api/userfeedback → bot-service on this laptop."
echo "═══════════════════════════════════════════════════"
