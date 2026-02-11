# Research Log: DatingApp MVP Foundation

## Objectives
- Validate matchmaking scoring tuning for small cohorts (≤5k users) and ensure fairness rules for daily queues.
- Confirm ML.NET moderation thresholds for photo privacy fit MVP safety requirements without excessive false positives.
- Determine best offline caching strategy in Flutter for swipe queues and pending messages.
- Assess infrastructure capacity for combined Auth/Matchmaking/Messaging when all run on single developer machine.

## Key Findings (Initial)
- Existing PostgreSQL schema supports necessary joins; need query plan review under realistic sample data.
- ImageSharp + OpenCvSharp pipeline can reuse current blur profiles; add automated regression images for acceptance.
- SignalR scale at MVP load should remain within current docker resources; keep keep-alive tuning at 15s.
- Demo scripts already provision test accounts; extend to cover cross-service token refresh scenarios.

### Competitive Onboarding Patterns
- **Tinder** (as documented in onboarding UI/UX teardowns such as Appcues 2024): email/phone verification → selfie/photo picker → interest tags → location permissions. Emphasizes quick swiping readiness with optional later refinements.
- **Bumble**: similar step count but inserts safety messaging and profile prompts (work/education) before the discovery feed; supports deferred completion through reminders.
- **Hinge**: longer questionnaire (prompts, voice notes) yet still launches user into discovery once the minimum card is complete; remaining prompts treated as progressive enhancement.
- Common thread: minimum viable profile is achieved within 4–6 screens; advanced personalization is additive. All flows treat photo upload + basic bio as table stakes, while more nuanced questions can be postponed.

## Open Questions
- What heuristics trigger fallback cohort expansion when match pool is exhausted? (Product alignment required.)
- Which push notification provider will back mobile notifications at launch? (Impacts Flutter plugin choices.)
- Do we require automated abuse detection beyond manual reporting for MVP? (Security review pending.)

## Next Steps
- Run load test harness against matchmaking endpoints once infrastructure/start.sh boots containers.
- Pair with product to lock scoring weights and privacy defaults; document in contracts/ directory.
- Prototype Flutter offline cache using Hive vs. shared_preferences, record trade-offs.
- Schedule threat modeling session focused on reporting workflow before implementation sprint.
- Translate competitive onboarding observations into concrete acceptance criteria (see spec update) and outline optional modules for post-MVP roadmap.
