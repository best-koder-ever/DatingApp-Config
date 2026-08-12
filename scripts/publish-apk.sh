#!/bin/bash
# Publish a new release APK to GitHub Releases (best-koder-org/mobile_dejtingapp).
#
# Usage: ./scripts/publish-apk.sh <versionName> <versionCode>
#   e.g. ./scripts/publish-apk.sh 1.0.1 2
#
# - Builds a release APK with flutter build.
# - Attaches it to a GitHub release (asset name encodes version+code).
# - The app + backend auto-detect the LATEST release; older releases stay
#   available for rollback. Default download = releases/latest.
set -euo pipefail

FLUTTER_DIR="${FLUTTER_DIR:-/home/m/development/mobile-apps/flutter/dejtingapp}"
REPO="best-koder-org/mobile_dejtingapp"
VERSION_NAME="${1:?usage: publish-apk.sh <versionName> <versionCode>}"
VERSION_CODE="${2:?usage: publish-apk.sh <versionName> <versionCode>}"
TAG="v${VERSION_NAME}"

echo "🚀 Building release APK ${VERSION_NAME}+${VERSION_CODE}..."
cd "$FLUTTER_DIR"
flutter build apk --release --build-name "$VERSION_NAME" --build-number "$VERSION_CODE"

SRC_APK="build/app/outputs/flutter-apk/app-release.apk"
ASSET="dejtingapp-${VERSION_NAME}+${VERSION_CODE}.apk"
TMP_APK="${TMPDIR:-/tmp}/${ASSET}"
cp "$SRC_APK" "$TMP_APK"

echo "📦 Creating GitHub release $TAG with $ASSET..."
gh release create "$TAG" "$TMP_APK" \
  --repo "$REPO" \
  --title "$TAG" \
  --notes "Release ${VERSION_NAME} (build ${VERSION_CODE})."

echo ""
echo "✅ Published: https://github.com/$REPO/releases/latest"
echo "   Download:  https://github.com/$REPO/releases/latest/download/$ASSET"
echo "   (Older releases are kept; the app checks /api/app/version for the latest.)"
