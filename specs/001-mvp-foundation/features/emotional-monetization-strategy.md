# Emotional Monetization Strategy
**The Philosophy: Emotion > Features**

**Status**: � BRAINSTORMING PHASE - Reference material for niche selection  
**Priority**: P1 (Strategic Planning - Informs Phase 12)  
**Last Updated**: 2026-01-28  
**Purpose**: This document provides niche options and emotional paywall strategies for consideration. **Backend will be built niche-agnostic** to support any/all of these approaches via Flutter app flavors.

---

## 🧠 Core Principle

> **People don't pay for features. They pay to avoid pain and chase hope.**

**Payment = Hope × Urgency × Friction**

- **Hope**: "This might actually work"
- **Urgency**: "I need to act NOW"  
- **Friction**: "I can't get this any other way"

---

## 🎯 The Niche Decision (Choose ONE)

**Current Problem**: We're targeting "people who date" = everyone = no one.

**Proposed Niche Options** (ranked by pain intensity):

### Option 1: 🔥 **Nyinflyttade i stad (25-35)** — NEW TO CITY
**Pain**: Loneliness in new place, no social network, urgency to connect before settling into isolation  
**Hook**: "Meet people who moved to [city] in the last 6 months"  
**Paywall Moment**: "3 people who just moved to your neighborhood want to meet — see who this weekend"  
**Why it works**: Geographic + temporal specificity = high urgency

### Option 2: 🔥 **Föräldrar varannan vecka (30-45)** — SHARED CUSTODY PARENTS  
**Pain**: Lonely every other week when kids are gone, limited time windows, need someone who understands  
**Hook**: "Date other single parents — we only show you matches when you're both kid-free"  
**Paywall Moment**: "You're kid-free this weekend. 5 matches are also free — unlock now"  
**Why it works**: Time-based FOMO + identity ("they get it")

### Option 3: 🔥 **Akademiker i småstäder** — EDUCATED IN SMALL TOWNS  
**Pain**: Limited dating pool, most people left for cities, fear of settling  
**Hook**: "Connect with university-educated people in [small town]"  
**Paywall Moment**: "Only 12 active users in Västerås this month — see all before they match"  
**Why it works**: Scarcity + fear of missing limited pool

### Option 4: **Nyskilda (35-50)** — NEWLY DIVORCED  
**Pain**: Haven't dated in 10+ years, fear of rejection, rusty social skills  
**Hook**: "Practice dating in a judgment-free space for newly single people"  
**Paywall Moment**: "Someone who got divorced 2 months ago (like you) wants to chat"  
**Why it works**: Empathy + similar life stage reduces fear

---

## 💰 Emotional Paywall Design

### ❌ **WRONG: Feature-Based Paywall (Current Design)**

```
FREE:
- 100 swipes/day
- See blurred likes

PREMIUM ($19.99/mo):
- Unlimited swipes
- See who liked you
- Advanced filters
```

**Why this fails:**  
- Rational decision ("Do I need unlimited swipes?")
- No emotion, no urgency
- Competes with Tinder on features = you lose

---

### ✅ **RIGHT: Emotion-Based Paywall**

**For Niche: "New to City" (25-35)**

#### **Free Experience Flow:**

1. **Onboarding Creates Hope**  
   - "23 people new to Stockholm this month"  
   - See 3 profiles (high-quality matches you'd actually like)  
   - Swipe right, get instant match notification  

2. **Lock at Peak Emotion**  
   - 🔒 **"[Name] wants to meet up this weekend"**  
   - Message preview: "Hey! I just moved here too, want to grab fika and..."  
   - **Can see they matched, can't read full message or reply**  

3. **Urgency + Friction**  
   - ⏰ "This message expires in 48 hours"  
   - 💬 "Unlock with 1 Spark ($1.99) or upgrade to Premium to chat unlimited"  

#### **Paywall Moment Psychology:**

```
HOPE:     "Someone like me wants to meet!"  
PAIN:     "They'll think I'm ghosting if I don't respond"  
URGENCY:  "48 hours before message expires"  
FRICTION: "Can't respond without paying"  
```

**This is 10x more powerful than "see who liked you"** because:
- **Specific person** (not anonymous likes)  
- **Time pressure** (48h expiry)  
- **Social cost** (they'll think you ignored them)  

---

## 🕐 Urgency Mechanics

### **Time-Based Triggers** (For "Shared Custody Parents" Niche)

**Backend Logic:**
```csharp
// Show matches who are ALSO kid-free RIGHT NOW
var userSchedule = await GetCustodySchedule(userId); // e.g., "kid-free every other weekend"
var currentWeekend = IsUserKidFree(userSchedule, DateTime.UtcNow);

if (currentWeekend)
{
    var matches = await GetMatchesWhoAreAlsoKidFreeNow();
    SendNotification($"{matches.Count} matches are free THIS WEEKEND — see who");
}
```

**Paywall:**
- Free: See 2 matches  
- Premium: See all matches + chat  

**Why it works:**  
- **Can't wait** (weekend ends Sunday night)  
- **Specific situation** (both kid-free = can actually meet)  
- **No generic "unlimited swipes" pitch**

---

### **Scarcity Triggers** (For "Small Town" Niche)

**Backend Logic:**
```csharp
var activeUsersInTown = await GetActiveUsers(userCity, lastActiveDays: 30);

if (activeUsersInTown.Count < 50)
{
    SendNotification($"Only {activeUsersInTown.Count} active users in {userCity} — see all");
}
```

**Paywall:**
- Free: See 5 profiles/day  
- Premium: See entire pool (17 people) + priority visibility  

**Psychology:**
- **Scarcity** (only 17 people in Västerås)  
- **FOMO** (someone else will match them first)  
- **Urgency** (few new users join small towns)

---

## 🔥 The "Ping" Feature (Feeld Model)

**Current Design**: 1 Spark = Send direct message before matching  
**Problem**: No emotion, just "another feature"

**Emotional Redesign:**

### **Scenario 1: Profile Standout**  
User sees someone perfect, already swiped left on them (didn't see user yet).

**Paywall Moment:**
```
"[Name] hasn't seen your profile yet.  
Send a Ping to appear at the top of their queue."

[Send Ping - 1 Spark] [Skip]
```

**Psychology:**
- **Fear**: They'll swipe left if they see me in normal queue  
- **Hope**: Ping = I stand out, better chance  
- **Impulse**: Saw cute profile, emotional purchase

---

### **Scenario 2: Expiring Match**  
User matched 3 days ago, other person hasn't replied.

**Paywall Moment:**
```
"[Name] matched with you but hasn't checked messages.  
Ping them to send a notification: 'Someone's waiting to chat!'"

[Send Ping - 1 Spark] [Give Up]
```

**Psychology:**
- **Sunk cost**: Already matched, feels wasteful to lose it  
- **Hope**: Maybe they just forgot to check app  
- **Avoidance**: Don't want to feel rejected (Ping = one more try)

---

## 📊 Monetization Model (Hybrid)

### **Subscription: "All Access Pass"**

**Positioning**: NOT "unlimited swipes"  
**Positioning**: ✅ **"Never miss a connection"**

**What you get:**
- See all matches when they happen (no delayed notifications)  
- Chat unlimited (no Spark costs for Pings)  
- Priority visibility (show up first in queues)  
- See when people are active NOW (green dot)

**Pricing:**
- Weekly: $9.99 (targets "trying it out for this weekend")  
- Monthly: $24.99  
- 3-Month: $49.99 (40% off)

**Why weekly matters for niche:**  
"Shared custody parents" → Kid-free every other weekend → Buy weekly pass for those weekends only

---

### **Sparks: Impulse Purchases**

**NOT**: "Buy Boosts and Super Likes"  
**YES**: **Emotional moments** 

| Action | Cost | Emotional Trigger |
|--------|------|-------------------|
| **Ping Person** | 1 Spark | Saw perfect match, don't want them to miss me |
| **Read Message** | 1 Spark | Got match notification, dying to see what they said |
| **See Who Viewed** | 2 Sparks | "8 people checked your profile — see who" (FOMO) |
| **Weekend Boost** | 3 Sparks | Friday 5pm: "23 new people joined this week — boost to meet them" |

**Spark Packages:**
- 1 Spark: $1.99 (impulse, instant)
- 5 Sparks: $7.99  
- 15 Sparks: $19.99

---

## 🧪 Implementation Checklist

### **Phase 1: Define Your Niche (CHOOSE NOW)**

- [ ] **Pick ONE niche from above** (or define custom painful niche)
- [ ] Write 3 specific user pain points for that niche
- [ ] Design onboarding flow that validates niche (e.g., "When did you move to [city]?" for new-to-city)
- [ ] Set match algorithm filters (e.g., only show people who moved <6 months ago)

### **Phase 2: Redesign Paywall Moments**

- [ ] Map user journey from signup → first paywall  
- [ ] Identify 3 **emotional peak moments** to lock (not features)  
- [ ] Write exact notification copy with urgency ("48h expiry", "only 12 users")  
- [ ] Design paywall UI (show person's face, message preview, countdown timer)

### **Phase 3: Update Technical Specs**

- [ ] Modify `monetization-architecture.md` → Remove "unlimited swipes", add "Ping for message", "See active now"  
- [ ] Update user stories → Rewrite from emotional perspective  
- [ ] Add time-based triggers to backend (e.g., custody schedule, weekend FOMO notifications)  
- [ ] Design Spark purchase flow for **impulse moments** (1-click buy, in-context)

### **Phase 4: A/B Test Copy**

Test these notification variants for "New to City" niche:

**Variant A (Feature):** "Upgrade to Premium to see who liked you"  
**Variant B (Emotion):** "[Name] just moved to your neighborhood and wants to meet"  
**Variant C (Urgency):** "You have 3 matches this weekend — they expire Monday"  

**Hypothesis**: Variant B/C will convert 3-5x better than A.

---

## 🎯 Solo Dev Strategy (Minimum Viable Emotion)

**Week 1: Niche Definition**
- Pick niche (recommend: "New to City 25-35" = largest addressable market)
- Add onboarding question: "When did you move to [city]?" (dropdown: <1mo, 1-3mo, 3-6mo, 6-12mo, 1yr+)
- Filter matches: Only show people who answered <6 months

**Week 2: First Emotional Paywall**  
- Build: User gets match → sees notification → can't read message  
- Add: "Unlock with 1 Spark" button  
- Implement: 1 Spark purchase flow (via `in_app_purchase` plugin)  

**Week 3: Urgency Mechanic**  
- Add: Message expiry (48h countdown)  
- Backend: Auto-revoke access to conversation after 48h if not unlocked  
- Notification: "12 hours left to reply to [Name]"  

**Week 4: Subscription Alternative**  
- Add: "Or upgrade to Premium to chat unlimited"  
- Show: "This week only: $9.99 for 7 days (meet people before weekend)"  

**Test:** Launch to 50 users, measure:
- Free → Spark buyer conversion (target: 20-30%)
- Spark buyer → Subscriber conversion (target: 10-15%)
- Compare to industry: Generic dating apps = 2-5% free→paid

---

## 💡 Key Insight: Niche = Urgency = Money

**Generic App:**
- "100 million singles"  
- No urgency (always more people tomorrow)  
- Low willingness to pay  

**Niche App:**
- "Only 23 people in Västerås"  
- High urgency (limited pool, someone will match them first)  
- High willingness to pay  

**Example:**
- Tinder: 2-5% conversion, $20/mo = $0.40-$1.00 per user  
- JSwipe (Jewish dating): 12-15% conversion, $30/mo = $3.60-$4.50 per user  

**Niche = 4x revenue per user.**

---

## 🚨 What NOT to Do

❌ **Don't** add "unlimited swipes" → Nobody cares, Tinder already has it  
❌ **Don't** use rational value propositions → "Advanced filters" is boring  
❌ **Don't** hide person behind blur → Show face, lock interaction  
❌ **Don't** make free tier unlimited → Must create scarcity to drive urgency  
❌ **Don't** target "everyone" → Pick painful niche or die competing with Tinder  

✅ **Do** lock emotional moments (got match, can't reply)  
✅ **Do** use time pressure (48h expiry, weekend-only matches)  
✅ **Do** show specific person (name, face, message preview)  
✅ **Do** create scarcity (only X people in your city)  
✅ **Do** pick ONE niche and dominate it  

---

## 📋 Next Steps

1. **DECIDE YOUR NICHE** (30 minutes)  
   - Read options above  
   - Pick ONE based on: market size, pain intensity, your ability to reach them  
   - Write in `NICHE_DECISION.md`  

2. **REWRITE USER STORIES** (2 hours)  
   - Open `monetization-architecture.md`  
   - Replace generic stories with emotional paywall moments  
   - Add urgency triggers (time-based, scarcity-based)  

3. **UPDATE ONBOARDING** (4 hours)  
   - Add niche validation question (e.g., "When did you move here?")  
   - Filter match algorithm (only show niche users)  
   - Test with 10 fake users  

4. **BUILD FIRST PAYWALL** (8 hours)  
   - Implement: Match notification → Can't read message → "Unlock with 1 Spark"  
   - Add Spark purchase (Google Play / App Store IAP)  
   - Test end-to-end flow  

**After this, you have a REAL dating app, not a Tinder clone.**

---

## 📖 Referenced Philosophy

> "Folk betalar inte för UI, animationer, kodkvalitet.  
> De betalar för: 'Tänk om detta funkar', 'Jag vill inte vara ensam', 'Jag vill inte missa den här matchen'  
> Dating = emotionell arbitrage"  

**Translation:** People don't pay for features. They pay for hope, fear of loneliness, and fear of missing out.

**This document operationalizes that philosophy.**
