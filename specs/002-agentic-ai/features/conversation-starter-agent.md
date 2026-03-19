# Conversation Starter Agent

**Agent**: 3 of 5
**Priority**: Premium Feature — Revenue Driver
**Wave**: 3
**Tasks**: T230–T236
**Estimated Effort**: 56h total

---

## Problem

**50%+ of matches never message.** The match sits there. Both people are interested, but:
- Neither knows what to say beyond "Hey"
- Fear of saying something awkward
- Decision paralysis — too many matches, can't personalize for all
- Conversation dies after 3 generic exchanges

This is the **biggest drop-off** in the dating funnel. Match → no message → dead match.

## Solution

An agent that reads both profiles and generates personalized conversation starters:
1. **Cross-analyzes profiles** — find real shared interests and conversation hooks
2. **Generates 3 unique openers** — not templates, actual questions only these two people would relate to
3. **Matches tone** — casual for casual profiles, deeper for thoughtful profiles
4. **Handles stalls** — suggests follow-ups when conversations lose momentum
5. **Learns from outcomes** — which opener styles get replies?

## Architecture

```
Match created → Conversation Agent triggered
  → Fetch Profile A + Profile B from UserService
  → LLM prompt:
    "These two people matched. Read both profiles.
     Generate 3 personalized conversation starters.
     Each should reference something specific from THEIR profiles.
     Match the tone to their vibe (casual/serious/funny).
     Make them questions that invite real conversation."
  → Store generated openers
  → Surface in Flutter chat UI as suggestion chips
  → User taps one → auto-fills message input (user can edit before sending)
```

## Key Design Decisions

### Why not templates?
- Templates feel fake: "What's your dream vacation?" — generic garbage
- Real openers reference *specific* profile details
- Users immediately know it's AI if the opener could apply to anyone
- Personalization is the entire value prop

### Where do openers appear?
- **Suggestion chips** above the keyboard in chat
- NOT auto-sent — user must tap to use
- User can edit before sending
- Option to regenerate ("Give me 3 more")
- Disappear after first message is sent

### Privacy: does the other person know?
- **No.** The opener is a suggestion, the user sends it as their own message
- Just like Google autocomplete — you chose to type it
- No "AI-assisted" badge on messages

## Tasks Breakdown

### T230: Profile Cross-Analysis (8h, P1)
- Fetch both profiles including bio, interests, prompts, photo metadata
- Extract shared interests, unique talking points, potential jokes
- Structure data for LLM prompt
- Handle edge cases: empty bios, minimal profiles

### T231: Opener Generation (8h, P1)
- LLM prompt engineering for 3 personalized openers
- Quality constraints: must reference specific profile details
- Tone matching: detect if profiles are casual/serious/funny
- Output format: 3 openers + reasoning (for debugging/learning)
- Fallback: if profiles are too sparse, use interest-based generic openers

### T232: Stale Conversation Nudger (8h, P2)
- Detect stalled conversations (>24h no messages after initial exchange)
- Analyze conversation so far
- Suggest follow-up or topic change
- Also suggest graceful exit: "It's okay if the vibe isn't there"
- Configurable: user can disable nudges

### T233: Tone Calibration (8h, P2)
- Detect profile tone signals: emoji use, bio style, prompt answers
- 3 modes: casual-fun, genuine-curious, witty-flirty
- User can set preference: "I prefer funny openers"
- Don't second-guess: if user picks "witty" but profile is serious → honor user preference

### T234: Flutter Conversation Coach UI (12h, P1)
- Suggestion chips in new match chat view
- Tap to fill → editable before sending
- "Refresh" button for 3 more suggestions
- Loading state while agent generates
- Empty state if agent couldn't generate (minimal profile)
- Settings: enable/disable, tone preference

### T235: Ghost Detection + Advice (4h, P2)
- Track message read status + time since last reply
- At 48h: "They might be busy. Want to try: [re-engagement message]?"
- At 72h: "You could move on, or try one more: [last-chance message]"
- Graceful: "No response? That's okay. New matches are waiting."
- Never pushy — normalize moving on

### T236: Effectiveness Tracking (8h, P3)
- Track: opener used → reply received? → conversation length
- A/B: AI openers vs organic openers → which get longer conversations?
- Per-style tracking: which tone gets most replies?
- Aggregate insight: "Casual questions about hobbies get 2x more replies than compliments"
- Feed winning patterns back into generation prompt

## Examples

### Profile A (Alice, 28):
> Bio: "Coffee snob. Weekend hiker. Currently reading too many books at once."
> Interests: Reading, Hiking, Coffee, Photography

### Profile B (Bob, 30):
> Bio: "Software dev who escapes to the mountains. Dog dad. Makes a mean pasta."
> Interests: Hiking, Cooking, Dogs, Tech

### Generated Openers:
1. 🥾 "Fellow mountain escaper! What's your favorite trail around here? I need new ones to add to the list."
2. 📚 "You're reading multiple books at once too? What's on the stack? I need recommendations."
3. ☕ "Coffee snob question: pour-over, espresso, or something fancier? I have opinions."

## Integration Points

- **UserService**: Profile data for both matched users
- **MatchmakingService**: Match events trigger agent
- **MessagingService**: Deliver openers as suggestions in chat context
- **Agent Gateway (T200)**: LLM routing, cost tracking
- **Flutter app**: Chat UI integration with suggestion chips

## Monetization Potential

- **Free tier**: 1 opener suggestion per match
- **Premium**: 3 openers, refresh, tone selection, stale conversation help
- **Super Premium**: Unlimited refreshes, ghost detection, effectiveness insights
