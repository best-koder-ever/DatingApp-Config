# Clarifications: DatingApp MVP Foundation

_Last updated: 2025-10-20_

## Resolved Items
| Ref | Question | Resolution | Notes |
|-----|----------|------------|-------|
| FR-011 | What is the retention policy for chat transcripts? | Retain 90 days in production. For MVP demo, keep full history until purge script introduced. | Align with compliance review before GA. |
| FR-012 | How are mobile push notifications handled? | MVP omits push; rely on in-app messaging cues. Reserve Firebase/APNS wiring for post-MVP. | Ensure client surfaces reminders when app resumes. |
| Verification Flow | Do we require SMS verification at MVP launch? | No. MVP uses Keycloak email verification; design flow to accept additional factors later. | Track an enhancement task for SMS rollout. |
| Onboarding Scope | Which steps are mandatory vs optional? | Mandatory: basic profile (name, age, gender, location consent), interest tags, min 1 photo. Optional modules (profession, voice prompt) deferred. | Wizard must save partial progress. |
| Safety Education | How prominent should safety messaging be? | Ship lightweight dismissible card post-onboarding. Expand with richer modules after messaging stability. | Provide analytics hook for engagement. |

## Outstanding Questions
| Topic | Question | Owner | Due |
|-------|----------|-------|-----|
| Moderation SLA | What turnaround do we promise for flagged content during MVP? | Safety Lead | 2025-10-27 |
| Demo Data | Do we need region-specific cohorts for demo scripts? | Product | 2025-10-22 |

## Actions
- Add SMS verification enhancement to post-MVP backlog once plan finalized.
- Capture safety education metrics in analytics design (Phase 7 task follow-up).
