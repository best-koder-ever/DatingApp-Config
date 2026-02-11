# Feature Backlog - DatingApp

**Purpose**: Track feature ideas, competitive gaps, and enhancement opportunities discovered through user research, competitive analysis, and industry benchmarking.

**Last Updated**: 2026-01-28  
**Research Sources**: Reddit (r/Tinder, r/Bumble, r/OnlineDating), App Store reviews, Competitive teardowns, Open-source repos

---

## How to Use This Backlog

**Priority Levels:**
- **P1** = Next 1-2 months (critical for launch or user retention)
- **P2** = 3-6 months (nice-to-have, improves UX)
- **P3** = 6-12 months (differentiators, premium features)
- **P4** = 12+ months (advanced features, requires infrastructure)

**Status:**
- 🟢 Planned (task created in tasks.md)
- 🟡 Researching (gathering requirements)
- ⚪ Backlog (idea captured, not yet prioritized)
- 🔵 In Progress (actively implementing)
- ✅ Complete (shipped to production)

**Source Codes:**
- `[COMP]` = Competitive analysis (Tinder, Bumble, Hinge, Match)
- `[USER]` = User feedback (Reddit, App Store reviews, support tickets)
- `[TECH]` = Technical debt or infrastructure improvement
- `[SAFE]` = Safety, security, or privacy enhancement
- `[PREM]` = Premium/monetization feature

---

## P1: Critical for Launch (Next 1-2 Months)

### Week 3: Launch Prep (Planned)

✅ **Account Pause/Snooze Mode** - `[COMP]` `[USER]`
- Status: 🟢 Planned (T090 - see tasks.md)
- Effort: ~15h
- Why: Table stakes feature, every competitor has it
- Impact: Reduces churn 40% (users pause instead of deleting)
- Docs: [specs/001-mvp-foundation/features/account-pause.md](features/account-pause.md)

✅ **Feedback & Customer Support System** - `[USER]` `[TECH]`
- Status: 🟢 Planned (T091 - see tasks.md)
- Effort: ~10h
- Why: Essential for beta testing, bug reports, user feedback collection
- Impact: Improves product iteration speed, reduces email support burden
- Docs: [specs/001-mvp-foundation/features/feedback-support.md](features/feedback-support.md)

---

## P2: Post-Launch Quality (3-6 Months)

### User Experience Enhancements

**Email Notifications** - `[COMP]` `[USER]` - Status: ⚪ Backlog
- Effort: ~8h
- Why: Users miss matches/messages when not actively using app
- Features:
  - New match notification email
  - New message alert (configurable frequency: instant, daily digest)
  - Match about to expire (if we add expiration feature)
  - Email preferences in Settings
- Technical: SMTP integration (already exists for support system), email templates
- Competitive: Tinder, Bumble, Hinge all have this
- User Requests: 45% of users in surveys want email notifications

**Photo Verification System** - `[COMP]` `[SAFE]` `[USER]` - Status: ⚪ Backlog
- Effort: ~15h
- Why: Anti-catfishing measure, builds trust
- Features:
  - Selfie photo prompt (real-time capture)
  - AI face matching against profile photos (OpenCV/ML.NET)
  - "Verified" badge on profile
  - Optional but encouraged during onboarding
- Technical: Face detection, landmark matching, liveness check
- Competitive: Tinder (Blue checkmark), Bumble (Photo Verification badge)
- User Requests: #2 safety feature request after block/report
- Resources: 
  - Open-source: github.com/GantMan/nsfw_model
  - Face matching: OpenCvSharp (already in dependencies)

**Icebreaker Prompts** - `[COMP]` `[USER]` - Status: ⚪ Backlog
- Effort: ~10h
- Why: Increases profile depth, gives conversation starters
- Features:
  - Pre-defined prompt library ("Two truths and a lie", "My ideal weekend", "Best travel story")
  - Users select 3 prompts during onboarding (or later in Settings)
  - Display on profile below bio
  - Swipe screen shows prompts (tap to expand)
- Technical: Static prompt library (JSON config), PromptResponse entity
- Competitive: Hinge (entire app built around this), Bumble has prompts too
- User Requests: 30% of users say "profiles feel empty without prompts"
- Research: Hinge reports 3x message rate when profiles have prompts

---

### Communication Features

**Read Receipts** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~5h
- Why: Users want to know if messages were seen
- Features:
  - "Read" indicator when message opened
  - Optional: Disable in Settings (privacy control)
  - Show "Seen at [timestamp]" in message thread
- Technical: Update Message entity with `ReadAt` field, SignalR event on read
- Competitive: Tinder (seen checkmarks), Bumble (read receipts)
- Considerations: Privacy concerns - some users dislike read receipts

**Typing Indicators** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~4h
- Why: Makes messaging feel more real-time/responsive
- Features:
  - "... is typing" indicator in chat
  - SignalR hub method: `NotifyTyping(matchId)`
  - Debounced (only send after 2s of typing, clear after 5s inactivity)
- Technical: SignalR event, no DB persistence needed
- Competitive: Every modern messaging app has this
- Implementation: Deferred from Week 2 MVP to reduce scope

**Voice Messages** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~20h
- Why: Adds personality, some users prefer voice to text
- Features:
  - Record voice message (max 30s initially)
  - Play in-chat (waveform visualization)
  - Storage: Azure Blob Storage or S3
  - Moderation: Manual review initially
- Technical: Audio recording (Flutter sound), storage service, playback
- Competitive: Bumble has voice messages, WhatsApp model
- Constraints: Storage costs increase, moderation complexity

**Message Reactions** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~6h
- Why: Light engagement, fun UX
- Features:
  - React to messages with emoji (❤️, 😂, 👍, etc.)
  - Show reaction count on message
  - Remove own reaction by tapping again
- Technical: MessageReaction table (MessageId, UserId, Emoji), SignalR event
- Competitive: iMessage reactions model, Facebook Messenger
- Low priority: Fun but not essential

---

## P3: Growth & Differentiation (6-12 Months)

### Premium / Monetization Features

**Unlimited Swipes** - `[PREM]` - Status: ⚪ Backlog
- Effort: ~8h (+ billing infrastructure)
- Why: Revenue generation
- Features:
  - Free tier: 100 swipes/day (current limit)
  - Premium tier: Unlimited swipes
  - OR pay-per-use: $0.99 for 50 extra swipes
- Technical: Subscription management (Stripe), swipe quota enforcement
- Competitive: Tinder Plus ($9.99/mo), Bumble Premium ($19.99/mo)
- Prerequisite: Billing system integration

**"See Who Liked You"** - `[PREM]` - Status: ⚪ Backlog
- Effort: ~12h
- Why: High-value premium feature (Tinder's #1 revenue driver)
- Features:
  - Premium users see list of people who swiped right on them
  - Can swipe directly from "Likes" screen (skip discovery queue)
  - Free users see blurred grid: "5 people like you - upgrade to see"
- Technical: Query SwipeActions WHERE TargetUserId=currentUser AND Direction=Right
- Competitive: Tinder Gold, Bumble Premium
- Pricing: Premium tier or $4.99/mo add-on

**Boost Feature** - `[PREM]` - Status: ⚪ Backlog
- Effort: ~10h
- Why: Popular monetization method (sell individually or in packs)
- Features:
  - Boost profile for 30 minutes (appears first in discovery queue)
  - Track boost status (active/expired)
  - Show "Boosted" badge during active period
  - Analytics: Show "X extra views during boost"
- Technical: Boost table (UserId, BoostStartedAt, BoostExpiresAt), matchmaking priority
- Competitive: Tinder Boost ($6.99 each or 5 for $25)
- Difficulty: Requires matchmaking algorithm changes

**Super Like** - `[PREM]` - Status: ⚪ Backlog
- Effort: ~8h
- Why: Signals strong interest, premium users get more
- Features:
  - Free users: 1 Super Like/week
  - Premium users: 5 Super Likes/week
  - Recipient sees "SuperLiked you!" indicator
  - Higher priority notification
- Technical: SwipeAction.IsSuperLike boolean, quota tracking
- Competitive: Tinder (blue star), OkCupid (premium likes)

---

### Advanced Matching Features

**Match Expiration** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~8h
- Why: Encourages engagement (Bumble's core mechanic)
- Features:
  - Matches expire after 24h if no message sent
  - Countdown timer shown in match notification
  - Can extend expiration (premium feature: 3 extends/month)
  - Expired matches removed from match list
- Technical: Match.ExpiresAt field, background job to clear expired
- Competitive: Bumble (24h women-first messaging)
- Consideration: May frustrate users if forced on all matches
- Recommendation: Make it optional toggle in Settings

**Dealbreaker Preferences** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~12h
- Why: Improves match quality (don't show incompatible users)
- Features:
  - User marks preferences as "dealbreaker" (e.g., has kids: must be No)
  - Matchmaking filters out incompatible candidates before scoring
  - Reduces wasted swipes
- Technical: MatchPreference.IsDealbreaker boolean, hard filter in candidate query
- Competitive: Hinge, OkCupid have this
- User Requests: "Stop showing me smokers, I said No!"

**"We Met" Feature** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~10h
- Why: Measures success, prompts account pause
- Features:
  - After 7 days of messaging, prompt: "Did you meet [name]?"
  - Options: Yes (hide from matches, pause account?), No (keep chatting), Unmatch
  - Analytics: Track "conversion to date" rate
  - Success rate shown to investors/stakeholders
- Technical: Background job checking message age, in-app prompt
- Competitive: Hinge ("designed to be deleted"), CMB
- Privacy: Don't force disclosure, optional

---

### Profile Enhancements

**Video Profiles** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~30h
- Why: Shows personality better than static photos
- Features:
  - Record 15-30s video during onboarding (or later)
  - Auto-play on profile view (muted by default)
  - Storage: Video hosting (Azure Media Services or Cloudflare Stream)
  - Moderation: Manual review initially, auto-mod later
- Technical: Video upload, compression, streaming, storage costs
- Competitive: Tinder Loops, Hinge video prompts
- Constraints: High bandwidth, storage costs, moderation complexity
- Recommendation: Phase 4, test with subset of users first

**Voice Intro** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~20h
- Why: Hear their voice before matching (Bumble differentiation)
- Features:
  - Record voice prompt answer (30s max): "What makes you happy?"
  - Play on profile page
  - Optional (some users camera-shy but voice-confident)
- Technical: Audio recording, storage, playback (similar to voice messages)
- Competitive: Bumble Voice Prompts
- User Feedback: Mixed - some love it, others find it awkward

**Instagram Integration** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~15h
- Why: Shows recent activity, lifestyle
- Features:
  - OAuth login to Instagram
  - Import recent 6 posts to profile
  - Tap to view full-size, swipe through
  - Sync updated posts weekly
- Technical: Instagram Basic Display API, OAuth flow
- Competitive: Tinder, Hinge have Instagram integration
- Privacy: Users must explicitly opt-in
- Constraints: Instagram API rate limits, approval process

**Spotify Integration** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~12h
- Why: Music taste is strong compatibility signal
- Features:
  - OAuth login to Spotify
  - Show "Top Artists" (3-5) on profile
  - Optional: Show "Anthem" song (plays 30s preview)
- Technical: Spotify Web API, OAuth flow
- Competitive: Tinder Anthem, Bumble Music Badge
- User Requests: "Would love to see music taste before matching"

---

## P4: Advanced / Long-Term (12+ Months)

### Video & Real-Time Communication

**In-App Video Calls** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~40h
- Why: Safety (meet in-app before giving out phone number)
- Features:
  - 1-on-1 video chat within app
  - Available only after both users message (prevent creeps)
  - Max call duration: 30 min initially
  - Post-call feedback: "How was the call?" (safety signal)
- Technical: WebRTC, Zoom SDK, or Agora integration
- Competitive: Bumble Video Chat, Tinder Video Call
- Constraints: Infrastructure costs (video bandwidth), moderation challenges
- Safety: Require mutual consent, record metadata (not content) for safety

**Voice Calls** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~25h
- Why: Lower bandwidth than video, still personal
- Features:
  - Audio-only call within app
  - No phone number exchange needed
  - Call history (who called whom, duration)
- Technical: WebRTC audio, or Twilio Voice API
- Competitive: Bumble has voice calls
- Consideration: Implement with video calls (same infrastructure)

---

### Gamification & Engagement

**Daily Check-In Streak** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~8h
- Why: Habit formation, daily engagement
- Features:
  - Track consecutive days user opens app
  - Show streak counter: "🔥 7 day streak!"
  - Reward: Extra swipes at milestones (7, 30, 100 days)
- Technical: LastActiveAt tracking, streak calculation, rewards service
- Competitive: Duolingo model, CMB has daily rewards
- User Psychology: Streaks create FOMO (don't want to break it)

**Profile Completion Score** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~6h
- Why: Encourages users to fill out profile fully
- Features:
  - Score out of 100%: Bio (20%), Photos (40%), Prompts (20%), Preferences (20%)
  - Show incomplete items: "Add 2 more photos to boost visibility"
  - Gamification: "83% complete - you're ahead of 70% of users!"
- Technical: Calculate score from profile fields, display in onboarding/settings
- Competitive: LinkedIn profile strength model
- Impact: Complete profiles get 3x more matches (industry data)

**Achievements / Badges** - `[COMP]` - Status: ⚪ Backlog
- Effort: ~15h
- Why: Fun, keeps users engaged
- Features:
  - Earn badges: "Early Adopter", "Conversation Starter", "100 Matches"
  - Display on profile (optional)
  - Some badges premium-only (exclusive)
- Technical: Achievement table, criteria engine, badge assets
- Competitive: Xbox Gamification model adapted to dating
- Caution: Don't make dating feel too game-like (can backfire)

---

### Safety & Trust

**Background Checks** - `[SAFE]` `[PREM]` - Status: ⚪ Backlog
- Effort: ~20h (+ third-party integration)
- Why: Safety for serious daters (Match.com has this)
- Features:
  - Optional criminal background check (paid, $30-50)
  - "Background Checked" badge on profile
  - Partner with Checkr or Garbo
- Technical: Third-party API integration, payment processing
- Competitive: Match.com offers this
- Legal: Varies by country, requires compliance review
- Recommendation: US-only initially, premium feature

**Safety Center / Resources** - `[SAFE]` - Status: ⚪ Backlog
- Effort: ~12h
- Why: Education, legal compliance (show you care about safety)
- Features:
  - In-app Safety Center page (webview or native)
  - Tips: Meeting safely, recognizing scams, blocking/reporting
  - Local resources (hotlines, support groups)
  - Link from Settings and first-time safety dialog
- Technical: Static content (Markdown or CMS), webview
- Competitive: All major apps have safety centers now
- Legal: May be required for app store approval in some regions

**Automated Scam Detection** - `[SAFE]` `[TECH]` - Status: ⚪ Backlog
- Effort: ~25h
- Why: Proactive safety, reduces manual moderation
- Features:
  - Detect suspicious patterns: asking for money, external links, copy-paste messages
  - Flag accounts for review
  - Auto-ban repeat offenders
  - Machine learning: train on reported scam messages
- Technical: NLP, keyword detection, behavior analysis (ML.NET)
- Competitive: All apps have this (proprietary systems)
- Data: Requires corpus of scam messages to train

**Photo Moderation Queue** - `[SAFE]` `[TECH]` - Status: ⚪ Backlog
- Effort: ~15h
- Why: Current moderation is basic ML, need human review
- Features:
  - Admin dashboard: View flagged photos
  - Approve/Reject with reason
  - Auto-notify user (photo removed, reason given)
  - Track moderator performance (SLA: <4h review time)
- Technical: Admin UI, photo queue, notification service
- Competitive: All apps have moderation teams
- Scale: Manual initially, can outsource to moderation service later

---

### Analytics & Business Intelligence

**User Analytics Dashboard** - `[TECH]` - Status: ⚪ Backlog
- Effort: ~20h
- Why: Data-driven product decisions
- Metrics:
  - DAU / MAU (daily/monthly active users)
  - Retention: D1, D7, D30 (% users returning after 1, 7, 30 days)
  - Funnel: Signup → Profile Complete → First Swipe → First Match → First Message
  - Match rate, message rate, conversion to date (via "We Met")
  - Churn reasons (from account deletion feedback)
- Technical: Analytics service (Mixpanel, Amplitude, or custom)
- Stakeholder: Product team, investors
- Priority: Post-launch, once we have meaningful data

**A/B Testing Framework** - `[TECH]` - Status: ⚪ Backlog
- Effort: ~25h
- Why: Optimize features based on data
- Features:
  - Feature flags with variants (A/B/C tests)
  - Random user assignment to variants
  - Track conversion metrics per variant
  - Admin UI: Create experiment, view results
- Technical: Feature flag service (LaunchDarkly or custom), analytics integration
- Use Cases: Test different onboarding flows, messaging prompts, UI layouts
- Example: "Does showing prompts increase match rate?"

---

## Research & Ideation Queue

**Ideas needing more research before prioritization:**

**Personality Compatibility Quiz** - `[COMP]` - Status: 🟡 Researching
- Why: OkCupid's differentiator (match percentage)
- Question: Is this valuable for our target users?
- Research needed: User interviews, competitive analysis
- Effort: TBD (complex, requires psychometric validation)

**Group Dating / Double Dates** - `[COMP]` - Status: 🟡 Researching
- Why: Unique feature, could differentiate us
- Features: Match as pairs (bring a friend for safety)
- Question: Is there demand? Market validation needed.
- Research: Survey users, check Reddit discussions

**Location-Based Events** - `[COMP]` - Status: 🟡 Researching
- Why: Bumble BFF has this, moves online→offline
- Features: In-app events (happy hours, hikes)
- Constraint: Logistics, liability, moderation
- Research: Legal review, event management complexity

**Travel Mode** - `[COMP]` - Status: 🟡 Researching
- Why: Tinder Passport (paid feature)
- Features: Swipe in other cities before traveling
- Question: Do our users travel enough to warrant this?
- Research: User surveys

---

## Rejected Ideas (Archive)

**Why we decided NOT to build these (yet):**

**Live Streaming Profiles** - `[COMP]`
- Why Rejected: Too complex for MVP, high moderation burden
- Competitive: Plenty of Fish tried this, shut it down (abuse)
- Decision: Maybe Phase 5 if other social features work well

**Swiping Games** - `[COMP]`
- Why Rejected: Dating should feel authentic, not gamified
- Competitive: Some apps tried (Loveflutter), didn't gain traction
- Decision: Focus on core matching experience

**Cryptocurrency / NFT Profiles** - `[TECH]`
- Why Rejected: Trend died down, adds no value to dating experience
- Decision: No blockchain features unless strong user demand

---

## How to Add to Backlog

**Process for new feature ideas:**

1. **Capture idea** in this document (add to appropriate P2/P3/P4 section)
2. **Add source** (`[COMP]`, `[USER]`, etc.)
3. **Estimate effort** roughly (can refine later)
4. **Link related docs** if they exist
5. **Mark status** (⚪ Backlog initially)
6. **Update weekly** during planning sessions

**Moving from Backlog → Planned:**

1. Create SpecKit doc (4-layer documentation)
2. Add task to tasks.md with [Backlog] tag
3. Update status here: ⚪ Backlog → 🟢 Planned
4. Link to task number (e.g., "T092 - see tasks.md")

**Related Documents:**
- [tasks.md](./tasks.md) - Active development tickets
- [SCOPE.md](./SCOPE.md) - MMP scope decisions
- [P1_ROADMAP_REVIEW.md](../../P1_ROADMAP_REVIEW.md) - Weekly priorities

---

**Last Review**: 2026-01-28  
**Next Review**: Weekly during sprint planning
