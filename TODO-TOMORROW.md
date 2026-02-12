# TODO-TOMORROW — Updated 2025-07-16

## Where We Are Now (Session Recap)

Task queue **fully emptied** — 27/27 tasks executed & committed across Flutter + .NET repos.
Anti-busywork gate added to copilot-instructions.md (3-question filter: WHO calls it? WHAT breaks? RUNNABLE output?).

### Health Metrics
| Layer | Tests | Status |
|-------|-------|--------|
| Flutter App | 289 | ✅ All pass, 0 warnings |
| UserService | 139 | ✅ All pass |
| MatchmakingService | ~4 | ✅ Pass |
| swipe-service | ~5 | ✅ Pass |
| photo-service | 36 (33+3 skip) | ✅ Pass |
| messaging-service | 36 | ✅ Pass |
| **Total** | **~509** | **All green** |

### MVP Progress: 43% (25/58 tasks)
- US1 Profile Onboarding: **70%** — 16 wizard screens, coordinator, l10n, backend endpoints
- US2 Match Discovery: **15%** — swipe service exists, scoring algo needs tests
- US3 Messaging: **20%** — SignalR hub works, message persistence missing
- US4 Safety & Recovery: **40%** — block/report/unblock, pause & support stubs

---

## 4 Layers — Current State & Important Notes

### Layer 1: Flutter Client (`mobile-apps/flutter/dejtingapp`)
- **289 tests**, 0 warnings (128 info-only dart lints)
- **16 onboarding wizard screens** fully built + tested (132 screen tests)
- **OnboardingCoordinator** — 16-step flow, 32 unit tests
- **Wizard models** — 50 unit tests, serialization/validation complete
- **Profile completeness ring** — animated widget + calculator, 41 tests
- **L10n infrastructure** — non-synthetic gen-l10n, 50+ ARB strings, 16 tests
- **Photo upload** — widget + model tests, camera/gallery picker wired
- **NOT wired**: Real Keycloak auth (still mock), real API calls to backend services
- **Key files**:
  - `lib/screens/onboarding/` — all wizard screens
  - `lib/services/onboarding_coordinator.dart` — flow orchestration
  - `lib/l10n/app_en.arb` — all localized strings
  - `lib/l10n/generated/` — gen-l10n output (non-synthetic)
  - `lib/models/wizard_models.dart` — onboarding data models

### Layer 2: .NET Backend Services
**30 controllers across 5 services**:

| Service | Controllers | Key Capabilities |
|---------|------------|------------------|
| **UserService** (10) | Profile, Demo, Safety, Wizard, Verification, OnboardingMetrics, Preferences, ProfileCompleteness, AccountStatus, Support | Full profile CRUD, wizard data, block/report, completeness calc, pause/support stubs |
| **MatchmakingService** (6) | Candidates, EloRating, Matches, MatchPreferences, FeedbackLoop, Profiles | Scoring algorithm, Elo, candidate fetch |
| **swipe-service** (5) | Swipe, SwipeAnalytics, SwipeBatch, SwipeHistory, SwipeUndo | Swipe ingestion, analytics, batch/undo |
| **photo-service** (4) | Photo, Moderation, Privacy, FaceVerification | Upload/fetch, ML moderation, privacy blur, DeepFace verify |
| **messaging-service** (5) | Messaging, Conversation, PresenceTracking, MessageRead, Notification | SignalR hub, conversations, read receipts, presence |

- **UserService** is the most mature (139 tests, 10 controllers)
- **photo-service** has face verification via DeepFace (T156)
- **messaging-service** SignalR hub path fixed to `/hubs/messages`
- **YARP gateway** routes all services, has diagnostics controller + rate limiting
- **NOT done**: Message persistence layer in messaging-service, matchmaking scoring tests

### Layer 3: Infrastructure
- **Keycloak** — OIDC provider, runs via `infrastructure/start.sh`
- **PostgreSQL** — shared DB containers per docker-compose
- **YARP Gateway** (`dejting-yarp`) — reverse proxy, rate limiting (GlobalLimiter), diagnostics
- **Docker** — each service has Dockerfile, compose orchestration in `infrastructure/`
- **Dev scripts**: `dev-start.sh`, `dev-stop.sh`, `dev-restart.sh`, `dev-status.sh`, `dev-logs.sh`
- **Multi-repo tooling**: `gita-workflow.sh`, `ai-commit-helper.sh`, `gh-multi-repo.sh`
- **NOT done**: CI/CD pipeline, automated Keycloak user provisioning (currently uses TestDataGenerator)

### Layer 4: Specs & Documentation
- **DASHBOARD.md** — 43% complete (25/58 tasks), has test tables & user story breakdowns
- **copilot-instructions.md** — AI guidelines including anti-busywork gate
- **API contracts** — `dejting-yarp/Contracts/api-spec.md` + `signalr-spec.md`
- **Spec Kit** — `specs/001-mvp-foundation/` has constitution, user stories, implementation plan
- **RATE_LIMITING.md** — YARP rate limit docs
- **PHOTO_SERVICE_DOCUMENTATION.md** — photo pipeline docs
- **NOT done**: OpenAPI/Swagger generation, contract sync automation

---

## What to Work on Next (Priority Order)

### 🔥 P0 — Unblock the MVP demo loop
1. **Keycloak → Flutter auth integration (T022)**
   - Wire real OIDC login in Flutter (replace mock auth)
   - WHO: Flutter app calls this on every launch
   - WHAT BREAKS: Can't demo real login → everything downstream blocked
   
2. **Flutter → Backend API wiring**
   - Connect wizard screens to UserService endpoints (save/load profile)
   - Connect photo upload screen to photo-service
   - WHO: Every wizard screen needs this to persist data

### 🔥 P1 — US2 Match Discovery (currently 15%)
3. **T030 — Matchmaking scoring algorithm tests**
   - Unit test the candidate scoring in MatchmakingService
   - WHO: Match discovery screen calls this
   - WHAT BREAKS: Can't verify scoring correctness

4. **Flutter match discovery UI**
   - Swipe card stack screen, candidate profile view
   - Wire to matchmaking + swipe service APIs

### 🔥 P1 — US3 Messaging (currently 20%)
5. **T043 — Message persistence layer**
   - Add EF Core message storage in messaging-service
   - WHO: SignalR hub calls this on every message send
   - WHAT BREAKS: Messages lost on restart

6. **Flutter messaging UI**
   - Chat screen, conversation list, real-time via SignalR
   - Wire to messaging-service

### 🟡 P2 — Polish & Safety
7. **US4 Safety — implement behind pause/support stubs**
   - AccountStatusController.Pause/Resume needs real logic
   - SupportController.Submit needs ticket persistence

8. **TestDataGenerator replacement**
   - Move to Keycloak-first user provisioning
   - Eliminate legacy demo seeding

---

## Recent Commits (for reference)

| Repo | Commit | Description |
|------|--------|-------------|
| DatingApp | `542602e` | Restore TODO-TOMORROW.md |
| DatingApp | `ccc2642` | Anti-busywork gate in copilot-instructions |
| DatingApp | `bd1d12f` | Dashboard updated to 43% |
| UserService | `1ecb486` | T091 Support API stubs, 19 tests |
| UserService | `14b8716` | T090 Account Pause API stubs |
| Flutter | `d6de462` | T067 Remove all analyzer warnings |
| Flutter | `d47663d` | T061 L10n infrastructure + 16 tests |
| Flutter | `32ca33c` | T154 Profile completeness ring tests |
| Flutter | `922e0be` | T026 Wizard model tests (50) |
| Flutter | `30c2282` | T026 OnboardingCoordinator (32 tests) |

---

## Decision Log
- **l10n**: Using non-synthetic gen-l10n (synthetic deprecated), output to `lib/l10n/generated/`
- **Anti-busywork gate**: 3 questions before any AI task — prevents scripts nobody calls
- **Multi-repo**: Always use gita/helper scripts, never manual cd loops
- **Terminal-first**: All file ops via `cat > file << 'EOF'`, never use create_file/replace tools
