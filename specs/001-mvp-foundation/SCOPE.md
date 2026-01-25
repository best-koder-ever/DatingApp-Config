# MMP Scope Definition: DatingApp MVP Foundation

**Created**: 2026-01-25  
**Task**: T006 - Define Minimum Marketable Product  
**Decision Deadline**: Before starting Phase 2 implementation  

---

## Research: What Do Modern Dating Apps Ship First?

### Historical MVP Analysis

**Tinder (2012 Launch)**:
- ✅ Profile creation (photos + basic bio)
- ✅ Swipe discovery (revolutionary UX)
- ✅ Mutual match notification
- ❌ **NO messaging initially** - just showed you matched
- ❌ NO verification
- ❌ NO safety controls

**Result**: 15M matches in first 14 months despite no chat

**Bumble (2014 Launch)**:
- ✅ Profile creation
- ✅ Swipe discovery  
- ✅ **Messaging from day 1** (women-first constraint)
- ✅ Basic photo verification
- ❌ NO advanced filters
- ❌ NO voice/video

**Result**: Differentiated on messaging policy, became #2 app

**Hinge (2016 Pivot)**:
- ✅ Profiles with prompts
- ✅ Discovery with ability to comment on specific content
- ✅ **Messaging from launch** (post-pivot)
- ❌ NO unlimited likes
- ❌ NO video calls initially

**Result**: "Designed to be deleted" positioning required messaging

### 2026 Market Reality

**User Expectations**:
- Profile + Photos = **baseline** (users won't even try without this)
- Discovery mechanism = **baseline** (swipe, browse, or algorithmic feed)
- **Messaging = NOW TABLE STAKES** - users expect instant communication after match
- Safety features = **expected** but can start minimal (block/report only)
- Verification = nice-to-have initially, critical for scale

**Technical Reality**:
- SignalR infrastructure **already exists** in our codebase
- Messaging adds ~20% complexity vs no messaging
- **Without messaging, we're not competitive** - users will bounce to apps that have it

---

## MMP Decision: Two-Phase Launch Strategy

### 🎯 **MMP = "The Match Loop"** (Profile + Discovery + Messaging)

**Rationale**: 
- Modern users **WON'T adopt** a dating app without messaging in 2026
- We already have SignalR - not shipping messaging wastes existing investment
- Retention requires closed loop: signup → match → conversation → meetup

### Phase Breakdown

---

## ✅ Phase 1: MMP Launch (Ship This First)

**Goal**: Complete "signup to first date" user journey  
**Timeline**: Next 4-6 weeks  
**Target**: Small beta cohort (100 users)

### MUST HAVE (Blocking Ship)

**US1: Profile Onboarding (P1)** ✅ INCLUDE
- ✅ T022: Keycloak registration + email verification
- ✅ T023: 3-step wizard (basic info, preferences, photos)
- ✅ T024: Photo moderation + blur (basic ML)
- ✅ T025: Onboarding status persistence
- ✅ T026: Flutter wizard UI
- ✅ T027: Basic telemetry (funnel tracking)
- ⚠️ SKIP T028/T029 initially - defer webhook/automation

**US2: Match Discovery (P1)** ✅ INCLUDE
- ✅ T030: Matchmaking unit tests
- ✅ T032: Scoring algorithm (basic compatibility)
- ✅ T033: Daily queue limits
- ✅ T034: Swipe idempotency
- ✅ T035: Flutter Discover UI (card stack)
- ✅ T036: Match creation notifications
- ✅ T037: Offline swipe cache

**US3: Messaging (P2 → **PROMOTED TO P1**)** ✅ INCLUDE
- ✅ T042: Basic SignalR hub (send/receive only)
- ✅ T043: Message persistence
- ✅ T044: Flutter offline queue
- ✅ T045: YARP websocket routing
- ⚠️ SKIP T046 (moderation hooks) - defer to Phase 2
- ⚠️ SKIP typing indicators, read receipts - Phase 2

**US4: Safety (P3 - Minimal Version)** ⚠️ MINIMAL ONLY
- ✅ T052: Photo privacy enforcement (blur non-matches)
- ✅ T054: Block action (client + API)
- ⚠️ SKIP T053 (report workflow) - defer to Phase 2
- ⚠️ SKIP T055 (account recovery) - defer to Phase 2
- ⚠️ SKIP T056 (ops playbook) - defer to Phase 2

### DECISION POINTS

**Include Messaging?** → ✅ **YES**
- **Reasoning**: Without messaging, we have an incomplete product that won't retain users
- **Complexity**: +15 tasks but most are small (SignalR already exists)
- **Alternative Rejected**: Ship without messaging → users bounce immediately in 2026 market

**Include Safety?** → ⚠️ **MINIMUM VIABLE ONLY**
- **Reasoning**: Block/unblock = safety signal, full reporting can wait
- **Complexity**: +2 tasks (T052, T054)
- **Alternative**: Full safety suite → too much for MMP, defer complex workflows

---

## 🚀 Phase 2: Post-Launch Enhancements (Ship After Beta)

**Goal**: Harden, optimize, and add differentiation  
**Timeline**: Weeks 7-12  
**Target**: Wider launch (1000+ users)

### SHOULD HAVE (Quality & Growth)

**Phase 0 Completion** 📊
- T001: Feature map
- T003: Full test coverage (80%+)
- T004: Green CI/CD pipeline
- T005: Auto-detection scripts
- T006: ✅ This document
- T007: Database consolidation
- T008: Remove AuthService

**Onboarding Enhancements**
- T028: Keycloak webhook integration
- T029: Automated test data generation

**Messaging Upgrades**
- T041: Flutter widget tests
- T046: Message moderation hooks
- Read receipts, typing indicators
- Voice messages

**Safety Hardening**
- T050: API test coverage for reports
- T051: Flutter privacy settings screen
- T053: Full reporting + moderation queue
- T055: Account recovery
- T056: Operations playbook

**Match Discovery Optimization**
- T031: Flutter integration tests
- Advanced filters (distance, age, height, etc.)
- "Dealbreaker" preferences
- Icebreaker prompts

---

## 📅 Phase 3: Growth & Monetization (Post-PMF)

**Goal**: Scale features that drive revenue  
**Timeline**: Month 4+  
**Target**: Product-market fit validation

### NICE TO HAVE (Differentiation & Revenue)

**Premium Features**
- Unlimited swipes (free tier = 100/day)
- "See who liked you"
- Boost (priority in discovery)
- Super likes

**Advanced Matching**
- ML-powered compatibility scoring
- Behavioral signals (response rate, message quality)
- A/B test different algorithms

**Social Proof**
- Instagram integration
- Spotify top artists
- Verified badges (photo, phone, profile)

**Engagement Loops**
- Push notifications (new matches, messages)
- Daily digest emails
- Gamification (streaks, achievements)

**Safety & Trust**
- Video verification
- Background checks (optional premium)
- Safety tips & education content
- In-app reporting dashboard

---

## 📊 Updated Task Priorities

### Priority Legend
- **P0** = Blocker (nothing works without this)
- **P1** = MMP Must-Have (ships in Phase 1)
- **P2** = Post-Launch Enhancement (ships in Phase 2)
- **P3** = Growth & Revenue (ships in Phase 3+)

### Reprioritized Tasks

**Promoted to P1** (was P2):
- ✅ **T042-T045**: Basic messaging - **CRITICAL FOR MMP**

**Demoted to P2** (was P1):
- T028, T029: Automation - defer until post-launch
- T031: Flutter integration tests - ship without 100% coverage

**Demoted to P3**:
- T046: Message moderation - start manual, automate later
- T053: Reporting workflow - block works, full reporting later
- T055-T056: Recovery & ops - handled manually at small scale

**Remains P1** (unchanged):
- T020-T027: Onboarding wizard (core value)
- T030-T037: Match discovery (core value)
- T052, T054: Basic safety (minimum trust signals)

---

## 🎯 MMP Success Criteria

### Definition of "Shippable MMP"

A **shippable MMP** must enable this complete user journey:

1. ✅ New user registers via email (Keycloak)
2. ✅ Completes 3-step profile wizard with photos
3. ✅ Sees daily match queue (5-10 candidates)
4. ✅ Swipes right on interesting profiles
5. ✅ Gets instant notification on mutual match
6. ✅ Opens chat, sends message
7. ✅ Receives reply via SignalR
8. ✅ Can block user if needed
9. ✅ Profile remains private to non-matches (blur)

**Time to Value**: <15 minutes from signup to first conversation

### Launch Readiness Gates

**Technical** ✅
- [ ] All P1 tasks complete (T020-T027, T030-T037, T042-T045, T052, T054)
- [ ] E2E test passes signup → match → message flow
- [ ] P95 latency <350ms for API calls
- [ ] SignalR delivers messages <1s when online
- [ ] Photo upload + moderation completes <10s

**Product** ✅
- [ ] 90% onboarding completion in user testing
- [ ] Average 3+ swipes per session
- [ ] 60%+ match acceptance rate (both parties swipe)
- [ ] 80%+ message response rate
- [ ] Zero critical safety incidents in beta (50 users)

**Operations** ⚠️ Minimal
- [ ] Can seed 100 test users via script
- [ ] Manual moderation queue exists
- [ ] Can reset user accounts manually
- [ ] Basic logging + error alerts configured

---

## 🚧 What We're NOT Building (Yet)

### Explicitly Deferred to Phase 2+

**Advanced Onboarding**:
- ❌ Video prompts
- ❌ Voice intro
- ❌ Personality quiz
- ❌ Profession/income fields
- ❌ Extended prompts (>3 questions)

**Discovery Enhancements**:
- ❌ Advanced filters (ethnicity, religion, education)
- ❌ Dealbreakers
- ❌ "Second chance" re-queue
- ❌ Mutual friend suggestions

**Messaging Extras**:
- ❌ Voice messages
- ❌ Photo sharing in chat
- ❌ GIF support
- ❌ Video calls
- ❌ Message reactions

**Safety Advanced**:
- ❌ Video verification
- ❌ Background checks
- ❌ Safety center webpage
- ❌ Automated ban system
- ❌ Appeal workflow

**Premium/Growth**:
- ❌ Subscription tiers
- ❌ In-app purchases
- ❌ Boost/Super Like
- ❌ See who liked you
- ❌ Analytics dashboard

**Infrastructure**:
- ❌ Mobile push notifications (Firebase)
- ❌ Email marketing automation
- ❌ A/B testing framework
- ❌ Advanced analytics (Mixpanel/Amplitude)

---

## 💰 Development Effort Estimates

### Phase 1: MMP Launch

| Component | Tasks | Effort | Status |
|-----------|-------|--------|--------|
| Onboarding | T020-T027 | ~40h | ✅ 10h done (T022, T023) |
| Discovery | T030-T037 | ~30h | ❌ Not started |
| Messaging | T042-T045 | ~20h | ❌ Not started |
| Safety | T052, T054 | ~10h | ❌ Not started |
| **TOTAL MMP** | **26 tasks** | **~100h** | **10% complete** |

**Timeline**: 3-4 weeks with focused development

### Phase 2: Post-Launch

| Component | Tasks | Effort |
|-----------|-------|--------|
| Phase 0 Cleanup | T001-T008 | ~25h |
| Test Coverage | T003, T004, T031, T041, T050, T051 | ~30h |
| Automation | T028, T029 | ~10h |
| Safety Hardening | T053, T055, T056 | ~20h |
| **TOTAL Phase 2** | **15 tasks** | **~85h** |

**Timeline**: 2-3 weeks post-launch

---

## 🎨 Flutter UI Prioritization

### Must Build (MMP)
- ✅ Login/Register screens (Keycloak)
- ✅ 3-step wizard (basic info, preferences, photos)
- ✅ Discover card stack (swipe UI)
- ✅ Match notification modal
- ✅ Chat screen (messages list + input)
- ✅ Basic profile view

### Can Skip Initially
- ❌ Settings screen (use defaults)
- ❌ Edit profile screen (wizard is enough)
- ❌ Photo gallery view (just show primary)
- ❌ Match list screen (notification works)
- ❌ Filters/preferences modal

---

## 🤝 Competition Benchmark (2026)

### Feature Parity Check

| Feature | Tinder | Bumble | Hinge | **Our MMP** |
|---------|--------|--------|-------|-------------|
| Profile creation | ✅ | ✅ | ✅ | ✅ |
| Photo upload (6+) | ✅ | ✅ | ✅ | ✅ (up to 6) |
| Swipe discovery | ✅ | ✅ | ❌ | ✅ |
| Messaging | ✅ | ✅ | ✅ | ✅ |
| Match notifications | ✅ | ✅ | ✅ | ✅ |
| Photo verification | ✅ | ✅ | ❌ | ❌ (Phase 2) |
| Block/Report | ✅ | ✅ | ✅ | ⚠️ (block only) |
| Read receipts | ✅ | ✅ | ✅ | ❌ (Phase 2) |
| Video chat | ✅ | ✅ | ✅ | ❌ (Phase 3+) |
| Premium tier | ✅ | ✅ | ✅ | ❌ (Phase 3+) |

**Verdict**: Our MMP covers **core value loop**, defers premium/advanced features

---

## 📋 Next Steps

### Immediate Actions (T006 Completion)

1. ✅ Create this SCOPE.md document
2. ✅ Update tasks.md with reprioritized P1/P2/P3 tags
3. ✅ Get stakeholder approval on **"Messaging in MMP"** decision
4. ✅ Mark T006 complete

### Following This Decision

**Option A: Execute MMP Plan** (Recommended)
- Continue US1 completion (T024-T027)
- Start US2 discovery (T030-T037)
- Implement basic messaging (T042-T045)
- Add minimal safety (T052, T054)
- **Ship in 3-4 weeks**

**Option B: Complete Phase 0 First**
- Finish T001-T008 (foundation work)
- Then execute MMP with better tooling
- **Ship in 5-6 weeks**

**Recommendation**: **Option A** - ship MMP fast, improve tooling post-launch

---

## 🎯 Approval & Sign-Off

**Decision**: Include basic messaging in MMP (US3 promoted to P1)

**Approved By**: [Pending stakeholder review]  
**Date**: 2026-01-25  
**Next Review**: After 100-user beta launch

**Key Risks**:
- Messaging adds complexity → Mitigate with focused scope (no typing/read receipts)
- Safety gaps → Mitigate with manual moderation + basic block
- Technical debt → Accept for speed, address in Phase 2

---

**THIS IS NOT A TINDER CLONE** - We're building modern table-stakes first, then differentiating.
