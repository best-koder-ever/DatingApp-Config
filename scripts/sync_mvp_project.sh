#!/usr/bin/env bash
# Sync tasks from specs/001-mvp-foundation/tasks.md to GitHub Projects board
#
# This script:
# - Creates issues for each task if they don't exist
# - Adds issues to the project board
# - Sets Phase and Spec Task ID metadata
# - Optionally creates phase parent issues and links tasks (if hierarchy enabled)
#
# To enable hierarchy view (BETA):
# 1. Go to https://github.com/users/best-koder-ever/projects/2/settings
# 2. Enable "Show hierarchy" or add a "Tracks" field
# 3. Re-run this script to create parent issues and link tasks
#
set -euo pipefail

OWNER="best-koder-ever"
REPO="best-koder-ever/DatingApp-Config"
PROJECT_TITLE="001-mvp-foundation"
TMP_TASK_FILE="/tmp/mvp_tasks.csv"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required" >&2
  exit 1
fi

PROJECT_NUMBER=$(gh project list --owner "$OWNER" --format json \
  | jq -r --arg title "$PROJECT_TITLE" '.projects[] | select(.title==$title) | .number')

if [[ -z "$PROJECT_NUMBER" ]]; then
  echo "Project '$PROJECT_TITLE' not found for owner '$OWNER'" >&2
  exit 1
fi

PROJECT_ID=$(gh project view "$PROJECT_NUMBER" --owner "$OWNER" --format json \
  | jq -r '.id')

FIELD_JSON=$(gh project field-list "$PROJECT_NUMBER" --owner "$OWNER" --format json)

PHASE_FIELD_ID=$(echo "$FIELD_JSON" \
  | jq -r '.fields[] | select(.name=="Phase") | .id')
SPEC_FIELD_ID=$(echo "$FIELD_JSON" \
  | jq -r '.fields[] | select(.name=="Spec Task ID") | .id')
TRACKS_FIELD_ID=$(echo "$FIELD_JSON" \
  | jq -r '.fields[] | select(.name=="Tracks") | .id')

if [[ -z "$PHASE_FIELD_ID" || -z "$SPEC_FIELD_ID" ]]; then
  echo "Required project fields ('Phase', 'Spec Task ID') are missing" >&2
  exit 1
fi

if [[ -n "$TRACKS_FIELD_ID" ]]; then
  echo "Hierarchy field 'Tracks' detected (ID: $TRACKS_FIELD_ID)"
  HIERARCHY_ENABLED=true
else
  echo "Hierarchy field not found - tasks will not be linked to phase parents"
  HIERARCHY_ENABLED=false
fi

declare -A PHASE_OPTION
while IFS='=' read -r name value; do
  PHASE_OPTION["$name"]="$value"
done < <(echo "$FIELD_JSON" \
  | jq -r '.fields[] | select(.name=="Phase") | .options[] | "\(.name)=\(.id)"')

if [[ ${#PHASE_OPTION[@]} -eq 0 ]]; then
  echo "No Phase options defined on project. Ensure the 'Phase' field has select values." >&2
  exit 1
fi

echo "Fetching existing project items..."
items_json=$(gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 200 --format json)

# Create phase parent issues if hierarchy is enabled
declare -A PHASE_PARENT_ISSUE
if [[ "$HIERARCHY_ENABLED" == "true" ]]; then
  echo "Creating phase parent issues for hierarchy..."
  for phase in "Phase 2" "Phase 3" "Phase 4" "Phase 5" "Phase 6" "Phase 7"; do
    phase_issue_json=$(gh issue list --repo "$REPO" --search "\"$phase\" in:title is:issue" --limit 1 --json number,url)
    phase_number=$(echo "$phase_issue_json" | jq -r '.[0].number // empty')
    phase_url=$(echo "$phase_issue_json" | jq -r '.[0].url // empty')
    
    if [[ -z "$phase_number" ]]; then
      echo "  Creating parent issue: $phase"
      phase_url=$(gh issue create --repo "$REPO" \
        --title "$phase" \
        --body "Parent tracking issue for all $phase tasks.\n\nThis issue groups tasks from \`specs/001-mvp-foundation/tasks.md\`." \
        | tail -n 1 | tr -d '\r' | xargs)
      phase_number="${phase_url##*/}"
      sleep 2
    fi
    
    PHASE_PARENT_ISSUE["$phase"]="$phase_url"
    echo "  $phase → Issue #$phase_number"
  done
fi

# Function to generate rich issue descriptions following best practices
generate_issue_body() {
  local task_id="$1"
  local task_title="$2"
  local task_phase="$3"
  
  # Determine agent recommendation and context based on task
  local agent_mode="CLI (Aider/Cursor)"
  local context=""
  local acceptance=""
  local testing=""
  local observability=""
  local affected=""
  local dependencies=""
  local estimate="2-4 hours"
  
  case "$task_id" in
    T015)
      agent_mode="GitHub Copilot"
      context="Without observability we can't diagnose production issues or validate success criteria (SC-001 through SC-005). Splunk/structured logging enables AI-assisted debugging."
      acceptance="- Document expected metrics for each user story (onboarding, matchmaking, messaging, safety)
- Define Splunk/OpenTelemetry dashboard layouts in \`monitoring/dashboards/\`
- Specify alert thresholds: P95 latency >500ms, error rate >1%
- Provide correlation ID tracing examples for end-to-end request tracking"
      testing="- Verify dashboard JSON validates
- Test example queries return results from demo logs"
      observability="- Add CorrelationId to all log entries
- Use structured logging: \`_logger.LogInformation(\"Event {EventType} for User {UserId}\", eventType, userId)\`"
      affected="- \`specs/001-mvp-foundation/plan.md\`
- \`monitoring/dashboards/mvp-overview.json\` (new)
- \`logs/README.md\` (new)"
      dependencies="None (foundational)"
      estimate="3-5 hours"
      ;;
      
    T016)
      agent_mode="GitHub Copilot"
      context="Matchmaking needs fallback rules when candidate queue is empty (expand distance/age after 24h) to prevent user frustration."
      acceptance="- Document scoring weights: distance (30%), shared interests (40%), recency (20%), profile completeness (10%)
- Define fallback heuristics: broaden distance by 10km/day, age range by 2 years/day (max 50km, ±10 years)
- Specify queue refresh schedule: every 6 hours or when <5 candidates remain
- Add examples to \`contracts/api-spec.md\`"
      testing="- Review with product owner
- Verify examples match MatchmakingService logic"
      observability="- Log scoring breakdown per candidate: \`MatchScoring {UserId} {CandidateId} {Score} {Factors}\`"
      affected="- \`specs/001-mvp-foundation/plan.md\`
- \`specs/001-mvp-foundation/contracts/api-spec.md\`"
      dependencies="None (foundational)"
      estimate="2-3 hours"
      ;;
      
    T021)
      agent_mode="CLI (test requires local execution)"
      context="Automated Flutter integration tests prevent UI regressions in the critical onboarding flow."
      acceptance="- Integration test at \`mobile-apps/flutter/dejtingapp/integration_test/profile_onboarding_test.dart\`
- Drives full wizard: name → age → location → interests → photo upload → review
- Validates step-by-step persistence (can resume mid-flow)
- Confirms profile appears in matchmaking after completion
- Runs in CI via \`flutter test integration_test/profile_onboarding_test.dart\`"
      testing="- Run test locally against demo backend
- Capture screenshots on failure
- Verify test completes <60 seconds"
      observability="- Add test logging to capture API responses
- Log wizard step transitions for debugging test failures"
      affected="- \`mobile-apps/flutter/dejtingapp/integration_test/profile_onboarding_test.dart\` (new)
- Update \`.github/workflows/flutter-tests.yml\` to include integration tests"
      dependencies="**Blocked by**: T023 (wizard endpoints must exist)"
      estimate="4-6 hours"
      ;;
      
    T024)
      agent_mode="CLI (complex ML integration)"
      context="Photos are the primary trust signal. ML moderation filters unsafe content + privacy controls (MatchOnly blur) give users agency."
      acceptance="- PhotoService applies ML.NET moderation on upload (detect NSFW, violence, hate symbols)
- Pipeline generates blurred versions for MatchOnly privacy level using ImageSharp
- Privacy metadata stored in \`PhotoMetadata\` table with enum: Everyone, MatchOnly
- Non-matches see blur; matches see original (Tinder-style UX)
- Processing completes <10s per 6-photo batch
- Integration test covers upload → moderation → privacy enforcement"
      testing="- Unit test: \`ModerationService.Tests/PhotoModerationTests.cs\`
- Integration: \`api_tests.py::test_photo_privacy_enforcement\`
- Visual: \`flutter test integration_test/visual_photo_upload_test.dart\`"
      observability="- Log moderation results: \`PhotoModeration {PhotoId} {ModerationResult} {ConfidenceScore} {DurationMs}\`
- Log privacy enforcement: \`PhotoAccess {PhotoId} {ViewerId} {Allowed} {Reason}\`
- Track metrics: moderation rejection rate (target <5%), processing latency P95"
      affected="- \`photo-service/Services/ModerationService.cs\`
- \`photo-service/Services/ImageProcessingService.cs\`
- \`photo-service/Data/PhotoMetadata.cs\` (add PrivacyLevel enum)
- \`specs/001-mvp-foundation/contracts/api-spec.md\` (PhotoUpload response)"
      dependencies="**Blocked by**: T023 (wizard must save privacy preferences first)"
      estimate="5-8 hours"
      ;;
      
    T029)
      agent_mode="CLI (end-to-end automation)"
      context="TestDataGenerator is deprecated. New automation uses Keycloak API for realistic user provisioning and validates full signup → match flow."
      acceptance="- Script provisions users via Keycloak API (register + verify email simulation)
- Triggers UserService webhook to create profiles automatically
- Executes swipe loop via API to create mutual matches
- Validates match creation in MatchmakingService
- Replaces TestDataGenerator usage in \`dev-start.sh\`
- Evidence logged: user IDs, profile IDs, match IDs with timestamps"
      testing="- Run script against fresh demo environment
- Verify mutual match appears in both users' match lists
- Check audit logs show complete flow"
      observability="- Log each step: \`AutomationStep {Step} {Status} {Data} {DurationMs}\`
- Capture correlation IDs across services
- Save detailed logs to \`logs/automation-YYYYMMDD-HHMMSS.log\`"
      affected="- \`api_tests.py\` (enhance with Keycloak flows)
- \`scripts/keycloak_automation.py\` (new)
- \`dev-start.sh\` (remove TestDataGenerator, add new script)"
      dependencies="**Blocked by**: T022 (Keycloak realm), T028 (webhook listener)"
      estimate="6-8 hours"
      ;;
      
    T032)
      agent_mode="CLI (complex algorithm tuning)"
      context="Matchmaking scoring quality determines user engagement. Weights must balance distance, interests, freshness to surface best candidates."
      acceptance="- Update MatchmakingService scoring with weighted factors: distance (30%), shared interests (40%), recency (20%), completeness (10%)
- Implement daily queue expansion: broaden distance by 10km/day, age by 2 years/day (max 50km, ±10 years)
- Add queue selection: prioritize fresh profiles, exclude recently rejected (<7 days)
- Log scoring breakdown for debugging
- Performance: P95 candidate fetch <350ms"
      testing="- Unit test scoring algorithm with known inputs
- Integration test: verify queue ordering matches expected weights
- Load test: 500 concurrent candidate fetches <350ms P95"
      observability="- Log scoring details: \`CandidateScore {UserId} {CandidateId} {TotalScore} {DistanceScore} {InterestScore} {RecencyScore} {CompletenessScore}\`
- Track queue metrics: candidates per user, refresh frequency, expansion trigger rate"
      affected="- \`MatchmakingService/Services/ScoringEngine.cs\`
- \`MatchmakingService/Services/CandidateQueue.cs\`
- Update \`specs/001-mvp-foundation/contracts/api-spec.md\`"
      dependencies="**Uses**: T016 (fallback heuristics doc)"
      estimate="5-7 hours"
      ;;
      
    *)
      # Default template for other tasks
      agent_mode="GitHub Copilot"
      context="Part of $task_phase - see spec for user story context."
      acceptance="- Check \`specs/001-mvp-foundation/tasks.md\` for detailed requirements
- Verify against \`contracts/\` API specifications
- Follow acceptance criteria from \`spec.md\`"
      testing="- Add unit tests for service logic
- Add integration test covering API endpoints
- Verify in demo environment"
      observability="- Add structured logging with CorrelationId
- Log key operations: \`_logger.LogInformation(\"Operation {Op} {Status} {Data}\", op, status, data)\`
- Track relevant metrics for success criteria"
      affected="- See task description in \`specs/001-mvp-foundation/tasks.md\`"
      dependencies="Check task sequence in \`tasks.md\`"
      estimate="3-5 hours"
      ;;
  esac
  
  cat <<EOF
## 📋 Overview

**Phase**: $task_phase  
**Task**: $task_title  
**Estimated Effort**: $estimate

### 🤖 Recommended Agent Mode

**$agent_mode**

$(if [[ "$agent_mode" == *"CLI"* ]]; then
  echo "**Why CLI**: Requires local testing, complex multi-file changes, or iterative development."
  echo ""
  echo "**Suggested tool**: [Aider](https://aider.chat) - context-aware AI coding assistant"
  echo "\`\`\`bash"
  echo "# Install: pip install aider-chat"
  echo "# Usage: aider --model claude-3-5-sonnet-20241022 <files>"
  echo "\`\`\`"
else
  echo "**Why Cloud**: Well-defined task, can delegate and review async, benefits from issue-to-PR workflow."
  echo ""
  echo "**How to delegate**: Assign this issue to \`@copilot\` or comment \`@copilot implement this\`"
fi)

### Why This Matters

$context

---

## ✅ Acceptance Criteria

$acceptance

---

## 🧪 Testing Requirements

$testing

**Test Coverage Expectation**: 
- Unit tests for business logic (>80% coverage)
- Integration test for end-to-end flow
- Evidence captured in logs/screenshots

---

## 📊 Observability & Logging

$observability

**Logging Best Practices**:
- Use structured logging: \`_logger.LogInformation("Event {EventName} {Data}", name, data)\`
- Always include CorrelationId for request tracing
- Log entry/exit of critical operations with timing
- Use LogLevel appropriately: Debug < Information < Warning < Error < Critical

**For Splunk/OpenTelemetry**:
- Include searchable fields: UserId, SessionId, OperationType
- Log errors with stack traces: \`_logger.LogError(ex, "Operation failed {Context}", ctx)\`

---

## 📂 Affected Components

$affected

---

## 🔗 Dependencies

$dependencies

---

## 📚 Reference Documentation

- [Feature Spec](https://github.com/$OWNER/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/spec.md)
- [Implementation Plan](https://github.com/$OWNER/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/plan.md)
- [Tasks List](https://github.com/$OWNER/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/tasks.md)
- [API Contracts](https://github.com/$OWNER/DatingApp-Config/tree/001-mvp-foundation/specs/001-mvp-foundation/contracts)

---

**Source**: \`specs/001-mvp-foundation/tasks.md\` → \`$task_id\`  
**Auto-generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF
}

cat <<'EOF' > "$TMP_TASK_FILE"
T015|Document observability expectations|Phase 2
T016|Document matchmaking fallback heuristics|Phase 2
T017|Run matchmaking load/perf harness|Phase 2
T021|Create Flutter onboarding integration test|Phase 3
T022|Configure Keycloak realm for registration + verification|Phase 3
T023|Update UserService wizard endpoints|Phase 3
T024|Enhance PhotoService moderation + blur tagging|Phase 3
T025|Persist onboarding status transitions|Phase 3
T026|Implement Flutter onboarding UI updates|Phase 3
T027|Add telemetry + audit logs for signup/photos|Phase 3
T028|Expose onboarding webhook/listener|Phase 3
T029|Replace TestDataGenerator flows with Keycloak automation|Phase 3
T032|Tune matchmaking scoring + queue selection|Phase 4
T033|Introduce daily suggestion limits + exhaustion handling|Phase 4
T034|Implement swipe retry/idempotency|Phase 4
T035|Update Flutter Discover UI|Phase 4
T036|Emit notifications + YARP route for matches|Phase 4
T037|Finalize Flutter offline cache strategy|Phase 4
T040|Add messaging hub integration test|Phase 5
T041|Extend Flutter chat widget test|Phase 5
T042|Finalize SignalR hub contracts|Phase 5
T043|Add message persistence + delivery receipts|Phase 5
T044|Implement offline queue + reconnection handling|Phase 5
T045|Ensure YARP websockets auth passthrough|Phase 5
T046|Update audit logging + moderation hooks for messages|Phase 5
T050|Write API test covering report/block lifecycle|Phase 6
T051|Add Flutter privacy controls integration test|Phase 6
T052|Expand PhotoService privacy enforcement|Phase 6
T053|Build reporting endpoints + moderation queue integration|Phase 6
T054|Implement block UX + state sync in Flutter|Phase 6
T055|Add account recovery + rehydration logic|Phase 6
T056|Publish operations playbook entry|Phase 6
T060|Consolidate documentation updates|Phase 7
T061|Harden Flutter error messaging + localization|Phase 7
T062|Optimize EF Core queries|Phase 7
T063|Finalize monitoring dashboards + alerts|Phase 7
T064|Run quickstart validation + capture evidence|Phase 7
T065|Plan TestDataGenerator removal|Phase 7
T066|Evaluate message broker introduction|Phase 7
T067|Address Flutter desktop plugin warnings|Phase 7
T068|Instrument onboarding completion metrics (SC-001)|Phase 7
T069|Capture matchmaking latency/conversion metrics (SC-002/003)|Phase 7
T070|Track messaging delivery metrics (SC-004)|Phase 7
T071|Automate safety report acknowledgement timing (SC-005)|Phase 7
T072|Publish decision log for Keycloak + scoring defaults|Phase 7
EOF

while IFS='|' read -r task_id task_title task_phase; do
  [[ -z "$task_id" ]] && continue
  task_phase=$(echo "$task_phase" | tr -d '\r' | xargs)
  existing_issue_json=$(gh issue list --repo "$REPO" --search "\"$task_id\" in:title" --state all --limit 1 --json number,url,id)
  issue_number=$(echo "$existing_issue_json" | jq -r '.[0].number // empty')
  issue_url=$(echo "$existing_issue_json" | jq -r '.[0].url // empty')
  issue_url=$(echo "$issue_url" | tr -d '\r' | xargs)

  if [[ -z "$issue_number" || -z "$issue_url" ]]; then
    echo "Creating issue: $task_id"
    issue_body=$(generate_issue_body "$task_id" "$task_title" "$task_phase")
    created_issue_url=$(gh issue create --repo "$REPO" \
      --title "$task_id – $task_title" \
      --body "$issue_body" \
      | tail -n 1)

    created_issue_url=$(echo "$created_issue_url" | tr -d '\r' | xargs)
    if [[ "$created_issue_url" =~ ^https?:// ]]; then
      issue_url="$created_issue_url"
      issue_number="${created_issue_url##*/}"
    else
      echo "Warning: could not create issue for $task_id" >&2
      continue
    fi
  fi

  issue_number=$(echo "$issue_number" | tr -d '\r' | xargs)
  issue_number="${issue_number//[^0-9]/}"
  if [[ -z "$issue_number" ]]; then
    echo "Warning: issue number missing for $task_id" >&2
    continue
  fi

  existing_item_id=$(echo "$items_json" | jq -r --argjson number "$issue_number" '.items[] | select(.content.number == $number) | .id' | head -n 1)

  if [[ -z "$existing_item_id" ]]; then
    if gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$issue_url" >/dev/null 2>&1; then
      echo "Added $task_id to project"
      sleep 2  # Rate limit protection
      items_json=$(gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 200 --format json)
      existing_item_id=$(echo "$items_json" | jq -r --argjson number "$issue_number" '.items[] | select(.content.number == $number) | .id' | head -n 1)
    else
      echo "Warning: could not add issue #$issue_number to project (likely already added); retrying fetch" >&2
      sleep 2
      items_json=$(gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 200 --format json)
      existing_item_id=$(echo "$items_json" | jq -r --argjson number "$issue_number" '.items[] | select(.content.number == $number) | .id' | head -n 1)
    fi
  fi

  if [[ -z "$existing_item_id" ]]; then
    echo "Warning: could not find project item for issue #$issue_number; skipping $task_id" >&2
    continue
  fi

  item_id="$existing_item_id"

  phase_option_id="${PHASE_OPTION["$task_phase"]:-}"
  if [[ -z "$phase_option_id" ]]; then
    echo "Phase option '$task_phase' not found; skip setting phase for $task_id" >&2
  else
    if gh project item-edit --project-id "$PROJECT_ID" --id "$item_id" \
      --field-id "$PHASE_FIELD_ID" \
      --single-select-option-id "$phase_option_id" >/dev/null 2>&1; then
      echo "Set Phase=$task_phase for $task_id"
    fi
    sleep 1  # Rate limit protection
  fi

  if gh project item-edit --project-id "$PROJECT_ID" --id "$item_id" \
    --field-id "$SPEC_FIELD_ID" \
    --text "$task_id" >/dev/null 2>&1; then
    echo "Set Spec Task ID for $task_id"
  fi
  sleep 1  # Rate limit protection

  # Set hierarchy parent if enabled
  if [[ "$HIERARCHY_ENABLED" == "true" ]]; then
    parent_url="${PHASE_PARENT_ISSUE["$task_phase"]:-}"
    if [[ -n "$parent_url" ]]; then
      if gh project item-edit --project-id "$PROJECT_ID" --id "$item_id" \
        --field-id "$TRACKS_FIELD_ID" \
        --text "$parent_url" >/dev/null 2>&1; then
        echo "Linked $task_id to parent $task_phase"
      fi
      sleep 1  # Rate limit protection
    fi
  fi

done < "$TMP_TASK_FILE"

echo "Synced tasks to project '$PROJECT_TITLE' (Project #$PROJECT_NUMBER)"
