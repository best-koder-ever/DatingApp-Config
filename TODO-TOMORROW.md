# TODO — Current State (2026-02-17)

## ✅ Recently Completed
- Profile Detail Screen (570 lines, Hinge-style) — committed `71059ad`
- Navigation wiring: Discover tap, Matches long-press, Chat avatar tap
- Renamed TinderLikeProfileScreen → EditProfileScreen — committed `9e11b3c`
- **Fixed SMS login route mismatch** — `/onboarding/phone` vs `/onboarding/phone-entry` — committed `fe6937f`
- **Fixed Firebase crash on Linux desktop** — DevMode bypass for non-mobile
- **Chat Polish: Typing Indicators** — backend hub method + Flutter service + animated dots UI — committed `63c1fb3` + `db83495`
- **Chat Polish: Live Read Receipts** — readReceiptStream in MessagingService, live checkmark updates (✓ → ✓✓ coral) — committed `db83495`
- Email screen attempted then reverted (phone-only for MVP) — committed `ab6f4b1`
- FaceVerificationServiceTests (19 tests), DailyPickStrategyTests (16), DailyPickGenerationServiceTests (20)
- All backend tests green: photo-service 82/82, MatchmakingService 168/168
- **l10n: English + Swedish (304+ keys, ALL screens wired)** — committed `1a5de9e` + `cf0b78f`
  - Expanded app_en.arb from ~70 to 304+ keys (auth, onboarding, discovery, chat, matches, profile, settings, verification, errors)
  - Created app_sv.arb with complete Swedish translations
  - ALL 25/26 screen files use AppLocalizations (account_consent_screen excluded — has own inline translations map)
- **E2E Journey Test (17 tests, 5 phases)** — committed `fbf5b95`
  - Phase 1: Onboarding (Alice + Bob register via Keycloak)
  - Phase 2: Discovery/Matching (mutual swipe → match)
  - Phase 3: Messaging (send/receive/conversation list)
  - Phase 4: Safety (block/unblock flow)
  - Phase 5: Edge cases (token refresh, swipe history)
- **Swipe API wired** — `_likeProfile` calls `SwipeService.swipe(isLike: true)` with match dialog, `_passProfile` sends pass (fire-and-forget) — committed `68b1278`
- **Logout wired** — `AppState().logout()` clears tokens before navigation — committed `68b1278`
- **Permissions wired** — `permission_handler` for location + notification real OS prompts — committed `68b1278`
- **Stale TODOs cleaned** — removed 3 misleading "Save to profile" comments in wizard screens — committed `68b1278`

## 📊 Current Position: ~95% through MVP

All core features are wired to backend APIs. No functional stubs remain for MVP flows.

### Auth Flow (SMS + Firebase)
- ✅ Phone entry screen (+46 Sweden default, country picker)
- ✅ SMS code verification (6-digit, auto-advance, resend timer)
- ✅ Firebase → Keycloak token exchange
- ✅ Desktop DevMode bypass (skip Firebase on Linux/macOS/Windows)
- ✅ Proper logout with token clearing
- ⚠️ Google/Apple Sign-In buttons show "Coming soon" — placeholders only (post-MVP)

### Onboarding Wizard (16 steps) — ALL WIRED
1. Phone Entry → 2. SMS Verify → 3. Community Guidelines →
4. First Name → 5. Birthday → 6. Gender → 7. Orientation →
8. Match Preferences → 9. Relationship Goals → 10. Lifestyle →
11. Interests → 12. About Me → 13. Photos → 14. Location →
15. Notifications → 16. Complete (submits 3-step PATCH to UserService)

### Core User Stories — ALL FUNCTIONAL
1. ✅ Register → 16-screen onboarding wizard (profile creation via 3-step PATCH)
2. ✅ Discover → Hinge-style scrollable cards, SwipeService with retry + idempotency
3. ✅ Match + Chat → SignalR with offline queue + typing indicators + live read receipts
4. ✅ Safety → block/report + photo privacy
5. ✅ l10n → English + Swedish, ARB-based, 304+ keys, ALL screens wired
6. ✅ E2E tests → full journey coverage (17 tests)
7. ✅ Photo upload → multipart POST to photo-service in wizard + standalone
8. ✅ Permissions → real OS permission prompts for location + notifications

## 🎯 Remaining Work (Priority Order)

### 1. Test SMS Login on Android Device (HIGH)
- Firebase phone auth only works on Android/iOS (not Linux desktop)
- Get phone authorized for USB debugging
- Test full flow: phone entry → SMS → verify code → onboarding

### 2. Android Permission Config (MEDIUM)
- `permission_handler` added but Android manifest entries may need `<uses-permission>` tags
- Location: `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`
- Notifications: `POST_NOTIFICATIONS` (Android 13+)

### 3. Clean warnings (LOW)
- ~20 unnecessary `!` assertions from l10n wiring (cosmetic)
- `withOpacity` deprecation warnings (use `.withValues()`)

### 4. Post-MVP Features (DEFERRED)
- Google/Apple Sign-In
- Voice prompt audio playback (home_screen L734)
- Verification flow (settings_screen L48)
- Privacy/location settings screens
- Help screen, Rate app
- Sparks/Spotlight premium features
- DejTing Plus subscription

## 📈 Test Counts
| Service | Tests |
|---------|-------|
| UserService | 173 |
| MatchmakingService | 168 |
| SwipeService | 103 |
| MessagingService | 90 |
| PhotoService | 82 |
| Flutter E2E | 17 |
| **Total** | **633** |

## 🏗️ Architecture
- **Backend**: .NET 8 — UserService, MatchmakingService, SwipeService, MessagingService, PhotoService
- **Auth**: Keycloak OIDC + Firebase Phone SMS
- **Gateway**: YARP (dejting-yarp)
- **Client**: Flutter 3.32.1 + Dart 3.5 (Android/iOS/Linux)
- **Real-time**: SignalR (messaging hub)
- **l10n**: English (en) + Swedish (sv), ARB-based, flutter_localizations
- **Permissions**: permission_handler ^12.0.1
