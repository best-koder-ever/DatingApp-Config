# TODO — Current State

**Updated**: 2026-03-07
**MVP Progress**: ~92% (all 17 screens wired + dark-themed, 7/7 backends healthy, i18n started, profanity filter added)

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
10. **Analyzer status** — 0 errors, 0 warnings, info-level issues only

### toAboutMePayload() Investigation
11. **Not a bug** — Flutter already sends `interests` as `List<String>` (proper JSON array). Backend `UpdateWizardStepHandler.cs` has defensive `.SelectMany()` normalizer at lines 137-143.

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

### Dark Theme Overhaul (evening session)
20. **`lib/theme/app_theme.dart`** — full dark premium ThemeData created (coral→purple gradient brand, dark navy surfaces)
21. **All 17 wizard screens dark-themed** — batch-replaced all hardcoded colors (`Colors.white`, `Colors.black`, `Colors.grey[xxx]`, `Color(0xFFFF6B6B)`) with AppTheme constants across all screen files
22. **Key colors**: primaryColor=#FF7F50 (coral), scaffoldDark=#0D0D1A, surfaceColor=#1A1A2E, surfaceElevated=#252540, dividerColor=#2A2A45, textPrimary=white, textSecondary=70% white, textTertiary=40% white
23. **Birthday screen rewrite** — DD/MM/YYYY in single Row (flex 1:1:2), 3-letter month abbreviations (Jan/Feb/Mar), hintText instead of floating labels, removed age display
24. **Gender checkbox visibility** — dark background + explicit `BorderSide(color: textSecondary, width: 2)` for visible unchecked state
25. **SMS digit boxes fix** — changed from fixed `width: 48` to `Expanded + AspectRatio(0.85)` + `contentPadding: EdgeInsets.zero`, 4px spacing
26. **DevMode "Skipped Keycloak" snackbar removed** from sms_code_screen.dart

### Profanity Filter
27. **`lib/utils/profanity_filter.dart`** — reusable client-side name filter with ~80 blocked words (English profanity/slurs/extremism + Swedish equivalents)
28. **Two-layer matching**: exact match (all words) + substring match (≥4 char words only, avoids "Kassandra" false positive from "ass")
29. **Wired into first_name_screen.dart** — red error text ("This name is not allowed"), red underline, Next button disabled on offensive names
30. **l10n key `nameNotAllowed`** added to both `app_en.arb` and `app_sv.arb`

---

## 🔴 UNCOMMITTED CHANGES
- None — all committed and pushed ✅

---

## ⏳ NEXT SESSION PRIORITIES

### P0 — Must Do for MVP
1. **Git commit all pending changes** — dark theme + profanity filter + screen fixes (FIRST THING!)
2. **Continue emulator walkthrough** — screens 7-17 not yet eyeballed:
   - Orientation, Relationship Goals, Interests, Lifestyle, About Me, Photos, Age Range, Match Preferences, Location Permission, Notification Permission, Onboarding Complete
   - Fix any visual issues found
3. **Photo upload E2E** — photos uploaded to PhotoService then referenced in wizard step 3

### P1 — Content Moderation: "Are You Sure?" Nudge + Server Gate

#### ✅ COMPLETED (Mar 7) — Client-Side Normalizer v2
- **`lib/utils/profanity_filter.dart`** — 5-step normalization pipeline: lowercase → accent strip → de-leet/homoglyph (60+ mappings) → strip separators → collapse repeated letters
- **Now catches**: leet-speak (sh1t, f4ck, @ss), double letters (Fukkboy, fuuuck), separators (f.u.c.k), Cyrillic homoglyphs, fullwidth Latin, accented chars (shït, bîtch)
- **40 tests passing** — `test/utils/profanity_filter_test.dart`, EN + SV blocklists
- **Key Dart gotcha**: `String.replaceAll` doesn't support `$1` backreferences — must use `replaceAllMapped`
- **Committed**: `8df64c9`, pushed to remote

#### 🔜 NEXT: Client "Are You Sure?" Nudge (Hinge-style)
- Wire `ProfanityFilter.isOffensive()` into chat message composer
- On flagged message → show bottom sheet: *"This message may be hurtful. Want to edit it?"*
- Two buttons: **Edit** / **Send Anyway**
- If "Send Anyway" → send with metadata flag `{ "user_overrode_warning": true }` for server-side trust scoring
- **Effort**: ~2 hours | **Value**: High — instant UX friction, 50% reduction in offensive messages (Hinge's published stat)

#### 🔜 NEXT: Server-Side Moderation Gate (3 Options Evaluated)

| Option | Cost | RAM/CPU | Latency | Accuracy | Vendor Lock-in | Best For |
|--------|------|---------|---------|----------|----------------|----------|
| **1. Our ProfanityFilter only** | $0/mo | 0 (client) | 0ms | Word-level only, no context | None | Names, bios, 90% of chat |
| **2. OpenAI Moderation API** | $0/mo (free!) | 0 (their servers) | 100-300ms | GPT-level semantic understanding | Medium — US data, could change terms | MVP → 10K users |
| **3. Detoxify (self-hosted)** | $20-40/mo VPS | 1.5-2GB RAM, 100-200ms/inference on CPU | 100-200ms | BERT-level (93-98% AUC) | None — runs on your infra | 10K+ users, zero vendor dependency |

**Decision**: Option 1 (done ✅) + Option 2 for MVP. Upgrade to Option 3 when revenue justifies $20-40/mo hosting.

**Key research findings (Mar 7)**:
- ⚠️ **Perspective API is SUNSETTING** — end of December 2026. Do NOT build on it.
- ✅ **OpenAI Moderation API** — free, handles text+images, categories: hate/harassment/sexual/violence/self-harm. Their usage policy explicitly encourages this use case ("We give developers moderation tools").
- ❌ **Detoxify** — requires PyTorch (~2GB) + model weights (~500MB-1.1GB) = ~2-3GB RAM. BERT/RoBERTa/XLM-R base models. Cold start 5-30 seconds. Not serverless-friendly. Overkill for MVP.
- 📝 **profanity_filter (Dart, pub.dev)** — uses LDNOOBW wordlists but has NO leet-speak normalization. Our custom filter is strictly better.
- 📝 **better-profanity (Python)** — has leet normalization (we ported its CHARS_MAPPING to Dart), but can't defeat double-letter evasion. Stale (5yr).
- 📝 **LDNOOBW** — 28-language wordlists, CC-BY-4.0, 3.3K stars. Good baseline source.

**Privacy note**: OpenAI Moderation API sends user messages to US servers. Needs GDPR Data Processing Agreement if targeting EU users. Acceptable for MVP, revisit at scale.

**How other apps do it**:
- **Hinge**: Client-side ML classifier → "Are you sure?" bottom sheet → silent server-side flag if sent anyway
- **Bumble**: Server-side AI → blurs message on recipient side with warning → recipient chooses to reveal or report
- **Tinder**: Server-side NLP after delivery → recipient sees "Does this bother you?" → sender gets no warning (anti-gaming)

### P2 — Should Do
5. **i18n: remaining ~130 API-value strings** — need mapping strategy
6. **Swedish translations** — fill in 34+ pending keys in `app_sv.arb`
7. **T004 CI/CD pipeline** — GitHub Actions for build + test
8. **T041 messaging E2E** — SignalR message delivery test

### P3 — Phase 002 Awareness
9. **Phase 002 (Agentic AI) specs exist** — `specs/002-agentic-ai/SCOPE.md` + 6 feature files
   - Wave 1: Agent Gateway + Safety Agent (~6 weeks)
   - **Safety Agent scope includes**: content moderation, name filtering, photo screening → natural home for multilingual profanity

---

## Architecture Quick Reference
- **Ports**: YARP(:8080), UserService(:8082), MatchmakingService(:8083), PhotoService(:8085), MessagingService(:8086), SwipeService(:8087), SafetyService(:8088)
- **Infra**: Keycloak(:8090), MySQL DBs (3308-3312), Keycloak-db (5432 Postgres)
- **Emulator**: DatingApp_Pixel6_API33 on emulator-5554
- **Brand gradient**: coral #FF7F50 → purple #7F13EC
- **Theme**: Dark premium (`AppTheme.darkTheme` in main.dart line 82)
- **Docker context**: `default` (not docker-desktop)
- **All services healthy**: 7/7 returning 200 on /health ✅

## Key Files
- **Theme**: `lib/theme/app_theme.dart` (dark premium, all brand colors/gradients/decorations)
- **Profanity filter**: `lib/utils/profanity_filter.dart` (v2, 5-step normalizer, EN+SV)
- **Profanity tests**: `test/utils/profanity_filter_test.dart` (40 tests)
- **Onboarding coordinator**: `lib/providers/onboarding_coordinator.dart` (17 steps)
- **Onboarding data model**: `lib/providers/onboarding_data.dart` (5 payloads)
- **API service**: `lib/services/onboarding_api_service.dart` (PATCH /api/wizard/step/1-5)
- **Test harness**: `test/helpers/onboarding_test_helper.dart`
- **Widget tests**: `test/screens/wizard/first_name_screen_test.dart` (11 tests)
- **ARB file**: `lib/l10n/app_en.arb` (~386 keys, +1 nameNotAllowed today)
