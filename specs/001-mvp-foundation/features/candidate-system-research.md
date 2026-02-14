# Candidate System Research — Industry Analysis & Architecture Design

**Created**: 2026-02-13
**Phase**: 14 (Strategy-Based Candidate Delivery System)
**Author**: AI-assisted research session

---

## 1. Industry Research: How Dating Apps Actually Work

### 1.1 Tinder — ELO & Desirability

**Source**: Wikipedia, Vox dating app analysis, system design interviews

- **Scale**: 75M monthly active users, 1.6B swipes/day, 12M matches/day at peak
- **ELO System (2012-2019)**: Each user had a hidden "desirability score" based on who swiped right on them. Being liked by high-ELO users boosted your score more than being liked by low-ELO users. Classic chess ELO adapted for dating.
- **Post-ELO (2019+)**: Replaced with ML-based system that considers: profile completeness, photo quality, bio length, response rate, message quality, app usage patterns. Still fundamentally a desirability metric but multi-dimensional.
- **Key insight**: Showing users profiles of SIMILAR desirability increases mutual match probability by 3-5x. Asymmetric matches (high-ELO shown to low-ELO) waste swipes and frustrate both parties.
- **Swipe limits**: Free users get ~100 swipes/day. Scarcity increases intentionality.
- **Profile recycling**: After all candidates exhausted, Tinder recycles profiles from further distances or older activity. Users see `QueueExhausted` state.

### 1.2 Hinge — "Most Compatible" (Gale-Shapley)

- **Algorithm**: Uses Gale-Shapley stable matching to compute daily "Most Compatible" picks. Each user gets 1 daily pick that maximizes mutual interest probability.
- **How it works**: Considers who you've liked, who's liked you, profile attributes, and behavioral patterns. Runs as a batch job (presumably nightly).
- **Product impact**: "Most Compatible" matches are 8x more likely to result in a date than regular matches (Hinge's published stats).
- **Our adaptation**: `DailyPickStrategy` (T174) — curated daily picks from pre-computed scores. Simpler than Gale-Shapley but same product concept.

### 1.3 Bumble — Time Pressure & Recency

- **24h window**: Matches expire if no message sent within 24h from the woman. Creates urgency.
- **Recently active**: Bumble heavily weights users who were active in the last few hours. "Online now" green dot drives engagement.
- **Distance-first**: Bumble defaults to 50km radius, no option to go unlimited. Proximity = meetability.
- **Our adaptation**: `LastActiveAt` field (T164), exponential decay activity score (T163), `DailyPick` expiry (T174).

### 1.4 Coffee Meets Bagel — Daily Curated

- **Model**: 21 curated matches ("bagels") per day at noon. No endless swiping.
- **Philosophy**: Combat decision fatigue by limiting choices. Quality > quantity.
- **Research backing**: Iyengar & Lepper (2000) "When Choice is Demotivating" — too many options reduce satisfaction and decision quality. Sweet spot is 6-9 options.
- **Our adaptation**: `DailyPickStrategy` defaults to 10 picks/day (configurable). Not as restrictive as CMB but same principle.

---

## 2. Key Performance Insights

### 2.1 "Recently Active" is #1 Quality Signal

All major dating apps weight recency because:
- Active users respond to messages (inactive ones don't → frustration)
- Active users are still looking (inactive may have found someone)
- Active users have fresh photos/bios

**Our implementation**: Exponential decay formula in `CalculateActivityScore` (T163). Half-life of 7 days means:
- Active today → score ~100
- Active 3 days ago → score ~74
- Active 7 days ago → score ~50
- Active 14 days ago → score ~25
- Active 30 days ago → score ~6

### 2.2 Bidirectional Filtering is Critical

The #1 complaint on dating apps: "Why am I seeing people who would never match with me?"

**Problem**: 50-year-old man with preference "women 18-25" is shown to 22-year-old woman whose preference is "men 22-30". She'd never swipe right, wasting her time.

**Solution**: Bidirectional age/gender/distance filtering. OUR `AgeRangeFilter` (T168) checks BOTH directions:
- Candidate's age within MY range ✓
- MY age within candidate's range ✓

Same for gender preferences. This alone dramatically improves match quality.

### 2.3 Distance at DB Level = 10x Performance

**Current**: Load ALL candidates from DB → check distance per-candidate in C# → discard 80%+.
**Target**: Haversine in SQL WHERE clause → only load candidates within radius.

With 100K users, this means:
- Current: Load 100K profiles, discard ~80K in memory = 100K rows transferred
- Target: DB returns ~20K profiles that are within radius = 20K rows transferred

**MySQL Haversine**: `6371 * ACOS(COS(RADIANS(lat1)) * COS(RADIANS(lat2)) * COS(RADIANS(lon2-lon1)) + SIN(RADIANS(lat1)) * SIN(RADIANS(lat2)))` — Pomelo 8.x should translate `Math.Acos/Cos/Sin` but verify.

**Fallback**: Bounding box pre-filter (`lat BETWEEN x-d AND x+d`) is always translatable and eliminates 90%+ candidates cheaply.

---

## 3. Architecture: Strategy Pattern Rationale

### 3.1 Scale Progression

| Users    | Strategy       | Latency Target | Why |
|----------|---------------|----------------|-----|
| < 10K   | Live Scoring  | < 200ms        | Few candidates, compute is cheap |
| 10K-500K | PreComputed   | < 50ms         | Pre-computed scores in MatchScores table |
| > 500K  | PreComputed + Sharding | < 50ms | Regional sharding, separate DB per region |

### 3.2 Config-Only Switching

```json
// Scale from 100 to 500K users by changing ONE line:
"CandidateOptions": {
  "Strategy": "Auto"  // ← Auto-detects based on user count
}
```

No code deployment needed. Operator changes config, `IOptionsMonitor` picks it up.

### 3.3 A/B Testing Ready

```
GET /api/matchmaking/profiles/123?strategy=dailypick
```

Flutter can (in the future) randomly assign users to strategies and compare engagement metrics. The backend supports this TODAY with the `?strategy=` query param (T180).

---

## 4. Existing Infrastructure Inventory

### 4.1 What We Already Have (Don't Rebuild)

| Asset | Location | Status | Used By |
|-------|----------|--------|---------|
| `MatchScores` table | MatchmakingDbContext | ✅ Table exists, 24h TTL, unique index | PreComputedStrategy |
| `UserInteractions` table | MatchmakingDbContext | ✅ Has LIKE/PASS data | GetSwipedUserIdsAsync fix |
| `ScoringConfiguration` | Models/, Program.cs | ⚠️ Registered but UNUSED | T162 wires it in |
| `MatchingAlgorithmMetrics` | MatchmakingDbContext | ✅ Table exists | Strategy metrics |
| `DailySuggestionLimits` | appsettings.json | ✅ Config exists | Strategy daily limits |
| `InternalApiKeyAuthFilter` | Common/ | ✅ Working | Sync endpoints |
| `OpenTelemetry` | Program.cs | ✅ Prometheus exporter configured | Candidate metrics |
| `IMemoryCache` | Program.cs | ⚠️ Registered but UNUSED for scoring | Filter pipeline cache |
| `CalculateCompatibilityScoreAsync` | AdvancedMatchingService | ✅ Working (6 sub-scores) | LiveScoringStrategy |

### 4.2 What's Broken (Must Fix First — Phase 14.1)

| Bug | Location | Impact | Fix |
|-----|----------|--------|-----|
| `GetSwipedUserIdsAsync` STUB | AdvancedMatchingService:269 | Swiped users shown again | T161: Query UserInteractions |
| `ScoringConfiguration` unused | AdvancedMatchingService | Penalties hardcoded, config changes ignored | T162: DI injection |
| `CalculateActivityScore` STUB | AdvancedMatchingService | Always returns 75.0 | T163: Exponential decay |
| `ProfilesController` dumb proxy | ProfilesController | Bypasses entire scoring engine | T179: Rewire to strategy |

### 4.3 What's Missing (Must Create — Phase 14.2-14.8)

| Component | Purpose | Task |
|-----------|---------|------|
| `LastActiveAt` field | Track user activity for recency scoring | T164 |
| `LookingFor` field | Intent-based filtering (relationship/casual/friendship) | T164 |
| `ICandidateFilter` | Pluggable filter interface | T167 |
| `CandidateFilterPipeline` | Filter chain orchestrator | T169 |
| `ICandidateStrategy` | Swappable candidate delivery interface | T171 |
| `LiveScoringStrategy` | Real-time scoring (small scale) | T172 |
| `PreComputedStrategy` | Read pre-computed scores (medium scale) | T173 |
| `DailyPickStrategy` | Curated daily recommendations | T174 |
| `StrategyResolver` | Config-driven strategy selection | T175 |
| `ScoreRefreshBackgroundService` | Proactive score computation | T176 |
| `CandidateOptions` | Configuration model | T181 |

---

## 5. Flutter Client Impact Analysis

**Impact: ZERO client-side changes required.**

### Current Flutter Flow
```
home_screen.dart → _loadCandidates()
  → MatchmakingApiService.getCandidates(userId)
    → api_service.dart → GET /api/matchmaking/profiles/$userId
      → Returns List<dynamic> → parsed to MatchCandidate
        → SwipeCacheService caches for 1h
```

### After Phase 14
```
home_screen.dart → _loadCandidates()        ← UNCHANGED
  → MatchmakingApiService.getCandidates()    ← UNCHANGED
    → GET /api/matchmaking/profiles/$userId  ← SAME ENDPOINT
      → Returns List<dynamic>               ← SAME SHAPE (+ optional new fields)
        → SwipeCacheService caches for 1h    ← UNCHANGED
```

**Additive fields** (Flutter ignores unknown JSON fields):
- `compatibilityScore` (double)
- `activityScore` (double)
- `strategyUsed` (string)
- `suggestionsRemaining` (int)
- `queueExhausted` (bool) — already in Flutter DTOs, currently always false

---

## 6. Risk Assessment

### 6.1 Low Risk
- T161-T163 (bug fixes): Replacing stubs with real implementations. No architectural changes.
- T167 (interface): Pure abstraction, no runtime behavior.
- T181 (config): Additive config section, nothing breaks.

### 6.2 Medium Risk
- T168 (filters): Haversine in EF Core may not translate to MySQL. Fallback plan exists (bounding box).
- T179 (controller rewire): Must preserve exact response shape. Extensive pre/post testing required.
- T166 (activity sync): Cross-service HTTP introduces coupling. Debounce/fire-and-forget mitigates.

### 6.3 Low Risk but High Effort
- T176-T178 (background services): First background services ever. Need careful cancellation, error handling, resource limits.
- T183 (ELO/desirability): Ethically sensitive, needs careful framing. Marked P3 (stretch).

---

## 7. Open Questions for Future Sessions

1. **UserInteractions vs SwipeServiceDb.Swipes**: Are swipe records synced between MatchmakingService and SwipeService? T161 assumes UserInteractions is populated. If it's not, need cross-service query.
2. **Region sharding**: At >500K users, single-DB filtering won't scale. Strategy pattern is ready for a `RegionalPreComputedStrategy` but the sharding infrastructure isn't designed yet.
3. **ML scoring**: Beyond ELO, could use ML models trained on match/conversation data to predict compatibility. Needs data volume + MLOps infrastructure (Phase 17+).
4. **Photo quality signal**: Users with more photos and verified photos get more matches. Could add photo-count and verification as scoring signals. Needs photo-service integration.
5. **Message response rate**: Users who actually respond to messages should rank higher. Needs messaging-service integration for "engagement score".
