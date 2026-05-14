# TODO — Current State

**Updated**: 2026-05-12
**Active spec**: `specs/005-core-differentiation` (Compatibility Engine + Match Insight) — **SHIPPED `mvp-005-insight-v1`**
**Active track**: Zero-cost tester APK + in-app voice feedback — **SHIPPED `mvp-tester-v0.2`**
**Tagged**: `mvp-demo-v0.1` (commit `ba559e9`), `mvp-005-insight-v1`, `mvp-tester-v0.2`

---

## 🟢 Where We Are Right Now (2026-05-12)

**Zero-cost tester pipeline is LIVE and fully verified end-to-end through the tunnel.**

- Public HTTPS: `https://fastdev.tail45c6a7.ts.net` → Tailscale Funnel → laptop YARP `:8080` → backend services.
- ✅ **Keycloak hostname fix applied** (2026-05-12). Tokens now issued with `iss=https://fastdev.tail45c6a7.ts.net/auth/realms/DatingApp`. Verified by acquiring a token via the tunnel and successfully hitting `/api/messages/conversations` (200) and other authenticated endpoints.
- Helper script: `scripts/start-keycloak-tunnel.sh` — re-runs the hostname override after any `./infrastructure/start.sh` (which would otherwise reset to plain dev mode).
- Tester credentials available: `demo-user` / `DemoTest123!` (resetable via Keycloak admin).
- Feedback FAB shipped in Flutter (debug builds or `--dart-define=DEJTING_FEEDBACK_VISIBLE=true`).
- Whisper transcription pump (`scripts/process-feedback.py`) runs locally, tolerates corrupt audio, optional `--gh-issue OWNER/REPO`.

### Commits shipped previously (all pushed, see git log)

| Repo | Commit | Branch | Summary |
|---|---|---|---|
| bot-service | `8ee032f` | `feature/bot-service-improvements` | UserFeedback entity/controller/tests + idempotent `CREATE TABLE IF NOT EXISTS` startup SQL |
| dejting-yarp | `675e5e8` | `feature/keycloak-auth-updates` | `/api/userfeedback` route + anonymous bypass |
| dejting-yarp | `e12d6c9` | `feature/keycloak-auth-updates` | Tunnel support: `/auth/{**}` → Keycloak with `PathRemovePrefix`, funnel issuer in `ValidIssuers`, 30/h userfeedback rate limit |
| mobile_dejtingapp | `7205001` | `main` | Feedback FAB widget + service + 5 widget tests |
| mobile_dejtingapp | `aacf56c` | `main` | "Submitting as <name>" identity hint, +1 test (6/6 green) |
| DatingApp meta | `2c5eee1` | `004-multi-app-architecture` | `scripts/process-feedback.py` Whisper pump |
| DatingApp meta | `7007116` | `004-multi-app-architecture` | `scripts/build-tester-apk.sh` + `--gh-issue` flag |
| DatingApp meta | `faa7c1b` | `004-multi-app-architecture` | Tolerate corrupt audio in transcription pump |

### Then ship the APK

```bash
./scripts/build-tester-apk.sh
adb install -r mobile-apps/flutter/dejtingapp/build/app/outputs/flutter-apk/app-release.apk
# Or scp to phone /sdcard/Download/
```

Tester opens APK → logs in via funnel (demo-user / DemoTest123!) → mic FAB visible → records voice memo → POSTs to laptop.

### Then transcribe on your laptop

```bash
cd /home/m/development/DatingApp
source .venv/bin/activate
python3 scripts/process-feedback.py --watch 600 \
  --base-url https://fastdev.tail45c6a7.ts.net \
  --model base \
  --gh-issue best-koder-ever/DatingApp-Feedback   # optional, requires gh CLI authed
```

### Optional follow-ups (not blocking)

- [ ] **Audio retention policy** — currently keeps `BotService/Data/UserFeedback/*.m4a` forever. Add a nightly job in bot-service to delete files older than 30 days (keep transcript row).
- [ ] **Crash/error capture** — attach last 50 log lines + current route name alongside voice memos.
- [ ] **Phone-side test** — record real speech via the mic FAB on a real Android phone (not just curl).
- [ ] **Onboard 2-3 real testers** — Keycloak fix is done; pipeline is ready.
- [ ] **Persist Keycloak overrides in dev compose** — if you stop running `start-keycloak-tunnel.sh` after every infra restart, edit `docker-compose.yml` keycloak service env to include `KC_HOSTNAME`/`KC_HOSTNAME_STRICT`/`KC_PROXY_HEADERS` permanently. Side-effect: all local dev tokens get the funnel iss. Backend service `ValidIssuers` configs may need the funnel URL added (currently only YARP has it).

### Useful inspection commands

```bash
# Tunnel status
tailscale funnel status

# Service health through tunnel
curl -sS https://fastdev.tail45c6a7.ts.net/health

# Inspect feedback queue
curl -sS https://fastdev.tail45c6a7.ts.net/api/userfeedback?pageSize=20 | python3 -m json.tool

# Verify Keycloak issuer (should be funnel URL, not localhost)
curl -sS https://fastdev.tail45c6a7.ts.net/auth/realms/DatingApp/.well-known/openid-configuration | python3 -c "import sys,json; print(json.load(sys.stdin)['issuer'])"

# Re-apply Keycloak hostname overrides after infra restart
./scripts/start-keycloak-tunnel.sh
```

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
- [ ] **PR cleanup**: open PR `feature/keycloak-auth-updates` → `004-multi-app-architecture`.
- [x] Tag `mvp-005-insight-v1` — DONE this session (all 4 repos).

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

# TODO for Tomorrow (2026-05-13)

## Feedback FAB Rewrite
- [x] All widget tests pass (feedback_fab_test.dart)
- [x] Static analysis complete (only warnings, no blocking errors)
- [ ] Commit all staged changes using ./ai-commit-helper.sh or ./gita-workflow.sh
- [ ] Push to remote and verify CI

## Next Steps
- [ ] Address analysis warnings (optional, mostly info/unrelated)
- [ ] Review UAT swipe-service contract blocker (see /memories/repo/uat-findings-2026-05-07.md)
- [ ] Clean up debug prints/logs before release
- [ ] Update documentation if workflows or endpoints change

## Notes
- All feedback FAB code is verified and ready for commit.
- No HTTP bypasses or security issues found in audit.
- Watcher polling interval is safe (150s, under YARP rate limit).

---
Session state saved. Resume from here tomorrow.
