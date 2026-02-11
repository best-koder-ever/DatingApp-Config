#!/usr/bin/env bash
# Synchronize feature contract documentation into service-specific reference folders.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FEATURE_DIR="${1:-specs/001-mvp-foundation/contracts}"
FEATURE_PATH="${ROOT_DIR}/${FEATURE_DIR}"

if [[ ! -d "${FEATURE_PATH}" ]]; then
  echo "❌ Contracts directory not found: ${FEATURE_PATH}" >&2
  exit 1
fi

SERVICES=(
  "AuthService"
  "UserService"
  "MatchmakingService"
  "messaging-service"
  "swipe-service"
  "photo-service"
  "dejting-yarp"
  "mobile-apps/flutter/dejtingapp"
)

echo "📄 Syncing contracts from ${FEATURE_DIR}";
for service in "${SERVICES[@]}"; do
  TARGET="${ROOT_DIR}/${service}/Contracts"
  mkdir -p "${TARGET}"
  rsync -a --delete "${FEATURE_PATH}/" "${TARGET}/"
  echo "   → ${service}/Contracts"

done

echo "✅ Contracts synchronized"
