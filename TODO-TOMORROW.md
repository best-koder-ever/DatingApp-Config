# TODO — Current State

**Updated**: 2026-05-07
**MVP Progress**: MVP-Demo v0.1 — real-time match notifications + REST→SignalR message broadcast wired
**GitHub**: 0 open issues, 0 open PRs on fork
**Last Commits**:
- messaging-service `a35f0a5` (origin/main) — broadcast MessageReceived via SignalR on REST send
- MatchmakingService `bdedc98` (feature/keycloak-auth-updates) — Hub joins user_{profileId} group so MatchCreated reaches Flutter
- bot-service `d3815cd` (feature/bot-service-improvements) — warn-log when keycloak-id resolution fails

---

## ✅ MVP-Demo v0.1 Wiring — DONE

### B1 — Live match notifications (FIXED)
`MatchmakingHub` now joins both `user_{keycloakId}` AND `user_{profileId}` groups on connect (resolves profileId via UserService `/api/profiles/me`). `NotificationService` broadcasts to `user_{profileId}` and Flutter's existing `MatchCreated` listener (`main_app.dart:136`) now receives the event and renders the "It's a Match!" dialog.
**Tests**: 200/200 MatchmakingService green. Commit `bdedc98`.

### B5 — REST message broadcast (FIXED)
`SendMessageHandler` now injects optional `IHubContext<MessagingHubSpec>` and broadcasts `MessageReceived` to receiver + sender after persist. Bot REST sends now reach Flutter without reload. Try/catch ensures persist succeeds even if hub broadcast fails.
**Tests**: 3 new + 132 existing pass. Commit `a35f0a5`.

### B2 — keycloak-id silent fail (HARDENED)
`DatingAppApiClient.GetKeycloakIdForProfileAsync` now logs structured `LogWarning` for null result and missing `keycloakId` (was silent skip). UserService endpoint `GET /api/UserProfiles/{id}` returns `KeycloakId` correctly.
**Tests**: 298/298 BotService green. Commit `d3815cd`.

### B4 — Photo URLs in match payload (VERIFIED)
`MatchmakingService/Controllers/ProfilesController.cs:176-177` already includes `photoUrl` and `photoUrls`. No change needed.

### Smoke test
All 6 backend services boot cleanly with new code. Health endpoints all green. MM logs show normal bot-bot match creation.

### Pending v0.1 acceptance
- ⏳ Live Flutter UAT on device (signup → wizard → swipe bot → "It's a Match!" → bot replies in chat)
- ⏳ Tag `mvp-demo-v0.1` post-UAT
- ⏳ B3 profile sync (deferred)

---

## ✅ P0 DONE — All Test Failures Fixed

**676/676 tests pass** (was 597/636). All 39+ failures resolved in commit `69bd1e7`.

---

## ⏳ NEXT SESSION PRIORITIES

### P1 — Device Verification of Fixes
Verify on physical device that past bug fixes (from Copilot agent PRs) actually work:
1. Verification code screen overflow (was #9)
2. Auth-required badge on Matches tab (was #10)
3. Bottom buttons cut off in onboarding (was #11)
4. Discover filter icon functionality (was #12)

### P2 — Post-Onboarding E2E Testing (needs backend running)
1. **Discover → Like → Match → Chat** — need test data seeded, verify full flow
2. **Photo upload E2E** — verify photos visible in wizard + profile
3. **Chat moderation UX** — safety agent amber warning on device

### P3 — Missing Features
1. **Push notifications** — no Firebase Cloud Messaging integrated yet
2. **Geolocation** — location_permission screen exists but no actual location service
3. **Error boundary** — no global error handling / crash reporting
4. **Phase 002 Wave 2** — Matchmaking Intelligence Agent, Profile Enhancement Agent

---

## ✅ DONE (Mar 20)

### Fixed All 39+ Remaining Test Failures → 676/676 Green
Root causes:
- `bySemanticsLabel` → `byWidgetPredicate` (21 files)
- Viewport resize for tall screens (selfie, photo, settings, home filter)
- `pumpAndSettle` → `pump(Duration)` for async screens
- `HttpOverrides.global` → `.current` (Dart 3.8 breaking change)
- `settings_screen_test` syntax corruption from PR #94 repaired
- `url_launcher` mock for Rate Us snackbar test
- Navigation route transition pump patterns
- Platform channel mocks (secure storage, shared prefs)
- Manual scroll-and-pump for off-screen ListView items

### Commit: `69bd1e7` pushed to fork/main

---

## ✅ DONE (Mar 19) — Fixed 52 UC Widget Tests

### Commit: `08bd073` pushed to fork/main

---

## ✅ DONE (Mar 18) — Device Walkthrough + Visual QA

### 72 screenshots, 4 bugs filed (#9-#12), PRs #100-#103 merged
