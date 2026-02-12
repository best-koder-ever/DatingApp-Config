#!/bin/bash
# Overnight comprehensive build, test, and analysis
# Run: nohup ./scripts/overnight-full-build.sh > logs/overnight-$(date +%Y%m%d).log 2>&1 &

set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
REPORT_FILE="reports/overnight-$(date +%Y%m%d).md"

mkdir -p logs reports

# Clear old report for today
> "$REPORT_FILE"

echo "🌙 Overnight Build Started: $TIMESTAMP" | tee -a "$REPORT_FILE"
echo "=================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. .NET Service Builds + Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "🏗️  Building & testing all .NET services..." | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# FIXED: Explicit .csproj paths to avoid MSB1011 ambiguity with multiple .sln files
declare -A SERVICE_PROJECTS=(
    ["UserService"]="UserService/UserService.csproj"
    ["MatchmakingService"]="MatchmakingService/MatchmakingService.csproj"
    ["photo-service"]="photo-service/PhotoService.csproj"
    ["swipe-service"]="swipe-service/SwipeService.csproj"
    ["messaging-service"]="messaging-service/MessagingService.csproj"
    ["dejting-yarp"]="dejting-yarp/src/dejting-yarp/dejting-yarp.csproj"
)

declare -A SERVICE_TESTS=(
    ["UserService"]="UserService/UserService.Tests/UserService.Tests.csproj"
    ["MatchmakingService"]="MatchmakingService/MatchmakingService.Tests/MatchmakingService.Tests.csproj"
    ["photo-service"]="photo-service/PhotoService.Tests/PhotoService.Tests.csproj"
    ["swipe-service"]="swipe-service/SwipeService.Tests/SwipeService.Tests.csproj"
    ["messaging-service"]="messaging-service/MessagingService.Tests/MessagingService.Tests.csproj"
    ["dejting-yarp"]="dejting-yarp/src/dejting-yarp.Tests/dejting-yarp.Tests.csproj"
)

BUILDS_PASSED=0
BUILDS_FAILED=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

for SERVICE in UserService MatchmakingService photo-service swipe-service messaging-service dejting-yarp; do
    MAIN_PROJ="${SERVICE_PROJECTS[$SERVICE]}"
    TEST_PROJ="${SERVICE_TESTS[$SERVICE]}"

    echo "  📦 $SERVICE" | tee -a "$REPORT_FILE"

    # Build — always use explicit .csproj, restore first time
    > "logs/${SERVICE}-build.log"
    if [ -f "$MAIN_PROJ" ]; then
        if dotnet build "$MAIN_PROJ" --verbosity quiet 2>&1 | tee -a "logs/${SERVICE}-build.log" | tail -1 > /dev/null; then
            BUILD_EXIT=${PIPESTATUS[0]}
        fi
        if [ "${BUILD_EXIT:-1}" -eq 0 ]; then
            echo "    🔨 Build: ✅" | tee -a "$REPORT_FILE"
            BUILDS_PASSED=$((BUILDS_PASSED+1))
        else
            echo "    🔨 Build: ❌ (see logs/${SERVICE}-build.log)" | tee -a "$REPORT_FILE"
            BUILDS_FAILED=$((BUILDS_FAILED+1))
        fi
    else
        echo "    🔨 Build: ⚠️  $MAIN_PROJ not found" | tee -a "$REPORT_FILE"
        BUILDS_FAILED=$((BUILDS_FAILED+1))
    fi

    # Test
    > "logs/${SERVICE}-test.log"
    if [ -f "$TEST_PROJ" ]; then
        if dotnet test "$TEST_PROJ" --verbosity quiet --logger "console;verbosity=minimal" 2>&1 | tee -a "logs/${SERVICE}-test.log" | tail -1 > /dev/null; then
            TEST_EXIT=${PIPESTATUS[0]}
        fi
        if [ "${TEST_EXIT:-1}" -eq 0 ]; then
            echo "    🧪 Tests: ✅" | tee -a "$REPORT_FILE"
            TESTS_PASSED=$((TESTS_PASSED+1))
        else
            echo "    🧪 Tests: ❌ (see logs/${SERVICE}-test.log)" | tee -a "$REPORT_FILE"
            TESTS_FAILED=$((TESTS_FAILED+1))
        fi
    else
        echo "    🧪 Tests: ⏭️  No test project" | tee -a "$REPORT_FILE"
        TESTS_SKIPPED=$((TESTS_SKIPPED+1))
    fi

    echo "" | tee -a "$REPORT_FILE"
done

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Flutter Analysis + Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLUTTER_DIR=""
for FDIR in "$PROJECT_ROOT/../mobile-apps/flutter/dejtingapp" "/home/m/development/mobile-apps/flutter/dejtingapp"; do
    if [ -d "$FDIR" ] && [ -f "$FDIR/pubspec.yaml" ]; then
        FLUTTER_DIR="$(cd "$FDIR" && pwd)"
        break
    fi
done

echo "🦋 Flutter App..." | tee -a "$REPORT_FILE"
if [ -n "$FLUTTER_DIR" ]; then
    echo "  📦 dejtingapp ($FLUTTER_DIR)" | tee -a "$REPORT_FILE"

    # Analyze
    cd "$FLUTTER_DIR"
    if flutter analyze --no-fatal-infos 2>&1 | tee "$PROJECT_ROOT/logs/flutter-analyze.log" | tail -1 > /dev/null; then
        ANALYZE_EXIT=${PIPESTATUS[0]}
    fi
    ERRORS=$(grep -c " error " "$PROJECT_ROOT/logs/flutter-analyze.log" 2>/dev/null || echo "0")
    if [ "${ANALYZE_EXIT:-1}" -eq 0 ]; then
        echo "    🔍 Analyze: ✅ ($ERRORS errors)" | tee -a "$PROJECT_ROOT/$REPORT_FILE"
    else
        echo "    🔍 Analyze: ❌ ($ERRORS errors — see logs/flutter-analyze.log)" | tee -a "$PROJECT_ROOT/$REPORT_FILE"
    fi

    # Tests
    cd "$FLUTTER_DIR"
    if flutter test --no-pub 2>&1 | tee "$PROJECT_ROOT/logs/flutter-test.log" | tail -1 > /dev/null; then
        FLUTTER_TEST_EXIT=${PIPESTATUS[0]}
    fi
    if [ "${FLUTTER_TEST_EXIT:-1}" -eq 0 ]; then
        echo "    🧪 Tests: ✅" | tee -a "$PROJECT_ROOT/$REPORT_FILE"
    else
        FAIL_COUNT=$(grep -c "EXCEPTION CAUGHT\|Some tests failed" "$PROJECT_ROOT/logs/flutter-test.log" 2>/dev/null || echo "?")
        echo "    🧪 Tests: ⚠️  (see logs/flutter-test.log)" | tee -a "$PROJECT_ROOT/$REPORT_FILE"
    fi

    cd "$PROJECT_ROOT"
else
    echo "  ⚠️  Flutter project not found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. PR Status Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "🔀 Open Pull Requests..." | tee -a "$REPORT_FILE"
for REPO in UserService MatchmakingService mobile_dejtingapp photo-service swipe-service messaging-service dejting-yarp; do
    PR_INFO=$(gh pr list --repo "best-koder-org/$REPO" --state open --json number,title,statusCheckRollup --limit 5 2>/dev/null || echo "[]")
    PR_COUNT=$(echo "$PR_INFO" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    if [ "$PR_COUNT" -gt 0 ]; then
        echo "  📌 $REPO: $PR_COUNT open PR(s)" | tee -a "$REPORT_FILE"
        echo "$PR_INFO" | python3 -c "
import sys, json
prs = json.load(sys.stdin)
for pr in prs:
    checks = pr.get('statusCheckRollup', [])
    passed = sum(1 for c in checks if c.get('conclusion','') == 'SUCCESS')
    total = len(checks)
    status = '✅' if passed == total and total > 0 else '⚠️' if total > 0 else '❓'
    print(f\"    #{pr['number']}: {pr['title']} — {status} {passed}/{total} checks\")
" 2>/dev/null | tee -a "$REPORT_FILE"
    fi
done
echo "" | tee -a "$REPORT_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "=================================" | tee -a "$REPORT_FILE"
echo "📈 EVAL SUMMARY" | tee -a "$REPORT_FILE"
echo "=================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

TOTAL_SERVICES=6
echo "  🔨 Builds:  $BUILDS_PASSED passed / $BUILDS_FAILED failed (of $TOTAL_SERVICES services)" | tee -a "$REPORT_FILE"
echo "  🧪 Tests:   $TESTS_PASSED passed / $TESTS_FAILED failed / $TESTS_SKIPPED skipped" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

TOTAL_CHECKS=$((BUILDS_PASSED + TESTS_PASSED))
TOTAL_POSSIBLE=$((TOTAL_SERVICES * 2 - TESTS_SKIPPED))
if [ $TOTAL_POSSIBLE -gt 0 ]; then
    SCORE=$(( (TOTAL_CHECKS * 100) / TOTAL_POSSIBLE ))
else
    SCORE=0
fi

echo "  🏆 Overall Score: ${SCORE}% ($TOTAL_CHECKS/$TOTAL_POSSIBLE checks passing)" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

if [ $SCORE -ge 90 ]; then
    GRADE="🟢 A — Ship it!"
elif [ $SCORE -ge 75 ]; then
    GRADE="🔵 B — Almost there"
elif [ $SCORE -ge 50 ]; then
    GRADE="🟡 C — Needs attention"
else
    GRADE="🔴 D — Fix critical issues"
fi
echo "  📋 Grade: $GRADE" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "🌅 Overnight Build Completed: $(date +"%Y-%m-%d %H:%M:%S")" | tee -a "$REPORT_FILE"
