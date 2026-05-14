# Flavor Strategy — DatingApp Multi-App Portfolio

> **Status: DECIDED** — 4 flavors confirmed. Updated 2026-03-26.

---

## Portfolio Overview (4 Flavors)

| # | Codename | Name | Concept | Inspiration | Status |
|---|----------|------|---------|-------------|--------|
| 1 | **dejting** | Dejting | Mainstream dating — serious & casual | Hinge + Tinder | ✅ EXISTS |
| 2 | **voice** | Voice | Voice-first blind dating, no photos | Love is Blind | 🆕 BUILD NEXT |
| 3 | **darkness** | Darkness | BDSM, kink, alt-sexual, body-positive | Feeld / FetLife | 🔄 REBRAND FROM FLEET |
| 4 | **oldies** | Oldies | Senior dating, 50-65+, companionship | OurTime / SilverSingles | 🆕 PLANNED |

### Why These 4?

Each flavor targets a **completely distinct audience** with zero overlap:

```
              MAINSTREAM                    NICHE
                  │                           │
   ┌──────────────┤                           ├──────────────┐
   │   DEJTING    │                           │   DARKNESS   │
   │   18-45      │                           │   18-45      │
   │   Hinge/     │                           │   BDSM/kink  │
   │   Tinder     │                           │   Alt-sexual │
   │   Mainstream │                           │   Body-pos   │
   └──────────────┘                           └──────────────┘

   ┌──────────────┐                           ┌──────────────┐
   │   OLDIES     │                           │   VOICE      │
   │   50-65+     │                           │   25-40      │
   │   Senior     │                           │   Personality│
   │   Companion- │                           │   No photos  │
   │   ship       │                           │   Blind date │
   └──────────────┘                           └──────────────┘
       VISUAL ◄──────────────────────────► PERSONALITY
```

**Market gap alignment:**
- **Dejting** → Mainstream Swedish dating (Hinge/Tinder alternative, local-first)
- **Voice** → Anti-superficiality gap (no "blind dating" app exists at scale)
- **Darkness** → Alt-sexual/kink segment (Feeld is only real competitor, no Swedish option)
- **Oldies** → Senior dating in Sweden (OurTime is mediocre, no local option, highest ARPU potential)

**What we dropped** (and why):
- ~~Nära (curated daily picks)~~ → Too similar to Dejting. Curated picks can be a Dejting premium feature.
- ~~Pulse (time-windowed)~~ → Lowest monetizer. Thursday model proved hard to grow. Can add "live events" inside any flavor later.

---

## Flavor 1: DEJTING (exists) — "Find your person"

**Target**: 18-45, relationship-seeking AND casual, mainstream Swedish dating.
**Vibe**: Warm coral (#FF7F50), intentional, prompts-driven. The "default" dating app.
**Inspiration**: Hinge (prompts, compatibility) + Tinder (swipe UX, broad appeal).

### Current Config
```dart
FlavorFeatureFlags(
  dailySwipeLimit: 10,
  showCompatibilityScores: true,
  prominentVoicePrompts: true,
  showProfilePrompts: true,
  photoForwardDiscovery: false,
);
```

### What's Built
- Hinge-style scrollable profile cards with text prompts
- Compatibility score badge on profiles
- Voice prompt integration (record + listen)
- 10 daily likes forces intentionality
- Full onboarding wizard
- Photo upload + moderation pipeline
- SignalR real-time messaging
- Swipe + match system

### What's Missing
- Nothing blocking. This is the fully functional baseline app.
- Monetization tiers (Plus/Premium) not yet implemented.

---

## Flavor 2: VOICE (new) — "Hear them first"

> 🎯 **"Love is Blind" concept — fall for their voice, not their face.**

**Target**: 25-40, personality-focused, frustrated by looks-based matching.
**Vibe**: Warm purple/indigo, intimate, voice-centric.
**Inspiration**: Love is Blind (Netflix). No direct app competitor at scale.

### Core Mechanic

```
DISCOVERY          CONVERSATION           REVEAL
───────────        ──────────────         ──────
Name + Age         Voice messages         Photos unlock
City + Interests   Answer questions →     after mutual
Voice answers      Hear their answers     decision or
NO PHOTOS          NO PHOTOS              message threshold
```

**How it works:**
1. **Onboarding**: Record voice answers to 3-5 personality questions
2. **Discovery**: Cards show name, age, city, interests + play button for voice answers. NO photos.
3. **Matching**: Like/pass based on voice + text. Mutual like = match.
4. **Chat**: Voice messages encouraged. Photos still hidden.
5. **Reveal**: After message threshold OR mutual "reveal" button, photos unlock simultaneously.

### What We Already Have

| Component | Status | Notes |
|-----------|--------|-------|
| Voice prompts (record/upload/play) | ✅ Built | photo-service: VoicePrompt model, AAC, moderation |
| Voice messages in chat | ✅ Built | photo-service: VoiceMessage model |
| Voice moderation (Whisper) | ✅ Built | Background transcription + text scanning |
| Photo storage + serving | ✅ Built | Need to conditionally hide |
| Compatibility scoring | ✅ Built | MatchmakingService multi-factor algorithm |
| FlavorId routing | ✅ Built | Backend filters by flavor |
| Safety/moderation | ✅ Built | LLM-based content moderation |

### What's NEW to Build

| Component | Effort | Description |
|-----------|--------|-------------|
| `hidePhotosInDiscovery` flag | S | Discovery cards show silhouette instead of photos |
| `voiceAnswersRequired` flag | S | Require 3+ voice answers during onboarding |
| `photoRevealThreshold` (int) | M | Messages before "reveal" button activates |
| Discovery card variant | M | Voice player prominent, silhouette image, name/age/interests |
| Photo visibility per match | M | `Match.PhotosRevealed` boolean, API gates photo URLs |
| Reveal flow UI | M | Mutual reveal button in chat + reveal animation |
| Voice question pool | S | Configurable voice prompt questions per flavor |
| Voice answer cards | L | New UI: voice player cards with waveform + question text |

**Estimated new work**: ~40-60h (reuses 70%+ of existing infrastructure)

### Proposed Config
```dart
FlavorFeatureFlags(
  dailySwipeLimit: 8,
  showCompatibilityScores: true,
  prominentVoicePrompts: true,
  showProfilePrompts: true,
  photoForwardDiscovery: false,
  // NEW:
  // hidePhotosInDiscovery: true,
  // voiceAnswersRequired: 3,
  // photoRevealThreshold: 15,
);
```

---

## Flavor 3: DARKNESS (rebrand from Fleet) — "Beyond the surface"

> 🔄 **Rebranded from "Fleet"**. Same codebase, new identity. BDSM, kink, alt-sexual, body-positive.

**Target**: 18-45, BDSM/kink community, sexually open, queer-inclusive, body-positive.
**Vibe**: Deep black + neon accents, bold, unapologetic. Dark UI literally.
**Inspiration**: Feeld (ENM/kink), FetLife (community), but as a modern swipe app.

### Why "Darkness"?
- Literal: dark theme, dark UI, nighttime energy
- Figurative: the "darker" side of dating — kink, BDSM, taboo interests
- Brand: bold, memorable, ownable. No ambiguity about what this app is for.

### Current Config (from Fleet)
```dart
FlavorFeatureFlags(
  dailySwipeLimit: 0,        // unlimited
  showCompatibilityScores: false,
  prominentVoicePrompts: false,
  showProfilePrompts: false,
  photoForwardDiscovery: true,
);
```

### What's Built (inherited from Fleet)
- Photo-forward discovery (0.65 aspect ratio, hidden bio)
- Unlimited swipes
- Dark theme (`FleetTheme.darkTheme`)
- All core infrastructure (auth, profiles, messaging, matching)

### What's NEW to Build

| Component | Effort | Description |
|-----------|--------|-------------|
| Rebrand: name, icons, splash | M | New app identity: "Darkness" branding, deep black + neon theme |
| Interest/kink tags | M | Profile tags for interests (BDSM, ENM, kink categories). Tag-based filtering. |
| Private photo albums | M | Reveal-on-request private photos. Key premium feature. |
| Couple/group profiles | M | Allow 2+ people to share a profile. Premium-gated. |
| Incognito mode | S | Browse without appearing in others' feeds. Premium feature. |
| Content guidelines | S | Clear rules: body-positive but no explicit nudity (App Store compliant) |

**Estimated new work**: ~30-50h (mostly branding + tag system + private albums)

### Key Design Notes
- **App Store compliance**: Must stay tasteful. No explicit photos. Tags use coded language where needed.
- **Privacy is paramount**: Many users don't want to be "found" by coworkers. Incognito mode is critical.
- **Body-positive**: No body-type filters. Inclusive of all bodies, genders, orientations.

---

## Flavor 4: OLDIES (new) — "Never too late"

> 🎯 **Senior dating for 50-65+. High ARPU, low competition, underserved market.**

**Target**: 50-65+, divorced/widowed/single, seeking companionship and romance.
**Vibe**: Warm, clean, large UI. Calming colors (warm gold/cream). Accessibility-first.
**Inspiration**: OurTime (Match Group), SilverSingles — but modern, Swedish, and not terrible.

### Why This Market?

**The numbers:**
- Sweden has ~1M people aged 60-75 with high smartphone adoption
- Senior dating apps charge 2-3x more than mainstream (OurTime ~$30/mo, SilverSingles ~$45/mo)
- Subscription renewal rates are highest in 50+ demographic (lower churn)
- No Swedish-focused senior dating app exists
- Pew Research: dating app usage among 55-64 doubled between 2013-2015, continues growing

**The opportunity:**
- **Highest willingness to pay** of any demographic (disposable income, serious intent)
- **Lowest competition** in Sweden (OurTime barely marketed here)
- **Highest loyalty** — seniors don't hop between 5 apps like 25-year-olds
- **Different needs** = different product = defensible niche

### Core Mechanic

```
SIMPLE DISCOVERY        REAL PROFILES           SAFE COMMUNICATION
──────────────          ──────────────          ──────────────────
Large cards             Verified photos         Video chat built-in
Big text, clear UI      Life story prompts      Message templates
No infinite scroll      "About my life now"     Safety tips on every
Limited daily picks     No games, no tricks     first message
```

**How it differs from Dejting:**
1. **Accessibility-first UI**: Larger fonts, higher contrast, simpler navigation, fewer nested screens
2. **Different prompts**: "What does your ideal Saturday look like?" not "Two truths and a lie"
3. **Life-stage content**: Prompts about grandchildren, retirement, travel, second chapters
4. **Video chat priority**: Older users prefer video calls before meeting IRL
5. **Safety emphasis**: Scam detection prominent (romance scams target seniors disproportionately)
6. **Curated daily picks**: Not infinite swiping — 5-8 quality matches per day
7. **Simpler onboarding**: Fewer steps, larger tap targets, optional phone support

### What's NEW to Build

| Component | Effort | Description |
|-----------|--------|-------------|
| Accessibility theme | M | Large fonts (18px+ base), high contrast, simplified nav, big tap targets |
| Senior-specific prompts | S | Life-stage appropriate questions (retirement, travel, family) |
| Video chat integration | L | In-app video calling (WebRTC or third-party SDK) |
| Curated daily picks mode | M | DailyPickStrategy exists — configure for 5-8 picks/day |
| Scam detection UI | M | Prominent warnings, "Is this a scam?" help button, verified badges |
| Simplified onboarding | M | Fewer wizard steps, larger inputs, optional guided setup |
| Age-gated discovery | S | Only show 45+ profiles (configurable floor) |

**Estimated new work**: ~60-80h (accessibility + video chat are the big items)

### Proposed Config
```dart
FlavorFeatureFlags(
  dailySwipeLimit: 8,          // curated, not infinite
  showCompatibilityScores: true,  // seniors value knowing "why" a match
  prominentVoicePrompts: false,   // text/video preferred over voice for this demo
  showProfilePrompts: true,       // life story prompts are essential
  photoForwardDiscovery: false,   // balanced layout, not photo-only
  // NEW:
  // accessibilityMode: true,
  // videoChatEnabled: true,
  // dailyPicksMode: true,
  // maxDailyPicks: 8,
  // minAgeFilter: 45,
);
```

---

## New FlavorFeatureFlags Needed

| Flag | Dejting | Voice | Darkness | Oldies | Type |
|------|---------|-------|----------|--------|------|
| `dailySwipeLimit` | 10 | 8 | 0 | 8 | int ✅ exists |
| `showCompatibilityScores` | ✓ | ✓ | ✗ | ✓ | bool ✅ exists |
| `prominentVoicePrompts` | ✓ | ✓ | ✗ | ✗ | bool ✅ exists |
| `showProfilePrompts` | ✓ | ✓ | ✗ | ✓ | bool ✅ exists |
| `photoForwardDiscovery` | ✗ | ✗ | ✓ | ✗ | bool ✅ exists |
| `hidePhotosInDiscovery` | ✗ | **✓** | ✗ | ✗ | bool 🆕 |
| `voiceAnswersRequired` | 0 | **3** | 0 | 0 | int 🆕 |
| `photoRevealThreshold` | 0 | **15** | 0 | 0 | int 🆕 |
| `privateAlbums` | ✗ | ✗ | **✓** | ✗ | bool 🆕 |
| `coupleProfiles` | ✗ | ✗ | **✓** | ✗ | bool 🆕 |
| `incognitoMode` | ✗ | ✗ | **✓** | ✗ | bool 🆕 |
| `accessibilityMode` | ✗ | ✗ | ✗ | **✓** | bool 🆕 |
| `videoChatEnabled` | ✗ | ✗ | ✗ | **✓** | bool 🆕 |
| `dailyPicksMode` | ✗ | ✗ | ✗ | **✓** | bool 🆕 |

**Summary**: 5 existing flags + 9 new flags needed.

---

## Backend Changes Per Flavor

### Voice (most new backend work)
1. **Match table**: Add `PhotosRevealed` bool, `RevealedAt` DateTime
2. **Photo API**: Gate photo URLs on `PhotosRevealed` status
3. **Voice question pool**: `FlavorVoiceQuestions` table
4. **Reveal endpoint**: `POST /api/matches/{id}/reveal`

### Darkness (medium backend work)
1. **Interest/kink tags**: New `ProfileTags` table + filtering
2. **Private albums**: Gated photo visibility per match
3. **Couple profiles**: `ProfileGroupId` linking mechanism
4. **Incognito**: Discovery exclusion flag

### Oldies (medium backend work)
1. **Age-gated discovery**: Matchmaking filter enforcing age floor
2. **Daily picks mode**: DailyPickStrategy already exists — configure for Oldies
3. **Video chat**: WebRTC signaling via SignalR (or third-party integration)
4. **Scam detection**: Enhanced safety flags + moderation rules

### All Flavors
1. **Per-flavor config** in `appsettings.json` (planned in spec 004)
2. **FlavorId on Match**: Track match origin flavor

---

## Build Priority

| Phase | Flavor | Effort | Revenue | Reasoning |
|-------|--------|--------|---------|-----------|
| **Now** | Dejting | Done | ★★★★★ | Core app. Ship + monetize. |
| **Next** | Voice | ~50h | ★★★★☆ | Most differentiated. No competitor. Viral potential. Reuses voice infra. |
| **Then** | Darkness | ~40h | ★★★☆☆ | Fleet code exists — rebrand + add kink features. Niche but loyal users. |
| **Later** | Oldies | ~70h | ★★★★★ | Highest ARPU potential but needs accessibility + video work. Build after the others prove the model. |

---

## Cross-Flavor Strategy

### Hard Isolation (Recommended)
Each flavor is its own world. Dejting users never see Voice users. Darkness users never see Oldies users.

**Why hard isolation:**
- Each app tells a fundamentally different story
- Mixing BDSM profiles into a senior dating app = disaster
- Voice's "blind" concept breaks if cross-matched with Dejting's photo profiles
- Clearer marketing: each app has ONE promise

### Cross-Sell Opportunity
- Users CAN use multiple apps (same Keycloak account, different FlavorId per profile)
- "DatingApp Universe" bundle subscription covers all flavors at discount
- In-app banners: "Try Voice — a completely different dating experience"

---

## Flavors Considered & Rejected

| Concept | Why Rejected |
|---------|-------------|
| **Nära (curated daily picks)** | Too similar to Dejting. Daily-picks can be a Dejting premium feature instead of a separate app. |
| **Pulse (time-windowed)** | Lowest monetizer. Thursday model proved hard to sustain. Can add "live events" inside any flavor. |
| **Fleet (original name)** | Rebranded to "Darkness" — name didn't match the alt-sexual positioning. |
| **Djup (quiz-heavy)** | eHarmony owns this niche. Questionnaire UX is boring. |
| **Trygga (women-first)** | Bumble owns this. Safety should be in ALL flavors. |
| **Lokal (events-based)** | Needs event management system. Too much new infrastructure. |

---

## Open Decisions

### D1: Voice reveal mechanic
- **Option A**: Mutual reveal (both tap "show photos" → simultaneous)
- **Option B**: Message threshold (auto after 15 msgs)
- **Option C**: Time-based (after 48h)
- **Recommendation**: A (most dramatic, Love is Blind energy)

### D2: Darkness App Store strategy
- Content must stay App Store compliant (no explicit imagery)
- Kink tags use tasteful language
- Private albums require match approval before viewing
- Consider web-only version for less restricted content

### D3: Oldies video chat implementation
- **Option A**: WebRTC via SignalR (full control, more work)
- **Option B**: Third-party SDK (Agora/Twilio — faster, has cost)
- **Recommendation**: B for MVP, migrate to A later if volume justifies

### D4: Cross-flavor matching
- **Decision: Hard isolation** — each app is its own world
- Same Keycloak account works across all, but separate profiles per flavor
