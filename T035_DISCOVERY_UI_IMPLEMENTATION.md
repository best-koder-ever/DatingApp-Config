# T035: Flutter Discovery UI Implementation

**Status**: IN PROGRESS  
**Started**: 2026-02-02  
**Completion Target**: 6-8 hours

---

## ✅ Completed (Phase 1: Design System)

### 1. Design Foundation
- ✅ Created [UI_UX_STRATEGY_FOR_NON_DESIGNERS.md](UI_UX_STRATEGY_FOR_NON_DESIGNERS.md)
  - Comprehensive guide for non-designers
  - Material Design 3 approach
  - Coral (#FF7F50) brand color selection
  - Wireframe examples and workflow
  - Screen-by-screen design patterns

### 2. Theme System
- ✅ Created `lib/theme/spacing.dart`
  - 8pt grid system (xs through xxxl)
  - Consistent border radii
  - Usage: `Spacing.md`, `Spacing.lg`, etc.

- ✅ Created `lib/theme/app_theme.dart`
  - Coral brand color palette
  - Poppins (headings) + Inter (body) fonts
  - Material 3 component themes
  - Typography scale (display → label)
  - Semantic colors (success, error, warning, info)

- ✅ Verified google_fonts package available

---

## 🔨 In Progress (Phase 2: Discovery Screen)

### Unique Differentiators (vs Tinder)
1. **Match Score Transparency**: Show "87% Match" with reasons
2. **Niche Context**: Display "Moved to Stockholm 2 months ago"
3. **Preview Value**: See conversation starters BEFORE matching
4. **Progressive Disclosure**: Tap to expand full profile

### Components to Build

#### Priority 1: Profile Card Widget
**File**: `lib/widgets/discovery/profile_card.dart`
```dart
// Stack-based layout:
// - Background: User photo (CachedNetworkImage)
// - Gradient overlay (makes text readable)
// - Content: Name, age, niche context, match score
// - Actions: Pass, Info, Like buttons
```

**Features**:
- [ ] CachedNetworkImage with shimmer loading
- [ ] Linear gradient overlay (black87 → transparent)
- [ ] Name + age display
- [ ] Niche context chip ("📍 Moved 2 months ago")
- [ ] Match score chip with percentage
- [ ] Match reasons list (collapsible)
- [ ] Action buttons (Pass/Info/Like)

#### Priority 2: Swipeable Card Stack
**File**: `lib/screens/discovery_screen.dart`
```dart
// Use flutter_card_swiper package
// Handle swipe gestures
// Visual feedback (green/red border)
// Prefetch next 3 profiles
```

**Features**:
- [ ] Card swiper integration
- [ ] Swipe direction feedback (visual)
- [ ] Empty state ("Keep swiping!")
- [ ] Loading state (shimmer cards)
- [ ] Error state ("Couldn't load profiles")

#### Priority 3: Match Notification Overlay
**File**: `lib/widgets/discovery/match_notification.dart`
```dart
// Full-screen modal
// Animated "It's a Match!" headline
// Side-by-side photos
// Shared interests
// CTA: "Say Hi" / "Keep Swiping"
```

**Features**:
- [ ] ScaleTransition animation (elasticOut curve)
- [ ] Hero animation for photos
- [ ] Shared interests display
- [ ] Navigation to messaging
- [ ] Dismiss to continue swiping

---

## 📦 Dependencies Needed

```yaml
dependencies:
  flutter_card_swiper: ^7.0.0   # Swipe mechanics
  cached_network_image: ^3.3.0  # Fast image loading
  shimmer: ^3.0.0              # Loading states
  # google_fonts: already added
```

---

## 🎨 Visual Design

### Color Usage
- **Primary (Coral)**: Like button, CTA buttons, focused state
- **Success (Green)**: Match notification, positive feedback
- **Secondary (Purple)**: Info button, accents
- **Text Primary**: Name, age (high contrast)
- **Text Secondary**: Bio, match reasons

### Typography Scale
- **Display Large (32pt)**: "It's a Match!"
- **Headline Large (24pt)**: Name on profile card
- **Body Large (16pt)**: Bio, match reasons
- **Label Medium (12pt)**: Match percentage, badges

### Spacing
- **Card Padding**: `Spacing.md` (16px)
- **Element Gaps**: `Spacing.sm` (8px)
- **Section Spacing**: `Spacing.lg` (24px)
- **Screen Edges**: `Spacing.xl` (32px)

---

## 🧪 Testing Strategy

### Unit Tests
- [ ] Profile card renders correctly
- [ ] Match score calculation
- [ ] Swipe gesture detection
- [ ] Empty state visibility logic

### Widget Tests
- [ ] Swipe animations smooth (60fps)
- [ ] Match notification modal appears
- [ ] Action buttons trigger correct events
- [ ] Loading states display properly

### Integration Tests
- [ ] Complete swipe flow (right → match → message)
- [ ] Complete swipe flow (left → next profile)
- [ ] Profile prefetching works
- [ ] Offline state handled gracefully

---

## 📝 Next Steps (Immediate)

### Today (2-3 hours)
1. ✅ Design system complete
2. Add required packages (flutter_card_swiper, shimmer)
3. Create profile_card.dart widget
4. Create match_score_chip.dart widget
5. Test visual appearance

### Tomorrow (4-5 hours)
6. Build discovery_screen.dart with card swiper
7. Implement swipe gestures + feedback
8. Create match_notification.dart overlay
9. Add loading/empty/error states
10. Integration test full flow

---

## 🎯 Success Criteria

- [ ] User can swipe through profiles smoothly (60fps)
- [ ] Match score visible and understandable
- [ ] Niche context ("new to city") prominently displayed
- [ ] Match notification feels celebratory (not boring)
- [ ] Empty state is encouraging (not punishing)
- [ ] Works on iPhone SE (small) and iPhone 14 Pro Max (large)
- [ ] No blank screens (all states handled)

---

## 🔗 Related Documents
- [UI_UX_STRATEGY_FOR_NON_DESIGNERS.md](UI_UX_STRATEGY_FOR_NON_DESIGNERS.md)
- [ specs/001-mvp-foundation/tasks.md](specs/001-mvp-foundation/tasks.md#T035)
- [.ai-context.json](.ai-context.json) (Fixture users for testing)
- [AI_HELPERS_CHEATSHEET.md](AI_HELPERS_CHEATSHEET.md) (Test data)

---

**Last Updated**: 2026-02-02 14:30  
**Next Update**: After completing profile card widget
