#!/bin/bash
# Overnight comprehensive build, test, and analysis
# Run: nohup ./scripts/overnight-full-build.sh > logs/overnight-$(date +%Y%m%d).log 2>&1 &

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
REPORT_FILE="reports/overnight-$(date +%Y%m%d).md"

mkdir -p logs reports

echo "🌙 Overnight Build Started: $TIMESTAMP" | tee -a "$REPORT_FILE"
echo "=================================" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# 1. Update dashboard
echo "📊 Updating dashboard..." | tee -a "$REPORT_FILE"
if ./scripts/generate_dashboard.sh >> logs/dashboard.log 2>&1; then
    echo "✅ Dashboard updated" | tee -a "$REPORT_FILE"
else
    echo "❌ Dashboard update failed" | tee -a "$REPORT_FILE"
fi

# 2. Run all service tests
echo "" | tee -a "$REPORT_FILE"
echo "🧪 Running all service tests..." | tee -a "$REPORT_FILE"

SERVICES=(
    "UserService"
    "MatchmakingService"
    "photo-service"
    "swipe-service"
    "messaging-service"
    "dejting-yarp"
)

TESTS_PASSED=0
TESTS_FAILED=0

for SERVICE in "${SERVICES[@]}"; do
    echo "  Testing $SERVICE..." | tee -a "$REPORT_FILE"
    
    if [ -d "$SERVICE" ] && [ -f "$SERVICE"/*.csproj ]; then
        if dotnet test "$SERVICE" --verbosity quiet --logger "console;verbosity=minimal" >> logs/test-$SERVICE.log 2>&1; then
            echo "    ✅ $SERVICE tests passed" | tee -a "$REPORT_FILE"
            ((TESTS_PASSED++))
        else
            echo "    ❌ $SERVICE tests failed (see logs/test-$SERVICE.log)" | tee -a "$REPORT_FILE"
            ((TESTS_FAILED++))
        fi
    else
        echo "    ⚠️  $SERVICE not found or no .csproj" | tee -a "$REPORT_FILE"
    fi
done

# 3. Code formatting
echo "" | tee -a "$REPORT_FILE"
echo "✨ Running code formatters..." | tee -a "$REPORT_FILE"

for SERVICE in "${SERVICES[@]}"; do
    if [ -d "$SERVICE" ] && [ -f "$SERVICE"/*.csproj ]; then
        dotnet format "$SERVICE" >> logs/format-$SERVICE.log 2>&1 || true
    fi
done
echo "✅ Code formatting complete" | tee -a "$REPORT_FILE"

# 4. Security scan (if available)
echo "" | tee -a "$REPORT_FILE"
echo "🔒 Running security scan..." | tee -a "$REPORT_FILE"
if command -v dotnet-outdated &> /dev/null; then
    dotnet outdated --output reports/outdated-packages.txt >> logs/security.log 2>&1 || true
    echo "✅ Security scan complete" | tee -a "$REPORT_FILE"
else
    echo "⚠️  dotnet-outdated not installed, skipping" | tee -a "$REPORT_FILE"
fi

# 5. Generate test skeletons (T003)
echo "" | tee -a "$REPORT_FILE"
echo "🧬 Generating missing test skeletons..." | tee -a "$REPORT_FILE"
if [ -f "scripts/generate-test-skeletons-t003.sh" ]; then
    if ./scripts/generate-test-skeletons-t003.sh >> logs/test-generation.log 2>&1; then
        echo "✅ Test skeletons generated" | tee -a "$REPORT_FILE"
    else
        echo "❌ Test generation failed" | tee -a "$REPORT_FILE"
    fi
else
    echo "⚠️  Test generation script not yet created" | tee -a "$REPORT_FILE"
fi

# Summary
echo "" | tee -a "$REPORT_FILE"
echo "=================================" | tee -a "$REPORT_FILE"
echo "📈 Summary" | tee -a "$REPORT_FILE"
echo "  Services tested: $((TESTS_PASSED + TESTS_FAILED))" | tee -a "$REPORT_FILE"
echo "  ✅ Passed: $TESTS_PASSED" | tee -a "$REPORT_FILE"
echo "  ❌ Failed: $TESTS_FAILED" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"
echo "🌅 Overnight Build Completed: $(date +"%Y-%m-%d %H:%M:%S")" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"
echo "📋 Next steps: cat TODO-NEXT.md" | tee -a "$REPORT_FILE"

# Generate TODO-NEXT.md based on failures
cat > TODO-NEXT.md << EOFTODO
# Priority Tasks for $(date +%Y-%m-%d)

## 🔴 Failed Tests to Fix
$(grep "❌.*tests failed" "$REPORT_FILE" | sed 's/^/- /')

## 🟡 In Progress
- T023: Complete wizard implementation
- T025: Database migration for OnboardingStatus

## 🟢 Ready to Start
- T024: PhotoService moderation enhancement
- T026: Flutter wizard UI
- T027: Telemetry + audit logs

## 📊 Progress
- Tasks complete: 11/65 (17%)
- Current sprint: User Story 1 (Profile Onboarding)

Run \`./scripts/overnight-summary.sh\` for detailed results.
EOFTODO

echo "✅ TODO-NEXT.md generated"
