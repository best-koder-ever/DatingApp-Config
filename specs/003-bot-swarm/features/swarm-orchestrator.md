# Feature: Swarm Orchestrator + A/B Framework

**Phase**: 003-bot-swarm | **Wave**: 3
**Tasks**: T340-T350

## Problem
Current bot modes are static: start all bots, they run forever in one mode. No way to say "spin up 10 bots targeting users who signed up today" or "run 50 bots to load-test the messaging pipeline for 30 minutes". No experiments. No mission-based swarms.

## Solution
A `SwarmOrchestrator` that dynamically provisions bot squads for specific missions with time limits, auto-cleanup, and metric collection. Plus an A/B experiment framework that splits bots into variant groups and measures which conversation strategy performs better.

## Swarm Modes

### 1. Onboarding Assist
**Mission**: New user signs up → gets a match + message within 10 minutes
- Listen for new user registration events (or poll UserService)
- Select N bots matching user's preference (gender, age ±5y, city)
- Bots auto-swipe right on target → instant match
- LLM generates personalized opener based on user's profile
- Auto-decommission bots after user has 3+ matches or 24h elapsed

### 2. Retention Boost
**Mission**: Re-engage users who went inactive
- Query UserService for users inactive >48h
- Select 1 bot per inactive user (personality compatible)
- Bot swipes right + sends curiosity-piquing opener
- Max 1 nudge per user per 7 days (prevent annoyance)
- Track: did user return? did they respond? how deep did convo go?

### 3. Load Test
**Mission**: Stress-test infrastructure without LLM cost
- Spin up 50-500 bots using `CannedConversationEngine` only
- Rapid-fire: swipe → match → message → repeat
- Collect: API latency percentiles (p50/p95/p99), error rates, throughput
- Auto-generate load test report with pass/fail thresholds
- Useful before major releases or infrastructure changes

### 4. Experiment
**Mission**: A/B test conversation strategies
- Split N bots into Group A and Group B
- Each group uses different config: opener style, response delay, chattiness
- Run for X days, collect engagement metrics per group
- Auto-calculate: match rate, response rate, conversation depth, fika invite rate
- Declare winner with statistical significance (p < 0.05)

## API

```
POST   /api/bot/swarm              → Create swarm
GET    /api/bot/swarm              → List active swarms
GET    /api/bot/swarm/{id}         → Swarm status + metrics
DELETE /api/bot/swarm/{id}         → Kill swarm + cleanup bots
POST   /api/bot/experiments        → Create A/B experiment
GET    /api/bot/experiments        → List experiments
GET    /api/bot/experiments/{id}/results → Statistical results
```

### Create Swarm Request
```json
{
  "mode": "onboarding-assist",
  "count": 5,
  "targetUserIds": ["user_abc123"],
  "durationMinutes": 60,
  "conversationEngine": "llm",
  "config": {
    "maxMatchesPerTarget": 3,
    "openerStyle": "question"
  }
}
```

### Swarm Status Response
```json
{
  "id": "swarm_001",
  "mode": "onboarding-assist",
  "status": "active",
  "startedAt": "2025-07-15T14:00:00Z",
  "endsAt": "2025-07-15T15:00:00Z",
  "bots": [
    { "personaId": "sofia_28", "status": "active", "matchesMade": 1, "messagesSent": 3 }
  ],
  "metrics": {
    "totalMatches": 3,
    "totalMessages": 12,
    "avgTimeToFirstMatch": "4m 23s",
    "findingsGenerated": 2
  }
}
```

## Experiment Framework

```
┌────────────────────────────────────────────────────────────┐
│                    Experiment                               │
│ ┌──────────────────────┐  ┌──────────────────────────────┐ │
│ │ Group A (control)    │  │ Group B (variant)            │ │
│ │ • casual openers     │  │ • question openers           │ │
│ │ • 30s response delay │  │ • 10s response delay         │ │
│ │ • chattiness: 0.5    │  │ • chattiness: 0.8            │ │
│ │                      │  │                              │ │
│ │ 25 bots              │  │ 25 bots                      │ │
│ └──────────┬───────────┘  └──────────────┬───────────────┘ │
│            │                              │                 │
│            ▼                              ▼                 │
│   Metrics Collection              Metrics Collection        │
│   • match_rate: 42%               • match_rate: 58%        │
│   • response_rate: 31%            • response_rate: 47%     │
│   • avg_depth: 3.2                • avg_depth: 5.1         │
│   • fika_rate: 8%                 • fika_rate: 15%         │
│                                                             │
│   ExperimentAnalyzer → p-value = 0.003 → B wins ✓          │
└────────────────────────────────────────────────────────────┘
```

## Success Criteria

- [ ] Swarm provisions N bots within 30s
- [ ] Auto-decommission works reliably (no orphaned bots)
- [ ] Onboarding assist: new user has match within 10 min
- [ ] Load test: generates valid percentile report
- [ ] Experiment: correctly calculates statistical significance
- [ ] Kill switch: `DELETE /swarm/{id}` stops all bots <5s
