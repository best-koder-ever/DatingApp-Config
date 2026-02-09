# 4-Layer Documentation: Onboarding Wizard Unification

**Session**: February 9, 2026 - Flutter Onboarding Flow Rewrite  
**Commit**: `5ccb780` (mobile_dejtingapp)  
**Status**: ✅ All 4 layers documented

---

## Documentation Philosophy

1. **Layer 1: Task/Project Management** — What was done, why, when
2. **Layer 2: Code/Implementation** — How it works, technical details
3. **Layer 3: Service/Integration** — How to use it, developer workflow
4. **Layer 4: System/Architecture** — Decisions, impacts, future direction

---

## Layer 1: Task/Project Management ✅

**Location**: This document + `specs/001-mvp-foundation/tasks.md` (T026 updated)

### What Was Done
| Item | Status | Details |
|------|--------|---------|
| Unified onboarding flow | ✅ | 8-screen wizard wired end-to-end with named routes |
| DevMode feature flag | ✅ | Skip buttons on every screen, debug-only, auto-enabled |
| Code cleanup (clutter) | ✅ | 63 root-level vibe-coded files deleted (*.py, *.sh, *.md) |
| Competing wizard removed | ✅ | Deleted 3-step wizard (onboarding_wizard_screen + wizard_steps/) |
| Photos screen created | ✅ | New final onboarding step with 2×3 grid |
| Navigation bugs fixed | ✅ | Gender→orientation (was skipping), orientation Next (was no-op) |
| Deprecation fixes | ✅ | `withOpacity` → `withAlpha` in welcome/gender screens |
| Dead code removed | ✅ | `MyHomePage` counter widget removed from main.dart |
| Route registration | ✅ | All 7 `/onboarding/*` routes + `/welcome` registered in main.dart |

### Effort
- **Estimate**: ~4h (cleanup + rewrite + wiring + testing)
- **Actual**: ~4h
- **Commit**: `5ccb780` — 66 files changed, 5286 insertions, 2239 deletions
- **Completion**: 2026-02-09

### Task Cross-References
- **T026** (Implement Flutter onboarding UI) — was marked complete with old 3-step wizard; this session replaced it with proper Tinder-style single-screen-per-step flow
- **T021** (Flutter integration test for onboarding) — still open, but flow is now testable
- **T028** (Keycloak webhook for initial profile) — deferred to Phase 2, not blocked

**Audience**: Project managers, sprint reviews, future planning

---

## Layer 2: Code/Implementation ✅

**Location**: Source files in `mobile-apps/flutter/dejtingapp/lib/`

### File Inventory

#### Created
| File | Purpose |
|------|---------|
| `lib/config/dev_mode.dart` | DevMode feature flag — `enabled` defaults to `kDebugMode`, fake data constants for auto-fill |
| `lib/widgets/dev_mode_banner.dart` | `DevModeSkipButton` widget — Positioned orange pill with bug icon, renders nothing in release |
| `lib/screens/wizard/photos_screen.dart` | Final onboarding step — 2×3 photo grid with tap-to-add, 2-photo minimum, finish → `/home` |

#### Modified (Rewritten)
| File | Changes |
|------|---------|
| `lib/main.dart` | Removed `MyHomePage`, registered 7 onboarding routes + `/welcome`, DevMode → `/welcome` initial route |
| `lib/screens/welcome_screen.dart` | Phone button → `/onboarding/phone` named route, `withOpacity` → `withAlpha`, DevMode skip |
| `lib/screens/wizard/phone_entry_screen.dart` | Continue → `/onboarding/community-guidelines`, added DevMode skip, progress 0.0 |
| `lib/screens/wizard/community_guidelines_screen.dart` | Added back button + close button, progress bar 0.14, DevMode skip |
| `lib/screens/wizard/first_name_screen.dart` | Progress 0.28, DevMode skip, expanded name regex to include À-ÿ accented chars |
| `lib/screens/wizard/birthday_screen.dart` | Progress 0.42, DevMode skip, added dispose for controllers |
| `lib/screens/wizard/gender_screen.dart` | **Fixed**: was navigating to `/onboarding/photos` (skipping orientation!), now → `/onboarding/orientation`. Progress 0.57, `withAlpha`, DevMode skip |
| `lib/screens/wizard/orientation_screen.dart` | **Fixed**: Next button was `() {}` no-op, now → `/onboarding/photos`. Progress 0.71, DevMode skip |
| `lib/screens/account_consent_screen.dart` | Replaced reference to deleted `OnboardingWizardScreen` with `pushReplacementNamed('/onboarding/phone')` |

#### Deleted
| File | Reason |
|------|--------|
| `lib/screens/onboarding_wizard_screen.dart` | Competing 3-step wizard orchestrator — replaced by single-screen-per-route flow |
| `lib/screens/wizard_steps/basic_info_step.dart` | Part of competing 3-step wizard |
| `lib/screens/wizard_steps/preferences_step.dart` | Part of competing 3-step wizard |
| `lib/screens/wizard_steps/photos_step.dart` | Part of competing 3-step wizard |
| 63 root-level *.py, *.sh, *.md files | Vibe-coded clutter from early sessions |

### Key Implementation Patterns

#### DevMode Skip Button Pattern
Every wizard screen wraps its body in a `Stack` with `DevModeSkipButton` overlay:
```dart
body: Stack(
  children: [
    // ... actual screen content ...
    DevModeSkipButton(
      onSkip: () => Navigator.pushNamed(context, '/onboarding/next-step'),
      label: 'Skip Name',
    ),
  ],
),
```
The `DevModeSkipButton` checks `DevMode.enabled` internally — renders `SizedBox.shrink()` if disabled, so zero overhead in release builds.

#### Route Registration Pattern
All onboarding routes registered as flat named routes in `MaterialApp.routes`:
```dart
routes: {
  '/welcome': (context) => const WelcomeScreen(),
  '/onboarding/phone': (context) => const PhoneEntryScreen(),
  '/onboarding/community-guidelines': (context) => const CommunityGuidelinesScreen(),
  // ... etc
}
```

#### Progress Indicator Values
Each screen has a `LinearProgressIndicator` with coral color `#FF6B6B`:
```
phone: 0.00, guidelines: 0.14, first-name: 0.28, birthday: 0.42,
gender: 0.57, orientation: 0.71, photos: 0.85
```

**Audience**: Developers maintaining or extending the onboarding flow

---

## Layer 3: Service/Integration (Developer Workflow) ✅

**Location**: This document

### How to Work With the Onboarding Flow

#### Running the App in DevMode
```bash
cd mobile-apps/flutter/dejtingapp
flutter run -d linux    # or -d chrome, or your device
```
DevMode is **auto-enabled** in debug builds. The app starts at the Welcome screen. Use the orange 🐛 skip buttons (top-right of each screen) to jump through the flow without entering real data.

#### Disabling DevMode (test real user flow)
In `lib/config/dev_mode.dart`:
```dart
static bool enabled = false;  // was: kDebugMode
```
App will then start at `/login` (or `/home` if auth session exists).

#### Adding a New Wizard Screen
1. Create `lib/screens/wizard/your_screen.dart`
2. Add `DevModeSkipButton` in a `Stack` wrapper
3. Set appropriate progress value (calculate: step_index / total_steps)
4. Register route in `lib/main.dart` routes map: `'/onboarding/your-step': (context) => const YourScreen()`
5. Update previous screen's Next button to navigate to your route
6. Update following screen's back button (or rely on `Navigator.pop`)

#### Onboarding Flow Order
```
/welcome → /onboarding/phone → /onboarding/community-guidelines →
/onboarding/first-name → /onboarding/birthday → /onboarding/gender →
/onboarding/orientation → /onboarding/photos → /home
```

#### Modifying Screen Order
1. Change the `Navigator.pushNamed` target in the "previous" screen
2. Change the progress indicator value
3. Update the `DevModeSkipButton.onSkip` target to match

#### Photos Screen — Backend Integration (TODO)
The photos screen currently uses local placeholder state (`_photoSlots` list of bools). To connect to the real photo-service:
1. Import `services/photo_service.dart`
2. Replace `_addPhoto` with actual upload call
3. Replace `_removePhoto` with actual delete call
4. Show real image thumbnails instead of person icon placeholders

**Audience**: Developers working on the Flutter app, new team members onboarding

---

## Layer 4: System/Architecture ✅

**Location**: This document

### Architectural Decisions

#### Decision 1: Single-Screen-Per-Route (not multi-step PageView)
**Choice**: Each wizard step is a separate named route, not tabs/pages in a single widget.  
**Rationale**: 
- Simpler navigation (back button = `Navigator.pop()`, works naturally)
- Each screen is independently testable
- Route-based deep linking possible for resuming onboarding
- No shared state lifecycle complexity between steps

**Trade-off**: More route registrations in main.dart, but cleaner separation.

#### Decision 2: DevMode as Compile-Time Flag (not runtime toggle)
**Choice**: `DevMode.enabled = kDebugMode` — skip buttons exist only in debug builds.  
**Rationale**: 
- Zero runtime cost in release builds (`kDebugMode` is a compile-time const)
- No UI needed for a toggle (no settings screen, no gesture detector)
- Can be overridden to `false` for testing "real" flow in debug

**Alternative rejected**: Runtime SharedPreferences toggle — adds complexity, risk of accidentally shipping with dev features enabled.

#### Decision 3: Deleted Competing 3-Step Wizard
**What existed**: `OnboardingWizardScreen` with `PageView` controlling `BasicInfoStep`, `PreferencesStep`, `PhotosStep` — registered as T026 evidence.  
**Why deleted**: 
- It was a completely separate flow from the Tinder-style individual screens
- Neither flow was wired to routing — both were dead code
- The Tinder-style screens better match the design-explorations (Stitch reference designs)
- Having two flows caused confusion about which was canonical

**Impact**: T026 evidence references in `tasks.md` now point to deleted files. The replacement (this commit) supersedes that evidence.

#### Decision 4: `api_services.dart` Retained
**Context**: Was initially deleted as a "duplicate" of `services/api_service.dart`.  
**Restored**: `tinder_like_profile_screen.dart` depends on `userApi` global from this file.  
**Future**: Should be refactored — the facade pattern is ok but the global `final userApi = UserApiService()` should eventually move to DI or a service locator.

### System Impact

#### What Changed
| Component | Before | After |
|-----------|--------|-------|
| Initial route (debug) | `/login` → Keycloak auth timeout | `/welcome` → visible immediately |
| Onboarding flow | 2 competing broken flows, neither routed | 1 unified flow, all routes registered |
| Navigation bugs | Gender→photos (skipping orientation), Orientation no-op | All transitions correct |
| Code size | 2239 lines of dead/duplicate code | Removed, net +3047 lines of working code |

#### What Didn't Change
- Backend services — no backend changes in this commit
- Auth flow — Keycloak ROPC still works for `/login` route
- State management — still `AppState` singleton, no Riverpod
- Data persistence — wizard data is local-only, no backend calls yet

### Future Work
| Item | Priority | Notes |
|------|----------|-------|
| Connect wizard to UserService WizardController | P1 | POST step data to backend as user progresses |
| Photos screen → photo-service integration | P1 | Real upload/moderation pipeline, not placeholder |
| Keycloak registration flow (T028) | P2 | Replace phone-entry placeholder with real SMS/OAuth |
| Onboarding resume on app restart | P2 | Check backend onboarding status, route to correct step |
| T021 integration test | P2 | Now possible since flow is wired end-to-end |
| Remove `api_services.dart` facade | P3 | Refactor `tinder_like_profile_screen` to use proper services |

**Audience**: Architects, new team members, future planning sessions

---

## Cross-Reference Summary

| Layer | Location | Key Content |
|-------|----------|-------------|
| L1: Tasks | This doc + `specs/001-mvp-foundation/tasks.md` T026 | Completion status, effort, commit hash |
| L2: Code | 10 source files (see inventory above) | Inline comments, DevMode pattern, progress values |
| L3: Integration | This doc §3 | How to run, add screens, modify flow |
| L4: Architecture | This doc §4 | Decisions (single-route, compile-time flag), impact matrix |

**Commit**: `5ccb780` on `best-koder-org/mobile_dejtingapp` main  
**Date**: 2026-02-09
