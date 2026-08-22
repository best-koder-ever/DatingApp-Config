#!/bin/bash
# Build + distribute a release APK to Firebase App Distribution testers.
#
# Usage: ./scripts/distribute-firebase.sh [versionName] [versionCode] [releaseNotes]
#   e.g. ./scripts/distribute-firebase.sh 1.0.1 45 "Fixed login crash"
#
# Requires (one-time):
#   1. npm install -g firebase-tools
#   2. firebase login            (browser auth, once per machine)
#   3. Add tester emails, e.g.:
#        firebase appdistribution:testers:add tester@email.com --app "$FIREBASE_APP_ID"
#      (or add them in the Firebase console → App Distribution → Testers)
#
# Config via env: FIREBASE_APP_ID (default set below), TESTERS_GROUP (default "testers")
set -euo pipefail

FLUTTER_DIR="${FLUTTER_DIR:-/home/m/development/mobile-apps/flutter/dejtingapp}"
FIREBASE_APP_ID="${FIREBASE_APP_ID:-1:281392688916:android:e6f7e76da4018d1770dc01}"
# Send to explicit tester emails (comma-separated) OR a group alias.
TESTERS_EMAILS="${TESTERS_EMAILS:-}"
TESTERS_GROUP="${TESTERS_GROUP:-testers}"

VERSION_NAME="${1:-}"
VERSION_CODE="${2:-}"
RELEASE_NOTES="${3:-Build ${VERSION_NAME:-current} ($(date +%Y-%m-%d))}"

if ! command -v firebase >/dev/null 2>&1; then
    echo "❌ firebase CLI not found. Install: npm install -g firebase-tools"
    exit 1
fi

# Build the release APK (use explicit version args only if provided).
# Tester builds include the in-app feedback FAB via the dart-define flag;
# a plain production release is built without it (FAB stays hidden).
FLUTTER_ARGS=("--release" "--dart-define=DEJTING_FEEDBACK_VISIBLE=true")
if [ -n "$VERSION_NAME" ]; then
    FLUTTER_ARGS+=("--build-name" "$VERSION_NAME")
    [ -n "$VERSION_CODE" ] && FLUTTER_ARGS+=("--build-number" "$VERSION_CODE")
fi

echo "🚀 Building release APK ${VERSION_NAME:-<pubspec version>}..."
cd "$FLUTTER_DIR"
flutter build apk "${FLUTTER_ARGS[@]}"
APK="build/app/outputs/flutter-apk/app-release.apk"
[ -f "$APK" ] || { echo "❌ APK not found at $APK"; exit 1; }
echo "✅ APK built: $APK"

DIST_ARGS=(--app "$FIREBASE_APP_ID" --release-notes "$RELEASE_NOTES")
if [ -n "$TESTERS_EMAILS" ]; then
    echo "📤 Distributing to Firebase App Distribution (testers: $TESTERS_EMAILS)..."
    DIST_ARGS+=(--testers "$TESTERS_EMAILS")
else
    echo "📤 Distributing to Firebase App Distribution (group: $TESTERS_GROUP)..."
    DIST_ARGS+=(--groups "$TESTERS_GROUP")
fi
firebase appdistribution:distribute "$APK" "${DIST_ARGS[@]}"

echo ""
echo "✅ Distributed. Testers will get the install/update link from Firebase."
