# Photo Coach Agent

**Agent**: 2 of 5
**Priority**: High Impact — Premium Feature
**Wave**: 2
**Tasks**: T220–T226
**Estimated Effort**: 68h total

---

## Problem

Bad photos are the **#1 reason profiles fail**. Users don't know:
- Their lighting is terrible
- All 6 photos are bathroom selfies
- They have no full-body or activity shots
- Their primary photo doesn't show their face clearly
- They're wearing sunglasses in every photo

No dating app helps users fix this. They just show a grid and say "upload 6 photos."

## Solution

An AI photo coach that:
1. **Analyzes each photo** — lighting, composition, face clarity, background
2. **Evaluates the set** — variety, missing categories, redundancy
3. **Gives specific advice** — "Add an outdoor activity shot" not "upload better photos"
4. **Ranks photos** — "This should be your primary" based on predicted engagement
5. **Tracks improvement** — before/after effect on match rates

## Architecture

```
User uploads photo → PhotoService stores it
  → Photo Coach Agent triggered (async)
    → Vision LLM (Claude 3.5 Sonnet / GPT-4o) analyzes:
      - Face visibility (0-10)
      - Lighting quality (0-10)
      - Background interest (0-10)
      - Photo category (selfie, full-body, activity, group, pet, travel)
      - Expression (smile, neutral, serious)
    → Set analysis (runs on all photos):
      - Category diversity score
      - Missing categories ("You need a full-body shot")
      - Redundancy ("Photos 2, 4, 5 are all indoor selfies — keep the best one")
    → Advice generation:
      - Top 3 actionable tips
      - Photo ranking (suggested primary)
      - "Your profile would improve most by adding: [activity shot]"
  → Results stored, surfaced in Flutter UI
```

## Key Design Decisions

### Why Vision LLM over custom ML?
- Custom photo scoring models need millions of labeled examples
- Vision LLMs already understand photo quality, composition, context
- Can give *natural language* advice, not just scores
- Cost: ~$0.02-0.05 per photo analysis (acceptable for premium feature)

### When to trigger analysis?
- On every new photo upload (individual analysis)
- When profile has 3+ photos (set analysis + ranking)
- On demand: "Coach me" button in profile editor
- NOT on every app open (too expensive)

### Premium or free?
- **Free**: Basic quality score (good/okay/poor) + one tip
- **Premium**: Full analysis, ranking, specific advice, tracking

## Tasks Breakdown

### T220: Photo Analysis Pipeline (12h, P1)
- Vision LLM integration for individual photo scoring
- Structured output: quality metrics + category + description
- Response caching (don't re-analyze unchanged photos)
- Error handling for LLM failures/timeouts

### T221: Photo Variety Scorer (8h, P1)
- Categorize each photo: selfie, full-body, activity, group, pet, travel, food
- Calculate diversity score across categories
- Detect over-representation (4+ selfies)
- Identify missing categories

### T222: Personalized Advice Generator (8h, P1)
- Generate 3 actionable tips based on what's *missing*
- Tone: encouraging, specific, non-judgmental
- Examples: "Your smile in photo 2 is great! Try getting a similar shot outdoors."
- Avoid: "Your photos are bad" — always frame positively

### T223: Photo Ranking (8h, P2)
- Predict which photo would get most engagement as primary
- Based on: face clarity, smile, lighting, uniqueness
- Suggest reordering with explanation
- "Photo 3 should be your primary — clear face, natural smile, good lighting"

### T224: Auto-enhance Suggestions (12h, P2)
- Detect fixable issues: too dark, off-center crop, weird aspect ratio
- Suggest crops and adjustments (preview in UI)
- Never auto-apply — user must confirm
- Use ImageSharp for basic adjustments (already in photo-service)

### T225: Flutter Photo Coach UI (12h, P1)
- Coach card in profile editor (collapsed by default)
- Per-photo quality indicator (green/yellow/red dot)
- Tips overlay on tap
- "Coach me" button → triggers full analysis
- Results show with photo thumbnails + advice

### T226: Before/After Tracking (8h, P3)
- Snapshot match rate before coaching
- Track match rate after user follows advice
- Aggregate data: "Users who follow coach advice get X% more matches"
- Feed back into advice quality — which tips actually help?

## Integration Points

- **PhotoService**: Photo storage, metadata, analysis trigger
- **Agent Gateway (T200)**: LLM routing and cost tracking
- **MatchmakingService**: Engagement data for ranking calibration
- **Flutter app**: Coach UI in profile editor
- **UserService**: Premium tier check (free vs full analysis)

## Example User Experience

```
User uploads 5 photos:
1. Dark bathroom selfie
2. Outdoor hiking shot (good lighting)
3. Selfie with sunglasses
4. Group photo at bar
5. Another selfie at home

Photo Coach says:
📸 Profile Photo Score: 6/10

✅ Great: Photo 2 (hiking shot) — clear face, natural setting, activity
⚠️ Tip 1: Make Photo 2 your primary — it's your strongest photo
⚠️ Tip 2: You have 3 selfies — keep Photo 5 (best lighting), remove 1 and 3
⚠️ Tip 3: Add a photo showing a hobby or interest (music, cooking, sports?)

Your profile is missing: full-body shot, pet photo (if you have one)
```
