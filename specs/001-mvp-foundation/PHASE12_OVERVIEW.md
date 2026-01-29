# Phase 12 Overview: Niche Strategy & Multi-Flavor Architecture

**Created**: 2026-01-28  
**Status**: Planning Phase (Not Implementation Yet)  
**Estimated Duration**: 22 hours of brainstorming/design work

---

## What We Just Created

### 📚 Documentation (3 Files)

1. **[emotional-monetization-strategy.md](features/emotional-monetization-strategy.md)**
   - 4 niche options analyzed (New to City, Shared Custody, Small Town, Divorced)
   - Emotional paywall design principles (Hope × Urgency × Friction)
   - Urgency mechanics per niche (time-based, scarcity-based)
   - **Purpose**: Reference material for brainstorming, NOT immediate implementation

2. **[niche-agnostic-architecture.md](features/niche-agnostic-architecture.md)**
   - Backend design: Generic metadata fields (NicheDate, NicheCategory, NicheLocation)
   - Flutter multi-flavor strategy: One codebase → multiple apps
   - Test new niche = 2 days of Flutter work, zero backend changes
   - **Purpose**: Technical blueprint for flexible niche experimentation

3. **[NICHE_DECISION.md](NICHE_DECISION.md)**
   - Decision template for choosing niche
   - Market size analysis per niche
   - Implementation plan per niche (onboarding, paywall, launch)
   - **Purpose**: Structured decision-making tool (fill out when ready)

### 📋 Task List (12 New Tasks in tasks.md)

**Phase 12.1: Strategic Research** (10 hours)
- T129: Niche psychology research (read emotional-monetization-strategy.md)
- T130: Competitor niche analysis (study JSwipe, Feeld, The League)
- T131: Market sizing (calculate TAM/SAM/SOM per niche)
- T132: Decision matrix (score niches, pick top 2)

**Phase 12.2: Backend Design** (5 hours)  
- T133: Generic metadata schema (NicheMetadata JSON field)
- T134: Flexible match filtering API (Dictionary<string, object> Filters)
- T135: Generic premium features enum (backend not niche-aware)

**Phase 12.3: Flutter Architecture** (8 hours)
- T136: Flavor config system (abstract FlavorConfig class)
- T137: Niche-specific onboarding flows (different questions per flavor)
- T138: Emotional paywall moments (copy per niche)

**Phase 12.4: Testing Strategy** (3 hours)
- T139: A/B test plan (launch 2 niches in parallel)
- T140: Niche experimentation playbook (how to add new niche in 2 days)

---

## Core Philosophy

### ❌ What We're NOT Doing

- **NOT building a generic dating app** (no niche = no urgency = low conversion)
- **NOT hardcoding niche logic in backend** (kills flexibility)
- **NOT rushing to implementation** (need to think through strategy first)
- **NOT committing to one niche forever** (might not hit right on first try)

### ✅ What We ARE Doing

- **Building solid niche-agnostic backend** (supports ANY niche via metadata)
- **Creating multiple Flutter app flavors** (test different niches, same backend)
- **Designing emotional paywalls** (lock at peak emotion, not feature gates)
- **Planning for experimentation** (fast iteration, data-driven decisions)

---

## The Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────┐
│ Backend Services (NICHE-AGNOSTIC)                      │
│                                                         │
│ - UserService: Generic NicheMetadata JSON field        │
│ - MatchmakingService: Accepts flexible Filters dict    │
│ - BillingService: Generic PremiumFeature enum          │
│ - MessagingService: No niche awareness                 │
│                                                         │
│ ONE set of APIs, supports ALL niches                   │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ Same API
           ┌──────────────┼──────────────┐
           │              │              │
┌──────────▼────────┐ ┌──▼──────────┐ ┌─▼──────────────┐
│ Flutter Flavor 1  │ │ Flavor 2    │ │ Flavor 3       │
│ "New to City"     │ │ "Custody"   │ │ "Small Town"   │
│                   │ │             │ │                │
│ Onboarding:       │ │ Onboarding: │ │ Onboarding:    │
│ "When moved?"     │ │ "Custody?"  │ │ "Education?"   │
│                   │ │             │ │                │
│ Paywall:          │ │ Paywall:    │ │ Paywall:       │
│ "48h expiry"      │ │ "Kid-free"  │ │ "17 users"     │
│                   │ │             │ │                │
│ Copy: Loneliness  │ │ Copy: FOMO  │ │ Copy: Scarcity │
└───────────────────┘ └─────────────┘ └────────────────┘

Test which converts best → Scale winner, kill losers
```

---

## How to Use This Phase

### Step 1: Research & Brainstorm (Now → 1 Week)

**Tasks**: T129-T132 (10 hours)

**Actions**:
1. Read [emotional-monetization-strategy.md](features/emotional-monetization-strategy.md) fully
   - Understand all 4 niche options
   - Note emotional triggers per niche
   - Study urgency mechanics (time-based vs scarcity)

2. Research competitor niche apps (T130)
   - JSwipe (Jewish dating): How do they validate niche?
   - Feeld: How does "Ping" create urgency?
   - The League: How do they use scarcity?

3. Calculate market size (T131)
   - New to City: ~30k/year in Stockholm alone
   - Shared Custody: ~80k total in Sweden (age 30-45)
   - Which has largest TAM/SAM/SOM?

4. Score niches in decision matrix (T132)
   - Pain intensity: How badly does this hurt? (1-10)
   - Market size: How many potential users?
   - Urgency: Time pressure or scarcity?
   - Choose top 2 to test

**Output**: Filled-out [NICHE_DECISION.md](NICHE_DECISION.md) with chosen niches

---

### Step 2: Backend Design (Week 2)

**Tasks**: T133-T135 (5 hours)

**Actions**:
1. Design User model extension (T133)
   - Add `NicheMetadata` JSON field
   - Add indexed fields: `NicheDate`, `NicheCategory`, `NicheLocation`
   - **Don't implement yet**, just document schema

2. Design flexible MatchmakingService API (T134)
   - Change GetMatches to accept `Dictionary<string, object> Filters`
   - Mobile app sends: `{"nicheDate": "2025-12-01", "nicheLocation": "Stockholm"}`
   - Backend filters generically (no niche-specific logic)

3. Design generic premium features (T135)
   - Enum: `UnlimitedMatches`, `ReadMessages`, `SendPings`, etc.
   - Backend just checks feature access
   - Mobile app maps to niche copy ("See all newcomers" vs "See kid-free matches")

**Output**: Backend architecture ready for ANY niche

---

### Step 3: Flutter Flavor Design (Week 3)

**Tasks**: T136-T138 (8 hours)

**Actions**:
1. Design FlavorConfig system (T136)
   - Abstract class: `FlavorConfig`
   - Concrete flavors: `NewToCityFlavor`, `SharedCustodyFlavor`
   - Controls: app name, colors, onboarding, paywall copy, filters

2. Design onboarding per niche (T137)
   - Flavor 1: "When did you move to [city]?"
   - Flavor 2: "What's your custody schedule?"
   - Flavor 3: "What's your education level?"

3. Write paywall copy per niche (T138)
   - Flavor 1: "[Name] moved here 2 weeks ago — 48h to reply"
   - Flavor 2: "You're both kid-free this weekend — meet now"
   - Flavor 3: "Only 17 users in Västerås — see all before they match"

**Output**: Ready to build 2 Flutter flavors (not built yet, just designed)

---

### Step 4: Testing Strategy (Week 4)

**Tasks**: T139-T140 (3 hours)

**Actions**:
1. Plan A/B test (T139)
   - Week 1: Launch Flavor 1 to 100 users
   - Week 3: Launch Flavor 2 to 100 users
   - Week 5: Analyze conversion rates, pick winner

2. Document "Add New Niche" playbook (T140)
   - Prove you can add niche in 2 days
   - Zero backend changes required
   - Test by adding mock "Fitness" flavor

**Output**: Clear test plan + playbook for future niches

---

## When to Implement (Not Now!)

**Phase 12 is PLANNING ONLY.** Implementation happens later:

### Implementation Sequence:

1. **First: Finish current MVP backend** (Phase 4-10)
   - Get UserService, MatchmakingService, SwipeService, MessagingService solid
   - Backend doesn't need to know about niches yet

2. **Then: Add niche fields** (T133 implementation)
   - 1 migration: Add NicheMetadata, NicheDate, NicheCategory, NicheLocation
   - Backward compatible (all nullable)

3. **Then: Build first 2 Flutter flavors** (T136-T138 implementation)
   - 2-3 days per flavor
   - Test with small user groups

4. **Then: Launch A/B test** (T139)
   - Measure conversion rates
   - Double down on winner

**Estimated Timeline**: Start implementation in 4-6 weeks (after core MVP proven)

---

## Key Decisions You Need to Make

### Decision 1: Which 2 Niches to Test First? (T132)

**Options**:
- 🥇 **Recommended**: New to City + Shared Custody
  - New to City = largest market, high urgency
  - Shared Custody = highest pain, unique mechanic
- Alternative: New to City + Small Town
- Alternative: All 3 in parallel (more work, more data)

**When to decide**: After completing T129-T131 (research + market sizing)

---

### Decision 2: Test Sequentially or Parallel? (T139)

**Sequential** (lower risk):
- Week 1: Launch Flavor 1, measure conversion
- If >15%, launch Flavor 2
- If <10%, pivot to Flavor 3 instead of Flavor 2

**Parallel** (faster learning):
- Week 1: Launch both flavors to different user segments
- Week 3: Compare conversion rates side-by-side
- Faster to winner, but need 2x users

**When to decide**: After niche selection (T132)

---

### Decision 3: When to Add Niche Fields to Backend? (T133)

**Option A**: Add now during Phase 4-10 implementation
- Pro: Ready for flavors when needed
- Con: Fields unused initially (YAGNI violation)

**Option B**: Add when ready to build first flavor
- Pro: Just-in-time implementation
- Con: Requires migration + deployment before Flutter work

**Recommendation**: Option A (add during Phase 5-6 UserService work)
- Minimal cost (4 nullable fields, 3 indexes)
- Future-proofs backend
- Can start populating data even before flavors exist

---

## Success Criteria (Planning Phase)

After completing Phase 12 tasks, you should have:

✅ **Niche Selection**: Top 2 niches chosen based on data (not guessing)
✅ **Backend Blueprint**: Schema/API design for niche-agnostic filtering
✅ **Flavor Designs**: 2 concrete FlavorConfig implementations documented
✅ **Paywall Copy**: Emotional triggers written for each niche
✅ **Test Plan**: A/B test strategy with success metrics defined
✅ **Playbook**: Documented process to add new niche in 2 days

**You do NOT need**:
❌ Implemented niche fields in database (not yet)
❌ Built Flutter flavors (not yet)
❌ Live A/B test running (not yet)

---

## Risk Mitigation

### Risk 1: "What if both test niches fail?"

**Mitigation**:
- Backend is niche-agnostic → can test Flavor 3 immediately
- Playbook exists to add new niche in 2 days
- No backend refactoring required to pivot

### Risk 2: "What if niche metadata doesn't scale?"

**Mitigation**:
- JSON field is flexible (supports any structure)
- Can add more indexed fields later if needed (NicheDate2, etc.)
- Worst case: Add niche-specific tables, but generic fields handle 90% of cases

### Risk 3: "What if we need to support multiple niches simultaneously?"

**Mitigation**:
- User can belong to multiple niches (set multiple nicheCategory values)
- Example: "new_to_city" AND "shared_custody" (single parent who just moved)
- Match algorithm filters by ANY matching category

### Risk 4: "What if emotional paywalls don't convert?"

**Mitigation**:
- A/B test emotional vs feature-based paywalls
- Measure: Emotion ("48h expiry") vs Feature ("unlimited swipes")
- Data will tell us which works (hypothesis: emotion wins 3-5x)

---

## Next Steps (Your Action Items)

### This Week:
1. **Read emotional-monetization-strategy.md** (1 hour)
   - Understand niche options
   - Note which resonates with your vision

2. **Think about target market** (30 min)
   - Who do you want to help?
   - Which pain point do you understand best?
   - Which niche can you market to?

### Next Week:
3. **Complete T129-T132** (10 hours)
   - Research competitors
   - Calculate market sizes
   - Score niches, pick top 2

4. **Fill out NICHE_DECISION.md** (30 min)
   - Document chosen niches
   - Rationale for each
   - Launch city selection

### Week 3-4:
5. **Complete T133-T138** (13 hours)
   - Design backend schema
   - Design Flutter flavors
   - Write paywall copy

6. **Complete T139-T140** (3 hours)
   - Plan A/B test
   - Document playbook

### After Planning Complete:
7. **Continue with current MVP implementation** (Phase 4-10)
   - Build solid backend first
   - Add niche fields during UserService work
   - Flavors come later (after backend proven)

---

## Questions to Consider

As you go through Phase 12 brainstorming, ask yourself:

1. **Niche Selection**:
   - Which niche pain do I understand personally?
   - Which niche can I reach via Facebook/Instagram ads?
   - Which niche has least competition?

2. **Emotional Triggers**:
   - What creates urgency for this niche? (time window? scarcity?)
   - What are they afraid of? (loneliness? missing out? rejection?)
   - When are they most emotional? (Friday nights? Kid-free weekends?)

3. **Paywall Moments**:
   - When does hope peak? (got match? saw profile?)
   - When does fear peak? (message expiring? someone else viewing profile?)
   - What creates impulse to buy? (specific person? limited time? FOMO?)

4. **Testing**:
   - How will I know if niche works? (conversion %? retention?)
   - What's my pivot threshold? (<10% conversion = kill niche?)
   - How fast can I iterate? (2 days to new flavor?)

---

## Summary

**What Phase 12 Is**:
- Strategic planning phase (22 hours of brainstorming)
- Niche selection process (data-driven, not guessing)
- Architecture blueprint (niche-agnostic backend + multi-flavor frontend)

**What Phase 12 Is NOT**:
- Immediate implementation (that comes later)
- Commitment to one niche (designed for experimentation)
- Rushing to launch (need to think through strategy)

**Why It Matters**:
- Generic dating app = 2-5% conversion = failure
- Niche dating app = 12-20% conversion = 4x revenue
- Flexible architecture = test fast, scale winners

**Your concern addressed**:
> "I might not hit right niche in one go"

**Solution**: Backend supports ANY niche. Test multiple flavors. Data decides winner. Pivot in 2 days if needed.

---

**Ready to start? Begin with T129 (Niche psychology research) → Read emotional-monetization-strategy.md**
