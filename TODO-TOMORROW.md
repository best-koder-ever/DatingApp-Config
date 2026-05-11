# TODO — Current State

**Updated**: 2026-05-11
**Active spec**: `specs/005-core-differentiation` (Compatibility Engine + Match Insight)
**Tagged**: `mvp-demo-v0.1` (commit `ba559e9`)

---

## ✅ Spec 005 — Phase 5 (Match Insight UI) Complete

### Phase 5 — Flutter Match Insight Card
- [x] T519 — Widget tests for `compatibility_questions_screen`
- [x] T540 — `MatchInsightService` API client with LRU cache (PR #23)
- [x] T541 — `CompatibilityBadge` circular gradient widget (PR #18)
- [x] T542 — `CompatibilityBarComparison` widget (PR #24)
- [x] T543 — `MatchInsightScreen` 4-section card (Why Connected, Friction, Growth, Premium-locked)
- [x] T544 — Badge in `profile_card.dart` discover deck (replaces older fire-icon pill)
- [x] T545 — Matches list badge tap → `MatchInsightScreen`
- [x] T546 — Widget tests for `MatchInsightScreen` (6 tests)
- [x] T547 — Widget tests for badge + bars
- Flutter commits: `2cac3d3` (T545 badge overlay), `82dda33` (T543/T544/T546) on `main`.

### Phase 4 — Backend Scoring Integration
- [x] T530 — `AdvancedMatchingService.ScoreCandidateAsync` blends compatibility (30%)
- [x] T531 — `ScoringConfiguration.CompatibilityWeight` configurable, weights sum to 1.0
- [x] T532 — "Why You Matched" reasons + frictions generated during scoring
- [x] T533 — `MatchInsight` entity + migration
- [x] T534 — `GET /api/matchmaking/matches/{matchId}/insight` (tiered free/premium)
- [x] T535 — DailyPick inherits compatibility blending via `LiveScoringStrategy` → `AdvancedMatchingService` (documented). Commit `6cee87a`.
- [x] T537 — Unit tests for MatchInsight generation (6 tests)
- All 217 MatchmakingService tests green. Branch `feature/keycloak-auth-updates`.

### Phase 3 — Compatibility Scoring Engine
- [x] T520-T523, T525 — `CompatibilityScorer`, `CompatibilityScore` entity, `GET /api/compatibility/score/{other}`, unit tests

---

## ⏳ Up Next

### Spec 005 — final loose ends
- [x] **T524** [P0] [Backend] `CompatibilityPrecomputeService` background pre-computation of scores for users who have answered questions. Shipped in `MatchmakingService` `36413fe`. Configurable via `CompatibilityPrecompute` options (Enabled / IntervalMinutes / MaxUsersPerCycle / MaxPairsPerCycle / StaleAfterHours). 8 unit tests.
- [x] **T536** [P0] [Test] Integration tests for `AdvancedMatchingService` compatibility integration — verified existing `AdvancedMatchingCompatibilityTests` (7 scenarios: no-scorer, no-keycloak, neutral, high compat, low compat, zero-weight, scorer-throws). All pass.

### Verification / Cleanup
- [ ] **Emulator UAT**: spin up `./infrastructure/start.sh && ./dev-start.sh`, run Flutter on emulator, verify the full flow: bot match → badge appears on matches list → tap → insight card renders with real reasons/frictions from `/api/matchmaking/matches/{id}/insight`.
- [ ] **PR cleanup**: open PR `feature/keycloak-auth-updates` → `004-multi-app-architecture` once T536 lands.
- [ ] Tag `mvp-005-insight-v1` once UAT passes.

---

## 🔮 Future Phases

- **Phase 6** — AI Psykolog (LLM-generated nuance, weekly insights digest, premium gating). Likely unlocks the `growth` field with richer LLM-derived content.
- **Phase 7** — Voice Prompts × insight ("She mentioned X in her voice prompt — try asking about that").
- **Phase 8** — Daily Picks UI surface (mailbox metaphor).
- **Asymmetric insight reasons** — currently both users see the same reasons/frictions; future work makes them viewer-specific (already noted in MatchInsightServiceTests).

---

## 📁 Where Things Live

| Concern | Repo / Path |
|---|---|
| Backend compatibility scorer | `MatchmakingService/Services/CompatibilityScorer.cs` |
| Backend insight generation | `MatchmakingService/Services/MatchInsightService.cs` |
| Backend daily picks | `MatchmakingService/Services/Background/DailyPickGenerationService.cs` |
| Backend endpoint | `MatchmakingService/Controllers/MatchmakingController.cs` (`GET /matches/{id}/insight`) |
| Flutter service | `mobile-apps/flutter/dejtingapp/lib/services/match_insight_service.dart` |
| Flutter insight screen | `lib/screens/match_insight_screen.dart` |
| Flutter badge | `lib/widgets/compatibility_badge.dart` |
| Flutter bars | `lib/widgets/compatibility_bar_comparison.dart` |
| Discover card | `lib/widgets/discovery/profile_card.dart` |
| Matches screen | `lib/screens/enhanced_matches_screen.dart` |
| Spec tasks | `DatingApp/specs/005-core-differentiation/tasks.md` |
