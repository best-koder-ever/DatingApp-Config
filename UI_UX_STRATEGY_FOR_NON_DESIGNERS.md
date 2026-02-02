# UI/UX Strategy for Non-Designers - DatingApp

**Goal**: Build an intuitive, beautiful dating app without being a designer
**Philosophy**: "Steal like an artist, but make it YOUR OWN"

---

## 🎨 Quick Win: 3-Hour Design System Setup

### Step 1: Choose a Foundation (1 hour)

**Option A: Material Design 3 (Recommended)**
```yaml
# pubspec.yaml (Flutter already uses this)
dependencies:
  flutter:
    sdk: flutter
  # Material Design is built-in!
```

**Why Material 3:**
- ✅ Pre-built components (buttons, cards, navigation)
- ✅ Automatic dark mode support
- ✅ Accessibility best practices baked in
- ✅ Used by Google, Spotify, Airbnb

**Color Selection Tool:**
```
1. Go to: https://m3.material.io/theme-builder
2. Pick ONE brand color (e.g., #FF6B6B for dating - warm, approachable)
3. Download Flutter theme → Copy into lib/theme/app_theme.dart
4. Done! You have a complete color palette.
```

**Your Brand Color Psychology:**
- 💗 Pink/Red (#FF6B6B): Romance, passion (but overdone in dating)
- 💜 Purple (#9B59B6): Creative, unique (less common, stands out)
- 🧡 Coral (#FF7F50): Warm, friendly, modern
- 💙 Teal (#1ABC9C): Calm, trustworthy, professional

**Recommendation**: Use **Coral (#FF7F50)** as primary - warm but not cliché pink.

### Step 2: Typography That Works (30 min)

**The 2-Font Rule:**
```dart
// lib/theme/app_theme.dart
import 'package:google_fonts/google_fonts.dart';

ThemeData appTheme = ThemeData(
  textTheme: TextTheme(
    // Headings: Bold, character
    displayLarge: GoogleFonts.poppins(fontSize: 32, fontWeight: FontWeight.bold),
    headlineMedium: GoogleFonts.poppins(fontSize: 24, fontWeight: FontWeight.w600),
    
    // Body: Readable, friendly
    bodyLarge: GoogleFonts.inter(fontSize: 16),
    bodyMedium: GoogleFonts.inter(fontSize: 14),
  ),
);
```

**Font Pairing That Never Fails:**
- **Headings**: Poppins (friendly, rounded)
- **Body**: Inter (readable, modern)

### Step 3: Spacing System (10 min)

**The 8pt Grid Rule:**
```dart
// lib/theme/spacing.dart
class Spacing {
  static const double xs = 4.0;   // Tight spacing
  static const double sm = 8.0;   // Between elements
  static const double md = 16.0;  // Card padding (most common)
  static const double lg = 24.0;  // Section spacing
  static const double xl = 32.0;  // Screen edges
  static const double xxl = 48.0; // Major sections
}
```

**Use consistently:**
```dart
Padding(
  padding: EdgeInsets.all(Spacing.md),  // Always 16.0
  child: Column(
    spacing: Spacing.sm,  // Always 8.0 between items
    children: [...],
  ),
)
```

### Step 4: Steal Smart (80 min)

**Apps to Study (Screenshot & Analyze):**

1. **Hinge** - Best onboarding flow
   - Download app → Take screenshots of every screen
   - Note: Progress indicator, friendly copy, "Skip for now" buttons
   - Steal: Multi-step wizard with clear progress

2. **Airbnb** - Best empty states & illustrations
   - Check: Wishlist empty state (friendly, not punishing)
   - Steal: Illustration style, encouraging copy

3. **Spotify** - Best card layouts
   - Note: How they show metadata (artist name, duration, etc.)
   - Steal: Consistent card structure

**Screenshot Organization:**
```
mobile-apps/flutter/dejtingapp/design_inspiration/
├── hinge_onboarding/
│   ├── step1_name.png
│   ├── step2_photos.png
│   └── step3_preferences.png
├── airbnb_empty_states/
│   ├── no_matches.png
│   └── no_messages.png
└── spotify_cards/
    ├── profile_card.png
    └── message_list.png
```

---

## 🎯 Your Unique UX Differentiators

**How to NOT be a Tinder clone while staying familiar:**

### 1. Discovery Screen Innovation

**TINDER WAY (Boring):**
```
[Photo]
Name, Age
Bio (if you tap)
[X Button] [Heart Button]
```

**YOUR WAY (Unique but Clear):**
```
┌─────────────────────────┐
│   [Photo - Full Screen] │  ← Keep this (users expect it)
│                         │
│   Name, 28              │  ← Keep this
│   📍 Moved to Stockholm │  ← YOUR NICHE! (new to city)
│      2 months ago       │
│                         │
│   🎯 Match Score: 87%   │  ← Show WHY they're compatible
│   • Same neighborhood   │     (transparency builds trust)
│   • Both love hiking    │
│                         │
│   [Swipe card up to     │  ← INNOVATION: Preview conversation
│    see conversation     │     starters BEFORE matching
│    starters]            │
│                         │
│   [Pass] [Info] [Like]  │  ← Keep familiar actions
└─────────────────────────┘
```

**What makes this unique:**
- ✅ Niche context (moved date - creates urgency)
- ✅ Transparency (match score visible - builds trust)
- ✅ Pre-match value (see what you could talk about)
- ❌ Not confusing (still swipe-based, still has pass/like)

### 2. Messaging Innovation

**TINDER WAY (Boring):**
```
[Matches Grid]
Tap → Chat
Empty text box, good luck!
```

**YOUR WAY (Conversation Boosters):**
```
┌─────────────────────────┐
│  Chat with Anna         │
│                         │
│  🎯 You both mentioned: │  ← Context from profiles
│     • New to city       │
│     • Love brunch spots │
│                         │
│  💬 Conversation Ideas: │  ← AI-generated (or template)
│  "Best brunch spot you  │     starters based on overlap
│   found in Södermalm?"  │
│  [Use this] [Write own] │
│                         │
│  Or start fresh:         │
│  [Text box]             │
└─────────────────────────┘
```

**What makes this unique:**
- ✅ Reduces "What do I say?" anxiety
- ✅ Personalized to THEIR profiles (not generic)
- ✅ Optional (can still write own message)
- ❌ Not forced (skip if you want)

### 3. Profile Depth (Without Overwhelming)

**TINDER WAY (Boring):**
```
Photos
Bio (200 chars)
Done.
```

**YOUR WAY (Progressive Disclosure):**
```
┌─────────────────────────┐
│  [Photo Gallery]        │  ← Swipe through 3-6 photos
│                         │
│  Erik, 29               │
│  📍 Vasastan (2 months) │  ← Niche context
│                         │
│  🗨️ "Looking for someone │  ← Short bio (KEEP short!)
│     to explore hidden   │
│     cafés with"         │
│                         │
│  [Tap to see more ↓]    │  ← Progressive disclosure
│                         │
│  ──────────────────────  │
│  When expanded:         │
│  ──────────────────────  │
│                         │
│  🎯 I'm here for:       │  ← Clear intent
│     Real connections    │
│                         │
│  💼 Software Engineer   │  ← Job (optional)
│  🎓 KTH                 │
│                         │
│  🎨 Interests:          │  ← Visual tags
│  [Hiking] [Photography] │
│  [Specialty Coffee]     │
│                         │
│  ❓ Two truths, one lie │  ← Hinge-style prompt
│  1. Lived in 4 countries│     (conversation starter)
│  2. Can't swim          │
│  3. Speak 3 languages   │
└─────────────────────────┘
```

**Progressive Disclosure = Less Overwhelming:**
- First glance: Photo, name, location, short bio (ENOUGH to swipe)
- Interested? Tap to expand (job, interests, prompts)
- Outcome: Faster browsing, deeper info available

---

## 🛠️ Practical Implementation Workflow

### Week 1: Design System (You're Here!)

**Day 1: Colors & Typography**
```bash
cd mobile-apps/flutter/dejtingapp
mkdir -p lib/theme

# Create theme file
cat > lib/theme/app_theme.dart << 'DART'
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Brand Colors
  static const primaryColor = Color(0xFFFF7F50);  // Coral
  static const secondaryColor = Color(0xFF6C63FF); // Purple accent
  static const backgroundColor = Color(0xFFF8F9FA);
  static const surfaceColor = Color(0xFFFFFFFF);
  static const errorColor = Color(0xFFE63946);
  
  // Text Colors
  static const textPrimary = Color(0xFF1A1A1A);
  static const textSecondary = Color(0xFF6B7280);
  
  static ThemeData lightTheme = ThemeData(
    primaryColor: primaryColor,
    scaffoldBackgroundColor: backgroundColor,
    colorScheme: ColorScheme.light(
      primary: primaryColor,
      secondary: secondaryColor,
      surface: surfaceColor,
      error: errorColor,
    ),
    textTheme: TextTheme(
      displayLarge: GoogleFonts.poppins(fontSize: 32, fontWeight: FontWeight.bold, color: textPrimary),
      headlineMedium: GoogleFonts.poppins(fontSize: 24, fontWeight: FontWeight.w600, color: textPrimary),
      bodyLarge: GoogleFonts.inter(fontSize: 16, color: textPrimary),
      bodyMedium: GoogleFonts.inter(fontSize: 14, color: textSecondary),
    ),
  );
}
DART

# Add to dependencies
flutter pub add google_fonts
```

**Day 2: Component Library**
```bash
mkdir -p lib/widgets/common

# Create reusable button component
cat > lib/widgets/common/primary_button.dart << 'DART'
import 'package:flutter/material.dart';
import '../../theme/app_theme.dart';
import '../../theme/spacing.dart';

class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  final bool isLoading;
  
  const PrimaryButton({
    required this.label,
    required this.onPressed,
    this.isLoading = false,
  });
  
  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: AppTheme.primaryColor,
        padding: EdgeInsets.symmetric(
          horizontal: Spacing.lg,
          vertical: Spacing.md,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),  // Rounded, modern
        ),
      ),
      child: isLoading 
        ? SizedBox(
            height: 20,
            width: 20,
            child: CircularProgressIndicator(color: Colors.white),
          )
        : Text(
            label,
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
    );
  }
}
DART
```

### Week 2: Key Screens (Wireframes → Code)

**Process for Each Screen:**

1. **Sketch on Paper** (5 min)
   - Draw boxes for each component
   - Label what goes where
   - Don't worry about beauty!

2. **Find Inspiration** (10 min)
   - Search Dribbble: "dating app [screen name]"
   - Pick 2-3 designs you like
   - Screenshot and save

3. **Wireframe in Figma** (30 min) - FREE!
   - Go to figma.com (free account)
   - Use "Phone Frame" template
   - Drag rectangles for components
   - Add text labels
   - Export as PNG

4. **Implement in Flutter** (2-4 hours)
   - Start with scaffold
   - Add components one-by-one
   - Use hot reload to see instantly

**Example: Discovery Screen Wireframe**

```
Figma → File → New Design File → Use "iPhone 14" frame

Components to add:
┌─────────────────────────┐
│ ┌─────────────────────┐ │ ← Image (Rectangle with rounded corners)
│ │                     │ │
│ │   [User Photo]      │ │   Height: 60% of screen
│ │                     │ │
│ └─────────────────────┘ │
│                         │
│ Name, 28  📍 2mo ago    │ ← Text (Headline)
│                         │
│ 🎯 87% Match            │ ← Text (Body)
│ • Same area             │
│ • Both love hiking      │ ← Auto Layout (Column with bullets)
│                         │
│ ┌───────┐ ┌───────────┐│
│ │ Pass  │ │   Like   ││ ← Buttons (Rounded rectangles)
│ └───────┘ └───────────┘│
└─────────────────────────┘

Export → PNG → Save to design_inspiration/wireframes/
```

---

## 📱 Screen-by-Screen Design Guide

### Screen 1: Onboarding Wizard

**Goal**: Get user from signup → first swipe in <3 minutes

**Flow**:
```
Welcome Screen
    ↓
Step 1: Name & Birthday
    ↓
Step 2: Photos (3 min upload)
    ↓
Step 3: Niche Validation ("When did you move?")
    ↓
Step 4: Preferences (age, distance)
    ↓
Step 5: Enable Notifications (optional)
    ↓
Discovery Screen (START SWIPING!)
```

**Design Principles:**
- ✅ Progress bar at top (user sees "almost done!")
- ✅ ONE question per screen (don't overwhelm)
- ✅ "Skip for now" on optional fields
- ✅ Big, friendly CTAs ("Next", "Let's Go!", "Start Matching")

**Copy Tone (Friendly, Not Corporate):**
```
❌ BAD: "Please provide your date of birth for age verification"
✅ GOOD: "When's your birthday? 🎂 (We only show your age)"

❌ BAD: "Upload profile photo"
✅ GOOD: "Show off your smile 📸 (3 photos minimum)"

❌ BAD: "Set preferences"
✅ GOOD: "Who are you hoping to meet?"
```

### Screen 2: Discovery (Swipe)

**Innovation: "Why This Person?" Card**

Instead of just showing a photo, show context:

```dart
// Pseudocode structure
Stack(
  children: [
    // Background: User photo
    CachedNetworkImage(candidate.photoUrl),
    
    // Gradient overlay (makes text readable)
    Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.bottomCenter,
          end: Alignment.center,
          colors: [Colors.black87, Colors.transparent],
        ),
      ),
    ),
    
    // Content overlay
    Positioned(
      bottom: 100,
      left: 16,
      right: 16,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Name & Age (Standard)
          Text("${candidate.name}, ${candidate.age}"),
          
          // UNIQUE: Niche context
          Text("📍 Moved to ${candidate.city} ${timeAgo(candidate.moveDate)}"),
          
          // UNIQUE: Match score (transparency)
          MatchScoreChip(score: candidate.matchScore),
          
          // UNIQUE: Why you matched
          ReasonsList(reasons: candidate.matchReasons),
        ],
      ),
    ),
    
    // Action buttons
    Positioned(
      bottom: 20,
      child: Row(
        children: [
          PassButton(),
          Spacer(),
          InfoButton(),  // See full profile
          Spacer(),
          LikeButton(),
        ],
      ),
    ),
  ],
)
```

**Visual Hierarchy:**
1. **Photo** (biggest, eye-catching)
2. **Name** (bold, 24pt)
3. **Niche context** (medium, 16pt, icon for scanability)
4. **Match details** (small, 14pt, collapsible)

### Screen 3: Match Notification

**Don't be boring! Celebrate the match:**

```
┌─────────────────────────┐
│    🎉 IT'S A MATCH!     │  ← Big, exciting headline
│                         │
│  ┌────┐      ┌────┐    │
│  │You │ ❤️❤️ │Anna│    │  ← Photos side-by-side
│  └────┘      └────┘    │     with hearts animation
│                         │
│  "We both love brunch   │  ← Shared interest
│   and specialty coffee" │     (personalized!)
│                         │
│  ┌─────────────────┐    │
│  │  Say Hi to Anna │    │  ← Clear CTA
│  └─────────────────┘    │
│                         │
│  [Keep Swiping]         │  ← Secondary action
└─────────────────────────┘
```

**Animation** (Flutter):
```dart
class MatchAnimation extends StatefulWidget {
  @override
  _MatchAnimationState createState() => _MatchAnimationState();
}

class _MatchAnimationState extends State<MatchAnimation> 
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 600),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.elasticOut),
    );
    
    _controller.forward();
  }
  
  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scaleAnimation,
      child: Text("🎉 IT'S A MATCH!", style: headlineStyle),
    );
  }
}
```

### Screen 4: Messaging

**Problem**: Blank text box is intimidating
**Solution**: Conversation starters

```
┌─────────────────────────┐
│  ← Anna                 │
│                         │
│  💬 Start the chat:     │
│                         │
│  You both mentioned:    │
│  • New to Stockholm     │  ← Pull from profiles
│  • Love hiking          │
│                         │
│  Try asking:            │
│  ┌─────────────────────┐│
│  │ "Best hiking spot   ││  ← Template starters
│  │  you've found near  ││     (tap to use)
│  │  the city?"         ││
│  │     [Use this 👆]    ││
│  └─────────────────────┘│
│                         │
│  Or write your own:     │
│  [___________________]  │  ← Text input
│  [Send]                 │
└─────────────────────────┘
```

After first message, switch to standard chat UI:
```
┌─────────────────────────┐
│  ← Anna                 │
│                         │
│  ┌──────────────────┐   │  ← Their message (left)
│  │ Hey! Yeah, I love│   │     Gray bubble
│  │ Tyresta forest!  │   │
│  └──────────────────┘   │
│  10:32 AM               │
│                         │
│           ┌──────────┐  │  ← Your message (right)
│           │ Nice! I  │  │     Brand color bubble
│           │ haven't  │  │
│           │ been yet │  │
│           └──────────┘  │
│           10:35 AM ✓✓   │
│                         │
│  [________________] [>] │  ← Input bar
└─────────────────────────┘
```

---

## 🎨 Animation & Delight (Small Touches That Matter)

### Micro-Interactions

**1. Swipe Feedback**
```dart
// Visual feedback as user swipes
Container(
  decoration: BoxDecoration(
    border: Border.all(
      color: swipeDirection == 'right' 
        ? Colors.green.withOpacity(swipeAmount)  // Green border on like
        : Colors.red.withOpacity(swipeAmount),   // Red border on pass
      width: 3,
    ),
  ),
)
```

**2. Like Button Press**
```dart
// Scale animation on tap
GestureDetector(
  onTapDown: (_) => setState(() => _isPressed = true),
  onTapUp: (_) => setState(() => _isPressed = false),
  child: AnimatedScale(
    scale: _isPressed ? 0.9 : 1.0,
    duration: Duration(milliseconds: 100),
    child: LikeButton(),
  ),
)
```

**3. Loading States (Never show blank screens)**
```dart
// Shimmer loading for profile cards
class ProfileCardShimmer extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: Column(
        children: [
          Container(height: 400, color: Colors.white),  // Photo placeholder
          SizedBox(height: 16),
          Container(height: 24, width: 150, color: Colors.white),  // Name
          Container(height: 16, width: 200, color: Colors.white),  // Bio
        ],
      ),
    );
  }
}
```

**4. Empty States (Make them friendly, not punishing)**

When user has no matches:
```
❌ BAD:
┌─────────────────────────┐
│  No matches yet.        │
└─────────────────────────┘

✅ GOOD:
┌─────────────────────────┐
│         🌟              │
│                         │
│  Keep swiping!          │
│                         │
│  You'll get matches as  │
│  more people join.      │
│                         │
│  Tip: Complete your     │
│  profile to boost       │
│  visibility by 3x       │
│                         │
│  [Complete Profile]     │
└─────────────────────────┘
```

---

## 🧰 Tools for Non-Designers

### Free Design Tools

**1. Figma (Wireframing)**
- URL: figma.com
- Cost: FREE
- Use: Create screen layouts before coding
- Time: 30 min/screen

**2. Coolors (Color Palettes)**
- URL: coolors.co
- Cost: FREE
- Use: Generate color schemes
- Tip: Lock your brand color, generate rest

**3. Unsplash (Placeholder Images)**
- URL: unsplash.com
- Cost: FREE
- Use: High-quality photos for mockups
- Flutter: `cached_network_image` package

**4. LottieFiles (Animations)**
- URL: lottiefiles.com
- Cost: FREE (10 downloads/day)
- Use: Ready-made animations (loading, success, etc.)
- Flutter: `lottie` package
- Example: Match celebration animation

**5. Dribbble (Inspiration)**
- URL: dribbble.com
- Cost: FREE to browse
- Search: "dating app ui", "profile card", etc.
- Time: 10 min research before each screen

---

## 📋 Implementation Checklist

### Before You Code ANY Screen:

- [ ] **Sketch on paper** (5 min) - boxes and labels
- [ ] **Find 2-3 examples** on Dribbble (10 min)
- [ ] **List components needed** (10 min)
  - What buttons?
  - What text?
  - What images?
  - What spacing?
- [ ] **Create Figma wireframe** (30 min) - optional but helpful
- [ ] **Break into widgets** (15 min) - plan your Flutter structure

### While Coding:

- [ ] Use **existing components** from lib/widgets/common/
- [ ] Follow **spacing constants** (Spacing.md, Spacing.lg)
- [ ] Use **theme colors** (AppTheme.primaryColor)
- [ ] Test on **multiple screen sizes** (iPhone SE, iPhone 14 Pro Max)
- [ ] Add **loading states** (shimmer, spinners)
- [ ] Add **empty states** (friendly, helpful)
- [ ] Add **error states** ("Oops! Try again")

### After Coding:

- [ ] **Accessibility**: Text contrast ratio >4.5:1 (use: webaim.org/resources/contrastchecker/)
- [ ] **Dark mode**: Does it look good? (toggle in settings)
- [ ] **Animation**: Does it feel smooth? (60fps target)
- [ ] **User test**: Show to 1 friend, watch them use it

---

## 🚀 Your First 3 Screens (This Week)

### Priority 1: Discovery Screen (T035)

**What to build:**
1. Swipeable card stack (use `flutter_card_swiper` package)
2. User photo + gradient overlay
3. Name, age, niche context
4. Match score chip
5. Pass/Like buttons

**Packages to use:**
```yaml
dependencies:
  flutter_card_swiper: ^7.0.0  # Swipe mechanics
  cached_network_image: ^3.3.0  # Fast image loading
  shimmer: ^3.0.0  # Loading states
```

**Time estimate:** 4-6 hours

### Priority 2: Match Notification (Part of T035)

**What to build:**
1. Full-screen overlay
2. Animated "It's a Match!" text
3. Side-by-side photos
4. "Say Hi" button
5. "Keep Swiping" button

**Animation:**
```dart
// Use ScaleTransition + CurvedAnimation
// Curve.elasticOut for bouncy "celebration" feel
```

**Time estimate:** 2-3 hours

### Priority 3: Messaging Screen (T041)

**What to build:**
1. Conversation starters (if first message)
2. Standard chat UI (after first message)
3. Text input with send button
4. Online indicator
5. Typing indicator (deferred to T044)

**Packages:**
```yaml
dependencies:
  flutter_chat_ui: ^1.6.13  # Pre-built chat components
  # OR build custom (more control, more time)
```

**Time estimate:** 3-4 hours (using package) or 6-8 hours (custom)

---

## 💡 Your Unique Visual Identity

**What makes YOUR app different visually:**

1. **Brand Color**: Coral (#FF7F50) - warm but not cliché
2. **Illustrations**: Use Lottie animations for delight
3. **Match Score**: Show compatibility % (transparency)
4. **Niche Context**: Always visible (moved date, custody schedule)
5. **Conversation Starters**: Built-in (reduce anxiety)

**Visual Language:**
- **Friendly**: Rounded corners (12px), soft shadows
- **Modern**: Clean layout, lots of whitespace
- **Trustworthy**: Transparent (show why matches work)
- **Delightful**: Small animations (NOT overdone)

---

## 🎯 Next Steps

**This Week:**
1. ✅ Read this guide (you're here!)
2. Set up design system (colors, fonts, spacing) - 2 hours
3. Screenshot 10 dating app screens from competitors - 30 min
4. Create Figma wireframes for Discovery, Match, Messaging - 2 hours
5. Implement Discovery screen (T035) - 6 hours

**Next Week:**
6. Implement offline cache (T037) - 4 hours
7. Implement messaging (T041, T044) - 8 hours
8. User test with 2 friends - 1 hour
9. Iterate based on feedback - 2 hours

**Total Time Investment:** ~25 hours = One focused work week

---

## 📚 Learning Resources

**Video Tutorials (Free):**
- Flutter UI Basics: youtube.com/flutterdev (official)
- Material Design 3: m3.material.io/develop/flutter
- Chat UI: "Flutter Chat App Tutorial" (search YouTube)

**Written Guides:**
- Flutter Cookbook: docs.flutter.dev/cookbook
- Material Design Guidelines: m3.material.io

**Design Inspiration:**
- Dribbble: dribbble.com/tags/dating_app
- Mobbin: mobbin.com (mobile design patterns)
- Refactoring UI: refactoringui.com (paid book but GOLD)

---

## ✅ Success Criteria

You'll know your UI is GOOD when:
- [ ] A new user understands what to do in <5 seconds
- [ ] Friend can complete onboarding without asking questions
- [ ] No blank/confusing screens (loading, empty, error states)
- [ ] Animations feel smooth (not janky)
- [ ] Works on small phones (iPhone SE) and big (iPhone 14 Pro Max)
- [ ] Dark mode doesn't break anything
- [ ] You feel PROUD showing it to others

**Remember**: Your first design won't be perfect. Ship it, get feedback, iterate!

---

**Last Updated**: 2026-02-02  
**Next Review**: After implementing Discovery screen (T035)

Good luck! You've got this. 🚀
