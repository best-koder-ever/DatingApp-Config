# TODO — Current State

**Updated**: 2026-06-11
**Active track**: 5-icon bottom navigation restructuring

---

## 🟢 What's New (2026-06-11)

### ✅ 5-Icon Bottom Navigation — IMPLEMENTED

Restructured the Flutter app's bottom nav from 3 tabs to 5 tabs:

**New navigation layout:**
| Index | Icon | Label | Screen |
|-------|------|-------|--------|
| 0 | `Icons.explore` 🔍 | Discover | `HomeScreen` (unchanged) |
| 1 | `Icons.auto_awesome` ✨ | Top Picks | `TopPicksScreen` (NEW) |
| 2 | `Icons.favorite` ❤️ | Matches | `EnhancedMatchesScreen` (simplified) |
| 3 | `Icons.chat_bubble_outline` 💬 | Messages | `MessagesScreen` (NEW) |
| 4 | Profile avatar 👤 | Profile | `ProfileHubScreen` (unchanged) |

**What changed:**
- **`TopPicksScreen`** (NEW) — Shows 5 daily curated profiles with spark credit cost (1 ⚡ to connect). Countdown timer. Falls back to shuffled discovery candidates when backend not ready.
- **`MessagesScreen`** (NEW) — Extracted conversation list from old matches tab. Adds filter chips: All | Unread | Active Now. Own messaging service initialization. Pull-to-refresh + 30s auto-refresh.
- **`EnhancedMatchesScreen`** (SIMPLIFIED) — Removed TabController, inner TabBar, messaging init, and messages tab. Now a clean matches-only screen.
- **`MainApp`** (MODIFIED) — 3→5 tabs. Unread message badge moved from heart to chat icon. Match dialog "Send a Message" now navigates to Messages tab (index 3).
- **Backend: MatchmakingController** — Added `GET api/matchmaking/top-picks` endpoint returning 5 high-compatibility profiles (score ≥ 70%), rotating daily, skipping already-swiped users. TopPicksResponse/Profile DTOs added.

**Verification:**
- ✅ `flutter analyze` — 0 errors from our changes (4 pre-existing in swipe_cache_service.dart)
- ✅ `dotnet build` — Build succeeded, 0 errors
- ✅ Backend tests — 224 passed, 1 pre-existing failure
- ✅ APK built and installed on emulator for visual testing

---

## 📋 Next Steps

### 🟡 Visual tweaks / polish on emulator
- [ ] Labels on 5-tab nav with 5 items — verify no truncation on smaller screens
- [ ] Heart icon — consider showing new match count badge instead of clean heart
- [ ] Messages "Active Now" filter — needs backend presence tracking to work fully
- [ ] Top Picks "Get Sparks" dialog button — wire to SparksStoreScreen or profile tab

### 🟡 Feature follow-ups (not blocking)
- [ ] **Top Picks backend endpoint** — Flutter client currently falls back to shuffled discovery candidates. Wire `GET api/matchmaking/top-picks` to the Flutter `_fetchTopPicksFromBackend()` method once the endpoint is deployed.
- [ ] **Spark deduction** — "Connect with ⚡" button only shows snackbar. Wire to backend spark deduction endpoint and actually navigate to profile/chat.
- [ ] **Hinge-style "Likes You" flow** — separate from this nav work. Would add a "who liked you" feature distinct from the mutual match dialog.
- [ ] **Messages tab unread badge** — verify badge count updates correctly when switching away from Messages tab and back.

### 🟡 Pre-existing follow-ups (from earlier work)
- [ ] Audio retention policy — nightly job in bot-service to delete `UserFeedback/*.m4a` older than 30 days
- [ ] Crash/error capture — attach last 50 log lines + route name alongside voice memos
- [ ] Persist Keycloak overrides in dev compose

---

## Repos with uncommitted changes

### mobile_dejtingapp (Flutter app) — our changes
- Modified: `main_app.dart`, `enhanced_matches_screen.dart`, `home_screen.dart`, etc.
- New files: `messages_screen.dart`, `top_picks_screen.dart`

### MatchmakingService — our changes
- Modified: `MatchmakingController.cs` (new top-picks endpoint)
- Modified: `MatchmakingDTOs.cs` (TopPicksResponse DTOs)

### Other repos with pre-existing uncommitted changes
- photo-service, swipe-service, UserService, dejting-yarp, DatingAppController
