# 002 — Agentic AI: Intelligent Dating

**Created**: 2026-02-21
**Phase**: 002
**Status**: 🧠 Brainstorming → Planning
**Depends on**: 001-mvp-foundation (core loop must work first)

---

## 🎯 Vision

> Dating apps optimize for **swipes** (engagement). We optimize for **connections** (outcomes).
> Every major dating app uses static ML models. Nobody ships agentic AI features in production yet.
> This is the window.

**Core Thesis**: An AI agent that *actively helps* users connect — not just passively matches them — is the differentiator that makes users choose us over Tinder/Bumble/Hinge.

---

## 🏗️ Agent Architecture (Shared Infrastructure)

All agents share:

```
User Action → Service Layer → Agent Gateway → LLM (Claude Haiku / GPT-4o-mini)
                                    ↓
                              Tool Registry (service APIs, DB queries, external APIs)
                                    ↓
                              Action → back to Service Layer
```

### Infrastructure Tasks

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| **T200** | Agent Gateway Service — shared orchestration loop, tool registry, LLM routing | 16h | P0 |
| **T201** | LLM abstraction layer — support Claude + GPT + local fallback, cost tracking per-call | 8h | P0 |
| **T202** | Agent memory/context store — per-user agent state, conversation history | 8h | P0 |
| **T203** | Cost control middleware — per-user daily LLM budget, circuit breaker on spend | 4h | P0 |
| **T204** | Agent observability — log every LLM call, latency, cost, tool usage, success/failure | 4h | P1 |
| **T205** | Agent A/B testing framework — route % of users to agent-powered vs traditional features | 8h | P2 |

---

## 🛡️ Agent 1: Safety Agent (Ship First)

**Why first**: Highest trust impact, uses existing infrastructure, clear ROI (user retention from feeling safe), no UX changes needed (runs invisibly).

**Goal**: Protect users from harassment, spam, catfishing, and scams in real-time.

### How It Works

```
User sends message → MessagingService → Safety Agent intercepts
  → LLM: "Classify this message: safe / warning / block"
  → safe: deliver normally
  → warning: deliver + flag for review + increment user risk score
  → block: reject message, notify sender, alert moderation queue
```

### Tasks

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| **T210** | Safety Agent core — intercept pipeline in MessagingService, classify messages via LLM | 12h | P1 |
| **T211** | Harassment escalation detection — track message patterns over time, not just single messages | 8h | P1 |
| **T212** | Catfish signal detection — reverse image search integration, profile inconsistency scoring | 12h | P2 |
| **T213** | Spam/copypasta detector — flag users sending identical messages to 10+ matches | 4h | P1 |
| **T214** | User risk scoring — aggregate safety signals into per-user trust score, feed into matchmaking | 8h | P2 |
| **T215** | Moderation dashboard — review flagged content, override agent decisions, feedback loop to improve | 12h | P2 |
| **T216** | Safety transparency report — show users "We blocked X threats this week" (trust signal) | 4h | P3 |

### Success Metrics
- 95%+ accuracy on harassment detection (measure via human review)
- <500ms added latency per message
- <$0.01 LLM cost per 100 messages
- 30% reduction in user-initiated blocks (agent catches it first)

---

## 📸 Agent 2: Photo Coach Agent

**Why second**: Bad photos are #1 reason profiles fail. No dating app helps users fix this. High perceived value = premium feature potential.

**Goal**: Analyze user photos and give specific, actionable advice to improve their profile.

### How It Works

```
User uploads photos → PhotoService → Photo Coach Agent triggered
  → Vision LLM analyzes: lighting, composition, variety, face clarity, background
  → Compares against engagement data from similar demographics
  → Returns: "Your photo 3 is too dark. Add a full-body outdoor shot. Your selfie angles are repetitive."
  → Optional: auto-crop/enhance suggestions
```

### Tasks

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| **T220** | Photo analysis pipeline — send photos to vision LLM, get structured quality assessment | 12h | P1 |
| **T221** | Photo variety scorer — detect if user has all selfies, no full-body, no activity shots | 8h | P1 |
| **T222** | Personalized advice generator — actionable tips based on what's *missing*, not generic rules | 8h | P1 |
| **T223** | Photo ranking — "This should be your primary" based on predicted engagement | 8h | P2 |
| **T224** | Auto-enhance suggestions — crop, brightness, contrast recommendations (not auto-apply) | 12h | P2 |
| **T225** | Flutter Photo Coach UI — coach card in profile editor, tips overlay on each photo | 12h | P1 |
| **T226** | Before/after tracking — measure if coached users get more matches | 8h | P3 |

### Success Metrics
- Users who follow coach advice get 40%+ more right-swipes
- 70%+ of users find advice "helpful" (in-app feedback)
- <$0.05 per photo analysis (vision models are pricier)

---

## 💬 Agent 3: Conversation Starter Agent

**Why third**: 50%+ of matches never message. This solves the cold-start problem and is a clear premium feature.

**Goal**: Help users start real conversations with their matches — personalized, not generic.

### How It Works

```
User matches with someone → Conversation Agent activated
  → Reads BOTH profiles (bios, interests, photos, prompts)
  → Generates 3 personalized openers:
    1. "I see you hiked Kungsleden — did you do the full trail or just Abisko to Nikkaluokta?"
    2. "Your dog is adorable! What breed? I've been thinking about getting a Golden."
    3. "Fellow coffee snob question — light or dark roast?"
  → User picks one or writes their own
  → If conversation stalls (>24h no reply), suggest follow-up or graceful exit
```

### Tasks

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| **T230** | Profile cross-analysis — read both profiles, extract shared interests and conversation hooks | 8h | P1 |
| **T231** | Opener generation — 3 personalized openers per match, tone-matched to profiles | 8h | P1 |
| **T232** | Stale conversation nudger — detect stalled chats, suggest re-engagement or graceful close | 8h | P2 |
| **T233** | Tone calibration — adjust formality/humor based on profile signals and user preference | 8h | P2 |
| **T234** | Flutter Conversation Coach UI — opener suggestions card in chat, non-intrusive placement | 12h | P1 |
| **T235** | Ghost detection + advice — "They haven't replied in 48h. Would you like to send X or move on?" | 4h | P2 |
| **T236** | Effectiveness tracking — which openers get replies? Feed back into generation | 8h | P3 |

### Success Metrics
- 60%+ of matches that use opener suggestions lead to a conversation (vs ~30% baseline)
- Users rate openers as "felt natural" 80%+ of the time
- <$0.005 per set of 3 openers

---

## 🧠 Agent 4: Smart Match Agent

**Why fourth**: Requires conversation outcome data to train properly — needs the other features running first.

**Goal**: Replace static scoring with an agent that learns what *actually works* for each user.

### How It Works

```
Traditional: score = age_match * 0.3 + distance * 0.2 + interests * 0.5
Agent:       score = learned_from_outcomes(this_user, that_user)

Agent observes:
  - Who you swipe right on (surface preference)
  - Who you actually message (real interest)
  - Who you have long conversations with (compatibility)
  - Who you unmatch (poor fit signal)
  → Builds preference model PER USER, not global averages
```

### Tasks

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| **T240** | Outcome tracking pipeline — track swipe → match → message → conversation_length → unmatch | 12h | P1 |
| **T241** | User preference learning — build per-user preference model from behavioral signals | 16h | P1 |
| **T242** | Match explanation — "We matched you because: shared hiking interest + similar message style" | 8h | P2 |
| **T243** | Anti-pattern detection — "You swipe right on everyone, let's focus on quality" | 8h | P2 |
| **T244** | Feedback incorporation — "Was this a good match?" → improve future recommendations | 8h | P2 |
| **T245** | A/B test: agent vs static scoring — measure conversation rate, unmatch rate, meetup rate | 12h | P2 |

### Success Metrics
- 2x conversation rate vs static algorithm
- 30% fewer unmatches within first 24h
- Users report "matches feel more relevant" in surveys

---

## 📅 Agent 5: Date Planner Agent (Future)

**Goal**: Help matched users who are chatting actually meet in person.

### Tasks

| Task | Description | Effort | Priority |
|------|-------------|--------|----------|
| **T250** | Mutual availability finder — "You're both free Saturday afternoon" | 12h | P3 |
| **T251** | Venue suggestion — local spots near both users, filtered by vibe (casual/coffee/active) | 12h | P3 |
| **T252** | Logistics handler — "Shall I suggest meeting at Café X at 3pm?" → both confirm in-app | 8h | P3 |
| **T253** | Safety check-in — optional "I arrived safely" / "I left" ping during dates | 8h | P3 |
| **T254** | Post-date feedback — "How did it go?" → feed into match quality learning | 4h | P3 |

---

## 🗺️ Implementation Roadmap

### Wave 1: Foundation + Safety (4-6 weeks)
**Build once, use everywhere**
- T200-T204: Agent infrastructure
- T210-T211, T213: Safety Agent core

**Ship criteria**: Safety agent intercepting messages in production, <500ms latency, cost < $10/day at 1000 users

### Wave 2: Photo Coach (3-4 weeks)
- T220-T223, T225: Photo Coach core + Flutter UI

**Ship criteria**: Every new user gets photo advice during onboarding

### Wave 3: Conversation Coach (3-4 weeks)
- T230-T232, T234: Opener generation + Flutter UI

**Ship criteria**: Opener suggestions appear on every new match

### Wave 4: Smart Matching (6-8 weeks)
- T240-T245: Outcome tracking + preference learning + A/B testing

**Ship criteria**: Agent-matched users have 2x conversation rate vs control group

### Wave 5: Date Planner (future)
- T250-T254: Only after proving earlier agents work

---

## 💰 Cost Model

| Agent | Cost per action | At 1,000 DAU | At 10,000 DAU |
|-------|----------------|--------------|---------------|
| Safety (per message) | $0.0001 | $3/day | $30/day |
| Photo Coach (per user) | $0.05 | $1.50/day | $15/day |
| Conversation (per match) | $0.005 | $2.50/day | $25/day |
| Smart Match (per candidate set) | $0.01 | $5/day | $50/day |
| **Total** | — | **~$12/day** | **~$120/day** |

At $10/month premium subscription, you need **12 paying users** to break even at 1,000 DAU.

---

## 🏁 Competitive Moat

| Feature | Tinder | Bumble | Hinge | **Us** |
|---------|--------|--------|-------|--------|
| Static ML matching | ✅ | ✅ | ✅ | ✅ |
| AI safety moderation | Basic regex | Basic ML | Basic ML | **Agentic LLM** |
| Photo coaching | ❌ | ❌ | ❌ | **✅ Agent** |
| Conversation help | ❌ | ❌ | Prompts only | **✅ Personalized** |
| Learned preferences | Basic | Basic | Better | **✅ Outcome-based** |
| Date planning | ❌ | ❌ | ❌ | **✅ Agent** |
| Match explanations | ❌ | ❌ | "Most Compatible" | **✅ Transparent** |

**Nobody else is doing this.** Big apps optimize for engagement (time in app).
We optimize for outcomes (actual connections). That's the pitch.

---

## 📋 Open Questions (Brainstorm Backlog)

- [ ] Should the safety agent explain *why* it blocked a message, or just silently filter?
- [ ] Can the photo coach use engagement data from production to improve recommendations?
- [ ] Premium vs free: which agents are free (safety?) vs premium (coach, planner)?
- [ ] Should conversation starters feel AI-generated or should the user always customize?
- [ ] How do we handle the "creepy" factor — users knowing AI read their profiles?
- [ ] Could agents work cross-language? (Swedish bio + English match = translated openers?)
- [ ] Multi-agent collaboration: safety agent flags → conversation agent adjusts tone?
- [ ] Can we run local/small models for cost-sensitive features (safety classification)?

---

*This phase is in brainstorm mode. Tasks will be refined as we prototype Wave 1.*
