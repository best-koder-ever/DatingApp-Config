# TODO — Current State (2026-02-17)

## ✅ Recently Completed
- Profile Detail Screen (570 lines, Hinge-style) — committed `71059ad`
- Navigation wiring: Discover tap, Matches long-press, Chat avatar tap
- Chat read receipts polish (single ✓ sent, double ✓✓ coral for read)
- Renamed TinderLikeProfileScreen → EditProfileScreen — committed `9e11b3c`
- **Fixed SMS login route mismatch** — `/onboarding/phone` vs `/onboarding/phone-entry` — committed `fe6937f`
- **Fixed Firebase crash on Linux desktop** — DevMode bypass for non-mobile
- **Added Email screen** to onboarding wizard (17-step flow now)
- FaceVerificationServiceTests (19 tests), DailyPickStrategyTests (16), DailyPickGenerationServiceTests (20)
- All backend tests green: photo-service 82/82, MatchmakingService 168/168

## 📊 Current Position: ~80% through MVP

### Auth Flow (SMS + Firebase)
- ✅ Phone entry screen (+46 Sweden default, country picker)
- ✅ SMS code verification (6-digit, auto-advance, resend timer)
- ✅ Firebase → Keycloak token exchange
- ✅ Desktop DevMode bypass (skip Firebase on Linux/macOS/Windows)
- ✅ Email collection step (after phone verify, before community guidelines)
- ⚠️ Google/Apple Sign-In buttons show "Coming soon" — placeholders only

### Onboarding Wizard (17 steps)
1. Phone Entry → 2. SMS Verify → 3. **Email** → 4. Community Guidelines →
5. First Name → 6. Birthday → 7. Gender → 8. Orientation →
9. Match Preferences → 10. Relationship Goals → 11. Lifestyle →
12. Interests → 13. About Me → 14. Photos → 15. Location →
16. Notifications → 17. Complete

### Core User Stories
1. ✅ Register → 17-screen onboarding wizard
2. ✅ Discover → drag-to-swipe with offline cache
3. ✅ Match + Chat → SignalR with offline queue
4. ✅ Safety → block/report + photo privacy

## 🎯 Next Tasks (Priority Order)

### 1. Test SMS Login on Android Device (HIGH)
- Firebase phone auth only works on Android/iOS (not Linux desktop)
- Get phone authorized for USB debugging (device R5CY74F6MFV)
- Test full flow: phone entry → SMS → verify code → email → onboarding

### 2. Chat Polish (MEDIUM — backend exists, Flutter partially wired)
- Read receipts: backend `POST /api/messages/{messageId}/read` exists
- Typing indicators: SignalR hub supports it
- Wire remaining features into `enhanced_chat_screen.dart`

### 3. Error Handling / l10n (MEDIUM)
- `l10n.yaml` exists but strings are hardcoded throughout Flutter
- Need systematic error messages

### 4. E2E Journey Tests (LOWER for now)
- Signup → match → chat → block flow untested end-to-end

## 📈 Test Counts
| Service | Tests |
|---------|-------|
| UserService | 173 |
| MatchmakingService | 168 |
| SwipeService | 103 |
| MessagingService | 90 |
| PhotoService | 82 |
| **Total** | **616** |

## 🏗️ Architecture
- **Backend**: .NET 8 — UserService, MatchmakingService, SwipeService, MessagingService, PhotoService
- **Auth**: Keycloak OIDC + Firebase Phone SMS
- **Gateway**: YARP (dejting-yarp)
- **Client**: Flutter 3.32.1 + Dart 3.5 (Android/iOS/Linux)
- **Real-time**: SignalR (messaging hub)
