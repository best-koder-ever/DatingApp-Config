# Date Planner Agent

**Agent**: 5 of 5
**Priority**: Future — Ship Last
**Wave**: 5
**Tasks**: T250–T254
**Estimated Effort**: 44h total

---

## Problem

The dating funnel has one final massive drop-off:

```
Swipe → Match → Message → Conversation → ... → Actually meet IRL
                                                   ↑ HERE. Most fail.
```

Users who are chatting well still don't meet because:
- Nobody wants to be the one to suggest it
- Logistics are hard (where? when? what if they say no?)
- Fear of rejection even *within* a match
- Conversations drift into pen-pal territory

**No dating app helps users cross the finish line.**

## Solution

An agent that gently facilitates the transition from chat to date:
1. **Detects date-readiness** — conversation is going well, time to meet?
2. **Suggests venues** — based on shared interests and location
3. **Handles logistics** — proposes time/place, both confirm in-app
4. **Safety features** — check-in during dates, share location with trusted contacts
5. **Post-date feedback** — "How did it go?" feeds back into matching

## Architecture

```
Conversation hits N messages or M days → Date Planner Agent evaluates
  → Analyze conversation sentiment and topic progression
  → If date-ready signal high:
    → Suggest to User A: "Things seem to be going great! Would you like to suggest meeting up?"
    → If User A agrees:
      → Generate venue suggestions based on:
        - Both users' interests (coffee lover? → café. Active? → park walk)
        - Mutual location (meeting point between two locations)
        - Time of day (coffee date vs dinner vs activity)
      → Present as suggestion card: "How about Café X on Saturday afternoon?"
    → If User B agrees → create date event in both calendars
    → Day of: optional safety check-in
    → After: "How did it go?" feedback
```

## Why Ship Last?

- Needs all other agents working first (safety, conversation, matching data)
- Requires the most trust from users (suggesting IRL meetups is sensitive)
- External API dependencies (location, venue data, possibly calendar)
- Liability concerns with facilitating IRL meetings
- Date planner without good matches = useless

## Tasks Breakdown

### T250: Mutual Availability Finder (12h, P3)
- In-app availability calendar (optional, privacy-first)
- "I'm usually free on weekends" — fuzzy availability
- Find overlap between two users
- Don't require exact calendar sync — suggest windows, not slots

### T251: Venue Suggestion (12h, P3)
- Integration with Google Places or similar API
- Filter by: distance, vibe (casual/active/romantic), type (café/park/bar)
- Match venue to shared interests from profiles
- Show venue card with photo, rating, distance
- Never suggest a private location — always public places

### T252: Logistics Handler (8h, P3)
- Propose: "How about [venue] on [day] at [time]?"
- Both users confirm/counter-propose/decline
- Reminders: "Your date with [name] is tomorrow at 3pm"
- Easy reschedule flow
- Graceful decline: "No worries! You can suggest a time that works better."

### T253: Safety Check-in (8h, P3)
- Optional "I arrived safely" button
- "Date started" → timer → "Check in: Are you okay?" after 1 hour
- Share live location with trusted contact (opt-in)
- Emergency button: call/text emergency contact
- Post-date: "I got home safely" ping

### T254: Post-Date Feedback (4h, P3)
- "How did it go?" — great / good / okay / not great
- Optional: "Would you like to see them again?"
- Feed into matching model: dates that went well → what did the match algorithm get right?
- Aggregate: "Users who follow our venue suggestions rate dates 20% higher"
- Never share feedback with the other person

## Integration Points

- **MessagingService**: Conversation analysis, date suggestions in chat
- **UserService**: Location data, availability preferences
- **MatchmakingService**: Date outcome feeds back into matching quality
- **Agent Gateway (T200)**: LLM for conversation analysis and venue matching
- **External APIs**: Google Places, calendar integration
- **Flutter app**: Date card UI, safety check-in screens, calendar view

## Privacy & Safety Considerations

- **No exact location sharing** between users — only mutual midpoint area
- **Public venues only** — agent never suggests private locations
- **Safety check-in is optional** — never mandatory, never judgmental
- **Emergency features** are always accessible, even without premium
- **Post-date feedback** is never shared with the other person
- **All data encrypted** — date history is highly sensitive

## Future Possibilities

- Integration with restaurant reservation APIs
- Activity booking (concerts, cooking classes, escape rooms)
- Weather-aware suggestions ("It's going to rain Saturday — indoor venue?")
- Group date coordination (double dates)
- Date idea generator based on both profiles ("You both like art → gallery opening this weekend")
