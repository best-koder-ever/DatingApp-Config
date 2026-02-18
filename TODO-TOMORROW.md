# Voice Prompt Feature — Status

## ✅ COMPLETED (Today)

### Backend (photo-service) — pushed `7590f68`
1. **EF Core Migration** — `AddVoicePromptReports` migration generated
   - `voice_prompt_reports` table (reporter, reason, status, timestamps)
   - `voice_prompts` table with moderation_status index
   - Unique constraint on (voice_prompt_id, reporter_user_id)
   - User-active filtered unique index
2. **Docker ffmpeg** — Added to runtime stage for audio processing
3. **.dockerignore** — Reduces build context (excludes bin/, obj/, tests, etc.)
4. **VoiceModeration config** — `appsettings.Development.json` updated

### Flutter App — pushed `4f47208`
5. **VoicePromptPlayer widget** — Reusable `lib/widgets/voice/voice_prompt_player.dart`
   - Mic icon header, "Hear X's voice" subtitle
   - Decorative 30-bar waveform with play/stop animation state
   - Play/Stop button using VoicePromptService singleton (auth headers)
   - onDoubleTap callback for like gestures
6. **voicePromptUrl on UserProfile** — Field + constructor + fromJson
7. **ProfileDetailScreen** — Voice prompt section between bio and prompts
8. **261 warnings cleaned** — 0 warnings, 0 errors
   - AppLocalizations.of(context)! → AppLocalizations.of(context) (257 files)
   - withOpacity → withValues (profile_card, environment_selector)
   - .value → .toARGB32() (widgetbook)
   - Curly braces in flow control (profile_completion_calculator)
   - Super parameters (widgetbook)
   - Unused imports + unused variables

## ⏳ REMAINING
- **Apply EF migration** — `dotnet ef database update --context PhotoContext` (needs DB running)
- **Test SMS login on Android device** — Needs physical device
- **Post-MVP Voice Features** (deferred):
  - Voice filters/effects during recording
  - Voice prompt duration display from actual audio metadata
  - Voice prompt in match notification cards

## Architecture Notes
- Discovery screen (`HomeScreen`) already had voice playback via `_buildVoicePromptCard()`
- `ProfileDetailScreen` now also shows voice prompts when `voicePromptUrl` is available
- `VoicePromptPlayer` is the reusable widget — use it anywhere a voice card is needed
- `VoicePromptService` is the singleton for all audio playback (handles auth + streaming)
