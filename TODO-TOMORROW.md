# TODO — Current State

**Updated**: 2026-03-04 (afternoon)
**MVP Progress**: ~90% (all 17 screens wired, 7/7 backends healthy, i18n started, test suite solid)

---

## ✅ COMPLETED (Today — Mar 4)

### Flutter Onboarding Polish (commits b3a6703, 0358872)
1. **All 17 wizard screens wired** — phone-entry → verify-code → community-guidelines → first-name → birthday → gender → orientation → match-preferences → age-range → relationship-goals → lifestyle → interests → about-me → photos → location → notifications → complete
2. **Next button standardized** — all screens: coral `0xFFFF6B6B`, disabled grey, height 54, borderRadius 27
3. **Abort (X) button** — added to lifestyle, interests, aboutme AppBars (was missing)
4. **Orientation combos rewrite** — proper multi-select with "Prefer Not To Say" toggle
5. **AgeRangeScreen** — fully rewritten with white background + RangeSlider
6. **first_name crash fix** — infinite width in Column resolved
7. **Welcome screen** — rewritten with clean split layout
8. **Phone/SMS hardening** — input validation, error handling, async safety
9. **Test harness + 11 widget tests** — `onboarding_test_helper.dart` + `first_name_screen_test.dart` all passing
10. **Analyzer status** — 0 errors, 0 warnings, 10 info-level issues only

### toAboutMePayload() Investigation
11. **Not a bug** — Flutter already sends `interests` as `List<String>` (proper JSON array). Backend `UpdateWizardStepHandler.cs` has defensive `.SelectMany()` normalizer at lines 137-143 that handles both arrays and comma-separated strings.

### T021: Integration Tests (commit 19ec20c)
12. **82 tests passing** — OnboardingCoordinator (14), OnboardingData (27), 6 screen widget tests (41 total)
13. **Test coverage**: coordinator navigation, data model validation, all wizard screen rendering

### i18n: Safe UI Strings (commit 3221946)
14. **25 new l10n keys added** to `app_en.arb` — 9 orientation descriptions, 3 lifestyle titles, 3 aboutme titles, 7 interest categories, 1 counter
15. **7 screens wired** — orientation, gender, match_preferences, age_range, lifestyle, interests, aboutme
16. **Swedish locale**: 34 keys pending translation (expected)

### PhotoService Health Fix (commit 4d7a0c9)
17. **Root cause**: HealthController used `/api/health` route, but YARP healthCluster probes `/health`
18. **Fix**: Added `builder.Services.AddHealthChecks()` + `app.MapHealthChecks("/health")` to Program.cs
19. **Result**: 7/7 services now return HTTP 200 on `/health` — all healthy

---

## ⏳ NEXT PRIORITIES

### P0 — Must Do for MVP
1. **Visual walkthrough on emulator** — deploy APK, confirm all 17 screens look right on Pixel 6 API 33
2. **Photo upload E2E** — photos uploaded to PhotoService then referenced in wizard step 3
3. **i18n: remaining ~130 API-value strings** — need mapping strategy (English values for backend, localized for display)

### P1 — Should Do
4. **T004 CI/CD pipeline** — GitHub Actions for build + test
5. **T041 messaging E2E** — SignalR message delivery test
6. **T051 privacy test** — GDPR compliance checks
7. **Swedish translations** — fill in 34 pending keys in `app_sv.arb`

### P2 — Phase 002 Awareness
8. **Phase 002 (Agentic AI) specs exist** — `specs/002-agentic-ai/SCOPE.md` + 6 feature files
   - Wave 1: Agent Gateway + Safety Agent (~6 weeks, requires T200-T204, T210-T213)
   - Wave 2: Photo Coach Agent (~4 weeks)
   - Wave 3: Conversation Coach Agent (~4 weeks)
   - Wave 4: Smart Match Agent (~8 weeks)
   - **Blocked on**: MVP core loop completion (Phase 001)
   - **Status**: brainstorming → planning, no code yet

---

## Architecture Quick Reference
- **Ports**: YARP(:8080), UserService(:8082), MatchmakingService(:8083), PhotoService(:8085), MessagingService(:8086), SwipeService(:8087), SafetyService(:8088)
- **Infra**: Keycloak(:8090), MySQL DBs (3308-3312), Keycloak-db (5432 Postgres)
- **Emulator**: DatingApp_Pixel6_API33 on emulator-5554
- **Brand color**: `Color(0xFFFF6B6B)` (coral)
- **Docker context**: `default` (not docker-desktop)
- **All services healthy**: 7/7 returning 200 on /health ✅

## Key Files
- **Onboarding coordinator**: `lib/providers/onboarding_coordinator.dart` (17 steps)
- **Onboarding data model**: `lib/providers/onboarding_data.dart` (5 payloads)
- **API service**: `lib/services/onboarding_api_service.dart` (PATCH /api/wizard/step/1-5)
- **Test harness**: `test/helpers/onboarding_test_helper.dart`
- **Widget tests**: `test/screens/wizard/first_name_screen_test.dart` (11 tests)
- **ARB file**: `lib/l10n/app_en.arb` (~385 keys, 25 new today)
