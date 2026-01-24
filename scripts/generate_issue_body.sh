#!/usr/bin/env bash
# Generate rich GitHub issue descriptions from task specs
# Usage: ./generate_issue_body.sh T024

set -euo pipefail

TASK_ID="$1"
SPEC_DIR="/home/m/development/DatingApp/specs/001-mvp-foundation"

# Extract task line from tasks.md
TASK_LINE=$(grep "^- \[.\] $TASK_ID " "$SPEC_DIR/tasks.md" || echo "")

if [[ -z "$TASK_LINE" ]]; then
  echo "Task $TASK_ID not found in tasks.md" >&2
  exit 1
fi

# Parse components
TASK_TITLE=$(echo "$TASK_LINE" | sed -E 's/^- \[.\] [^ ]+ (\[.*?\] )*//; s/ \(.*//; s/`$//')
TASK_PHASE=$(grep -B 5 "^- \[.\] $TASK_ID " "$SPEC_DIR/tasks.md" | grep "^## Phase" | tail -1 | sed 's/^## //')
TASK_STORY=$(grep -B 10 "^- \[.\] $TASK_ID " "$SPEC_DIR/tasks.md" | grep "^## Phase.*User Story" | tail -1 | sed 's/^## Phase [0-9]: //')

# Determine context
CONTEXT=""
DEPENDENCIES=""
ACCEPTANCE=""

case "$TASK_ID" in
  T015)
    CONTEXT="Without observability we can't diagnose production issues or validate success criteria (SC-001 through SC-005)."
    DEPENDENCIES="None (foundational)"
    ACCEPTANCE="- Document expected metrics for onboarding (SC-001), matchmaking (SC-002/003), messaging (SC-004), safety (SC-005)
- Define dashboard layouts in monitoring/
- Specify alert thresholds for P95 latency, error rates
- Provide example queries for correlation ID tracing"
    ;;
  T024)
    CONTEXT="Photos are the primary trust signal in dating apps. We need automated moderation to filter unsafe content AND privacy controls so users can choose who sees their photos (Everyone vs MatchOnly blur)."
    DEPENDENCIES="T023 (wizard must save privacy preferences)"
    ACCEPTANCE="- PhotoService applies ML-based moderation on upload (flag NSFW, violence, etc.)
- Pipeline generates blurred versions for MatchOnly privacy level
- Privacy metadata stored in PhotoMetadata table
- Non-matches see blur; matches see original (consistent with Tinder behavior)
- Processing completes <10s per batch"
    ;;
  T029)
    CONTEXT="TestDataGenerator was legacy scaffolding for demos. Now that Keycloak handles registration + verification, we need end-to-end automation that mirrors real user flows."
    DEPENDENCIES="T022 (Keycloak realm configured), T028 (webhook to populate profiles)"
    ACCEPTANCE="- Script provisions users via Keycloak API (register + verify)
- Triggers UserService webhook to create profiles
- Executes swipe loop via API to create matches
- Validates mutual match creation in MatchmakingService
- Replaces TestDataGenerator usage in dev-start.sh
- Evidence logged in api_tests.py or new automation script"
    ;;
  T021)
    CONTEXT="We need automated regression tests covering the full Flutter onboarding flow so UI changes don't break profile completion."
    DEPENDENCIES="T023 (wizard endpoints), T024 (photo upload API)"
    ACCEPTANCE="- Flutter integration test at integration_test/profile_onboarding_test.dart
- Drives full wizard: name → age → location → interests → photo upload → review
- Validates step-by-step persistence (can resume mid-flow)
- Confirms profile appears in matchmaking after completion
- Runs in CI via 'flutter test integration_test/profile_onboarding_test.dart'"
    ;;
  T032)
    CONTEXT="Matchmaking scoring determines who sees whom. We need tuned weights for distance, shared interests, recency, and fallback rules when queue is empty."
    DEPENDENCIES="T016 (fallback heuristics documented)"
    ACCEPTANCE="- Update MatchmakingService scoring algorithm with weighted factors
- Implement daily queue expansion rules (broaden distance/age after 24h)
- Add queue selection logic: prioritize fresh profiles, avoid recently rejected
- Log scoring breakdown for debugging
- Performance: P95 candidate fetch <350ms"
    ;;
  *)
    CONTEXT="Part of $TASK_PHASE"
    DEPENDENCIES="See tasks.md for task sequence"
    ACCEPTANCE="Check spec.md and contracts/ for detailed requirements"
    ;;
esac

# Generate rich markdown body
cat <<EOF
## 📋 Overview

**Task ID**: \`$TASK_ID\`  
**Phase**: $TASK_PHASE  
**User Story**: ${TASK_STORY:-N/A (foundational)}

### Why This Matters

$CONTEXT

---

## ✅ Acceptance Criteria

$ACCEPTANCE

---

## 🔗 Dependencies

$DEPENDENCIES

---

## 📂 Affected Components

<!-- Auto-populate based on task analysis -->
- See \`specs/001-mvp-foundation/tasks.md\` for service/file hints
- Check \`specs/001-mvp-foundation/contracts/\` for API/DTO requirements

---

## 🧪 Testing Strategy

<!-- Customize per task -->
- **Unit tests**: Service-level logic
- **Integration tests**: End-to-end API flows via api_tests.py or Flutter integration_test/
- **Evidence**: Capture logs/screenshots demonstrating acceptance criteria

---

## 📚 Reference Links

- [Spec](https://github.com/best-koder-ever/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/spec.md)
- [Plan](https://github.com/best-koder-ever/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/plan.md)
- [Tasks](https://github.com/best-koder-ever/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/tasks.md)
- [Contracts](https://github.com/best-koder-ever/DatingApp-Config/tree/001-mvp-foundation/specs/001-mvp-foundation/contracts)

---

**Source**: \`specs/001-mvp-foundation/tasks.md\` → $TASK_ID
EOF
