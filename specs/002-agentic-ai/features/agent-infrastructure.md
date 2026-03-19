# Agent Infrastructure (Shared)

**Priority**: P0 — Build First
**Wave**: 1 — Foundation
**Tasks**: T200–T205
**Estimated Effort**: 48h total

---

## Overview

All 5 agents share a common infrastructure layer. Build this once, every agent plugs in.

```
┌─────────────────────────────────────────────┐
│              Agent Gateway Service           │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐ │
│  │ Router  │  │ Tool     │  │ Cost       │ │
│  │ (which  │  │ Registry │  │ Controller │ │
│  │  agent) │  │ (APIs)   │  │ (budgets)  │ │
│  └─────────┘  └──────────┘  └────────────┘ │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐ │
│  │ LLM     │  │ Memory   │  │ Observa-   │ │
│  │ Abstrac-│  │ Store    │  │ bility     │ │
│  │ tion    │  │          │  │            │ │
│  └─────────┘  └──────────┘  └────────────┘ │
└─────────────────────────────────────────────┘
         ↕              ↕            ↕
    LLM APIs     Service APIs    PostgreSQL
 (Claude, GPT)  (User, Match,    (state,
                 Photo, Msg)      memory)
```

## Technology Choices

| Component | Technology | Why |
|-----------|-----------|-----|
| Gateway Service | .NET 8 (ASP.NET Core) | Consistent with other services |
| LLM Client | Semantic Kernel or raw HTTP | MS ecosystem, good .NET support |
| Memory Store | PostgreSQL + pgvector | Already in stack, vector search for embeddings |
| Tool Registry | Custom DI-based | Simple, testable, no framework overhead |
| Observability | OpenTelemetry + existing logging | Already set up in other services |
| Cost tracking | Custom middleware | Simple counter + circuit breaker |

## Tasks Breakdown

### T200: Agent Gateway Service (16h, P0)
New .NET 8 service: `agent-service/`
- Agent orchestration loop: receive request → select agent → call LLM → execute tools → return result
- Tool registry: typed tool interfaces that agents can call (IUserService, IPhotoService, etc.)
- Request/response contracts for each agent type
- Health check, dependency injection, standard middleware
- Docker + docker-compose integration

### T201: LLM Abstraction Layer (8h, P0)
- `ILlmClient` interface with implementations:
  - `ClaudeClient` — Anthropic API (Claude Haiku for classification, Sonnet for reasoning)
  - `OpenAiClient` — GPT-4o-mini for fallback
  - `MockLlmClient` — for testing (deterministic responses)
- Structured output parsing (JSON mode)
- Retry logic with exponential backoff
- Cost tracking per call (input tokens, output tokens, model, cost)
- Model selection by agent type and task complexity

### T202: Agent Memory/Context Store (8h, P0)
- Per-user agent context (what has the agent told this user before?)
- Conversation history for multi-turn agent interactions
- PostgreSQL tables:
  - `agent_contexts` — user_id, agent_type, context_json, updated_at
  - `agent_interactions` — user_id, agent_type, input, output, cost, latency, created_at
- TTL-based cleanup (delete contexts older than 30 days)
- Context window management (don't exceed LLM token limits)

### T203: Cost Control Middleware (4h, P0)
- Per-user daily LLM budget (configurable, default $0.50/user/day)
- Per-agent cost caps (safety has higher budget than photo coach)
- Circuit breaker: if total spend exceeds $X/hour → pause non-critical agents
- Real-time cost dashboard (admin endpoint)
- Alert on cost anomalies (sudden 10x spike)

### T204: Agent Observability (4h, P1)
- Structured logging for every LLM call:
  - Agent type, user_id, model, input_tokens, output_tokens, cost, latency_ms
  - Tool calls made, success/failure
- Metrics: requests/sec, latency p50/p95/p99, cost/hour, error rate
- Trace correlation: link agent calls to originating user action
- Dashboard: Grafana or simple admin page

### T205: Agent A/B Testing Framework (8h, P2)
- Feature flags: per-agent enable/disable
- User segmentation: % of users get agent-powered features
- Variant tracking: which users are in which experiment
- Outcome measurement: compare agent vs non-agent user metrics
- Automatic promotion: if variant wins by statistical significance → promote

## Service Configuration

```json
{
  "AgentService": {
    "DefaultModel": "claude-haiku",
    "FallbackModel": "gpt-4o-mini",
    "CostLimits": {
      "PerUserDailyBudget": 0.50,
      "PerHourGlobalBudget": 100.00,
      "CircuitBreakerThreshold": 500.00
    },
    "Agents": {
      "Safety": { "Enabled": true, "Model": "claude-haiku", "MaxLatencyMs": 500 },
      "PhotoCoach": { "Enabled": false, "Model": "claude-sonnet", "MaxLatencyMs": 5000 },
      "ConversationStarter": { "Enabled": false, "Model": "claude-haiku", "MaxLatencyMs": 2000 },
      "SmartMatch": { "Enabled": false, "Model": "claude-haiku", "MaxLatencyMs": 3000 },
      "DatePlanner": { "Enabled": false, "Model": "claude-haiku", "MaxLatencyMs": 3000 }
    }
  }
}
```

## API Contracts

```
POST /api/agent/invoke
{
  "agentType": "safety" | "photo-coach" | "conversation" | "smart-match" | "date-planner",
  "userId": "uuid",
  "payload": { ... agent-specific data ... }
}

Response:
{
  "agentType": "safety",
  "result": { ... agent-specific response ... },
  "metadata": {
    "model": "claude-haiku",
    "inputTokens": 150,
    "outputTokens": 30,
    "costUsd": 0.0001,
    "latencyMs": 120,
    "toolsCalled": ["classify_message"]
  }
}
```

## Testing Strategy

- Unit tests: each agent with MockLlmClient (deterministic)
- Integration tests: agent + real services + mock LLM
- Cost tests: verify budget limits work (mock expensive calls)
- Latency tests: verify timeout/circuit breaker behavior
- A/B test: verify user segmentation and outcome tracking
