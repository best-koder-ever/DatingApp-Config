# Tasks: 003 — Intelligent Bot Swarm

**Input**: SCOPE.md, existing bot-service codebase, LLM provider research
**Prerequisites**: bot-service shipped with safety guards, MatchmakingService ExcludeBotFilter, UserService IsBot flag

---

## Wave 0: LLM Infrastructure (Week 1)

**Goal**: Build provider-agnostic LLM abstraction. Ship Gemini integration first. Validate Swedish output quality.

### LLM Abstraction Layer
- [x] T300 [P0] [Infra] Create `ILlmProvider` interface — `Task<string> GenerateAsync(LlmRequest request, CancellationToken ct)` with `LlmRequest { SystemPrompt, Messages[], MaxTokens, Temperature }` and `LlmResponse { Content, TokensUsed, LatencyMs, Provider }`
- **Estimate**: 2h
- **File**: `Services/Llm/ILlmProvider.cs`, `Models/LlmRequest.cs`, `Models/LlmResponse.cs`
- **Evidence**: Interface compiles, used by T301-T303

- [x] T301 [P0] [Infra] Implement `GeminiLlmProvider` — HTTP client calling `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent`, API key from `GEMINI_API_KEY` env var, JSON request/response mapping, retry on 429 with exponential backoff
- **Estimate**: 4h
- **File**: `Services/Llm/GeminiLlmProvider.cs`
- **Depends on**: T300
- **Evidence**: `dotnet test` with integration test hitting Gemini free tier, Swedish response received

- [x] T302 [P1] [Infra] Implement `GroqLlmProvider` — HTTP client calling `https://api.groq.com/openai/v1/chat/completions` (OpenAI-compatible), API key from `GROQ_API_KEY`, model default `llama-3.3-70b-versatile`, automatic fallback to `llama-3.1-8b-instant` on 429
- **Estimate**: 3h
- **File**: `Services/Llm/GroqLlmProvider.cs`
- **Depends on**: T300
- **Evidence**: Integration test passes with Groq free tier

- [x] T303 [P2] [Infra] Implement `OllamaLlmProvider` — HTTP client calling `http://localhost:11434/v1/chat/completions`, model from config (default `qwen3:32b`), timeout 30s, health check on startup
- **Estimate**: 2h
- **File**: `Services/Llm/OllamaLlmProvider.cs`
- **Depends on**: T300
- **Evidence**: Works with locally running Ollama instance

- [x] T304 [P0] [Infra] Create `LlmRouter` — selects provider based on config priority, implements circuit breaker (3 failures → fallback), tracks token usage per provider per day, respects daily budget caps
- **Estimate**: 4h
- **File**: `Services/Llm/LlmRouter.cs`
- **Depends on**: T301, T302, T303
- **Evidence**: Unit test: primary fails → falls to secondary. Budget exceeded → returns canned fallback.

- [x] T305 [P0] [Infra] Add LLM configuration to `BotServiceOptions` — `LlmOptions { PrimaryProvider, FallbackProvider, DailyTokenBudget, MaxTokensPerMessage, Temperature, ApiKeys }`, bind from appsettings.json + env vars
- **Estimate**: 1h
- **File**: `Configuration/BotServiceOptions.cs`, `appsettings.json`
- **Evidence**: Config loads, providers initialize from config

- [x] T306 [P0] [Infra] Register LLM services in DI — `AddSingleton<ILlmProvider, GeminiLlmProvider>()` etc, `AddSingleton<LlmRouter>()`, keyed by provider name
- **Estimate**: 1h
- **File**: `Program.cs`
- **Depends on**: T305
- **Evidence**: `dotnet build` succeeds, services resolve from DI

### Prompt Engineering
- [x] T307 [P0] [AI] Design Swedish bot system prompt template — incorporate persona fields (name, age, city, occupation, interests, bio, chattiness), conversation stage detection, persona voice (formal/casual/flirty based on `BotBehavior`), explicit Swedish language instruction, max length guardrail (2 sentences)
- **Estimate**: 3h
- **File**: `Services/Llm/PromptTemplates.cs`
- **Depends on**: T300
- **Evidence**: 10 sample prompts reviewed for naturalness. Swedish native speaker evaluation.

- [x] T308 [P0] [AI] Build conversation context formatter — takes last N messages from `DatingAppApiClient.GetConversationsAsync()`, formats as `[user]: message\n[bot]: message\n...` for LLM context window, truncates to 2000 tokens max
- **Estimate**: 2h
- **File**: `Services/Llm/ConversationContextBuilder.cs`
- **Depends on**: T307
- **Evidence**: Unit test: 20 messages → truncated to last 8 within 2K tokens

- [x] T309 [P1] [AI] LLM output guardrails — post-processing filter that rejects responses containing: real phone numbers, URLs, "jag är en AI/bot", English (>20% English words), messages longer than 280 chars. Falls back to canned message on rejection.
- **Estimate**: 2h
- **File**: `Services/Llm/ResponseGuardrails.cs`
- **Evidence**: Unit tests for all rejection cases

**Wave 0 Total: ~24h / 10 tasks**

---

## Wave 1: Conversation Engine (Week 2)

**Goal**: Replace canned messages with LLM-powered, persona-aware conversations. Keep canned as fallback.

### Core Engine
- [x] T310 [P0] [Core] Create `IConversationEngine` interface — `Task<string> GenerateReplyAsync(BotPersona persona, string matchKeycloakId, ConversationContext context, CancellationToken ct)` where `ConversationContext` includes stage, message history, match profile snippet, bot mood
- **Estimate**: 2h
- **File**: `Services/Conversation/IConversationEngine.cs`, `Models/ConversationContext.cs`

- [x] T311 [P0] [Core] Implement `CannedConversationEngine` — wraps existing `MessageContentProvider`, implements `IConversationEngine`, zero LLM calls, used as fallback and for load testing mode
- **Estimate**: 1h
- **File**: `Services/Conversation/CannedConversationEngine.cs`
- **Depends on**: T310
- **Evidence**: Returns same messages as current `MessageContentProvider.GetMessageForDepth()`

- [x] T312 [P0] [Core] Implement `LlmConversationEngine` — builds prompt from persona + context, calls `LlmRouter`, applies guardrails, falls back to canned on failure, logs token usage + latency
- **Estimate**: 4h
- **File**: `Services/Conversation/LlmConversationEngine.cs`
- **Depends on**: T304, T307, T308, T309, T310
- **Evidence**: Integration test: persona "Sofia" generates Swedish response to "Hej! Hur mår du?"

- [x] T313 [P0] [Core] Wire `IConversationEngine` into `SyntheticUserService.ChatWithMatchesAsync()` — replace `_messageProvider.GetMessageForDepth()` with `_conversationEngine.GenerateReplyAsync()`, pass conversation history from API
- **Estimate**: 2h
- **File**: `Services/BotModes/SyntheticUserService.cs`
- **Depends on**: T312
- **Evidence**: Bots send LLM-generated Swedish messages instead of canned

- [x] T314 [P0] [Core] Wire `IConversationEngine` into `WarmupBotService.WarmupRespondAsync()` — same integration for warmup mode
- **Estimate**: 1h
- **File**: `Services/BotModes/WarmupBotService.cs`
- **Depends on**: T312

### Conversation Intelligence
- [x] T315 [P1] [AI] Implement conversation stage detection — LLM-based or rule-based classifier: `intro → getting_to_know → deep_talk → suggest_fika → post_fika`. Updates `BotState.ConversationStageJson` per match.
- **Estimate**: 3h
- **File**: `Services/Conversation/ConversationStageDetector.cs`
- **Depends on**: T310
- **Evidence**: Unit test: 5 sample convo transcripts → correct stage classification

- [ ] T316 [P1] [AI] Persona voice calibration — test matrix: generate 10 messages per persona across all 12 personas, evaluate Swedish naturalness 1-5 via LLM-judge (`gemini-2.5-flash`), tune system prompt based on results
- **Estimate**: 3h
- **File**: `Tests/Integration/PersonaVoiceTests.cs`
- **Depends on**: T312
- **Evidence**: All 12 personas score >3.5/5.0 Swedish naturalness

- [x] T317 [P2] [AI] Implement received-message analysis — when bot receives a message, briefly classify: `normal / flirty / cold / suspicious / spam / sexual`. Use classification to adjust bot response tone + feed into BotObserver safety signals.
- **Estimate**: 3h
- **File**: `Services/Conversation/MessageClassifier.cs`
- **Depends on**: T304
- **Evidence**: Unit test: "Hej vackra!" → `flirty`. "Kolla min länk" → `suspicious`.

- [x] T318 [P1] [Core] Add conversation engine config toggle — `BotServiceOptions.ConversationEngine: "llm" | "canned" | "hybrid"`. Hybrid = LLM for first contact + deepening, canned for fill messages. Per-persona override possible.
- **Estimate**: 1h
- **File**: `Configuration/BotServiceOptions.cs`, `Program.cs`
- **Evidence**: Toggle works at runtime via `IOptionsMonitor`

**Wave 1 Total: ~20h / 9 tasks**

---

## Wave 2: Bot Observer + Findings Report-Back (Week 3)

**Goal**: Bots report what they see — like a normal user complaining about bugs, but structured and actionable.

### Data Model
- [x] T320 [P0] [Data] Create `BotFinding` entity — `{ Id, BotPersonaId, FindingType (enum), Severity (info/warning/critical), Title, Description, Metadata (JSON), CreatedAt, Acknowledged }`. Types: `SlowEndpoint, ApiError, EmptyState, MatchQualityIssue, ConversationDead, SafetyIncident, RateLimitHit, FeatureGap`
- **Estimate**: 2h
- **File**: `Models/BotFinding.cs`

- [x] T321 [P0] [Data] Add `DbSet<BotFinding>` to `BotDbContext`, create migration
- **Estimate**: 1h
- **File**: `Data/BotDbContext.cs`
- **Depends on**: T320

### Observer Layer (instruments DatingAppApiClient)
- [x] T322 [P0] [Core] Create `BotObserver` service — wraps `DatingAppApiClient` to measure every API call: latency, status code, payload size. Records findings when: latency >2s, 4xx/5xx errors, empty results for expected data
- **Estimate**: 4h
- **File**: `Services/Intelligence/BotObserver.cs`
- **Depends on**: T320, T321
- **Evidence**: Integration test: mock slow API → finding created with type=SlowEndpoint

- [x] T323 [P0] [Core] Instrument `SyntheticUserService` with observer — after `GetCandidatesAsync()`: record empty_state if 0 results. After `SwipeAsync()`: record match quality (age delta, distance). After `ChatWithMatchesAsync()`: record conversation depth + dead convos.
- **Estimate**: 3h
- **File**: `Services/BotModes/SyntheticUserService.cs`
- **Depends on**: T322

- [x] T324 [P1] [Core] Add safety incident recording — when bot receives classified `suspicious`/`spam`/`sexual` message (from T317), create finding with full context: sender ID, message content hash (not plain text for privacy!), pattern, timestamp
- **Estimate**: 2h
- **File**: `Services/Intelligence/SafetyIncidentRecorder.cs`
- **Depends on**: T317, T322

- [x] T325 [P1] [Core] Track conversation metrics per match — `{ matchId, firstMessageAt, lastMessageAt, messagesExchanged, avgResponseTimeMs, conversationStage, outcome (ongoing/dead/fika_suggested/blocked) }`. Updates BotState JSON field.
- **Estimate**: 2h
- **File**: `Services/Intelligence/ConversationTracker.cs`
- **Depends on**: T315

### Reporting API
- [x] T326 [P0] [API] `GET /api/bot/findings` — paginated list of findings, filter by type/severity/date/persona. Returns JSON array. Used by dashboard/scripts.
- **Estimate**: 2h
- **File**: `Controllers/BotController.cs`
- **Depends on**: T321

- [x] T327 [P0] [API] `GET /api/bot/findings/summary` — aggregated dashboard: counts by type, top 5 critical findings, avg API latency by endpoint, conversation health metrics, findings trend (last 7 days)
- **Estimate**: 3h
- **File**: `Controllers/BotController.cs`
- **Depends on**: T326

- [x] T328 [P1] [Core] `BotReporter` background service — runs every 6 hours, generates "daily digest" of findings: top issues, trends, anomalies. Logs structured summary. Optionally webhooks to Slack/Discord.
- **Estimate**: 3h
- **File**: `Services/Intelligence/BotReporter.cs`
- **Depends on**: T326, T327

- [x] T329 [P1] [API] `GET /api/bot/findings/export` — CSV/JSON export of all findings for analysis. Useful for product meetings.
- **Estimate**: 1h
- **File**: `Controllers/BotController.cs`
- **Depends on**: T326

- [ ] T330 [P2] [Script] `scripts/bot-daily-digest.py` — Python script that queries `/api/bot/findings/summary`, formats Markdown report, optionally sends to email/Slack. Cron-schedulable.
- **Estimate**: 2h
- **File**: `scripts/bot-daily-digest.py`
- **Depends on**: T327

**Wave 2 Total: ~25h / 11 tasks**

---

## Wave 3: Swarm Orchestrator + A/B Framework (Week 4)

**Goal**: Dynamically spin up/down bot swarms for specific missions. Run experiments.

### Swarm Orchestration
- [x] T340 [P0] [Core] `SwarmOrchestrator` service — manages bot lifecycle: provision N bots on demand, assign to specific mode, set duration, auto-decommission when done. Supports concurrent swarms.
- **Estimate**: 6h
- **File**: `Services/Swarm/SwarmOrchestrator.cs`, `Models/SwarmConfig.cs`
- **Evidence**: API call creates 5 bots, they act for 30min, then auto-stop

- [x] T341 [P0] [API] `POST /api/bot/swarm` — `{ mode: "onboarding-assist"|"retention-boost"|"load-test"|"experiment", count, targetUserIds?, durationMinutes, experimentId? }`. Returns swarm ID for tracking.
- **Estimate**: 3h
- **File**: `Controllers/SwarmController.cs`
- **Depends on**: T340

- [x] T342 [P0] [API] `GET /api/bot/swarm/{id}` — swarm status: active bots, matches made, messages sent, findings generated, time remaining
- **Estimate**: 2h
- **File**: `Controllers/SwarmController.cs`
- **Depends on**: T341

- [x] T343 [P1] [API] `DELETE /api/bot/swarm/{id}` — stop a running swarm, decommission all its bots
- **Estimate**: 1h
- **File**: `Controllers/SwarmController.cs`
- **Depends on**: T341

### Swarm Modes
- [x] T344 [P0] [Mode] `OnboardingAssistSwarm` — dynamic persona factory picks N bots to match new user's gender preference + age range + location, auto-swipes right on target user, sends opener within 5 min of match. Goal: new user has match within 10 min.
- **Estimate**: 4h
- **File**: `Services/Swarm/Modes/OnboardingAssistSwarm.cs`
- **Depends on**: T340

- [x] T345 [P1] [Mode] `RetentionBoostSwarm` — finds users inactive >48h, sends them a "new match" by having a bot swipe right + send interesting opener. Max 1 retention nudge per user per week.
- **Estimate**: 3h
- **File**: `Services/Swarm/Modes/RetentionBoostSwarm.cs`
- **Depends on**: T340

- [x] T346 [P1] [Mode] `LoadTestSwarm` — spin up 50-500 bots doing rapid swipe/match/message cycles using canned engine (no LLM cost). Measure: API latency percentiles, error rates, DB connection pool usage. Output: load test report.
- **Estimate**: 4h
- **File**: `Services/Swarm/Modes/LoadTestSwarm.cs`
- **Depends on**: T340, T322

- [ ] T347 [P2] [Mode] `ExperimentSwarm` — A/B testing: split bots into groups, each group uses different conversation strategy (opener style, response delay, chattiness level). Track engagement metrics per group.
- **Estimate**: 5h
- **File**: `Services/Swarm/Modes/ExperimentSwarm.cs`
- **Depends on**: T340, T325

### A/B & Experiment Framework
- [x] T348 [P1] [Data] Create `Experiment` entity — `{ Id, Name, Status, GroupA config, GroupB config, StartedAt, EndsAt, Metrics JSON }`. Stored in BotDbContext.
- **Estimate**: 2h
- **File**: `Models/Experiment.cs`, `Data/BotDbContext.cs`

- [x] T349 [P1] [API] `POST /api/bot/experiments` — create experiment, `GET` list, `GET /{id}/results` — statistical comparison of group A vs B metrics (match rate, conversation depth, response rate)
- **Estimate**: 3h
- **File**: `Controllers/ExperimentController.cs`
- **Depends on**: T348, T347

- [ ] T350 [P2] [Core] Experiment result calculator — compute: p-value for metric differences, confidence intervals, sample size adequacy, winner declaration. Simple t-test implementation.
- **Estimate**: 3h
- **File**: `Services/Swarm/ExperimentAnalyzer.cs`
- **Depends on**: T349

**Wave 3 Total: ~36h / 11 tasks**

---

## Wave 4: Photo Pipeline + Advanced Personas (Week 5)

**Goal**: Bots get profile photos. Personas become richer and more diverse. Quality polish.

### Photo Pipeline
- [ ] T360 [P1] [Core] AI photo generation integration — use Stitch MCP or Stability AI API to generate diverse, realistic profile photos. One portrait + 2-3 lifestyle photos per persona. Match persona demographics (age, gender, ethnicity).
- **Estimate**: 6h
- **File**: `Services/Photo/BotPhotoGenerator.cs`
- **Evidence**: 12 personas each have 3-4 generated photos

- [ ] T361 [P1] [Core] Upload generated photos via photo-service API — `POST /api/photos/upload` with multipart form, set as profile photos, handle moderation pipeline
- **Estimate**: 3h
- **File**: `Services/Photo/PhotoUploader.cs`
- **Depends on**: T360

- [ ] T362 [P2] [Core] Photo variety testing — A/B test different photo styles per persona (casual vs professional vs activity-based), track which generate more right-swipes via BotObserver
- **Estimate**: 3h
- **Depends on**: T347, T361

### Persona Expansion
- [ ] T363 [P1] [Content] Expand from 12 to 50 personas — cover wider age range (20-55), diverse occupations, suburban/rural personas (not just Stockholm), different chattiness levels, varied relationship goals. Use LLM to generate persona bios.
- **Estimate**: 4h
- **File**: `Content/Personas/*.json` (38 new files)
- **Evidence**: `dotnet test` validates all 50 personas load correctly

- [ ] T364 [P2] [AI] Dynamic persona generation — API endpoint `POST /api/bot/personas/generate` that generates a persona on-the-fly via LLM, given constraints: `{ ageRange, gender, city, interests[] }`. Stores in SQLite for reuse.
- **Estimate**: 4h
- **File**: `Services/PersonaGenerator.cs`, `Controllers/BotController.cs`
- **Depends on**: T304

- [ ] T365 [P2] [AI] Persona behavior learning — after 100+ interactions, adjust persona behavior based on success rates: if "Sofia" gets more matches with casual openers, increase her casual response probability. Self-tuning bots.
- **Estimate**: 5h
- **File**: `Services/Intelligence/PersonaTuner.cs`
- **Depends on**: T325, T348

### Quality & Polish
- [ ] T366 [P1] [Test] Swedish naturalness benchmark — create evaluation suite: 100 generated messages scored 1-5 by LLM-judge for naturalness, grammar, persona consistency. Run as part of CI. Fail if avg <3.5.
- **Estimate**: 3h
- **File**: `Tests/Integration/SwedishNaturalnessTests.cs`
- **Depends on**: T312

- [ ] T367 [P1] [Ops] Bot health dashboard script — `scripts/bot-dashboard.sh` that queries `/api/bot/status`, `/api/bot/findings/summary`, formats terminal-friendly overview. For daily monitoring.
- **Estimate**: 2h
- **File**: `scripts/bot-dashboard.sh`

- [ ] T368 [P1] [Docs] Bot swarm operations runbook — document all API endpoints, swarm modes, LLM providers, configuration, troubleshooting. Add to RUNBOOK.md.
- **Estimate**: 2h
- **File**: `RUNBOOK.md` additions, `README.md` update

**Wave 4 Total: ~32h / 9 tasks**

---

## Wave 5: Continuous Improvement (Ongoing)

**Goal**: Monitor, tune, expand capabilities over time.

- [ ] T380 [P2] [Ops] Prometheus metrics exporter — expose bot metrics in Prometheus format: `bot_swipes_total`, `bot_messages_total`, `bot_findings_total`, `llm_tokens_used_total`, `llm_latency_seconds`
- **Estimate**: 3h

- [ ] T381 [P2] [Core] Webhook notifications — push critical findings to Slack/Discord webhook. Configurable severity threshold.
- **Estimate**: 2h

- [ ] T382 [P3] [AI] Multi-language bot support — add English personas for international testing. Finnish and Norwegian personas for Nordics expansion.
- **Estimate**: 4h

- [ ] T383 [P3] [AI] Voice message bot support — use TTS to generate voice messages via messaging-service. Test voice chat feature when implemented.
- **Estimate**: 6h

- [ ] T384 [P3] [Core] Bot marketplace API — allow configuring bot swarms via admin UI (not just API). Flutter admin panel for bot management.
- **Estimate**: 8h

---

## 📊 Summary

| Wave | Tasks | Estimate | Focus |
|------|-------|----------|-------|
| 0: LLM Infrastructure | 10 | ~24h | Provider abstraction, Gemini/Groq/Ollama, prompts |
| 1: Conversation Engine | 9 | ~20h | IConversationEngine, persona-aware LLM chat |
| 2: Bot Observer + Reporting | 11 | ~25h | Findings store, API telemetry, daily digest |
| 3: Swarm Orchestrator | 11 | ~36h | Dynamic swarms, onboarding/retention/load/A-B modes |
| 4: Photos + Personas | 9 | ~32h | Photo gen, 50 personas, naturalness benchmark |
| 5: Continuous | 5 | ~23h | Prometheus, webhooks, multi-lang, admin UI |
| **TOTAL** | **55** | **~160h** | **Full intelligent bot swarm platform** |

### Critical Path
```
T300 → T301 → T304 → T312 → T313 (bots talk with LLM) ← WEEK 2
T320 → T322 → T323 → T326 → T327 (bots report findings) ← WEEK 3
T340 → T341 → T344 (swarm orchestration) ← WEEK 4
```

### Quick Wins (ship in 1 day)
1. T300 + T301 + T305 + T306 = LLM talks (4 tasks, ~8h)
2. T310 + T311 + T313 = conversation engine wired up (3 tasks, ~5h)
3. T320 + T321 + T326 = findings visible via API (3 tasks, ~5h)
