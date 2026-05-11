# TODO — Current State

**Updated**: 2026-05-08
**Active spec**: `specs/005-core-differentiation` (Compatibility Engine + Match Insight)
**Tagged**: `mvp-demo-v0.1` (commit `ba559e9`)

---

## ✅ Recently Shipped (spec 005)

### Phase 3 — Compatibility Scoring Engine
- [x] T520-T523, T525 — `CompatibilityScorer`, `CompatibilityScore` entity, `GET /api/compatibility/score/{other}`, unit tests

### Phase 4 — Scoring Integration (backend)
- [x] T530 — `AdvancedMatchingService.ScoreCandidateAsync` blends compatibility (30% weight)
- [x] T531 — `ScoringConfiguration.CompatibilityWeight` (default 0.30), weights sum to 1.0
- [x] T532 — "Why You Matched" reasons + frictions generated during scoring
- [x] T533 — `MatchInsight` entity + migration
- [x] T534 — `GET /api/matchmaking/matches/{matchId}/insight` (tiered free/premium)
- All 217 MatchmakingService tests green. Commits: MatchmakingService `54c2f5a`, `a3fa924` on `feature/keycloak-auth-updates`.

### Phase 5 — Match Insight Flutter UI (partial)
- [x] T519 — Widget tests for `compatibility_questions_screen`
- [x] T540 — `MatchInsightService` API client with LRU cache (shipped by Copilot coding agent PR #23)
- [x] T541 — `CompatibilityBadge` circular gradient widget (shipped PR #18)
- [x] T542 — `CompatibilityBarComparison` widget (shipped PR #24)
- [x] T547 — Widget tests for badge + bars
- [~] T545 — Badge overlay on matches list (visible); tap-to-insight-card pending T543. Commit `2cac3d3` on `main`.

---

## ⏳ Up Next

### Spec 005 — finish Phase 5
- [ ] **T543** [P0] [Flutter] `MatchInsightScreen` — full 4-section card (Why Connected, Friction, Growth, Premium). Wire `enhanced_matches_screen` badge tap → this screen.
- [ ] **T544** [P1] [Flutter] Integrate badge into `profile_card.dart` (discover deck).
- [ ] **T546** [P0] [Test] Widget tests for `MatchInsightScreen`.

### Spec 005 — finish Phase 4
- [ ] **T535** [P1] [Backend] `DailyPickGenerationService` uses compatibility-blended scoring.
- [ ] **T536** [P0] [Test] Integration tests for `AdvancedMatchingService` compatibility integration.
- [ ] **T537** [P0] [Test] Unit tests for `MatchInsight` generation (asymmetric per-user reasons).

### Verification
- [ ] **Emulator UAT**: spin up `./infrastructure/start.sh && ./dev-start.sh`, run flutter on emulator, verify badge appears on real match between demo-user + Maja.
- [ ] **PR cleanup**: merge `feature/keycloak-auth-updates` → `004-multi-app-architecture` for MatchmakingService once T536/T537 land.

---

## 🔮 Future Phases

- **Phase 6** — AI Psykolog (LLM-generated nuance, weekly insights digest, premium gating)
- **Phase 7** — Voice Prompts integration with insight ("She mentioned X in her voice prompt — try asking about that")
- **Phase 8** — Daily Picks UI surface (mailbox metaphor, T535 prerequisite)

---

## 📁 Where Things Live

| Concern | Repo / Path |
|---|---|
| Backend compatibility | `MatchmakingService/Services/CompatibilityScorer.cs` + `MatchInsightService.cs` |
| Backend endpoint | `MatchmakingService/Controllers/MatchmakingController.cs` (`GET /matches/{id}/insight`) |
| Flutter service | `mobile-apps/flutter/dejtingapp/lib/services/match_insight_service.dart` |
| Flutter badge | `lib/widgets/compatibility_badge.dart` |
| Flutter bars | `lib/widgets/compatibility_bar_comparison.dart` |
| Matches screen | `lib/screens/enhanced_matches_screen.dart` |
| Spec tasks | `DatingApp/specs/005-core-differentiation/tasks.md` |

