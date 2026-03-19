# TODO — Current State

**Updated**: 2026-03-18 (late evening)
**MVP Progress**: ~97% (all screens, 7/7 backends, i18n, 710+ tests passing)

---

## ⏳ NEXT SESSION PRIORITIES

### P0 — Visual QA Automation (4 Layers) — Issues #14-#17
**Goal**: Automated visual regression testing that survives screen changes, runs in CI, needs no human.

| Layer | Issue | What | Status |
|-------|-------|------|--------|
| 1. Screen Signatures | [#14](https://github.com/best-koder-ever/mobile_dejtingapp-1/issues/14) | Python module: detect current screen from uiautomator XML content-desc text | Copilot agent |
| 2. Semantic Navigator | [#15](https://github.com/best-koder-ever/mobile_dejtingapp-1/issues/15) | State machine: tap elements by TEXT not coordinates, reactive to screen changes | Copilot agent |
| 3. Regression Detection | [#16](https://github.com/best-koder-ever/mobile_dejtingapp-1/issues/16) | UI tree diff + screenshot comparison against baselines | Copilot agent |
| 4. Dev Container | [#17](https://github.com/best-koder-ever/mobile_dejtingapp-1/issues/17) | Dockerfile with headless Android emulator + Flutter + Python | Copilot agent |

**Key design**: Reactive state machine, NOT fixed sequence. Detects current screen → looks up action → executes → repeats. Handles screen reordering/additions automatically. Text-based matching (content-desc), never pixel coordinates.

**Screen change sync strategy**:
- Layout changes → no impact (text-based detection)
- Text changes → update signature entry in signatures.py
- Screen added → add signature + action entry
- Screen removed → auto-skipped (never detected)
- Screen reordered → no impact (state machine, not sequence)

**⚠️ ACTION REQUIRED**: Assign issues #14-#17 to Copilot agent on GitHub (need to approve agent access for new issues)

### P0 — Bugs Found in Device Walkthrough (Issues Filed)
1. **[#9] Verification code screen overflow** — overflows by 73px when keyboard opens. `sms_code_screen.dart` needs `SingleChildScrollView` wrapping.
2. **[#10] "Auth required" badge on Matches screen** — dev sign-in doesn't properly set auth token for messaging service. `enhanced_matches_screen.dart` line ~66.
3. **[#11] [SYSTEMIC] Bottom buttons cut off on ALL wizard/permission screens** — no `SafeArea` wrapping, affects 6+ screens. Needs fix in shared wizard scaffold, not per-screen.
4. **[#12] Discover filter icon does nothing** — `home_screen.dart` line ~218, `onPressed: () {}` empty callback.

### P1 — Review Copilot Agent PRs
5. **8+ PRs on fork** (`best-koder-ever/mobile_dejtingapp-1`):
   - PR #5: Remove dead code `swipeProfile()`
   - PR #6: Fix analyzer warnings
   - PR #7: Widget test welcome_screen
   - PR #8: Widget test settings_screen
   - PRs from #9-#12 bug fixes (if agent picks them up)
   - PRs from #14-#17 visual QA layers (if agent picks them up)

### P2 — Post-Onboarding Testing (needs backend)
6. **Discover → Like → Match → Chat** — need test data seeded
7. **Photo upload E2E** — verify photos visible in wizard + profile
8. **Chat moderation UX** — safety agent amber warning on device

### P3 — Should Do (Unchanged)
9. **Push notifications** — no Firebase Cloud Messaging integrated yet
10. **Geolocation** — location_permission screen exists but no actual location service
11. **Error boundary** — no global error handling / crash reporting
12. **Phase 002 Wave 2** — Matchmaking Intelligence Agent, Profile Enhancement Agent

---

## ✅ DONE TODAY (Mar 18) — Full Device Walkthrough Complete + Visual QA Plan

### Device Visual QA Walkthrough — ALL SCREENS TESTED
- Connected physical Samsung device (1080x2340) via ADB
- ADB-automated screenshot capture + resize pipeline (screenshots 01-72)
- 14 UI tree XML fixtures saved (`walkthrough-screenshots/ui-trees/`)

**Wizard screens tested (17/17)**:
Welcome → Phone Entry → SMS Code → Community Guidelines → First Name → Birthday → Gender → Orientation → Match Preferences → Age Range → Relationship Goals → Lifestyle → Interests → About Me → Photos → Location Permission → Notification Permission

**Post-onboarding screens tested (9)**:
Onboarding Complete (auth error) → Discover (empty state) → Matches: New Matches → Matches: Messages → Profile: Get More (DejTing Plus) → Profile: Safety → Profile: My DejTing → Settings (full scroll) → Discover filter icon

**4 bugs found and filed**: #9 (overflow), #10 (auth badge), #11 (systemic nav bar overlap), #12 (filter no-op)

### Visual QA Automation Plan — 4 Issues Created
- #14: Screen signatures module (text-based screen detection)
- #15: Semantic navigation engine (state machine, tap by text)
- #16: Regression detection (UI tree diff + baselines)
- #17: Dev container with headless emulator

### Copilot Coding Agent
- Enabled on fork `best-koder-ever/mobile_dejtingapp-1`
- 4 issues created (#1-#4), all picked up by agent, 4 Draft PRs opened (#5-#8)
- 4 bug issues filed from walkthrough (#9-#12)
- 4 visual QA automation issues filed (#14-#17)

### Previous TODO Verification
- P1#4 MessagingHub URL toggle: already implemented in `messaging_service.dart` lines 61-66
- P2#7 Widget tests: all 8 core screens already have tests (181 passing)
- P2#8 Flutter CI: already exists (`.github/workflows/ci.yml`)
- P1#6 Wire bot-service: skipped (anti-busywork: internal tooling only, not user-facing)

---

## ✅ DONE (Mar 17) — Phase 002 Wave 1 Complete

### Shared DatingApp.Llm Library + Safety Agent + Flutter Client
- Created `shared/DatingApp.Llm/` with 3 LLM providers + circuit breaker
- `SafetyAgentService` for LLM-powered message classification
- Amber warning indicator in chat for flagged messages
- **128/128 messaging-service tests, 406/406 Flutter tests**

## ✅ DONE (Mar 16)
- Fixed 7 failing Flutter widget tests, full suite 406 passing
- Fixed 25 analyzer warnings (111→86), committed + pushed
