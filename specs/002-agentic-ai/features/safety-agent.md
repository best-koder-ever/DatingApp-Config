# Safety Agent

**Agent**: 1 of 5
**Priority**: Ship First
**Wave**: 1 — Foundation + Safety
**Tasks**: T210–T216
**Estimated Effort**: 60h total

---

## Problem

Current dating app safety relies on:
- Static word filters (easily bypassed: "you're h0t" vs "you're hot")
- User-initiated reporting (reactive, not proactive)
- Manual moderation (doesn't scale)

Users — especially women — leave apps because they don't feel safe.
Losing users to safety issues is the #1 preventable churn cause.

## Solution

An agentic safety system that:
1. **Intercepts every message** through an LLM classifier (safe/warning/block)
2. **Tracks patterns over time** — not just single messages
3. **Builds risk profiles** — users who trigger warnings accumulate a trust score
4. **Feeds back into matching** — high-risk users get deprioritized silently

## Architecture

```
MessagingService.SendMessage()
  → Safety Agent Pipeline (async, non-blocking for "safe")
    → LLM Classification (Claude Haiku — fast, cheap)
      → Category: SAFE | WARNING | BLOCK
      → Confidence: 0.0-1.0
    → If WARNING:
      → Deliver message normally
      → Log to safety_events table
      → Increment sender risk_score
      → If risk_score > threshold → auto-review queue
    → If BLOCK:
      → Reject message (don't deliver)
      → Notify sender: "This message couldn't be sent"
      → Add to moderation queue
      → Alert receiver: "A message was blocked for your safety"
```

## Key Design Decisions

### Why LLM over ML classifier?
- ML classifiers need labeled training data (we have none yet)
- LLMs understand context: "I'll kill you" (threat) vs "you're killing it!" (compliment)
- Can be fine-tuned later with our own labeled data
- Claude Haiku: ~$0.0001 per classification = $0.10 per 1,000 messages

### Why async non-blocking?
- Safe messages (99%+) should have zero added latency
- Only warnings and blocks add processing time
- Classify in background, deliver immediately, flag retroactively if needed

### Why not just auto-block everything?
- False positives destroy trust faster than false negatives
- Better to flag for review than wrongly block legitimate messages
- Users who get wrongly blocked will leave the app immediately

## Tasks Breakdown

### T210: Safety Agent Core (12h, P1)
- Message interception pipeline in MessagingService
- LLM prompt engineering for classification
- Safe/warning/block routing logic
- safety_events database table
- Integration tests with mock LLM

### T211: Harassment Escalation Detection (8h, P1)
- Track message history per sender-receiver pair
- Detect escalation patterns: friendly → pushy → aggressive
- Window-based scoring (last 10 messages, last 24 hours)
- Threshold-based automatic escalation to block

### T212: Catfish Signal Detection (12h, P2)
- Profile photo reverse image search (Google/TinEye API)
- Profile inconsistency scoring (claimed age vs photo age estimation)
- Bio analysis: copied from generic templates?
- Cross-reference: same photos on multiple accounts?

### T213: Spam/Copypasta Detector (4h, P1)
- Hash-based message deduplication per sender
- Flag users sending same message to 10+ different matches
- "Hey beautiful" / "Hey handsome" copypasta detection
- Low-effort opener scoring

### T214: User Risk Scoring (8h, P2)
- Aggregate safety signals into per-user score (0-100)
- Signals: blocked messages, reported, copypasta, escalation patterns
- Feed score into MatchmakingService as negative weight
- Decay function: old signals reduce over time

### T215: Moderation Dashboard (12h, P2)
- Web UI for reviewing flagged content
- Override agent decisions (approve blocked, block approved)
- Feedback loop: human decisions improve future classification
- Aggregate stats: blocked/day, false positive rate, top offenders

### T216: Safety Transparency Report (4h, P3)
- Weekly email/in-app notification: "We kept you safe this week"
- Show aggregate stats (never individual messages)
- Trust signal: users know we're actively protecting them
- Marketing asset: "Our AI blocked X% of harassment"

## Integration Points

- **MessagingService**: Primary integration — intercept pipeline
- **UserService**: Risk score storage, user flags
- **MatchmakingService**: Risk score as negative matching weight
- **PhotoService**: Catfish detection uses photo analysis
- **Flutter app**: Safety transparency UI, blocked message notifications

## Open Questions

- Silent filtering vs explaining why a message was blocked?
- Should the receiver know a message was blocked, or just never see it?
- Appeal process for false positives?
- GDPR implications of LLM processing message content?
- Can we process messages on-device (local model) for privacy?
