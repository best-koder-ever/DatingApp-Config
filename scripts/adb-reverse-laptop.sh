#!/usr/bin/env bash
# adb-reverse-laptop.sh — point a USB-connected phone at the dev laptop's backend.
#
# The Flutter app's "Laptop (USB)" option uses http://localhost on the phone.
# adb reverse forwards those ports over the USB cable to this laptop, so the
# phone reaches the laptop's backend without needing the same WiFi or any IP.
#
# Usage:
#   ./scripts/adb-reverse-laptop.sh            # single device
#   ./scripts/adb-reverse-laptop.sh <serial>   # specific device
#
# Reverse-list (view active): adb reverse --list
# Clear all reverses:        adb reverse --remove-all

set -euo pipefail

SERIAL="${1:-}"

# Ports the app talks to when "Laptop (USB)" is selected (see environment.dart).
PORTS=(
  8080  # YARP gateway
  8082  # UserService
  8083  # MatchmakingService
  8085  # PhotoService
  8086  # MessagingService
  8087  # SwipeService
  8090  # Keycloak
)

DEVICE_ARGS=()
if [[ -n "$SERIAL" ]]; then
  DEVICE_ARGS=(-s "$SERIAL")
fi

echo "🔌 Setting up adb reverse → laptop backend (${SERIAL:-default device})"

if ! adb "${DEVICE_ARGS[@]}" get-state >/dev/null 2>&1; then
  echo "❌ No device connected. Plug in your phone (USB debugging on) and retry."
  exit 1
fi

for port in "${PORTS[@]}"; do
  if adb "${DEVICE_ARGS[@]}" reverse "tcp:$port" "tcp:$port" 2>/dev/null; then
    echo "  ✅ tcp:$port → tcp:$port"
  else
    echo "  ⚠️  Failed to reverse tcp:$port"
  fi
done

echo ""
echo "✅ Done. In the app, select: Laptop (dev)"
echo "   Active reverses:"
adb "${DEVICE_ARGS[@]}" reverse --list
