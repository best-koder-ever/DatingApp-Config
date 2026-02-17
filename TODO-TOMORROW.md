# TODO — Current State (2026-02-18)

## ✅ Completed Today (2026-02-18)
- **Voice Prompt: Hinge-style UX simplification** — removed preview/re-record step. Now: tap mic → recording → tap stop → auto-upload → done. 3-phase state machine (idle/recording/uploading). Committed `c267abe` (Flutter).
- **Voice Prompt: Whisper.net async moderation pipeline** — background service polls AUTO_APPROVED prompts every 30s, transcribes via Whisper.net, scans text for policy violations (phone numbers, emails, social media handles, hate speech, explicit content). Committed `402c136` (photo-service).
- **Voice Prompt: Report endpoint** — `POST /api/voice-prompts/report/{userId}` with reason validation, duplicate prevention, PENDING_REVIEW escalation. VoicePromptReport entity + DB config.
- **44 new backend tests** — 17 VoicePromptsController tests (upload validation, CRUD, report, moderation filtering) + 27 VoicePromptModerationService tests (text violation detection). All green.
- **6 Flutter widget tests** — VoicePromptScreen idle state rendering. All green.
- **Documentation** — `VOICE_PROMPT_MODERATION.md` in photo-service.
- **Flutter analyze** — 0 errors, 0 warnings (only pre-existing info hints).

## ✅ Previously Completed
- All onboarding wizard screens (16 steps, all wired to backend)
- Discovery with Hinge-style scrollable cards + SwipeService
- Match + Chat via SignalR (typing indicators, live read receipts)
- Photo upload with 4-tier privacy + ML.NET moderation
- l10n: English + Swedish (304+ keys, all screens)
- E2E journey test (17 tests, 5 phases)
- SMS auth (Firebase → Keycloak token exchange)
- Voice prompt recording/playback/upload
- Face verification service + tests
- Daily picks system + tests
- Profile detail screen (570 lines, Hinge-style)

## 📊 Current Position: ~96% through MVP

### Test Counts (Updated)
| Service | Tests | Status |
|---------|-------|--------|
| UserService | 173 | ✅ |
| MatchmakingService | 168 | ✅ |
| PhotoService | 126 (123+3 skip) | ✅ |
| SwipeService | 103 | ✅ |
| MessagingService | 90 | ✅ |
| Flutter E2E | 17 | ✅ |
| Flutter Widget | 6 | ✅ |
| **Total** | **683** | **All green** |

## 🎯 Tomorrow's Plan (Priority Order)

### 1. EF Core Migration for VoicePromptReport (HIGH, 15 min)
The new `VoicePromptReport` entity needs an actual DB migration.
The InMemory tests pass but MySQL needs the migration applied.
```bash
cd photo-service
dotnet ef migrations add AddVoicePromptReports
dotnet ef database update
```

### 2. Docker: Add ffmpeg to photo-service Dockerfile (HIGH, 10 min)
Whisper moderation pipeline needs ffmpeg for m4a → WAV conversion.
Add `apt-get install -y ffmpeg` to the Dockerfile's runtime stage.
Also add `models/` to `.dockerignore` — the ggml-base.bin (142MB) is
downloaded at runtime, not baked into the image.

### 3. Test SMS Login on Android Device (HIGH, 30 min)
- Firebase phone auth only works on Android/iOS (not Linux desktop)
- Connect phone via USB, `flutter run` on physical device
- Test full: phone entry → SMS → verify code → onboarding → discover
- This is THE remaining blocker for "MVP works end-to-end on real device"

### 4. Voice Prompt Playback in Discovery (MEDIUM, 45 min)
Voice prompts can be recorded + uploaded + moderated, but the discovery
card doesn't play them yet. Need:
- Add play button to `ProfileCard` widget when voice prompt exists
- Call `GET /api/voice-prompts/audio/{userId}` via VoicePromptService
- Audio playback with `just_audio` or the existing record plugin's player

### 5. Voice Prompt in Profile Detail Screen (MEDIUM, 30 min)
The profile detail screen (570 lines) should show/play the voice prompt.
Add a voice prompt section between photos and bio.

### 6. Appsettings: VoiceModeration Config (LOW, 5 min)
Add VoiceModeration config block to `appsettings.Development.json`:
```json
"VoiceModeration": {
  "Enabled": true,
  "PollIntervalSeconds": 30
}
```

### 7. Clean Warnings (LOW, 15 min)
- ~20 unnecessary `!` assertions from l10n wiring
- `withOpacity` → `.withValues()` deprecation
- Cosmetic only, no functional impact

### 8. Post-MVP Features (DEFERRED)
- Google/Apple Sign-In
- Verification flow (settings_screen L48)
- Privacy/location settings screens
- Help screen, Rate app
- Sparks/Spotlight premium features
- DejTing Plus subscription

## 🏗️ Architecture
- **Backend**: .NET 8 — UserService, MatchmakingService, SwipeService, MessagingService, PhotoService
- **Auth**: Keycloak OIDC + Firebase Phone SMS
- **Gateway**: YARP (dejting-yarp)
- **Client**: Flutter 3.32.1 + Dart 3.5 (Android/iOS/Linux)
- **Real-time**: SignalR (messaging hub)
- **Moderation**: Whisper.net (voice), ML.NET (photos), regex+blocklist (text)
- **l10n**: English (en) + Swedish (sv), ARB-based
- **Permissions**: permission_handler ^12.0.1

## 📝 Git Status (All repos pushed, all clean)
| Repo | Latest Commit | Status |
|------|--------------|--------|
| photo-service | `402c136` moderation pipeline + tests | ✅ pushed |
| Flutter | `c267abe` Hinge-style flow + widget tests | ✅ pushed |
| dejting-yarp | `eb4d0dd` voice-prompts route | ✅ pushed |
| DatingApp root | `914ddfb` submodule pointers | ✅ pushed |
| UserService | `1c08d7f` metrics | ✅ pushed |
| MatchmakingService | `6e533d3` daily pick tests | ✅ pushed |
| SwipeService | `00fb597` metrics | ✅ pushed |
| MessagingService | `63c1fb3` typing indicators | ✅ pushed |
