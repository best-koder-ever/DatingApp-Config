# 005 — Core Differentiation: Compatibility Questions, Match Insight, AI Psykolog, Forum & Radar Chart

**Created**: 2026-04-02
**Phase**: 005
**Status**: 📋 Planning
**Depends on**: 001-mvp-foundation (core loop), 003-bot-swarm (LLM infrastructure)

---

## 🎯 Vision

> Every dating app has profiles, swipes, and messaging. None explain WHY two people match,
> measure compatibility with psychology-backed instruments, or evolve the profile as users grow.
> This spec builds the **five features that transform the app from "another swipe app" into
> "the one that actually tries to match well."**

**Core Thesis**: Compatibility questions + vector matching + AI psykolog + transparent scoring + community forum = a self-reinforcing flywheel where engagement drives matching quality, not addiction.

---

## 📦 Deliverables

### Phase 1: Compatibility Questions (Foundation)
- 32-question battery: TIPI-10 (Big Five), ECR-S 12 (Attachment), 10 Values/Dealbreakers
- Question entity + answer storage in MatchmakingService
- Scoring engine: weighted compatibility calculation
- Flutter onboarding wizard step 6 (questions screen)
- API: submit answers, get compatibility score vs. another user

### Phase 2: Scoring Integration
- AdvancedMatchingService uses compatibility scores in candidate ranking
- Scoring weights: psykolog vectors 40%, questions 30%, behavioral 20%, logistics 10%
- Replace raw desirability with multi-dimensional scoring
- DailyPick generation uses compatibility
- "Why You Matched" data generation (top reasons per match)

### Phase 3: Match Insight Card
- Flutter UI: gradient badge on discover card, bar comparison on profile preview
- 4-section Match Insight Card (Why You Connected, Differences, Growth, Learn)
- Asymmetric match explanations (each user sees personalized reasons)
- Premium gating: free = %, top 2 reasons; premium = full card

### Phase 4: AI Psykolog (Reflection Coach)
- Psykolog conversation endpoint in new psykolog-service (or UserService extension)
- LLM-powered Swedish reflection conversations (NOT therapy)
- Session storage, theme extraction, vector embedding generation
- pgvector integration for embedding storage
- Free: 1 session/month; Premium: unlimited

### Phase 5: Vector Matching
- Psykolog session vectors feed MatchmakingService as deep compatibility signal
- Anonymous vectors only (original text never stored permanently)
- Anti-gaming: vectors from unguarded reflection can't be optimized
- Scoring recalibration: post-date feedback adjusts vector weights

### Phase 6: 7-Axis Radar Chart
- Flutter radar chart widget: 7 axes (Emotional Stability, Social Energy, Openness, Warmth, Life Structure, Intimacy, Conflict Style)
- Two overlaid polygons: coral (user) + teal (match), 30% opacity fill
- Progressive disclosure: faded at 60% confidence → vivid at 90%+
- Living Profile: chart evolves with psykolog sessions + post-date feedback

### Phase 7: Anonymous Forum ("Forumet")
- Jodel-style anonymous posts about dating life
- Channels: First Dates, Red Flags, Vent, Success Stories, Ask the Community
- Upvote/downvote, karma, random color per post
- NO link to dating identity, NO photos, NO DMs
- Safety moderation via safety-service

---

## 🏗️ Architecture

### New Tables
| Service | Table | Purpose |
|---------|-------|---------|
| MatchmakingService | CompatibilityQuestion | 32 seeded questions with category, scale, weight |
| MatchmakingService | UserQuestionAnswer | User answers (value 1-7 Likert) |
| MatchmakingService | CompatibilityScore | Cached pairwise scores |
| MatchmakingService | MatchInsight | Per-match explanation data (JSON reasons) |
| UserService | PsykologSession | Session metadata (start, end, theme count) |
| UserService | ReflectionVector | 128-d embeddings per user (pgvector) |
| New DB / safety-service | ForumPost | Anonymous posts with channel, karma, color |
| New DB / safety-service | ForumVote | Upvote/downvote records |

### Service Dependencies
```
Flutter → UserService (wizard questions) → MatchmakingService (scoring)
Flutter → PsykologService (LLM reflections) → MatchmakingService (vectors)
Flutter → ForumService (posts/votes) → SafetyService (moderation)
MatchmakingService → DailyPickGeneration (uses all signals)
```

### Scoring Weights (Target)
| Signal | Weight | Source |
|--------|--------|--------|
| Psykolog vectors | 40% | Reflections → embeddings → cosine similarity |
| Compatibility questions | 30% | TIPI-10 + ECR-S + values answers |
| Behavioral signals | 20% | Swipe patterns, conversation depth, response time |
| Logistics | 10% | Distance, age range, dealbreakers |

---

## 🚫 Out of Scope
- AI Dating Coach (match-specific coaching) — separate spec
- Secret Match / voice-gated discovery — parked
- Video profiles — eliminated (all video-first apps died)
- ELO / league-based scoring — explicitly rejected
- Profile decoration / virtual rooms / avatars — eliminated
