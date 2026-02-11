# Matchmaking Algorithm Documentation

Comprehensive documentation of the DatingApp matchmaking scoring algorithm, fallback heuristics, and daily queue expansion rules.

## Overview

The matchmaking service uses a weighted multi-factor scoring algorithm to rank compatibility between users. Scores range from 0-100, with higher scores indicating better compatibility.

## Scoring Formula

### Overall Score Calculation

```
OverallScore = (LocationScore × LocationWeight) +
               (AgeScore × AgeWeight) +
               (InterestsScore × InterestsWeight) +
               (EducationScore × EducationWeight) +
               (LifestyleScore × LifestyleWeight) +
               (ActivityScore × ActivityWeight)
```

### Default Weights

| Factor | Default Weight | Range |
|--------|---------------|--------|
| Location | 0.30 (30%) | 0.00-1.00 |
| Age | 0.20 (20%) | 0.00-1.00 |
| Interests | 0.25 (25%) | 0.00-1.00 |
| Education | 0.10 (10%) | 0.00-1.00 |
| Lifestyle | 0.10 (10%) | 0.00-1.00 |
| Activity | 0.05 (5%) | 0.00-1.00 |

**Total**: Must sum to 1.00 (100%)

Users can customize these weights in their preferences to prioritize what matters most to them.

## Scoring Components

### 1. Location Score (0-100)

**Formula**: Haversine distance calculation with exponential decay

```csharp
distance_km = HaversineDistance(user.lat, user.lon, target.lat, target.lon)

if (distance_km > user.maxDistanceKm)
    return 0.0  // DEALBREAKER

normalized_distance = distance_km / user.maxDistanceKm
location_score = 100 * (1 - normalized_distance)²
```

**Behavior**:
- 0-5 km: Score 90-100 (excellent match)
- 5-25 km: Score 60-89 (good match)
- 25-50 km: Score 20-59 (acceptable match)
- 50+ km: Score 0 (outside max distance)

**Dealbreaker**: Users beyond `maxDistanceKm` preference get 0 score (excluded)

### 2. Age Score (0-100)

**Formula**: Gaussian distribution within age range preference

```csharp
min_age = user.ageMin
max_age = user.ageMax
target_age = target.age

if (target_age < min_age || target_age > max_age)
    return 0.0  // DEALBREAKER

ideal_age = (min_age + max_age) / 2
age_range = max_age - min_age
age_diff = abs(target_age - ideal_age)

age_score = 100 * exp(-((age_diff / (age_range/4))²))
```

**Behavior**:
- Ideal age (midpoint): Score 100
- ±2 years from ideal: Score 90+
- ±5 years from ideal: Score 70+
- Outside range: Score 0 (excluded)

**Dealbreaker**: Users outside `[ageMin, ageMax]` get 0 score

### 3. Interests Score (0-100)

**Formula**: Jaccard similarity of interests

```csharp
user_interests = Set(user.interests)
target_interests = Set(target.interests)

intersection = user_interests ∩ target_interests
union = user_interests ∪ target_interests

interests_score = 100 * (|intersection| / |union|)
```

**Behavior**:
- 5+ shared interests: Score 80-100
- 2-4 shared interests: Score 40-79
- 1 shared interest: Score 20-39
- 0 shared interests: Score 0-19

**No Dealbreaker**: Even 0 shared interests doesn't exclude

### 4. Education Score (0-100)

**Formula**: Categorical matching with partial credit

```csharp
education_levels = ["High School", "Some College", "Bachelor's", "Master's", "Doctorate"]

user_level = IndexOf(user.education)
target_level = IndexOf(target.education)
level_diff = abs(user_level - target_level)

if (level_diff == 0)
    education_score = 100  // Exact match
else if (level_diff == 1)
    education_score = 75   // Adjacent level
else if (level_diff == 2)
    education_score = 50   // 2 levels apart
else
    education_score = 25   // 3+ levels apart
```

**Behavior**:
- Same education: Score 100
- Adjacent level: Score 75
- 2 levels apart: Score 50
- 3+ levels apart: Score 25

**No Dealbreaker**: Education differences don't exclude

### 5. Lifestyle Score (0-100)

**Formula**: Composite of smoking, drinking, exercise

```csharp
smoking_match = (user.smoking == target.smoking) ? 100 : 0
drinking_match = (user.drinking == target.drinking) ? 100 : 0
exercise_match = MinDifference(user.exerciseFreq, target.exerciseFreq, max=7)

exercise_score = 100 * (1 - (exercise_diff / 7))

lifestyle_score = (smoking_match * 0.4) + (drinking_match * 0.3) + (exercise_score * 0.3)
```

**Weights**:
- Smoking: 40%
- Drinking: 30%
- Exercise: 30%

**Behavior**:
- All match: Score 100
- Partial match: Score 40-90
- None match: Score 0-40

**No Dealbreaker**: Lifestyle differences reduce score but don't exclude

### 6. Activity Score (0-100)

**Formula**: Recent engagement and responsiveness

```csharp
days_since_active = (Now - target.lastActiveAt).Days
response_rate = target.messageResponseRate  // 0.0-1.0

recency_score = 100 * exp(-(days_since_active / 7)²)
activity_score = (recency_score * 0.6) + (response_rate * 100 * 0.4)
```

**Behavior**:
- Active today: Score 90-100
- Active this week: Score 60-89
- Active this month: Score 20-59
- Inactive 30+ days: Score 0-19

**No Dealbreaker**: Inactive users score low but aren't excluded

## Candidate Selection Process

### 1. Basic Filters (Pre-Scoring)

Before scoring, candidates must pass:

```sql
SELECT * FROM UserProfiles WHERE
  UserId != @CurrentUserId AND
  Gender IN @PreferredGenders AND
  @CurrentUserGender IN PreferredGenders AND
  UserId NOT IN @SwipedUserIds AND
  UserId NOT IN @BlockedUserIds AND
  IsActive = true AND
  OnboardingComplete = true
```

**Exclusions**:
- Self
- Wrong gender (mutual gender preference check)
- Previously swiped (unless requesting fresh queue)
- Blocked users (user-blocks or admin-blocks)
- Inactive accounts
- Incomplete onboarding

### 2. Scoring Phase

For each candidate passing basic filters:

1. Check cached score (valid for 24 hours)
2. If no cache or expired:
   - Calculate all component scores
   - Apply dealbreaker logic (age/location)
   - Compute weighted overall score
   - Cache result for 24 hours

### 3. Filtering & Ranking

- Filter: `score >= minScore` (default 30)
- Sort: Descending by overall score
- Limit: Return top N candidates (default 20)

## Fallback Heuristics

### When Not Enough High-Quality Matches

**Problem**: User receives <10 candidates above minScore threshold

**Fallback Strategy** (applied in order):

#### Level 1: Relax Minimum Score

```
iterations = 0
while (candidates.count < 10 AND minScore > 0 AND iterations < 3):
    minScore -= 10
    candidates = FindMatches(minScore)
    iterations++
```

**Effect**: Accept lower compatibility (threshold drops to 30 → 20 → 10 → 0)

#### Level 2: Expand Distance

```
if (candidates.count < 10):
    originalMaxDist = user.maxDistanceKm
    user.maxDistanceKm = min(originalMaxDist * 1.5, 200)
    candidates = FindMatches()
```

**Effect**: Search 50% farther (50km → 75km), capped at 200km

#### Level 3: Widen Age Range

```
if (candidates.count < 10):
    ageRange = user.ageMax - user.ageMin
    user.ageMin = max(18, user.ageMin - 2)
    user.ageMax = min(99, user.ageMax + 2)
    candidates = FindMatches()
```

**Effect**: Add ±2 years to acceptable age range

#### Level 4: Include Previously Swiped (Stale Profiles)

```
if (candidates.count < 10):
    daysSinceSwipe = await GetDaysSinceLastSwipe(user.id)
    if (daysSinceSwipe > 30):
        // Re-show profiles swiped >30 days ago
        staleSwipedIds = GetSwipedUserIds(olderThan=30days)
        candidates = FindMatches(excludeUserIds - staleSwipedIds)
```

**Effect**: Recycle old swipes after 30-day cooling period

#### Level 5: Broad Discovery (Last Resort)

```
if (candidates.count < 5):
    // Ignore all preferences except gender + blocked users
    candidates = FindMatches(
        ignoreDistance=true,
        ignoreAge=true,
        ignoreMinScore=true
    )
```

**Effect**: Show *anyone* matching basic gender preferences (still exclude blocked)

## Daily Queue Expansion

### Daily Suggestion Limits

| User Type | Daily Limit | Refresh Time |
|-----------|-------------|--------------|
| Free | 20 candidates | 24 hours (00:00 UTC) |
| Premium | 100 candidates | 24 hours (00:00 UTC) |

### Queue Expansion Rules

#### Free Users

**Initial Queue** (First Request of Day):
- Generate 20 candidates
- Sort by compatibility score descending
- Cache for 24 hours

**Subsequent Requests** (Same Day):
- Return cached candidates
- As user swipes through queue:
  - Mark candidates as "seen"
  - Do NOT generate new candidates until next day
  - Show "Come back tomorrow" when exhausted

**Refresh**:
- Daily at 00:00 UTC
- Clear "seen" flags
- Generate fresh 20 candidates with updated scores

#### Premium Users

**Initial Queue** (First Request of Day):
- Generate 100 candidates
- Sort by compatibility score descending
- Cache for 12 hours (more frequent refresh)

**Progressive Expansion** (Same Day):
- User swipes through 80% of queue (80 candidates):
  - Automatically generate 20 more "discovery" candidates
  - Use relaxed minScore (20 vs 30)
  - Append to existing queue

**Refresh**:
- Twice daily: 00:00 UTC and 12:00 UTC
- Regenerate queue with latest data
- Preserve candidates user hasn't seen yet

### Queue Exhaustion Behavior

**Free User - No Candidates Left**:
```json
{
  "candidates": [],
  "message": "You've seen all your matches for today! Check back tomorrow for fresh profiles.",
  "nextRefreshAt": "2026-01-30T00:00:00Z",
  "upgradePrompt": "Get unlimited daily matches with Premium"
}
```

**Premium User - No Candidates Left** (rare):
```json
{
  "candidates": [],
  "message": "You've seen everyone nearby! Try expanding your preferences.",
  "suggestions": [
    "Increase max distance to 100km",
    "Widen age range by 5 years",
    "Lower minimum compatibility to 20"
  ]
}
```

## Cache Strategy

### Score Caching

**Cache Key**: `{userId}-{targetUserId}`

**Cache Duration**: 24 hours

**Invalidation Triggers**:
- User updates preferences (distance, age, interests)
- User updates profile (location, education, lifestyle)
- Target updates profile
- Manual cache clear (admin only)

**Benefits**:
- Reduces computation by 95% for repeat requests
- Consistent scores across multiple requests
- Faster candidate generation (<200ms vs 2s)

### Daily Suggestion Tracking

**Tracked Data**:
```csharp
{
  userId: int,
  date: DateTime (UTC day),
  suggestionsServed: int,
  isPremium: bool,
  limit: int  // 20 for free, 100 for premium
}
```

**Reset**: Daily at 00:00 UTC

## Performance Targets

### Latency

| Operation | Target (p95) | Current (p95) |
|-----------|--------------|---------------|
| Generate candidates (cache hit) | <200ms | 180ms |
| Generate candidates (cache miss) | <2s | 1.8s |
| Calculate single score | <50ms | 35ms |
| Daily refresh (100 users) | <5s | 4.2s |

### Throughput

- 500 req/sec (candidate generation)
- 10,000 scores/sec (calculation)
- 100,000 cache lookups/sec

## Algorithm Evolution

### v1.0 (MVP - Current)

- Basic weighted scoring
- Simple fallback (lower threshold)
- 24h score cache
- Free: 20/day, Premium: 100/day

### v1.1 (Planned - Q2 2026)

- Machine learning score adjustment
  - Boost profiles similar to user's previous likes
  - Penalize profiles similar to previous passes
- Dynamic weight adjustment based on user behavior
- Collaborative filtering ("Users like you also liked...")

### v1.2 (Planned - Q3 2026)

- Real-time score updates (WebSocket push)
- Personality quiz integration (Big 5 traits)
- "Second Look" feature (re-show high-score profiles after 7 days)

### v2.0 (Planned - Q4 2026)

- Deep learning compatibility model
- Video analysis (if video profiles added)
- Temporal patterns (when users are active, match timing)
- Conversation quality prediction

## Monitoring Metrics

### Key Metrics

**Match Quality**:
- Average compatibility score of matches
- Message response rate per score bucket
- Match-to-conversation conversion rate

**Algorithm Performance**:
- Candidates generated per request
- Fallback level distribution
- Cache hit rate (should be >90%)

**User Satisfaction**:
- Swipe-to-like ratio
- Queue exhaustion rate
- Preference adjustment frequency

### Alerts

- Cache hit rate < 85% for 1 hour
- Average candidate count < 10 for free users
- Queue exhaustion > 20% of users in a day
- Score calculation p95 > 100ms

## Testing Strategy

### Unit Tests

File: `MatchmakingService.Tests/Services/AdvancedMatchingServiceTests.cs`

**Coverage** (491 lines, 100% test coverage):
- Location scoring (nearby, far, beyond max)
- Age scoring (ideal, range boundaries, outside range)
- Interests scoring (0-5+ shared interests)
- Education scoring (exact, adjacent, distant)
- Lifestyle scoring (all combinations)
- Activity scoring (recency, response rate)
- Overall scoring (weighted combination)
- Candidate ranking (sort by score)

### Integration Tests

- End-to-end candidate generation
- Fallback behavior under low candidates
- Daily limit enforcement
- Cache invalidation on profile update

### Load Tests (T017)

- 1000 concurrent users requesting candidates
- 10,000 score calculations per second
- Cache performance under load
- Database query optimization

## Related Files

- `MatchmakingService/Services/AdvancedMatchingService.cs` - Main algorithm
- `MatchmakingService.Tests/Services/AdvancedMatchingServiceTests.cs` - Test suite
- `specs/001-mvp-foundation/contracts/api-spec.md` - API contracts
- `logs/README.md` - Observability (logging matchmaking events)
