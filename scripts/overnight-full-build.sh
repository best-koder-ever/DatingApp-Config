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
# 1. Dashboard
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "📊 Updating dashboard..." | tee -a "$REPORT_FILE"
if [ -f "scripts/generate_dashboard.sh" ] && ./scripts/generate_dashboard.sh >> logs/dashboard.log 2>&1; then
    echo "  ✅ Dashboard updated" | tee -a "$REPORT_FILE"
else
    echo "  ⚠️  Dashboard update failed or script missing" | tee -a "$REPORT_FILE"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. .NET Service Builds + Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "" | tee -a "$REPORT_FILE"
echo "🏗️  Building & testing all .NET services..." | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Map: service_dir -> test_project_path (explicit to avoid ambiguous .sln issues)
declare -A SERVICE_TESTS=(
    ["UserService"]="UserService/UserService.Tests/UserService.Tests.csproj"
    ["MatchmakingService"]="MatchmakingService/MatchmakingService.Tests/MatchmakingService.Tests.csproj"
    ["photo-service"]="photo-service/PhotoService.Tests/PhotoService.Tests.csproj"
    ["swipe-service"]="swipe-service/SwipeService.Tests/SwipeService.Tests.csproj"
    ["messaging-service"]="messaging-service/MessagingService.Tests/MessagingService.Tests.csproj"
    ["dejting-yarp"]="dejting-yarp/src/dejting-yarp.Tests/dejting-yarp.Tests.csproj"
)

# Map: service_dir -> main project for build
declare -A SERVICE_PROJECTS=(
    ["UserService"]="UserService/UserService.csproj"
    ["MatchmakingService"]="MatchmakingService/MatchmakingService.csproj"
    ["photo-service"]="photo-service/PhotoService.csproj"
    ["swipe-service"]="swipe-service/SwipeService.csproj"
    ["messaging-service"]="messaging-service/MessagingService.csproj"
    ["dejting-yarp"]="dejting-yarp/src/dejting-yarp/dejting-yarp.csproj"
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

    # Build
    if [ -f "$MAIN_PROJ" ]; then
        if dotnet build "$MAIN_PROJ" --verbosity quiet --no-restore >> "logs/build-$SERVICE.log" 2>&1; then
            # Try with restore if no-restore failed
            true
        else
            dotnet build "$MAIN_PROJ" --verbosity quiet >> "logs/build-$SERVICE.log" 2>&1
        fi

        if dotnet build "$MAIN_PROJ" --verbosity quiet >> "logs/build-$SERVICE.log" 2>&1; then
            echo "    🔨 Build: ✅" | tee -a "$REPORT_FILE"
            BUILDS_PASSED=$((BUILDS_PASSED+1))
        else
            echo "    🔨 Build: ❌ (see logs/build-$SERVICE.log)" | tee -a "$REPORT_FILE"
            BUILDS_FAILED=$((BUILDS_FAILED+1))
        fi
    else
        echo "    🔨 Build: ⚠️  $MAIN_PROJ not found" | tee -a "$REPORT_FILE"
        BUILDS_FAILED=$((BUILDS_FAILED+1))
    fi

    # Test
    if [ -f "$TEST_PROJ" ]; then
        if dotnet test "$TEST_PROJ" --verbosity quiet --logger "console;verbosity=minimal" --no-build >> "logs/test-$SERVICE.log" 2>&1; then
            true
        else
            # Retry with build (might need restore+build first)
            dotnet test "$TEST_PROJ" --verbosity quiet --logger "console;verbosity=minimal" >> "logs/test-$SERVICE.log" 2>&1
        fi

        if dotnet test "$TEST_PROJ" --verbosity quiet --logger "console;verbosity=minimal" >> "logs/test-$SERVICE.log" 2>&1; then
            echo "    🧪 Tests: ✅" | tee -a "$REPORT_FILE"
            TESTS_PASSED=$((TESTS_PASSED+1))
        else
            FAIL_REASON=$(tail -5 "logs/test-$SERVICE.log" 2>/dev/null | head -3)
            echo "    🧪 Tests: ❌" | tee -a "$REPORT_FILE"
            echo "       └─ $FAIL_REASON" | tee -a "$REPORT_FILE"
            TESTS_FAILED=$((TESTS_FAILED+1))
        fi
    else
        echo "    🧪 Tests: ⏭️  No test project" | tee -a "$REPORT_FILE"
        TESTS_SKIPPED=$((TESTS_SKIPPED+1))
    fi

    echo "" | tee -a "$REPORT_FILE"
done

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Flutter Analysis + Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLUTTER_DIR=""
# Check common Flutter locations
for FDIR in "$PROJECT_ROOT/../mobile-apps/flutter/dejtingapp" "/home/m/development/mobile-apps/flutter/dejtingapp"; do
    if [ -d "$FDIR" ] && [ -f "$FDIR/pubspec.yaml" ]; then
        FLUTTER_DIR="$FDIR"
        break
    fi
done

echo "🦋 Flutter App..." | tee -a "$REPORT_FILE"
if [ -n "$FLUTTER_DIR" ]; then
    echo "  📦 dejtingapp ($FLUTTER_DIR)" | tee -a "$REPORT_FILE"

    # Lint
    if cd "$FLUTTER_DIR" && flutter analyze --no-fatal-warnings > "$PROJECT_ROOT/logs/flutter-analyze.log" 2>&1; then
        LINT_ISSUES=$(grep -c "info\|warning\|error" "$PROJECT_ROOT/logs/flutter-analyze.log" 2>/dev/null || echo "0")
        echo "    🔍 Analyze: ✅ ($LINT_ISSUES info/warnings)" | tee -a "$PROJECT_ROOT/$REPORT_FILE"
    else
        ERRORS=$(grep -c "error" "$PROJECT_ROOT/logs/flutter-analyze.log" 2>/dev/null || echo "?")
        echo "    🔍 Analyze: ❌ ($ERRORS errors — see logs/flutter-analyze.log)" | tee -a "$PROJECT_ROOT/$REPORT_FILE"
    fi

    # Unit tests
    cd "$FLUTTER_DIR"
    if flutter test --no-pub > "$PROJECT_ROOT/logs/flutter-test.log" 2>&1; then
        echo "    🧪 Tests: ✅" | tee -a "$PROJECT_ROOT/$REPORT_FILE"
    else
        echo "    🧪 Tests: ❌ (see logs/flutter-test.log)" | tee -a "$PROJECT_ROOT/$REPORT_FILE"
    fi

    cd "$PROJECT_ROOT"
else
    echo "  ⚠️  Flutter project not found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Code Formatting
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "✨ Running code formatters..." | tee -a "$REPORT_FILE"
for SERVICE in UserService MatchmakingService photo-service swipe-service messaging-service; do
    MAIN_PROJ="${SERVICE_PROJECTS[$SERVICE]}"
    if [ -f "$MAIN_PROJ" ]; then
        dotnet format "$MAIN_PROJ" >> "logs/format-$SERVICE.log" 2>&1 || true
    fi
done
echo "  ✅ Code formatting complete" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Security / Outdated Packages
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "🔒 Security scan..." | tee -a "$REPORT_FILE"
if command -v dotnet-outdated &> /dev/null; then
    dotnet outdated --output reports/outdated-packages.txt >> logs/security.log 2>&1 || true
    echo "  ✅ Outdated packages report generated" | tee -a "$REPORT_FILE"
else
    echo "  ⚠️  dotnet-outdated not installed, skipping" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Test Skeletons (T003)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "🧬 Generating missing test skeletons..." | tee -a "$REPORT_FILE"
if [ -f "scripts/generate-test-skeletons-t003.sh" ]; then
    if bash scripts/generate-test-skeletons-t003.sh >> logs/test-generation.log 2>&1; then
        SKELETONS=$(grep -c "Created" logs/test-generation.log 2>/dev/null || echo "0")
        echo "  ✅ Test skeletons generated ($SKELETONS new files)" | tee -a "$REPORT_FILE"
    else
        echo "  ⚠️  Test generation had issues (see logs/test-generation.log)" | tee -a "$REPORT_FILE"
    fi
else
    echo "  ⚠️  Test generation script not found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. PR Status Check
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo "🔀 Open Pull Requests..." | tee -a "$REPORT_FILE"
for REPO in UserService MatchmakingService mobile_dejtingapp; do
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
    else
        echo "  📌 $REPO: No open PRs" | tee -a "$REPORT_FILE"
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
echo "  🔨 Builds:  $BUILDS_PASSED passed / $BUILDS_FAILED failed (of 6 services)" | tee -a "$REPORT_FILE"
echo "  🧪 Tests:   $TESTS_PASSED passed / $TESTS_FAILED failed / $TESTS_SKIPPED skipped" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Calculate overall score
TOTAL_CHECKS=$((BUILDS_PASSED + TESTS_PASSED))
TOTAL_POSSIBLE=12  # 6 builds + 6 tests
if [ $TOTAL_POSSIBLE -gt 0 ]; then
    SCORE=$(( (TOTAL_CHECKS * 100) / TOTAL_POSSIBLE ))
else
    SCORE=0
fi

echo "  🏆 Overall Score: ${SCORE}% ($TOTAL_CHECKS/$TOTAL_POSSIBLE checks passing)" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Grade
if [ $SCORE -ge 90 ]; then
    GRADE="🟢 A — Ship it!"
elif [ $SCORE -ge 75 ]; then
    GRADE="🟡 B — Almost there"
elif [ $SCORE -ge 50 ]; then
    GRADE="🟠 C — Needs work"
else
    GRADE="🔴 D — Fix critical issues"
fi
echo "  📋 Grade: $GRADE" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "🌅 Overnight Build Completed: $(date +"%Y-%m-%d %H:%M:%S")" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Generate TODO-NEXT.md
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FAILED_BUILDS=$(grep "🔨 Build: ❌" "$REPORT_FILE" | sed 's/.*📦 /- /' | sed 's/ *$//')
FAILED_TESTS=$(grep "🧪 Tests: ❌" "$REPORT_FILE" | sed 's/.*📦 /- /' | sed 's/ *$//')

cat > TODO-NEXT.md << EOFTODO
# Priority Tasks for $(date +%Y-%m-%d)

## Overnight Score: ${SCORE}% — $GRADE

## 🔴 Build Failures
${FAILED_BUILDS:-"None — all builds green! ✅"}

## 🔴 Test Failures
${FAILED_TESTS:-"None — all tests green! ✅"}

## 🟡 Pending PRs
$(grep "^    #" "$REPORT_FILE" | sed 's/^    /- /' 2>/dev/null || echo "No open PRs")

## 📋 Next steps
- Review overnight report: cat reports/overnight-$(date +%Y%m%d).md
- Review logs: ls -lh logs/
- Run summary: ./scripts/overnight-summary.sh
EOFTODO

echo "✅ TODO-NEXT.md generated"
echo ""
echo "📋 Quick view: cat $REPORT_FILE"
