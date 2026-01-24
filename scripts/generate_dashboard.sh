#!/usr/bin/env bash
# Generate DASHBOARD.md from GitHub Projects + codebase metrics
#
# Usage: ./scripts/generate_dashboard.sh
# Output: specs/001-mvp-foundation/DASHBOARD.md

set -euo pipefail

OWNER="best-koder-ever"
PROJECT_NUMBER=2
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_FILE="$REPO_ROOT/specs/001-mvp-foundation/DASHBOARD.md"

echo "📊 Generating dashboard from GitHub Projects + codebase..."

# Fetch project data
echo "  Fetching project items..."
PROJECT_JSON=$(gh project view "$PROJECT_NUMBER" --owner "$OWNER" --format json)
ITEMS_JSON=$(gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 500 --format json)

# Calculate overall metrics
TOTAL_TASKS=$(echo "$ITEMS_JSON" | jq '[.items[] | select(.content.type=="Issue")] | length')
CLOSED_TASKS=$(echo "$ITEMS_JSON" | jq '[.items[] | select(.content.type=="Issue" and .content.state=="CLOSED")] | length')
OPEN_TASKS=$(echo "$ITEMS_JSON" | jq '[.items[] | select(.content.type=="Issue" and .content.state=="OPEN")] | length')

if [[ $TOTAL_TASKS -gt 0 ]]; then
  COMPLETION_PCT=$(echo "scale=1; ($CLOSED_TASKS * 100) / $TOTAL_TASKS" | bc)
else
  COMPLETION_PCT=0
fi

# Calculate phase breakdown
echo "  Analyzing phases..."
declare -A PHASE_TOTAL
declare -A PHASE_CLOSED

for phase in "Phase 0" "Phase 1" "Phase 2" "Phase 3" "Phase 4" "Phase 5" "Phase 6" "Phase 7"; do
  # Get field value for Phase
  total=$(echo "$ITEMS_JSON" | jq --arg phase "$phase" '[.items[] | select(.content.type=="Issue" and (.fieldValues.nodes[]? | select(.field.name=="Phase" and .name==$phase)))] | length')
  closed=$(echo "$ITEMS_JSON" | jq --arg phase "$phase" '[.items[] | select(.content.type=="Issue" and .content.state=="CLOSED" and (.fieldValues.nodes[]? | select(.field.name=="Phase" and .name==$phase)))] | length')
  
  PHASE_TOTAL["$phase"]=$total
  PHASE_CLOSED["$phase"]=$closed
done

# Calculate test coverage from codebase
echo "  Scanning test coverage..."
declare -A SERVICE_TESTS

for service_dir in UserService MatchmakingService swipe-service photo-service messaging-service; do
  service_path="$REPO_ROOT/$service_dir"
  test_path="$REPO_ROOT/$service_dir.Tests"
  
  if [[ -d "$service_path" ]]; then
    # Count controller actions (rough estimate of endpoints)
    controllers=$(find "$service_path" -name "*Controller.cs" 2>/dev/null | wc -l)
    
    # Count test files
    if [[ -d "$test_path" ]]; then
      tests=$(find "$test_path" -name "*.cs" -type f 2>/dev/null | wc -l)
    else
      tests=0
    fi
    
    SERVICE_TESTS["$service_dir"]="$controllers|$tests"
  fi
done

# Generate markdown
echo "  Generating DASHBOARD.md..."

cat > "$OUTPUT_FILE" << EOF
# MVP Foundation Dashboard

**Last Updated**: $(date -u +"%Y-%m-%d %H:%M UTC")  
**Project**: [001-mvp-foundation](https://github.com/users/$OWNER/projects/$PROJECT_NUMBER)  
**Auto-generated**: \`./scripts/generate_dashboard.sh\`

---

## 📊 Overall Progress

**${COMPLETION_PCT}% Complete** (${CLOSED_TASKS}/${TOTAL_TASKS} tasks)

\`\`\`
Progress: $(printf '█%.0s' $(seq 1 $((CLOSED_TASKS * 20 / TOTAL_TASKS))))$(printf '░%.0s' $(seq 1 $((20 - CLOSED_TASKS * 20 / TOTAL_TASKS)))) ${COMPLETION_PCT}%
\`\`\`

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Closed | ${CLOSED_TASKS} | ${COMPLETION_PCT}% |
| 🔄 Open | ${OPEN_TASKS} | $(echo "scale=1; ($OPEN_TASKS * 100) / $TOTAL_TASKS" | bc)% |
| **Total** | **${TOTAL_TASKS}** | **100%** |

---

## 📅 Phase Breakdown

EOF

# Add phase details
for phase in "Phase 0" "Phase 1" "Phase 2" "Phase 3" "Phase 4" "Phase 5" "Phase 6" "Phase 7"; do
  total=${PHASE_TOTAL["$phase"]:-0}
  closed=${PHASE_CLOSED["$phase"]:-0}
  
  if [[ $total -gt 0 ]]; then
    pct=$(echo "scale=0; ($closed * 100) / $total" | bc)
    bar_filled=$(echo "scale=0; ($closed * 18) / $total" | bc)
    bar_empty=$((18 - bar_filled))
    
    cat >> "$OUTPUT_FILE" << EOF
### $phase

- **Status**: ${closed}/${total} tasks complete (${pct}%)
- **Progress**: $(printf '█%.0s' $(seq 1 $bar_filled))$(printf '░%.0s' $(seq 1 $bar_empty)) ${pct}%

EOF
  fi
done

# Add test coverage section
cat >> "$OUTPUT_FILE" << EOF

---

## 🧪 Test Coverage by Service

| Service | Controllers | Test Files | Coverage Est. |
|---------|-------------|------------|---------------|
EOF

for service in UserService MatchmakingService swipe-service photo-service messaging-service; do
  if [[ -n "${SERVICE_TESTS["$service"]:-}" ]]; then
    IFS='|' read -r controllers tests <<< "${SERVICE_TESTS["$service"]}"
    
    if [[ $controllers -gt 0 ]]; then
      coverage_est=$(echo "scale=0; ($tests * 100) / ($controllers * 5)" | bc)  # Assume 5 tests per controller is 100%
      [[ $coverage_est -gt 100 ]] && coverage_est=100
    else
      coverage_est=0
    fi
    
    if [[ $coverage_est -lt 30 ]]; then
      status="🔴"
    elif [[ $coverage_est -lt 70 ]]; then
      status="🟡"
    else
      status="🟢"
    fi
    
    echo "| $service | $controllers | $tests | $status ${coverage_est}% |" >> "$OUTPUT_FILE"
  fi
done

# Add user story status
cat >> "$OUTPUT_FILE" << EOF

---

## 🎯 User Story Status

### 🟢 US1: Profile Onboarding (Priority: P1)
**Goal**: New visitor completes registration, profile wizard, and photo upload.

- **Evidence**: \`api_tests.py\` creates profiles successfully
- **Blockers**: Keycloak integration (T022), Flutter wizard UI (T026)
- **Next Task**: T022 - Configure Keycloak realm

### 🔴 US2: Match Discovery (Priority: P1)
**Goal**: Logged-in member browses prioritized candidates and swipes.

- **Evidence**: None yet
- **Blockers**: US1 incomplete, onboarding must finish first
- **Next Task**: T030 - Unit tests for matchmaking scoring

### 🔴 US3: Messaging (Priority: P2)
**Goal**: Matched users exchange real-time messages.

- **Evidence**: SignalR hub exists (20% complete)
- **Blockers**: Message persistence missing (T043)
- **Next Task**: T043 - Add message persistence layer

### 🔴 US4: Safety & Recovery (Priority: P3)
**Goal**: Privacy toggles, block/report actions, recovery flows.

- **Evidence**: None
- **Blockers**: US1-3 incomplete
- **Next Task**: T050 - API tests for reporting

---

## ✅ Success Criteria Tracking

| ID | Criteria | Status | Evidence |
|----|----------|--------|----------|
| SC-001 | 90% onboarding completion <12min | ❌ Not tracked | No telemetry configured |
| SC-002 | ≤350ms P95 API latency | ❌ Not measured | No load tests |
| SC-003 | 80% mutual match <48h | ❌ Not measured | No metrics pipeline |
| SC-004 | 95% message delivery <1s | ❌ Not implemented | Messaging incomplete |
| SC-005 | Safety reports <2min response | ❌ No system | Reporting not built |

---

## 🚀 Quick Actions

**View Live Project Board**:
- [Project Board](https://github.com/users/$OWNER/projects/$PROJECT_NUMBER)
- [Backlog](https://github.com/users/$OWNER/projects/$PROJECT_NUMBER?query=is%3Aopen+sort%3Aupdated-desc)

**Update This Dashboard**:
\`\`\`bash
./scripts/generate_dashboard.sh
\`\`\`

**Sync Tasks to GitHub**:
\`\`\`bash
./scripts/sync_mvp_project.sh
\`\`\`

**Run API Tests**:
\`\`\`bash
python3 api_tests.py
\`\`\`

---

## 📝 Recent Activity

EOF

# Add recent closed issues
echo "  Fetching recent activity..."
RECENT_CLOSED=$(gh issue list --repo best-koder-ever/DatingApp-Config --state closed --limit 5 --json number,title,closedAt --jq '.[] | "- ✅ [#\(.number)](\(.url)) \(.title) - Closed \(.closedAt | fromdateiso8601 | strftime("%Y-%m-%d"))"' 2>/dev/null || echo "- No recent closed issues")

echo "$RECENT_CLOSED" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

*Dashboard auto-generated from GitHub Projects API. Run \`./scripts/generate_dashboard.sh\` to refresh.*
EOF

echo ""
echo "✅ Dashboard generated: $OUTPUT_FILE"
echo "📊 Overall: ${COMPLETION_PCT}% complete (${CLOSED_TASKS}/${TOTAL_TASKS})"
echo ""
echo "💡 View dashboard:"
echo "   cat specs/001-mvp-foundation/DASHBOARD.md"
echo "   # Or commit and view on GitHub"
