# Parallel Build Plan — 4 Flavors Without Conflict

> How to build Dejting, Voice, Darkness, and Oldies simultaneously without stepping on each other.

---

## The Problem

4 flavors share one Flutter codebase and 8 backend services. If 4 streams edit the same files, we get constant merge conflicts and broken builds. The solution is **shared foundation first, then isolated streams**.

---

## Architecture: Serial Foundation → Parallel Streams

```
WEEK 1-2          WEEK 3-6              WEEK 7+
─────────          ─────────              ─────────
                  ┌──── Stream A: Voice ────────────► SHIP
                  │
PHASE 0 ─────────┼──── Stream B: Darkness ──────────► SHIP
(Foundation)      │
                  ├──── Stream C: Oldies ───────────► SHIP
                  │
                  └──── Stream D: Dejting (polish) ─► CONTINUES
```

**Rule**: Phase 0 is SERIAL. Nothing else starts until it merges to main.

---

## Phase 0: Shared Foundation (SERIAL — ~8-12h)

> Everything that ALL flavors need. One branch. Merge to main before parallel work begins.

### 0A. Flutter: Expand FlavorFeatureFlags (~2h)

Add ALL 9 new flags at once (with safe defaults) so no stream needs to edit this file later:

```dart
class FlavorFeatureFlags {
  // EXISTING (unchanged)
  final int dailySwipeLimit;
  final bool showCompatibilityScores;
  final bool prominentVoicePrompts;
  final bool showProfilePrompts;
  final bool photoForwardDiscovery;

  // NEW — Voice
  final bool hidePhotosInDiscovery;   // default: false
  final int voiceAnswersRequired;     // default: 0
  final int photoRevealThreshold;     // default: 0 (disabled)

  // NEW — Darkness
  final bool privateAlbums;           // default: false
  final bool coupleProfiles;          // default: false
  final bool incognitoMode;           // default: false

  // NEW — Oldies
  final bool accessibilityMode;       // default: false
  final bool videoChatEnabled;        // default: false
  final bool dailyPicksMode;          // default: false
}
```

All defaults = `false`/`0`, so existing Dejting and Fleet configs don't break.

### 0B. Flutter: Create all 4 FlavorConfig files + entry points (~2h)

| File | Action |
|------|--------|
| `lib/flavors/hinge_config.dart` | Keep as-is (Dejting) |
| `lib/flavors/fleet_config.dart` | Rename → `darkness_config.dart`, update class name + values |
| `lib/flavors/voice_config.dart` | **New** — VoiceFlavorConfig |
| `lib/flavors/oldies_config.dart` | **New** — OldiesFlavorConfig |
| `lib/main_hinge.dart` | Keep (Dejting) |
| `lib/main_fleet.dart` | Rename → `main_darkness.dart` |
| `lib/main_voice.dart` | **New** |
| `lib/main_oldies.dart` | **New** |

Each config sets its own flags. No stream needs to create config files later.

### 0C. Flutter: Create placeholder theme files (~1h)

| File | Description |
|------|-------------|
| `lib/theme/app_theme.dart` | Already exists (Dejting coral) |
| `lib/theme/fleet_theme.dart` | Rename → `darkness_theme.dart` (deep black + neon) |
| `lib/theme/voice_theme.dart` | **New** — warm purple/indigo, skeleton |
| `lib/theme/oldies_theme.dart` | **New** — warm gold/cream, large fonts, skeleton |

Streams will flesh out themes, but the files and class names exist so imports work.

### 0D. Backend: Per-flavor config sections in appsettings (~2h)

Add `Flavors` section to all services that need it (swipe-service, MatchmakingService, photo-service):

```json
{
  "Flavors": {
    "dejting": { "DailySwipeLimit": 10, "SameFlavorBoost": 0.10 },
    "voice":  { "DailySwipeLimit": 8,  "SameFlavorBoost": 0.10 },
    "darkness": { "DailySwipeLimit": 0, "SameFlavorBoost": 0.10 },
    "oldies":  { "DailySwipeLimit": 8,  "SameFlavorBoost": 0.10 }
  }
}
```

Plus a `FlavorSettings` C# class that reads this. One implementation, all services use it.

### 0E. Backend: Register FlavorId values (~1h)

Add "voice", "darkness", "oldies" to any enum/validation that currently only knows "hinge" and "fleet".

### 0F. Tests: Verify nothing breaks (~2h)

- `flutter analyze` passes
- `flutter test` — 659+ existing pass
- `dotnet build` on all 8 services
- `dotnet test` on all services with tests
- Commit. Push. Merge to main. DONE.

**Phase 0 deliverable**: A codebase where `main_voice.dart` / `main_darkness.dart` / `main_oldies.dart` all compile and run (showing Dejting-like app with correct flags). Each stream can now diverge independently.

---

## Parallel Streams — File Ownership Matrix

> **THE RULE**: Each file has ONE owner. If two streams need to change the same file, extract a shared piece into Phase 0 instead.

### Exclusive File Ownership

| File / Area | Owner | Other streams: HANDS OFF |
|-------------|-------|--------------------------|
| `lib/flavors/voice_config.dart` | Stream A | — |
| `lib/flavors/darkness_config.dart` | Stream B | — |
| `lib/flavors/oldies_config.dart` | Stream C | — |
| `lib/theme/voice_theme.dart` | Stream A | — |
| `lib/theme/darkness_theme.dart` | Stream B | — |
| `lib/theme/oldies_theme.dart` | Stream C | — |
| `lib/main_voice.dart` | Stream A | — |
| `lib/main_darkness.dart` | Stream B | — |
| `lib/main_oldies.dart` | Stream C | — |
| `lib/screens/voice/` (new dir) | Stream A | — |
| `lib/screens/darkness/` (new dir) | Stream B | — |
| `lib/screens/oldies/` (new dir) | Stream C | — |
| `lib/widgets/voice/` (new dir) | Stream A | — |
| `lib/widgets/darkness/` (new dir) | Stream B | — |
| `lib/widgets/oldies/` (new dir) | Stream C | — |
| Backend: `Match.PhotosRevealed` | Stream A | — |
| Backend: `ProfileTags` table | Stream B | — |
| Backend: Video chat signaling | Stream C | — |

### Shared Files (touch carefully, use flags)

| File | How streams share it |
|------|---------------------|
| `FlavorFeatureFlags` | **LOCKED after Phase 0** — nobody adds flags |
| `FlavorConfig` abstract | **LOCKED after Phase 0** |
| `home_screen.dart` | Use `if (FlavorConfig.current.featureFlags.X)` branching — never change default behavior |
| `profile_card.dart` | Same — flavor-flag branching only |
| `enhanced_chat_screen.dart` | Same |
| Shared widgets | Don't modify — create new flavor-specific widgets instead |
| Backend controllers | Add new endpoints only — never modify existing endpoint behavior |
| DB migrations | **Sequential numbering** — coordinate via PR title prefix |

---

## Stream A: Voice (~40-60h)

> **Branch**: `feat/voice-flavor`
> **Dependencies**: Phase 0 only
> **Touches backend**: MatchmakingService, photo-service, messaging-service

### Work Items (ordered)

| # | Task | Effort | Files (new/modified) |
|---|------|--------|---------------------|
| A1 | Voice discovery card widget | M | `lib/widgets/voice/voice_discovery_card.dart` (NEW) |
| A2 | Silhouette placeholder for hidden photos | S | `lib/widgets/voice/silhouette_avatar.dart` (NEW) |
| A3 | Wire hidePhotosInDiscovery into home_screen | S | `home_screen.dart` (flag branch only) |
| A4 | Voice question pool — backend table + API | M | `photo-service/` — new FlavorVoiceQuestions table |
| A5 | Voice question pool — Flutter UI | M | `lib/screens/voice/voice_questions_screen.dart` (NEW) |
| A6 | Match.PhotosRevealed — backend migration + API | M | `MatchmakingService/` — Match model + migration |
| A7 | Photo API gating — hide URLs until revealed | M | `photo-service/` — PhotosController change |
| A8 | Reveal button in chat UI | M | `lib/widgets/voice/reveal_button.dart` (NEW) |
| A9 | Reveal endpoint — POST /api/matches/{id}/reveal | S | `MatchmakingService/Controllers/` |
| A10 | Onboarding: require voice answers | M | `lib/screens/voice/voice_onboarding.dart` (NEW) |
| A11 | Voice theme polish | S | `lib/theme/voice_theme.dart` |
| A12 | Tests | M | `test/screens/voice/`, `test/widgets/voice/` |

**Key risk**: The reveal mechanic (A6-A9) is the most complex piece. Build A1-A5 first to have a playable prototype early.

---

## Stream B: Darkness (~30-50h)

> **Branch**: `feat/darkness-flavor`
> **Dependencies**: Phase 0 only
> **Touches backend**: UserService, photo-service

### Work Items (ordered)

| # | Task | Effort | Files (new/modified) |
|---|------|--------|---------------------|
| B1 | Rebrand: theme deep black + neon accents | M | `lib/theme/darkness_theme.dart` |
| B2 | Rebrand: splash screen, app icon, copy | M | `lib/flavors/darkness_config.dart`, `assets/darkness/` (NEW) |
| B3 | Interest/kink tags — backend table + API | M | `UserService/` — ProfileTags model + migration |
| B4 | Interest/kink tags — Flutter tag picker UI | M | `lib/widgets/darkness/tag_picker.dart` (NEW) |
| B5 | Interest/kink tags — Discovery filtering | M | `MatchmakingService/` — tag-based filter |
| B6 | Private photo albums — backend | M | `photo-service/` — PrivateAlbum model + reveal-on-request |
| B7 | Private photo albums — Flutter UI | M | `lib/screens/darkness/private_album_screen.dart` (NEW) |
| B8 | Couple/group profiles — backend | M | `UserService/` — ProfileGroupId field |
| B9 | Couple/group profiles — Flutter UI | M | `lib/screens/darkness/couple_profile_screen.dart` (NEW) |
| B10 | Incognito mode — backend visibility flag | S | `MatchmakingService/` — discovery exclusion |
| B11 | Incognito mode — Flutter toggle | S | `lib/screens/darkness/incognito_toggle.dart` (NEW) |
| B12 | Tests | M | `test/screens/darkness/`, `test/widgets/darkness/` |

**Note**: B3-B5 (tags) is the foundation — everything else in Darkness builds on being able to express interests. Do tags first.

---

## Stream C: Oldies (~60-80h)

> **Branch**: `feat/oldies-flavor`
> **Dependencies**: Phase 0 only
> **Touches backend**: MatchmakingService, messaging-service (or new video service)

### Work Items (ordered)

| # | Task | Effort | Files (new/modified) |
|---|------|--------|---------------------|
| C1 | Accessibility theme — large fonts, high contrast | M | `lib/theme/oldies_theme.dart` |
| C2 | Simplified navigation — fewer nested screens | M | `lib/screens/oldies/oldies_home_screen.dart` (NEW) |
| C3 | Senior-specific prompts — content | S | `lib/flavors/oldies_config.dart` |
| C4 | Age-gated discovery — backend filter | S | `MatchmakingService/` — age floor config |
| C5 | Daily picks mode — curated instead of infinite | M | `MatchmakingService/` — DailyPickStrategy config |
| C6 | Simplified onboarding — fewer steps, bigger UI | M | `lib/screens/oldies/oldies_onboarding.dart` (NEW) |
| C7 | Video chat — signaling service (WebRTC/Twilio) | L | `messaging-service/Hubs/` or new service |
| C8 | Video chat — Flutter UI | L | `lib/screens/oldies/video_chat_screen.dart` (NEW) |
| C9 | Scam detection — backend heuristics | M | `safety-service/` — senior scam rules |
| C10 | Scam detection — Flutter warnings UI | M | `lib/widgets/oldies/scam_warning.dart` (NEW) |
| C11 | Verified badge emphasis — UI prominence | S | Uses existing VerificationBadge widget |
| C12 | Tests | M | `test/screens/oldies/`, `test/widgets/oldies/` |

**Key risk**: Video chat (C7-C8) is ~30% of the effort. Get C1-C6 done first for a usable MVP without video, then add video as a follow-up.

---

## Stream D: Dejting Polish (ongoing)

> **Branch**: `main` (or `feat/dejting-monetization`)
> **Touches**: Existing Dejting code only

| # | Task | Effort |
|---|------|--------|
| D1 | Monetization tiers (Plus/Premium gates) | L |
| D2 | "See who liked you" feature | M |
| D3 | Profile boost mechanic | M |
| D4 | Bug fixes, UX polish | Ongoing |

This stream never conflicts because it only changes existing Dejting-specific code.

---

## Merge Strategy

### Database Migrations

Each stream prefixes migrations with its flavor letter:

```
A001_AddPhotosRevealedToMatch.cs        (Voice)
A002_AddFlavorVoiceQuestions.cs          (Voice)
B001_AddProfileTags.cs                  (Darkness)
B002_AddPrivateAlbums.cs                (Darkness)
B003_AddProfileGroupId.cs               (Darkness)
C001_AddAgeFloorConfig.cs               (Oldies — if needed)
C002_AddVideoCallSignaling.cs           (Oldies)
```

Migrations are additive (ADD columns/tables, never DROP or ALTER existing). No conflicts possible.

### Merge Order

1. **Phase 0** → main (FIRST, before any stream)
2. **Stream B (Darkness)** → main (smallest delta, rebrand of existing code)
3. **Stream A (Voice)** → main (medium delta, most differentiated)
4. **Stream C (Oldies)** → main (largest delta, video chat)
5. Stream D is continuous on main

Why this order: Darkness is mostly a rebrand of Fleet (least new code → fewest conflicts). Voice is medium. Oldies has video chat (most new infrastructure → merge last when others are stable).

### CI/CD

Each stream's branch runs:
```
flutter analyze --no-fatal-infos --no-fatal-warnings
flutter test
dotnet build (affected services)
dotnet test (affected services)
```

If CI fails after merge: the stream that broke it fixes it, not the next merging stream.

---

## Conflict Prevention Checklist

| Risk | Prevention |
|------|-----------|
| Two streams edit FlavorFeatureFlags | **Locked after Phase 0** — all flags pre-declared |
| Two streams add migrations to same service | **Letter-prefixed names** — can't conflict |
| Two streams modify home_screen.dart | **Flag branching only** — `if (flags.X)` wraps new code, doesn't change default path |
| Two streams modify same backend controller | **New endpoints only** — never modify existing method signatures |
| Two streams need a new shared widget | **Don't share** — duplicate into `widgets/voice/` vs `widgets/darkness/` until proven shared, then extract in Phase 0.5 |
| Merge conflict in pubspec.yaml | **Phase 0 adds all deps** — streams don't add new packages without coordinating |
| Flutter test count drops | **Hard gate**: each stream must have ≥ starting test count at merge |

---

## Timeline Estimate

```
Week 1-2:   Phase 0 (Foundation)          ████████████
Week 3-4:   Stream B (Darkness rebrand)   ░░░░████████
Week 3-5:   Stream A (Voice core)         ░░░░████████████
Week 3-6:   Stream C (Oldies w/o video)   ░░░░████████████████
Week 5-6:   Merge B → main                         ░░██
Week 6-7:   Merge A → main                           ░░██
Week 7-8:   Stream C: Add video chat               ░░░░████████
Week 8-9:   Merge C → main                                 ░░██
Week 3+:    Stream D (Dejting ongoing)    ░░░░░░░░░░░░░░░░░░░░░░░░
```

**Total**: ~8-9 weeks from start to all 4 flavors merged.
**Parallel acceleration**: Without parallelism this would be ~14-16 weeks sequential.

---

## What to Build If You're SOLO

If one developer does all streams, the order changes — still use the same branch/file isolation, but work sequentially within streams:

1. **Phase 0** (8-12h) — foundation
2. **Stream B** (30-50h) — Darkness (easiest, rebrand of existing)
3. **Stream A** (40-60h) — Voice (most differentiated, needs the reveal mechanic)
4. **Stream C without video** (30-40h) — Oldies MVP (accessibility + daily picks + scam UI)
5. **Stream C video** (25-35h) — Add video chat last (biggest single feature, needs SDK eval)
6. **Stream D** — Dejting monetization (ongoing)

Same file ownership rules apply even when solo — keeps you from creating spaghetti.

---

## Open Decisions Before Starting

| # | Decision | Options | Recommended |
|---|----------|---------|-------------|
| P1 | Video chat SDK for Oldies | WebRTC via SignalR (DIY) vs Twilio/Agora (paid SDK) | Twilio for MVP (faster), migrate later |
| P2 | Darkness private albums: App Store risk? | Allow slightly edgy content vs play safe | Play safe — flag for review, no explicit nudity |
| P3 | Voice reveal: mutual tap or message count? | A: Both tap / B: Auto after 15 msgs / C: Hybrid | A (mutual tap) for drama, B as fallback timer |
| P4 | Solo or parallel team? | 1 dev sequential vs 2-3 devs parallel | Depends on resources — plan works either way |
| P5 | Oldies: separate home screen or shared? | New OldiesHomeScreen vs flag-branch existing | New screen — accessibility needs are too different |
