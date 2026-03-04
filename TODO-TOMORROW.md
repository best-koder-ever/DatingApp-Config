# TODO — Current State

**Updated**: 2026-03-04
**MVP Progress**: ~85% (17/17 onboarding screens wired, backends healthy, UI polished)

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

### Backend Verification
12. **6/7 services running** — UserService(:8082), MatchmakingService(:8083), MessagingService(:8086), SwipeService(:8087), SafetyService(:8088), YARP(:8080)
13. **PhotoService(:8085) unhealthy** — returns HTTP 404 on health check, needs investigation (runs on port but bad routes?)

---

## ⏳ NEXT PRIORITIES

### P0 — Must Do for MVP
1. **T021: Integration test for onboarding wizard** — gets US1 85%→100%. Use `onboarding_test_helper.dart` harness.
2. **PhotoService health check** — diagnose why it returns 404 (startup? route config? missing migrations?)
3. **i18n: 10 screens have hardcoded English** — aboutme, interests, lifestyle, orientation, match_preferences, relationship_goals, gender, age_range, location, notifications

### P1 — Should Do
4. **Visual walkthrough on emulator** — deploy APK, confirm all 17 screens look right on Pixel 6 API 33
5. **Remaining MVP tasks**: T004 CI/CD, T041 messaging E2E, T051 privacy test, polish
6. **Photo upload E2E** — photos uploaded to PhotoService then referenced in wizard step 3

### P2 — Phase 002 Awareness
7. **Phase 002 (Agentic AI) specs exist** — `specs/002-agentic-ai/SCOPE.md` + 6 feature files
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

## Key Files
- **Onboarding coordinator**: `lib/providers/onboarding_coordinator.dart` (17 steps)
- **Onboarding data model**: `lib/providers/onboarding_data.dart` (5 payloads)
- **API service**: `lib/services/onboarding_api_service.dart` (PATCH /api/wizard/step/1-5)
- **Test harness**: `test/helpers/onboarding_test_helper.dart`
- **Widget tests**: `test/screens/wizard/first_name_screen_test.dart` (11 tests)
