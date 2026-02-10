# Flutter Discover Screen — Feature Documentation

**Task**: T035 [US2] Update Flutter Discover UI for compatibility indicators + empty-state messaging  
**Status**: ✅ COMPLETE  
**Completion**: 2026-02-10  
**File**: `lib/screens/home_screen.dart` (887 lines)

---

## Layer 1: Feature Specification

### Business Context

The Discover screen is the core engagement loop of any dating app — it's where users spend 80%+ of their active session time. Users swipe through a ranked queue of candidate profiles, express interest (like/pass), and receive instant feedback on mutual matches. This screen directly drives the key metrics: daily active time, swipe-to-match conversion, and retention.

Previously the screen was a hardcoded prototype with 3 fake profiles (Emma, Sofia, Isabella), no backend integration, and a hardcoded "2.5 km away" label. T035 replaces this with a fully production-ready implementation.

### User Stories

**US2-A: Browse Real Candidates**
```
As a logged-in user
I want to see real candidate profiles ranked by compatibility
So that I can discover people I'm most likely to connect with
```

**US2-B: Compatibility Visibility**
```
As a user viewing a candidate
I want to see a compatibility score and shared interests at a glance
So that I can make informed swipe decisions quickly
```

**US2-C: Swipe with Confidence**
```
As a user
I want my swipes to be reliably recorded even on flaky networks
So that I don't miss potential matches due to technical issues
```

**US2-D: Instant Match Feedback**
```
As a user who receives a mutual match
I want to see an immediate celebration dialog with the option to message
So that I feel rewarded and can start conversations while excited
```

**US2-E: Graceful Empty/Error States**
```
As a user who has seen all candidates (or is offline)
I want a clear, non-frustrating empty/error screen with recovery options
So that I understand the situation and know what to do next
```

### Acceptance Criteria

- [x] Calls `matchmakingApi.getCandidates()` for real ranked profiles
- [x] Shows compatibility score badge (purple gradient, fire icon, percentage)
- [x] Shows real distance from `MatchCandidate.distanceKm` (formatted km/m)
- [x] Shows shared interest chips from `MatchCandidate.interestsOverlap`
- [x] Shows occupation with work icon
- [x] Calls `matchmakingApi.swipe()` with idempotency on each swipe action
- [x] Handles `SwipeResponse.isMatch` with celebration dialog
- [x] Loading state with spinner + "Finding amazing people near you..."
- [x] Error state with cloud_off icon + "Try Again" button
- [x] Empty state with "You've seen everyone!" + "Refresh" button
- [x] Drag-to-swipe gesture (right=like, left=pass) with LIKE/NOPE overlay
- [x] Card stack peek animation (next card scales up during drag)
- [x] Prefetch more candidates when ≤3 remain in queue
- [x] `flutter analyze`: 0 issues

---

## Layer 2: Implementation Details

### Architecture

```
HomeScreen (StatefulWidget + TickerProviderStateMixin)
│
├─ _loadCandidates()          → matchmakingApi.getCandidates()
│   └─ Returns List<MatchCandidate>
│
├─ _onSwipe(isLike)           → matchmakingApi.swipe(targetUserId, isLike)
│   ├─ Animates card off-screen (slide + rotate + fade)
│   ├─ Calls backend (idempotent via SwipeService)
│   ├─ If SwipeResponse.isMatch → _showMatchCelebration()
│   └─ Advances _currentIndex, resets animation
│
├─ _prefetchIfNeeded()        → loads more candidates at threshold
│
├─ Drag gesture (GestureDetector)
│   ├─ onPanStart → _isDragging = true
│   ├─ onPanUpdate → accumulate _dragOffset
│   └─ onPanEnd → if |dx| > 30% screen width → swipe, else snap back
│
├─ _buildCandidateCard()      → Card UI with photo, info, badges
│   ├─ CachedNetworkImage for photo (with placeholder/error)
│   ├─ Gradient overlay (transparent → 0.25 → 0.8 black)
│   ├─ Compatibility badge (top-right, purple gradient)
│   ├─ Name, age (28pt bold white)
│   ├─ Distance row (location icon + formatted km/m)
│   ├─ Occupation row (work icon)
│   ├─ Bio (max 2 lines)
│   └─ Interest chips (max 4, semi-transparent white)
│
├─ _MatchCelebrationDialog    → Full-screen modal on mutual match
│   ├─ "It's a Match! 🎉" heading
│   ├─ Candidate photo (120px circle)
│   ├─ "Send a Message" button (white, navigates to chat)
│   └─ "Keep Swiping" text button
│
└─ 4 states: loading / error / empty / discover
```

### Key Design Decisions

| Decision | Choice | Rationale | **Change if...** |
|----------|--------|-----------|------------------|
| **Compatibility score display** | Purple gradient pill, fire icon + percentage (e.g., "87%") | Matches the existing ProfileCard widget badge style; purple stands out on photo background | You prefer a different color, position, or format (e.g., bar chart, stars, words like "Great Match") |
| **Drag threshold** | 30% of screen width | Standard Tinder-like threshold; prevents accidental swipes but feels responsive | Users find it too easy/hard to trigger — adjust in `_onDragEnd` |
| **LIKE/NOPE overlay** | Green "LIKE" / Red "NOPE" text with border, appears after 40px drag | Gives immediate visual feedback during drag; industry standard pattern | You want different colors, icons instead of text, or a stamp-style overlay |
| **Swipe animation duration** | 350ms ease-out | Fast enough to feel snappy, slow enough to see the card fly off | Feels too slow/fast — change `_swipeController` duration |
| **Card stack peek** | Next card at 0.92 scale / 0.6 opacity, animates toward 1.0/1.0 as you drag | Creates depth illusion; user knows more cards exist | You want a different stack depth (3 cards visible) or no peek |
| **Interest chips** | Max 4 shown, semi-transparent white with border | Prevents overflow; enough to spark curiosity without cluttering | You want all interests shown, different chip style, or scrollable |
| **Distance format** | "X.X km away" for ≥1km, "X m away" for <1km | Natural reading; auto-adapts to proximity | You want miles, want to hide distance, or want city name instead |
| **Empty state message** | "You've seen everyone!" with Refresh button | Friendly, non-blaming tone; encourages return | You want different copy, "Broaden Preferences" as primary CTA, or countdown to next refresh |
| **Match celebration** | Modal dialog with gradient background (pink→gold), not dismissible by tapping outside | Forces acknowledgment; "Send a Message" is primary CTA | You want it auto-dismissible, want confetti animation, or want both users' photos side by side |
| **Action buttons layout** | Pass (56px white) — Super Like (48px teal) — Like (64px pink) | Like button largest = primary action; super like smaller = secondary; pass smallest = easy escape | You want different order, different colors, want to remove super like, or want button labels |
| **Prefetch threshold** | Load more when ≤3 candidates remain | Prevents visible loading gaps between batches | Too aggressive (wastes data) or too late (users see loading) |
| **Error state** | cloud_off icon + "Could not load profiles. Check your connection." + Try Again | Covers network errors without technical jargon | You want more specific error messages or auto-retry |

### Data Flow

```
User opens Discover tab
  → HomeScreen.initState()
    → _loadCandidates()
      → matchmakingApi.getCandidates()
        → MatchmakingService.getProfiles(userId)
          → Backend scoring/ranking
        → Returns List<MatchCandidate>
      → setState(_candidates = [...], _isLoading = false)

User swipes right
  → _onSwipe(isLike: true)
    → _swipeController.forward() (animate card off-screen)
    → matchmakingApi.swipe(targetUserId, isLike: true)
      → SwipeService.swipe() (UUID idempotency, 3 retries, exponential backoff)
        → POST /matches/swipe {targetUserId, direction, idempotencyKey}
      → Returns Map<String, dynamic>?
    → SwipeResponse.fromJson(response)
    → if isMatch → _showMatchCelebration()
    → _currentIndex++
    → _prefetchIfNeeded()

User drags card past threshold
  → GestureDetector.onPanEnd
    → |_dragOffset.dx| > screenWidth * 0.3
    → _onSwipe(_dragOffset.dx > 0)  // right=like, left=pass
```

### Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| `cached_network_image` | 3.3.1 | Photo loading with disk/memory cache + placeholder/error widgets |
| `api_services.dart` | — | `matchmakingApi` global instance with `getCandidates()`, `swipe()` |
| `models.dart` | — | `MatchCandidate`, `SwipeResponse` model classes |
| `swipe_service.dart` | — | Retry + idempotency layer (called internally by `matchmakingApi.swipe()`) |

---

## Layer 3: Integration Guide

### Using the Discover Screen

The `HomeScreen` widget is mounted as tab 0 in `MainApp` (or equivalent navigation). It's self-contained — no props needed.

```dart
// In your tab navigation:
HomeScreen()  // That's it — self-loads candidates on mount
```

### API Endpoints Called

| Endpoint | Method | When Called | Response Used |
|----------|--------|-------------|---------------|
| `GET /api/matchmaking/candidates` | via `matchmakingApi.getCandidates()` | On mount + on refresh + on prefetch | `List<MatchCandidate>` |
| `POST /matches/swipe` | via `matchmakingApi.swipe()` | On each swipe action | `SwipeResponse` (isMatch, matchId) |

### MatchCandidate Fields Displayed

| Field | Display | Fallback |
|-------|---------|----------|
| `displayName` | "Name, age" heading (28pt) | — |
| `age` | Next to name | — |
| `photoUrl` / `photoUrls[0]` | Full-bleed card background | Gray person icon |
| `compatibility` | Green/purple badge "87%" (top-right) | Hidden if 0 |
| `distanceKm` | "12.3 km away" or "800 m away" | City name, or hidden |
| `city` | Shown if no distanceKm | Hidden |
| `occupation` | Work icon + text | Hidden if null |
| `bio` | 2-line text below name | Hidden if null/empty |
| `interestsOverlap` | Up to 4 glass-morphism chips | Hidden if empty |

### State Machine

```
LOADING → (success) → DISCOVER
LOADING → (error)   → ERROR
DISCOVER → (all swiped) → EMPTY
ERROR → (retry tap) → LOADING
EMPTY → (refresh tap) → LOADING
DISCOVER → (swipe) → DISCOVER (or EMPTY)
```

### Customization Points

To change behavior without rewriting:

1. **Compatibility threshold to show badge**: Change `if (compatibilityPercent > 0)` to a higher value
2. **Max interests chips**: Change `.take(4)` to desired count
3. **Drag threshold**: Change `screenWidth * 0.3` in `_onDragEnd`
4. **Animation speed**: Change `Duration(milliseconds: 350)` in `_swipeController`
5. **Prefetch threshold**: Change `_prefetchThreshold = 3` constant
6. **Empty state copy**: Edit strings in `_buildEmptyState()`
7. **Match celebration style**: Edit `_MatchCelebrationDialog` widget

---

## Layer 4: Architecture & Design Decisions

### Why This Architecture

**Problem**: The discover screen is the most performance-sensitive screen in the app. Users expect instant card transitions, no loading spinners between swipes, and reliable swipe recording even on spotty mobile networks.

**Solution**: 
- **Optimistic UI**: Card animates away immediately on swipe. Backend call happens in parallel. If it fails, the swipe is still visually processed (no jarring undo).
- **Prefetch pipeline**: When ≤3 cards remain, silently fetch more in the background. Users never see a loading state between batches.
- **Idempotent swipes**: Every swipe gets a UUID. If the network drops and the app retries, the backend deduplicates. No double-match risk.
- **Single-widget state**: All state lives in `_HomeScreenState` — no external state management needed for the MVP. This can be extracted to Riverpod/Bloc later.

### Comparison to Industry Standards

| Feature | Our Implementation | Tinder | Bumble | Hinge |
|---------|-------------------|--------|--------|-------|
| Compatibility score | ✅ Purple badge with % | ❌ Hidden | ❌ Hidden | ✅ "Most Compatible" label |
| Drag-to-swipe | ✅ With LIKE/NOPE overlay | ✅ | ✅ | ✅ |
| Card stack peek | ✅ Next card scales up | ✅ | ✅ | ❌ (list view) |
| Match celebration | ✅ Modal with message CTA | ✅ + confetti | ✅ + time limit | ✅ |
| Shared interests | ✅ Chip badges | ❌ | ❌ | ✅ (Dealbreakers) |
| Empty state | ✅ Friendly with refresh | "No one new around you" | "You've reached the end" | "We're expanding" |
| Offline resilience | ✅ Idempotent retry | Unknown | Unknown | Unknown |

### Known Limitations & Future Work

| Limitation | Impact | Future Solution | Task |
|-----------|--------|-----------------|------|
| No offline candidate cache | If offline at launch, shows error state | Cache last batch in SharedPreferences/Hive | T037 |
| Super Like = same as Like | No special handling on backend | Add `direction: 'superlike'` to swipe API | Backlog |
| No photo gallery (only first photo) | Users see single image per candidate | Add horizontal swipe between photos on card | Backlog |
| No "Undo last swipe" | Accidental swipes can't be corrected | Add undo buffer (premium feature) | T098 area |
| Match dialog doesn't navigate to chat | "Send a Message" closes dialog but stays on Discover | Wire navigation to EnhancedChatScreen with matchId | T041 integration |
| No pull-to-refresh gesture | Must tap Refresh button on empty state | Add RefreshIndicator wrapper | Minor polish |
| Single-widget state management | All state in StatefulWidget, no global state | Extract to Riverpod provider for cross-screen state | Architecture pass |
| No daily limit UI | Backend enforces limits but UI doesn't show "X swipes remaining" | Add limit indicator from `GET /daily-suggestions/status` (T033) | Polish |
| No preference-stale detection | If user changes preferences mid-session, queue is stale | Listen to preference change events and auto-refresh | T037 |

### Performance Characteristics

| Metric | Target | Current |
|--------|--------|---------|
| Time to first card | <2s | Depends on getCandidates() P95 (~420ms) + photo load |
| Swipe-to-next-card | <400ms | 350ms animation + async backend call |
| Prefetch latency | Invisible | Background fetch when ≤3 remain |
| Memory per card | Minimal | CachedNetworkImage handles memory/disk cache |
| Animation frame rate | 60fps | AnimatedBuilder with simple transforms |

### Security Considerations

- **Auth token**: `matchmakingApi` internally uses `AppState().getOrRefreshAuthToken()` — expired tokens auto-refresh
- **User ID**: Extracted from JWT server-side, not sent from client (swipeService sends only targetUserId)
- **Photo privacy**: Photos served through photo-service which enforces MatchOnly privacy rules
- **Rate limiting**: Backend enforces daily swipe limits; YARP gateway has rate limiting rules

---

## Related Documentation

- **User Journey**: [02-match-discovery.md](user-journeys/02-match-discovery.md) — Full sequence diagrams
- **Scoring Algorithm**: [MATCHMAKING.md](../../MATCHMAKING.md) — 6-factor weighted scoring
- **API Contracts**: [api-spec.md](../contracts/api-spec.md) — Endpoint specifications
- **Swipe Idempotency**: T034 in [tasks.md](../tasks.md) — Backend + Flutter retry logic
- **Offline Cache Strategy**: T037 in [tasks.md](../tasks.md) — Future offline support
- **Match Notifications**: T036 in [tasks.md](../tasks.md) — SignalR push notifications

---

**Last Updated**: 2026-02-10  
**Commit**: `993e941` (mobile_dejtingapp)
