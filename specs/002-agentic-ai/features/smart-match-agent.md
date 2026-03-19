# Smart Match Agent

**Agent**: 4 of 5
**Priority**: Core Differentiator — Long-term
**Wave**: 4
**Tasks**: T240–T245
**Estimated Effort**: 64h total

---

## Problem

Current matching algorithms are **static and dumb**:
- Weight-based scoring: `age_match * 0.3 + distance * 0.2 + interests * 0.5`
- Same weights for everyone — a 22-year-old and a 45-year-old get matched the same way
- No learning from outcomes — a user who unmatches 90% of suggestions still gets the same algo
- No explanation — "Why was I shown this person?" → silence

Hinge's "Most Compatible" is the closest competitor, but it's still a black box.

## Solution

An agent that **learns what works for each individual user**:
1. **Tracks the full funnel** — swipe → match → message → conversation quality → unmatch
2. **Builds per-user preference models** — not global averages
3. **Explains matches** — "We matched you because: shared hiking + similar message style"
4. **Detects anti-patterns** — "You swipe right on everyone → your matches are low quality"
5. **A/B tests itself** — agent-matched vs traditional scoring

## Architecture

```
User opens Discover → MatchmakingService generates candidates
  → Smart Match Agent overlay:
    → Fetch user's outcome history (swipes, messages, unmatch data)
    → For each candidate:
      → Static score (existing algorithm)
      → Agent score (learned preference model)
      → Combined score = weighted blend (start 80/20 static/agent → shift as data grows)
    → Rank by combined score
    → Generate explanation for top matches
    → Return ranked candidates with explanations

Learning loop:
  → User swipes right → signal: surface interest
  → Match + message within 24h → signal: real interest
  → 10+ messages exchanged → signal: compatibility
  → Unmatch within 24h → signal: poor match
  → Block/report → signal: very poor match
  → Update user preference model
```

## Key Design Decisions

### Why not pure ML from day 1?
- Need data first — the agent uses LLM reasoning while ML model accumulates training data
- LLM can reason about *why* two profiles might click (shared context, complementary interests)
- Once we have 10K+ outcome data points → train a dedicated ML model
- Agent and ML model can be blended

### Per-user vs global model?
- **Both.** Global model handles cold-start (new users)
- Per-user model kicks in after ~20 swipes + 3 matches
- Per-user model never overrides safety signals (high-risk users stay deprioritized)

### How transparent should explanations be?
- Show general themes: "shared interests," "similar communication style"
- Never show negative reasons: don't say "low match because they unmatch a lot"
- Explanations build trust and differentiate from competitors

## Tasks Breakdown

### T240: Outcome Tracking Pipeline (12h, P1)
- Event tracking: swipe, match, first_message, message_count, unmatch, block
- Per-pair outcome table: user_a, user_b, event_type, timestamp
- Aggregate stats per user: swipe_right_rate, message_rate, avg_conversation_length
- Data pipeline for ML training set generation

### T241: User Preference Learning (16h, P1)
- Feature extraction: what do right-swipes have in common?
- Embedding-based similarity: profile text → vector, cluster preferences
- Behavioral signals: response speed, message length, conversation depth
- Cold-start handling: use global stats + demographics
- Model update frequency: nightly batch, not real-time

### T242: Match Explanation (8h, P2)
- LLM generates human-readable explanation per match
- Template: "You both [shared activity]. You have similar [trait]."
- Show in discover card and match notification
- A/B test: do explanations increase message rate?

### T243: Anti-Pattern Detection (8h, P2)
- Detect: swipe right on everyone (>90% right-swipe rate)
- Detect: never message matches (match-to-message < 10%)
- Detect: instant unmatch pattern (unmatch within 1h of matching)
- Gentle nudge: "Quality over quantity — being selective leads to better matches"
- Don't punish — educate

### T244: Feedback Incorporation (8h, P2)
- "How was this match?" thumb up/down after first conversation
- Feed into preference model as strong signal
- Don't badger: ask once per match, only after 5+ messages exchanged
- Use feedback to detect model drift

### T245: A/B Test Framework (12h, P2)
- Split users: agent-ranked vs static-ranked discovery
- Track: conversation rate, unmatch rate, message depth, user satisfaction
- Statistical significance calculator
- Auto-promote winner after N users
- Guard rail: auto-rollback if agent performs 20%+ worse

## Data Schema

```sql
-- Outcome events
CREATE TABLE match_outcomes (
    id UUID PRIMARY KEY,
    user_a_id UUID NOT NULL,
    user_b_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- swipe_right, match, first_message, conversation, unmatch, block
    event_data JSONB,                -- message_count, conversation_hours, etc.
    created_at TIMESTAMPTZ NOT NULL
);

-- User preference model (stored as embedding + metadata)
CREATE TABLE user_preference_models (
    user_id UUID PRIMARY KEY,
    model_version INT NOT NULL,
    preference_embedding VECTOR(256),
    behavioral_stats JSONB,          -- swipe_rate, message_rate, avg_conv_length
    updated_at TIMESTAMPTZ NOT NULL
);
```

## Integration Points

- **MatchmakingService**: Primary integration — overlay on candidate scoring
- **SwipeService**: Swipe events feed outcome pipeline
- **MessagingService**: Message events, conversation depth tracking
- **UserService**: Profile data, preference model storage
- **Agent Gateway (T200)**: LLM for explanations and cold-start reasoning
- **Flutter app**: Match explanations in discover and match screens

## Risks

- **Cold start**: New users have no data → agent adds no value initially
- **Filter bubbles**: Agent might reinforce biases ("you always swipe X → only show X")
- **Computational cost**: Per-user models at scale = significant DB/compute
- **Creepiness**: "The app knows my type better than I do" — need careful framing
