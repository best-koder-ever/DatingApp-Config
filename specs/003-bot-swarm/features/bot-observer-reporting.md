# Feature: Bot Observer + Intelligence Reporting

**Phase**: 003-bot-swarm | **Wave**: 2
**Tasks**: T320-T330

## Problem
Bots interact with every API endpoint, swipe on profiles, read matches, send messages — yet all that telemetry disappears. We're throwing away the best QA data we have. A real user would tell us "the app felt slow", "I got weird matches", "nobody replied". Our bots can do this systematically, 24/7.

## Solution
Instrument the bot's API client (`DatingAppApiClient`) with an observer layer that measures every interaction and records **findings** — structured reports that describe what the bot experienced, scored by severity, and queryable via API. Then a `BotReporter` background service digests findings into actionable summaries.

## Finding Types

| Type | What Triggers It | Severity |
|------|-----------------|----------|
| `SlowEndpoint` | API call >2s | warning |
| `ApiError` | 4xx/5xx response | critical |
| `EmptyState` | GetCandidates returns 0 | info |
| `MatchQualityIssue` | Match age delta >15y or distance >200km | warning |
| `ConversationDead` | No reply after 3 messages in 48h | info |
| `SafetyIncident` | Classified suspicious/spam/sexual message | critical |
| `RateLimitHit` | 429 from any service | warning |
| `FeatureGap` | Expected feature missing (e.g. no read receipts) | info |

## Data Model

```csharp
public class BotFinding
{
    public int Id { get; set; }
    public string BotPersonaId { get; set; }
    public FindingType Type { get; set; }          // enum
    public FindingSeverity Severity { get; set; }   // info/warning/critical
    public string Title { get; set; }               // "Slow response from /api/matchmaking/candidates"
    public string Description { get; set; }         // "3247ms latency, expected <2000ms"
    public string MetadataJson { get; set; }        // { endpoint, statusCode, latencyMs, ... }
    public DateTime CreatedAt { get; set; }
    public bool Acknowledged { get; set; }
}
```

## Observer Architecture

```
┌─────────────────────┐
│ SyntheticUserService │
│ WarmupBotService     │
│ LoadTestService      │
└──────────┬──────────┘
           │ uses
           ▼
┌─────────────────────┐        ┌──────────────┐
│    BotObserver      │───────▶│ BotFinding   │
│ (wraps ApiClient)   │ writes │   (SQLite)   │
│                     │        └──────────────┘
│ • measures latency  │                │
│ • checks errors     │                │ reads
│ • detects anomalies │                ▼
└─────────────────────┘        ┌──────────────┐
                               │ BotReporter  │
                               │ (every 6h)   │
                               │              │
                               │ • aggregate  │
                               │ • summarize  │
                               │ • webhook    │
                               └──────┬───────┘
                                      │
                               ┌──────▼──────┐
                               │ REST API    │
                               │ /findings   │
                               │ /summary    │
                               │ /export     │
                               └─────────────┘
```

## Reporting API

### `GET /api/bot/findings`
```json
{
  "items": [
    {
      "id": 42,
      "botPersonaId": "sofia_28_stockholm",
      "type": "SlowEndpoint",
      "severity": "warning",
      "title": "Slow /api/matchmaking/candidates",
      "description": "3247ms latency from matchmaking service",
      "metadata": { "endpoint": "/api/matchmaking/candidates", "latencyMs": 3247 },
      "createdAt": "2025-07-15T14:32:00Z",
      "acknowledged": false
    }
  ],
  "total": 156,
  "page": 1,
  "pageSize": 20
}
```

### `GET /api/bot/findings/summary`
```json
{
  "period": "24h",
  "totalFindings": 42,
  "bySeverity": { "critical": 2, "warning": 15, "info": 25 },
  "byType": { "SlowEndpoint": 8, "EmptyState": 12, "ConversationDead": 15, ... },
  "topIssues": [
    { "title": "Matchmaking latency spike", "count": 8, "avgLatencyMs": 2847 },
    { "title": "Dead conversations after 3 messages", "count": 15 }
  ],
  "conversationHealth": {
    "avgDepth": 4.2,
    "fikaInviteRate": 0.12,
    "deadConvoRate": 0.35
  },
  "apiHealth": {
    "avgLatencyMs": 234,
    "p95LatencyMs": 1200,
    "errorRate": 0.02
  }
}
```

## Bot Daily Digest (sample output)

```markdown
# 🤖 Bot Intelligence Digest — 2025-07-15

## 🚨 Critical (2)
- SafetyIncident: User u_382 sent suspicious link to bot "Erik"
- ApiError: photo-service 500 error during upload (3 occurrences)

## ⚠️ Warnings (15)
- Matchmaking latency spike 14:00-15:00 (avg 2.8s, normally 200ms)
- 3 bots hit rate limit on messaging-service

## 📊 Conversation Health
- Avg conversation depth: 4.2 messages
- Dead convo rate: 35% (↑ from 28% yesterday)
- Fika invite success: 12% of conversations reached stage 4

## 💡 Insights
- "Sofia" persona has 2x match rate vs "Erik" — investigate profile factors
- Users respond faster (avg 3min) when bot asks a question vs statement
- Peak response hours: 19:00-22:00, lowest: 06:00-09:00
```

## Success Criteria

- [ ] Every API call measured with <1ms observer overhead
- [ ] Findings stored in SQLite with full metadata
- [ ] Summary API returns in <500ms for 24h window
- [ ] Daily digest generates automatically every 6h
- [ ] Critical findings surface within 1 cycle (normally 5-15 min)
- [ ] Export produces valid CSV/JSON for product analysis
