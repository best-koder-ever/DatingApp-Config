# Vikunja Kanban Board — DatingApp MVP

Vikunja is running at **http://localhost:3456**

First-time setup:
1. Open http://localhost:3456 in browser
2. Create an account (local, first user = admin)
3. Create a new project called "DatingApp MVP"

## Board Columns

| Column | Description | WIP Limit |
|--------|-------------|-----------|
| **Backlog** | Future work, not prioritized for current sprint | — |
| **Ready** | Prioritized, defined, ready to work on | — |
| **In Progress** | Currently being worked on | 3 |
| **Done** | Implemented and verified | — |
| **Verified** | Passed use-case checker agent verification | — |

## Labels

| Label | Meaning |
|-------|---------|
| `001-foundation` | Core MVP — user stories 1-4 |
| `002-agentic-ai` | AI agent features |
| `003-bot-swarm` | Bot swarm + testing |
| `004-multi-app` | Multi-app architecture |
| `005-core-diff` | Compatibility engine + AI psykolog |
| `bug` | Known defect |
| `test` | Test coverage work |
| `polish` | UI/UX polish, debug print removal |
| `infra` | Infrastructure, CI/CD, monitoring |
| `docs` | Documentation |
| `P0-blocker` | Blocks tester handoff |
| `P1-critical` | Must-do before next milestone |
| `P2-important` | Should do |
| `P3-nice` | Nice to have |

## Task Inventory

### DONE (Mark in "Done" column)

#### US1: Profile Onboarding (001-foundation)
- T022 — Keycloak registration + email verification
- T023 — 3-step wizard (basic info, preferences, photos)
- T024 — Photo moderation + blur
- T025 — Onboarding status persistence
- T026 — Flutter wizard UI (16 screens)
- T027 — Basic telemetry (funnel tracking)

#### US2: Match Discovery (001-foundation)
- T030 — Matchmaking unit tests
- T032 — Scoring algorithm
- T033 — Daily queue limits
- T034 — Swipe idempotency
- T035 — Flutter Discover UI (card stack)
- T036 — Match creation notifications
- T037 — Offline swipe cache

#### US3: Messaging (001-foundation)
- T042 — Basic SignalR hub
- T043 — Message persistence
- T044 — Flutter offline queue
- T045 — YARP websocket routing

#### US4: Safety (001-foundation)
- T052 — Photo privacy enforcement
- T054 — Block action (client + API)

#### Spec 005: Compatibility Engine (005-core-diff)
- T519 — Compatibility questions widget tests
- T530 — AdvancedMatchingService compatibility blend
- T531 — ScoringConfiguration compatibility weight
- T532 — "Why You Matched" reasons + frictions
- T533 — MatchInsight entity + migration
- T534 — GET /api/matchmaking/matches/{id}/insight
- T535 — DailyPick compatibility integration
- T537 — MatchInsight unit tests
- T540 — MatchInsightService API client
- T541 — CompatibilityBadge widget
- T542 — CompatibilityBarComparison widget
- T543 — MatchInsightScreen
- T544 — Badge in discover deck
- T545 — Matches list badge tap
- T546/T547 — Widget tests
- T524 — CompatibilityPrecomputeService background job

#### Tester Pipeline
- Tester APK builder script (`scripts/build-tester-apk.sh`)
- Feedback FAB widget + service
- Keycloak tunnel support (`scripts/start-keycloak-tunnel.sh`)
- Whisper transcription pump (`scripts/process-feedback.py`)
- Swipe contract fix (2026-05-29)

#### Infrastructure
- T006 — MMP scope definition
- T007 — Database strategy consolidation (MySQL)
- T008 — AuthService removal (Keycloak migration)
- T072 — CI/CD workflow fix
- T073 — Skipped tests fix
- T074 — API smoke tests in CI
- T075 — Test coverage reporting

### READY (Move to "Ready" column, in priority order)

#### P0-Blocker: T021 — Flutter onboarding integration test
- **What**: `integration_test/profile_onboarding_test.dart`
- **Where**: `mobile-apps/flutter/dejtingapp/integration_test/`
- **Why**: Only remaining Flutter integration test gap for US1

#### P0-Blocker: T041 — Flutter messaging widget test
- **What**: Chat screen renders messages, send button works
- **Where**: `mobile-apps/flutter/dejtingapp/test/screens/`
- **Why**: Only remaining Flutter test gap for US3

#### P0-Blocker: T051 — Flutter privacy screen test
- **What**: Privacy settings screen renders, toggles work
- **Why**: Only remaining Flutter test gap for US4

#### P1-Critical: Remove debug prints from Flutter
- **What**: Remove `ENRICH` logs, `debugPrint`, `print(` calls
- **Where**: `api_services.dart`, `AuthenticatedAvatar` widget
- **Labels**: `polish`, `001-foundation`

#### P1-Critical: Fix bot-to-bot message flooding
- **What**: Add MaxConversationsPerBot or "bots skip bots" rule
- **Where**: `bot-service/Services/SyntheticUserService.cs`
- **Labels**: `bug`, `003-bot-swarm`

#### P1-Critical: MatchmakingService test coverage
- **What**: Increase from 18 tests to 40+ (scoring edge cases)
- **Labels**: `test`, `001-foundation`

#### P2-Important: Fix geo-location timeout (cosmetic)
- **What**: Handle emulator GPS timeout gracefully
- **Labels**: `bug`, `polish`

#### P2-Important: T004 — Fix CI/CD coverage gate
- **What**: Add 80% coverage threshold to workflow
- **Labels**: `infra`

#### P2-Important: T002 — Add Mermaid dependency graphs to tasks.md
- **What**: Visual task dependency diagrams
- **Labels**: `docs`

#### P3: Audio retention policy — delete old feedback .m4a files
- **Labels**: `polish`, `003-bot-swarm`

#### P3: Crash/error capture — attach logs to voice memos
- **Labels**: `polish`

#### P3: Persist Keycloak hostname overrides in docker-compose
- **Labels**: `infra`

### BACKLOG (Future phases — don't touch until testers validate core loop)

#### 001-foundation: Deferred
- T028/T029 — Webhook/automation (deferred from Phase 1)
- T046 — Moderation hooks (deferred)
- T053 — Report workflow (deferred)
- T055 — Account recovery (deferred)
- T056 — Ops playbook (deferred)
- T009-T015 — Full test automation platform (deferred until post-MVP)

#### 005-core-diff: Future phases
- AI Psykolog (LLM reflection coach)
- Vector matching
- Radar chart
- Anonymous forum
- Post-date feedback

#### 002-agentic-ai: Not started
- Safety agent, photo coach, conversation starter, smart match

#### 003-bot-swarm: Advanced features
- Bot photo generation, multi-language, admin UI

#### 004-multi-app: Blueprint only
- Shared Flutter packages, flavor config

## Quick Start

```bash
# After setting up project in Vikunja UI:
# 1. Create labels matching the table above
# 2. Create tasks from the DONE list first (mark them)
# 3. Move READY items into column
# 4. Start with P0-blockers
```
