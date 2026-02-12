#!/usr/bin/env bash
# Synchronize feature contract documentation into service-specific reference folders.
# Enhanced with completion detection (T005).
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

# ──────────────────────────────────────────────
# Phase 1: Sync contracts
# ──────────────────────────────────────────────
echo "📄 Syncing contracts from ${FEATURE_DIR}"
SYNCED=0
for service in "${SERVICES[@]}"; do
  TARGET="${ROOT_DIR}/${service}/Contracts"
  mkdir -p "${TARGET}"
  rsync -a --delete "${FEATURE_PATH}/" "${TARGET}/"
  echo "   → ${service}/Contracts"
  SYNCED=$((SYNCED + 1))
done
echo "✅ Contracts synchronized to ${SYNCED} services"

# ──────────────────────────────────────────────
# Phase 2: Completion detection
# ──────────────────────────────────────────────
echo ""
echo "🔍 Running completion checks..."

TOTAL_CHECKS=0
PASSED_CHECKS=0
WARNINGS=()

# Check 1: Each service has a Contracts directory with files
for service in "${SERVICES[@]}"; do
  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
  CONTRACT_DIR="${ROOT_DIR}/${service}/Contracts"
  FILE_COUNT=$(find "${CONTRACT_DIR}" -type f 2>/dev/null | wc -l)
  if [[ ${FILE_COUNT} -gt 0 ]]; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    echo "   ✅ ${service}: ${FILE_COUNT} contract files"
  else
    WARNINGS+=("${service}: No contract files found")
    echo "   ⚠️  ${service}: No contract files found"
  fi
done

# Check 2: .NET services have controllers referencing DTOs from contracts
for service in AuthService UserService MatchmakingService messaging-service swipe-service photo-service; do
  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
  CONTROLLER_DIR="${ROOT_DIR}/${service}/Controllers"
  if [[ -d "${CONTROLLER_DIR}" ]]; then
    CONTROLLER_COUNT=$(find "${CONTROLLER_DIR}" -name "*.cs" -type f 2>/dev/null | wc -l)
    if [[ ${CONTROLLER_COUNT} -gt 0 ]]; then
      PASSED_CHECKS=$((PASSED_CHECKS + 1))
      echo "   ✅ ${service}: ${CONTROLLER_COUNT} controllers found"
    else
      WARNINGS+=("${service}: Controllers directory exists but no .cs files")
      echo "   ⚠️  ${service}: Controllers directory exists but no .cs files"
    fi
  else
    WARNINGS+=("${service}: No Controllers directory")
    echo "   ⚠️  ${service}: No Controllers directory"
  fi
done

# Check 3: Flutter app has lib/services or lib/models referencing API contracts
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
FLUTTER_DIR="${ROOT_DIR}/../mobile-apps/flutter/dejtingapp"
if [[ -d "${FLUTTER_DIR}/lib/services" ]] || [[ -d "${FLUTTER_DIR}/lib/models" ]]; then
  SERVICE_FILES=$(find "${FLUTTER_DIR}/lib/services" "${FLUTTER_DIR}/lib/models" -name "*.dart" -type f 2>/dev/null | wc -l)
  PASSED_CHECKS=$((PASSED_CHECKS + 1))
  echo "   ✅ Flutter: ${SERVICE_FILES} service/model files found"
else
  WARNINGS+=("Flutter: No lib/services or lib/models directory")
  echo "   ⚠️  Flutter: No lib/services or lib/models directory"
fi

# Check 4: Test coverage exists for each .NET service
for service in AuthService UserService MatchmakingService messaging-service swipe-service photo-service; do
  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
  # Try common test directory patterns
  TEST_DIR=""
  for pattern in "${ROOT_DIR}/${service}/${service}.Tests" "${ROOT_DIR}/${service}/Tests" "${ROOT_DIR}/${service}/*.Tests"; do
    # shellcheck disable=SC2086
    if compgen -G "${pattern}" > /dev/null 2>&1; then
      TEST_DIR="${pattern}"
      break
    fi
  done

  if [[ -n "${TEST_DIR}" ]]; then
    TEST_COUNT=$(find ${TEST_DIR} -name "*Test*.cs" -type f 2>/dev/null | wc -l)
    if [[ ${TEST_COUNT} -gt 0 ]]; then
      PASSED_CHECKS=$((PASSED_CHECKS + 1))
      echo "   ✅ ${service}: ${TEST_COUNT} test files"
    else
      WARNINGS+=("${service}: Test directory exists but no test files")
      echo "   ⚠️  ${service}: Test directory exists but no test files"
    fi
  else
    WARNINGS+=("${service}: No test directory found")
    echo "   ℹ️  ${service}: No test directory found"
  fi
done

# Check 5: Flutter tests exist
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
FLUTTER_TEST_COUNT=$(find "${FLUTTER_DIR}/test" -name "*_test.dart" -type f 2>/dev/null | wc -l)
if [[ ${FLUTTER_TEST_COUNT} -gt 0 ]]; then
  PASSED_CHECKS=$((PASSED_CHECKS + 1))
  echo "   ✅ Flutter: ${FLUTTER_TEST_COUNT} test files"
else
  WARNINGS+=("Flutter: No test files found")
  echo "   ⚠️  Flutter: No test files found"
fi

# ──────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
COMPLETION_PCT=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
echo "📊 Completion: ${PASSED_CHECKS}/${TOTAL_CHECKS} checks passed (${COMPLETION_PCT}%)"

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo ""
  echo "⚠️  Warnings (${#WARNINGS[@]}):"
  for w in "${WARNINGS[@]}"; do
    echo "   - ${w}"
  done
fi

if [[ ${COMPLETION_PCT} -ge 80 ]]; then
  echo "🟢 Project health: Good"
elif [[ ${COMPLETION_PCT} -ge 50 ]]; then
  echo "🟡 Project health: Moderate"
else
  echo "🔴 Project health: Needs attention"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
