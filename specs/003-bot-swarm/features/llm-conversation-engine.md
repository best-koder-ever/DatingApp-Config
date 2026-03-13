# Feature: LLM Conversation Engine

**Phase**: 003-bot-swarm | **Waves**: 0 + 1
**Tasks**: T300-T318

## Problem
Current bots use 41 canned Swedish messages (`MessageContentProvider`). After 5-6 exchanges, all conversations feel identical. Users recognize the pattern and disengage. Bots can't adapt to what the user actually says.

## Solution
Replace canned messages with LLM-generated, persona-aware Swedish conversations. Each of the 12 personas gets a unique "voice" calibrated by their BotBehavior config (chattiness, formality, interests). Canned messages remain as fallback when LLM is unavailable or budget-exhausted.

## Architecture

```
BotPersona + ConversationHistory + Stage
        │
        ▼
┌──────────────────┐     ┌───────────────┐
│ PromptTemplates  │────▶│ LlmRouter     │
│ (system prompt   │     │ ┌─────────┐   │
│  + context)      │     │ │ Gemini  │←──primary (free)
└──────────────────┘     │ ├─────────┤   │
                         │ │ Groq    │←──fallback (free)
                         │ ├─────────┤   │
                         │ │ Ollama  │←──dev (local)
                         │ └─────────┘   │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │ Guardrails    │
                         │ • No English  │
                         │ • No URLs     │
                         │ • Max 280ch   │
                         │ • No bot leak │
                         └───────┬───────┘
                                 │
                         ┌───────▼───────┐
                         │ IConversation │
                         │    Engine     │
                         └───────────────┘
```

## LLM Provider Strategy

| Provider | Model | Cost | Speed | Swedish | Rate Limit |
|----------|-------|------|-------|---------|------------|
| **Gemini** | `gemini-2.5-flash-lite` | FREE | ~200 tok/s | ★★★★★ | 500 RPD |
| **Groq** | `llama-3.3-70b-versatile` | FREE tier | ~280 tok/s | ★★★☆☆ | 1000 RPD |
| **Ollama** | `qwen3:32b` / `gemma3:27b` | $0 (local) | ~30 tok/s | ★★★★☆ | unlimited |
| **Cerebras** | `llama-3.3-70b` | FREE tier | ~3000 tok/s | ★★★☆☆ | 1000 RPM |

**Daily budget**: 100 bots × 20 messages = 2000 LLM calls. Gemini free tier covers ~500 RPD → batch across hours. Groq fallback covers overflow.

## System Prompt Template (skeleton)

```
Du är {Name}, {Age} år, bor i {City}. Du jobbar som {Occupation}.
Dina intressen: {Interests}.
Du pratar på en dejtingapp med nĺgon du matchat med.

Personlighet: {ChattinessDescription} {FormalityDescription}
Samtalsstadium: {Stage}

Regler:
- Svara BARA pĺ svenska
- Max 2 meningar
- Var naturlig, inte robotaktig  
- Fräga nĺgot om personen ibland
- Om stadiet är "fika_invite": föreslĺ att träffas för fika

Konversationshistorik:
{LastNMessages}
```

## Conversation Stages

| Stage | Message Count | Bot Behavior |
|-------|---------------|-------------|
| `intro` | 0-2 | Opener, basic greeting, first impression |
| `getting_to_know` | 3-8 | Exchange interests, ask about work/hobbies |
| `deep_talk` | 9-15 | Deeper topics, humor, personal stories |
| `suggest_fika` | 16+ | Naturally suggest meeting for fika/coffee |
| `post_fika` | After suggestion | Wind down, express excitement about meeting |

## Guardrail Rules

1. **Language**: Reject if >20% English words (tokenize + dictionary check)
2. **Safety**: Reject if contains phone numbers (`\d{3,}-?\d{3,}`), URLs (`http|www|\.com`), or bot-awareness ("jag är en AI", "jag är en bot", "jag är ett program")
3. **Length**: Max 280 characters (dating app message style)
4. **Tone**: Reject overtly sexual content (keyword list)
5. **Fallback**: Any rejection → return canned message from `MessageContentProvider`

## Success Criteria

- [ ] Gemini generates Swedish response in <2s for 95% of calls
- [ ] All 12 personas produce distinguishable conversation styles
- [ ] Guardrails catch 100% of English-only responses
- [ ] Fallback to canned works seamlessly when LLM budget exhausted
- [ ] Swedish naturalness score >3.5/5.0 via LLM-judge evaluation (T366)
