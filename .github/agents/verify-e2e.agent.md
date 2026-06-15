---
name: verify-e2e
description: "Run all four use-case verifiers in sequence and produce a consolidated pass/fail report. Use this to validate the entire system before tester onboarding sessions."
---

# End-to-End System Smoke Test

## Prerequisites
- Run `./infrastructure/start.sh` and `./dev-start.sh`
- All 8 services must be available (YARP:8080, User:8082, Matchmaking:8083, Photo:8085, Messaging:8086, Swipe:8087, Safety:8088, Bot:8089)
- Keycloak must be running on :8090

## Orchestration

This agent runs the following verifiers in order:

### 1. verify-onboarding
Register a test user → create profile → verify completeness.
- **Critical path**: Keycloak → UserService
- **If fails**: System cannot accept new users. Stop here.

### 2. verify-discovery
Login as demo-user → reset state → fetch candidates → swipe → check for matches.
- **Critical path**: MatchmakingService → SwipeService → bot-service
- **If fails**: Matching loop is broken. Fix before tester handoff.

### 3. verify-messaging
Find match → send message → retrieve conversation.
- **Critical path**: MessagingService (REST) → DB persistence
- **If fails**: Messaging is broken. REST fallback only.

### 4. verify-safety
Block user → verify → unblock.
- **Critical path**: SafetyService
- **If fails**: Safety features degraded. Acceptable for initial testers but note it.

## Consolidated Report Format

```
╔═════════════════════════════════════════╗
║     DatingApp E2E Smoke Test Report     ║
║     $(date)              ║
╚═════════════════════════════════════════╝

  ONBOARDING  [PASS|FAIL]  — Keycloak → UserService → Profile
  DISCOVERY   [PASS|FAIL]  — Login → Candidates → Swipe → Match
  MESSAGING   [PASS|FAIL]  — Match → Send → Retrieve → Conversations
  SAFETY      [PASS|FAIL]  — Block → Verify → Unblock

  ───────────────────────────────────────
  OVERALL: [PASS|PARTIAL|FAIL]
  ───────────────────────────────────────

  Failures:
  - Step X: detailed error

  Notes:
  - Bot seeding status: [OK|NEEDS_RUN]
  - Tunnel status: [UP|DOWN]
  - Last known issues: see /memories/repo/known-issues.md
```

## Quick Run
```bash
# Sequential run, stop on first failure
echo "=== E2E Smoke Test ==="
echo "Running verify-onboarding..."
# ... (delegate to each verify agent)

echo "Running verify-discovery..."
# ... 

echo "Running verify-messaging..."
# ...

echo "Running verify-safety..."
# ...
```
