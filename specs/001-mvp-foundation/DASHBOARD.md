# MVP Foundation Dashboard

**Last Updated**: 2026-05-31 UTC  
**Project Board**: Vikunja running at http://localhost:3456  
**Board Reference**: `docs/VIKUNJA_BOARD.md` — complete task inventory organized by column/label  
**Use-Case Checker Agents**: `.github/agents/` — 5 agents: onboarding, discovery, messaging, safety, e2e  
**Health Check**: `./scripts/health-check.sh` — 9 services status

---

## 📊 Overall Progress (Core MVP: Phases 0–7)

**~66% Complete** (50/76 core tasks; many Spec 005 tasks also shipped since Jul 2025)

```
Progress: █████████████░░░░░░░░ 66%
```

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Completed | 50 | 66% |
| 🔄 In Progress | 1 | 1% |
| ⬚ Remaining | 25 | 33% |
| **Total (Phases 0-7)** | **76** | **100%** |

> **Note**: Phases 8-12 (E2E automation, monetization, niche strategy) add 112 additional tasks tracked separately. Total across all phases: 69/188.

---

## 📅 Recent Completions (This Sprint)

| Task | Description | Commit | Repo |
|------|-------------|--------|------|
| T036-Flutter | MatchmakingHub SignalR real-time client + match notification dialog | `2a4a6b0` | mobile_dejtingapp |
| T044-Flutter | Unified messaging service wired into app initialization | `2a4a6b0` | mobile_dejtingapp |
| T035-Polish | Unread message badges (red dots) on bottom nav | `2a4a6b0` | mobile_dejtingapp |
| BugFix | MatchmakingService /health endpoint clash (duplicate removed) | `5808c51` | MatchmakingService |
| BugFix | YARP safety rate-limit split (reports 10/hr, block/unblock 60/hr) | `33c2347` | dejting-yarp |
| T026-SCREEN | Location, Notification, Onboarding Complete screens | `ae3ef70` | mobile_dejtingapp |
| T026-COORD | Onboarding Flow Coordinator (16-step) | `30c2282` | mobile_dejtingapp |
| T026-TEST | Wizard models unit tests (50 tests) | `922e0be` | mobile_dejtingapp |
| T154-RING | Profile completeness ring tests (41 tests) | `32ca33c` | mobile_dejtingapp |
| T153-BE | Profile completeness calculation backend | `14b8716` | UserService |
| T090-PAUSE | Account Pause API stubs + DTOs | `14b8716` | UserService |
| T091-SUPPORT | Feedback/Support API stubs + DTOs (19 tests) | `1ecb486` | UserService |
| T061-L10N | Flutter l10n infrastructure + ARB + 16 tests | `d47663d` | mobile_dejtingapp |
| T067-DESKTOP | Analyzer warning cleanup (0 warnings) | `d6de462` | mobile_dejtingapp |

---

## 🧪 Test Coverage by Service

| Service | Unit Tests | Test Status | Coverage Trend |
|---------|-----------|-------------|----------------|
| **Flutter App** | 289+ | ✅ All pass | 🟢 Growing |
| UserService | 139 | ✅ All pass | 🟢 Growing |
| MatchmakingService | 18 | ✅ Pass | 🟡 Needs growth |
| swipe-service | 5 | ✅ Pass | 🟡 Needs growth |
| photo-service | 14 | ✅ Pass | 🟡 Needs growth |
| messaging-service | 4 | ✅ Pass | 🟡 Needs growth |

### Flutter Test Breakdown (289+ total)
- Wizard screens: 132 tests (16 screens)
- Onboarding coordinator: 32 tests
- Wizard models: 50 tests
- Profile completeness ring: 41 tests
- Localization: 16 tests
- Other (photo upload, models): 18 tests

### UserService Test Breakdown (139 total)
- Profile controller: 12 tests
- Demo controller: 12 tests
- Safety controller: 16 tests
- Wizard controller: 5 tests
- Verification controller: 8 tests
- Onboarding metrics: 7 tests
- Preferences controller: 9 tests
- Profile completeness: 14 tests
- Account Pause DTOs: 18 tests
- Support Ticket DTOs: 19 tests
- DB integration: 1 test
- User profile: 18 tests

---

## 🎯 User Story Status

### ✅ US1: Profile Onboarding (Priority: P1) — 85%
**Goal**: New visitor completes registration, profile wizard, and photo upload.

- **Evidence**: 16 wizard screens built + tested, coordinator wired, l10n ready, onboarding gating in Flutter
- **Completed**: T020, T022, T023, T024, T025, T026, T027
- **Remaining**: T021 (Flutter integration test), T028/T029 (deferred)
- **Flutter screens**: ✅ All 16 onboarding screens + onboarding completion gating
- **Backend**: ✅ Wizard controller, preferences, verification, Keycloak config

### 🟡 US2: Match Discovery (Priority: P1) — 90%
**Goal**: Logged-in member browses prioritized candidates and swipes.

- **Evidence**: Full scoring algorithm + tests, discover UI with compatibility, offline cache, real-time match notifications via SignalR
- **Completed**: T030, T031, T032, T033, T034, T035, T036, T037
- **Remaining**: None for MMP (all core tasks done)
- **Flutter**: ✅ Discover screen, swipe UI, match notifications, offline cache
- **Backend**: ✅ Scoring, daily limits, swipe idempotency, MatchmakingHub SignalR

### 🟡 US3: Messaging (Priority: P2) — 80%
**Goal**: Matched users exchange real-time messages.

- **Evidence**: SignalR hub + persistence, offline queue + reconnection, YARP websocket routing
- **Completed**: T040, T042, T043, T044, T045
- **Remaining**: T041 (Flutter widget test), T046 (deferred)
- **Flutter**: ✅ UnifiedMessagingService with offline queue, wired into app initialization
- **Backend**: ✅ MessagingHub, message persistence, YARP websocket passthrough

### 🟡 US4: Safety & Recovery (Priority: P3) — 50%
**Goal**: Privacy toggles, block/report actions, recovery flows.

- **Evidence**: Safety controller with block/report/unblock (16 tests), Account Pause API stubs, Support ticket API stubs, photo privacy enforcement
- **Completed**: T050, T052, T054
- **Remaining**: T051 (Flutter privacy test), T053/T055/T056 (deferred)
- **Flutter**: ✅ Block UX with confirmation dialog  
- **Backend**: ✅ Safety controller, photo privacy enforcement, API test coverage

---

## ✅ Success Criteria Tracking

| ID | Criteria | Status | Evidence |
|----|----------|--------|----------|
| SC-001 | 90% onboarding completion <12min | 🟡 Instrumented | OnboardingMetricsService (T068) + funnel tracking |
| SC-002 | ≤350ms P95 API latency | 🟡 Instrumented | MatchmakingMetricsService (T069) + K6 harness (T017) |
| SC-003 | 80% mutual match <48h | 🟡 Instrumented | Match conversion metrics (T069) |
| SC-004 | 95% message delivery <1s | 🟡 Instrumented | MessagingMetricsService (T070) + SignalR hub |
| SC-005 | Safety reports <2min response | 🟡 Instrumented | SafetyMetricsService (T071) + audit logging |

---

## 🏗️ Architecture Status

| Component | Status | Notes |
|-----------|--------|-------|
| YARP Gateway | ✅ Running | Rate limiting (split safety), routing, websocket passthrough |
| Keycloak Auth | ✅ Running | OIDC, JWT validation, realm configured |
| UserService | ✅ Active | 8 controllers, 139 tests, wizard + safety + metrics |
| MatchmakingService | ✅ Active | Scoring algo, daily limits, SignalR hub, 18 tests |
| SwipeService | ✅ Active | Idempotent swipe ingestion, retry logic |
| PhotoService | ✅ Active | Upload + moderation + privacy pipeline |
| MessagingService | ✅ Active | SignalR hub + REST, message persistence |
| SafetyService | ✅ Active | Block/report/unblock endpoints |
| Flutter Client | ✅ Active | 16 wizard screens, discover, messaging, match notifications, 289+ tests |
| L10n Infrastructure | ✅ Ready | ARB + gen-l10n, English locale |
| Profile Completeness | ✅ Complete | Ring widget + backend calculator |
| Real-time Notifications | ✅ Complete | MatchmakingHub + Flutter client |

---

## 🚀 Quick Actions

```bash
# Start infrastructure
./infrastructure/start.sh

# Run services
./dev-start.sh

# Run API tests
python3 api_tests.py

# Run Flutter tests
cd mobile-apps/flutter/dejtingapp && flutter test

# Run UserService tests
cd UserService && dotnet test

# Update this dashboard
./scripts/generate_dashboard.sh
```

---

## 📋 Remaining MMP Tasks (High Priority)

| Task | Category | Description |
|------|----------|-------------|
| T004 | CI/CD | Fix CI/CD pipeline for green builds (coverage gate) |
| T021 | US1 Test | Flutter integration test for onboarding wizard |
| T041 | US3 Test | Flutter widget test for conversation view |
| T051 | US4 Test | Flutter integration test for privacy settings |
| T060 | Polish | Consolidate documentation updates |
| T061 | Polish | Harden error messaging + localization |
| T063 | Polish | Finalize monitoring dashboards + alerts |
| T064 | Polish | Quickstart validation + screenshots |
| T067 | Polish | Address desktop plugin analyzer warnings |

**Deferred (not needed for beta)**:  
T002, T005, T009-T015, T028, T029, T046, T053, T055, T056, T066, T072

---

*Dashboard regenerated 2025-07-17. 50/76 core MVP tasks completed (66%).*
