# 003 — Intelligent Bot Swarm: LLM-Powered Synthetic Users + App Intelligence

**Created**: 2026-03-13
**Phase**: 003
**Status**: 📋 Planning
**Depends on**: 001-mvp-foundation (core loop), bot-service (safety guards shipped)

---

## 🎯 Vision

> Real dating apps run bot swarms for onboarding, retention, load testing, and product research.
> Our bots should be **indistinguishable from real users**, generate **actionable product intelligence**,
> and serve as an **always-on QA team** that finds bugs before users do.

**Core Thesis**: Bots that talk like real humans AND report back what they observe = the cheapest, fastest product team you can hire.

---

## 📊 What Bots Report Back (App Intelligence)

Bots are **instrumented observers**. Every interaction generates structured telemetry:

### 1. UX Pain Points (API-level)
- **Slow endpoints**: "GET /api/Matchmaking/profiles/{id} took 4200ms" → performance alert
- **Error rates**: "POST /api/Messages returned 500 3x in 10 min" → reliability alert
- **Empty states**: "0 candidates returned for bot_sofia (F, 28, Stockholm)" → matchmaking tuning signal
- **Rate limit hits**: "429 on swipe after 12 swipes in 90s" → rate limit calibration

### 2. Product Quality Signals
- **Match quality**: "Matched with user age 65 despite age preference 25-35" → filter bug
- **Dead conversations**: "8/10 matches never responded to opener" → opener quality signal
- **Conversation depth**: "Average conversation dies at message #3" → engagement insight
- **Time-to-match**: "New bot took 45min to get first match" → onboarding friction metric

### 3. Safety & Trust Signals
- **Harassment received**: Bot receives suspicious messages → feeds Safety Agent training data
- **Catfish detection**: Bot detects inconsistencies in matched profiles → trust scoring input
- **Spam patterns**: "User X sent identical message to 3 bots" → spam detection training
- **Block patterns**: "Bot blocked by 5 users in 1 hour" → bot behavior needs tuning

### 4. Feature Usage Analytics
- **Conversation patterns**: What topics do users discuss? (anonymized, aggregated)
- **Peak activity**: When are users most active? → optimize bot active hours
- **Photo engagement**: Which bot profile photos generate more right-swipes?
- **Message response rates**: Which opener styles get the most replies?

---

## 🤖 LLM Strategy — Free & Fast

### Primary: Google Gemini 2.5 Flash-Lite (FREE)
- **Cost**: $0.00 on free tier (standard), $0.10/M tokens on paid
- **Speed**: ~200 tokens/sec, optimized for throughput
- **Swedish**: Excellent — Google's multilingual training is top-tier
- **Context**: 1M tokens — can feed entire conversation history
- **Rate limit**: ~500 RPD free, 30 RPM — enough for 100 bots × 5 msgs/day
- **Why primary**: Free, fast, great Swedish, massive context window

### Fallback: Groq (Llama 3.3 70B) — FREE tier
- **Cost**: $0.00 on free tier, $0.59/M on paid
- **Speed**: 280 tokens/sec on Groq LPU — world's fastest inference
- **Swedish**: Good (Llama 3.3 70B trained on multilingual data)
- **Context**: 131K tokens
- **Rate limit**: 1K RPD free for 70B, 30 RPM — good burst capacity
- **Why fallback**: OpenAI-compatible API, fastest inference, good Swedish
- **Also available**: `qwen/qwen3-32b` (400 tok/s, excellent multilingual)

### Development/Testing: Ollama (Local) — $0.00
- **Cost**: Electricity only
- **Models**: Qwen3 32B, Llama 3.3, Gemma 3 — all good for Swedish
- **Speed**: 30-80 tok/s on GPU, sufficient for dev
- **Rate limit**: None — your hardware is the limit
- **Why dev**: Zero cost, zero rate limits, privacy, offline capable

### Scaling backup: Cerebras (free tier)
- **Cost**: $0.00 free, $0.35/M paid
- **Speed**: 3000 tokens/sec (!!) — 20x faster than OpenAI
- **Models**: GPT-OSS 120B, Llama 3.1 8B
- **Why backup**: Incredible speed for burst scenarios (load testing mode)

### Cost Projection (100 bots, production)
| Scenario | Tokens/day | Gemini Free | Groq Free | Paid (cheapest) |
|----------|-----------|-------------|-----------|-----------------|
| 20 msgs/bot/day | 200K | ✅ Free | ✅ Free | $0.02/day |
| 50 msgs/bot/day | 500K | ✅ Free | ⚠️ Near limit | $0.05/day |
| 100 msgs/bot/day | 1M | ⚠️ Near limit | ❌ Over limit | $0.10/day |

**Bottom line**: Completely free for typical usage. Under $3/month even at aggressive scale.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│  bot-service                                             │
│                                                         │
│  ┌─────────────┐     ┌──────────────────┐               │
│  │ BotPersona  │────▶│ IConversationEngine │             │
│  │ (identity)  │     │  ├─ CannedEngine   │◀──messages.json│
│  └─────────────┘     │  ├─ GeminiEngine   │◀──Gemini API  │
│         │            │  ├─ GroqEngine     │◀──Groq API    │
│         ▼            │  └─ OllamaEngine   │◀──localhost   │
│  ┌─────────────┐     └──────────────────┘               │
│  │ BotObserver │────▶ BotFindingsStore (SQLite)          │
│  │ (telemetry) │     │ ├─ ApiLatency                     │
│  └─────────────┘     │ ├─ ConversationMetrics            │
│         │            │ ├─ MatchQualitySignals             │
│         ▼            │ ├─ SafetyIncidents                │
│  ┌─────────────┐     │ └─ UxPainPoints                   │
│  │ BotReporter │     └────────────────────┘              │
│  │ (scheduled) │────▶ POST /api/bot/findings (API)       │
│  └─────────────┘────▶ DailyDigestEmail (optional)        │
│                 ────▶ Structured logs (Seq/Grafana)       │
│                                                         │
│  SwarmOrchestrator ───────────────────────────┐         │
│  │ POST /api/bot/swarm                        │         │
│  │  { mode, count, target, duration, experiment }│        │
│  │  → spin up/down bots dynamically            │         │
│  └─────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

---

## 📐 Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Bot indistinguishability | <10% of users suspect bot | Post-unmatch survey |
| LLM response latency | <2s p95 | BotObserver timing |
| Swedish naturalness | >4.0/5.0 | LLM-judge evaluation |
| Findings per day | >50 actionable signals | BotFindingsStore count |
| False positive rate (safety) | <5% | Human review of bot-reported incidents |
| Time-to-first-match (new bot) | <10 min | BotObserver.MatchLatency |
| Cost per bot per month | <$1 | LLM token tracking |
| Bug detection rate | >3 bugs/week found by bots | Findings → JIRA pipeline |

---

## 🔗 Integration Points (What Exists Today)

| Component | Status | Notes |
|-----------|--------|-------|
| `BotPersona` model | ✅ Shipped | Has identity, interests, behavior — perfect for system prompts |
| `MessageContentProvider` | ✅ Shipped | Canned messages by stage — replace with `IConversationEngine` |
| `DatingAppApiClient` | ✅ Shipped | Full HTTP client for all 6 services + safety |
| `BotState` tracking | ✅ Shipped | Per-user message counts, blocked cache, unresponsive tracking |
| `BotController` API | ✅ Shipped | Status, pause/resume, personas — extend with findings/swarm |
| `ExcludeBotFilter` | ✅ Shipped | Bots never match each other (MatchmakingService) |
| `IsBot` transparency | ✅ Shipped | UserService + MatchmakingService flag bots in DB |
| Safety service integration | ✅ Shipped | Block checking, blocked-by cache per cycle |
| Credential security | ✅ Shipped | Env var overrides for passwords |

---

## 📅 Timeline

| Wave | Duration | Focus |
|------|----------|-------|
| **Wave 0** | 1 week | LLM abstraction + Gemini integration + prompt engineering |
| **Wave 1** | 1 week | Conversation engine (persona-aware, multi-stage, Swedish) |
| **Wave 2** | 1 week | BotObserver + findings store + reporting API |
| **Wave 3** | 1 week | Swarm orchestrator + A/B framework |
| **Wave 4** | 1 week | Photo pipeline + advanced personas + polish |
| **Wave 5** | Ongoing | Monitoring, tuning, new swarm modes, LLM improvements |

Total: **5 weeks** to production-ready intelligent bot swarm.
