#!/bin/bash
# Setup script: wait for emulator boot, install APK, grant permissions, launch app
set -e

ADB_HOST="${ADB_HOST:-localhost}"
ADB_PORT="${ADB_PORT:-5555}"
APK_PATH="${APK_PATH:-/app/apk/app-release.apk}"
SERIAL="${ADB_HOST}:${ADB_PORT}"
PACKAGE="com.dejting.app"

echo "🔌 Connecting to emulator at ${SERIAL}..."
for i in $(seq 1 30); do
    adb connect "$SERIAL" 2>/dev/null | grep -qi "connected" && break
    echo "  Retry $i/30..."
    sleep 5
done

echo "⏳ Waiting for emulator boot..."
for i in $(seq 1 60); do
    BOOT=$(adb -s "$SERIAL" shell getprop sys.boot_completed 2>/dev/null || true)
    [ "$BOOT" = "1" ] && break
    echo "  Boot check $i/60..."
    sleep 5
done

echo "📦 Installing APK..."
if [ -f "$APK_PATH" ]; then
    adb -s "$SERIAL" install -r -g "$APK_PATH"
    echo "✅ APK installed"
else
    echo "⚠️  APK not found at $APK_PATH — skipping install"
fi

echo "🔓 Granting permissions..."
for PERM in ACCESS_FINE_LOCATION ACCESS_COARSE_LOCATION CAMERA READ_EXTERNAL_STORAGE POST_NOTIFICATIONS; do
    adb -s "$SERIAL" shell pm grant "$PACKAGE" "android.permission.${PERM}" 2>/dev/null || true
done

echo "🚀 Launching app..."
adb -s "$SERIAL" shell am start -n "${PACKAGE}/.MainActivity"

echo "⏳ Waiting for app to render..."
sleep 5

echo "✅ Emulator setup complete"
