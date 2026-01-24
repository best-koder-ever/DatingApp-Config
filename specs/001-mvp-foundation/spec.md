# Feature Specification: DatingApp MVP Foundation

**Feature Branch**: `001-mvp-foundation`  
**Created**: 2025-10-20  
**Status**: Draft  
**Input**: User description: "DatingApp MVP foundation spec"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - First-Time Profile Creation (Priority: P1)

As a new visitor I can register, verify my email, complete a guided profile, and upload up to 6 photos so the system can surface me to compatible matches immediately.

**Why this priority**: Without complete and safe profiles the rest of the experience fails; this is the single most critical activation moment for both sides of the marketplace.

**Independent Test**: Launch the demo environment, create a new account, walk through the full profile wizard (bio, interests, preferences) and confirm photos are processed, privacy settings applied, and the user appears in matchmaking search results.

**Acceptance Scenarios**:

1. **Given** a visitor with valid credentials, **When** they register and confirm via email or SMS (mirroring Tinder/Bumble verification), **Then** the account activates and Keycloak issues a JWT that grants access to onboarding.
2. **Given** a newly authenticated user, **When** they progress through the wizard’s minimum steps (display name, age, gender, location consent, interest tags), **Then** each step saves independently so they can resume later, and a visual progress indicator reflects completion.
3. **Given** a user on the photo step, **When** they upload 1–6 photos within size limits, **Then** moderation/blur processing runs, privacy badges display, and at least one approved photo is required before continuing.
4. **Given** a completed minimum profile, **When** the user enters the final review screen, **Then** optional modules (e.g., extended prompts, profession) are surfaced as “add later” cards so future enhancements slot in without blocking MVP.
5. **Given** a completed profile, **When** the matchmaking service refreshes the candidate pool, **Then** the new user is eligible for discovery within 5 minutes without manual intervention.

---

### User Story 2 - Daily Match Discovery (Priority: P1)

As a logged-in member I can browse daily match suggestions, express interest via swipe actions, and get notified when a mutual interest occurs so I feel progress even with a small user base.

**Why this priority**: Ongoing engagement hinges on how quickly users see potential matches; without responsive discovery the MVP fails retention.

**Independent Test**: Seed demo data, perform swipe flows across devices, verify match scoring, and confirm API + UI show updated states without needing messaging to be available.

**Acceptance Scenarios**:

1. **Given** a verified member, **When** they open the Discover view, **Then** they see a prioritized queue with distance, shared interests, and photo blur rules applied correctly (aligns with Tinder-style card stack UX).
2. **Given** a member returning after partial onboarding, **When** they still have optional profile modules outstanding, **Then** the Discover view surfaces gentle prompts (e.g., “Add more interests”) similar to Hinge’s progressive enhancement pattern.
3. **Given** two members who both swipe right, **When** the second swipe is recorded, **Then** a match record persists, both users receive a push-style in-app notification, and the candidate is removed from the queue.
4. **Given** a user who exhausts daily suggestions, **When** no more candidates exist, **Then** the UI shows a wait state and the backend schedules a refresh event while offering optional “broaden preferences” suggestions.

---

### User Story 3 - Secure Match Messaging (Priority: P2)

As a matched duo we can exchange near-real-time messages across devices with read receipts and system-enforced privacy rules so conversations feel responsive and safe.

**Why this priority**: Messaging is the conversion moment from match to meetup; it is the key differentiator after acquisition but can ship just after first match loop proves viable.

**Independent Test**: Use demo accounts to create a match, open the chat view on two sessions, exchange messages, confirm delivery guarantees, presence indicators, and history persistence without running other flows.

**Acceptance Scenarios**:

1. **Given** two matched users, **When** one sends a message while both are online, **Then** SignalR pushes the message to the peer within 1 second and logs delivery.
2. **Given** a user reconnecting after a disconnect, **When** they re-open the chat, **Then** full history and unread counts sync from persistence without duplicates.
3. **Given** a report of inappropriate content, **When** a user flags a message, **Then** the system marks it for moderation and hides it pending review.

---

### User Story 4 - Safety & Recovery Controls (Priority: P3)

As any participant I can control my visibility, report bad actors, and recover access if something goes wrong so I trust the platform enough to continue.

**Why this priority**: Trust signals unlock virality; while not required for the very first loop, the MVP must include minimum viable safety within launch window.

**Independent Test**: Walk through privacy settings, toggle photo visibility, submit a report, and confirm audit logs and admin notifications fire without touching matching or messaging flows.

**Acceptance Scenarios**:

1. **Given** a user editing privacy, **When** they switch a photo to MatchOnly, **Then** non-matches see a blurred placeholder instantly, consistent with Tinder’s blurred preview conventions.
2. **Given** a user feeling unsafe, **When** they hit block/report, **Then** communication stops, match is archived, and moderators receive context, and the UI confirms the action with language inspired by Bumble’s safety messaging (“You’re in control”).
3. **Given** a user who uninstalls, **When** they sign back in, **Then** their profile, matches, and preferences rehydrate in under 10 seconds.
4. **Given** a newly onboarded user, **When** they attempt to skip safety tips, **Then** the system shows a concise reminder card (optional) that can be expanded later for richer education modules.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

- What happens when photo uploads exceed quota or fail moderation? → Reject with actionable error, preserve partially completed profile state.
- How does system handle intermittent connectivity on swipe/messaging actions? → Retry idempotent operations with exponential backoff and surface cached UI state until confirmation.
- What happens when Keycloak token expires mid-session? → Force silent refresh; if refresh fails, log the user out gracefully and preserve unsent actions locally.
- How does system behave when matchmaking returns zero candidates for >24h? → Trigger fallback cohort expansion rules and send proactive notifications about broadened discovery.
- What happens if SignalR hub is unreachable? → Queue outbound messages client-side, fall back to REST send endpoint, and alert user of degraded experience.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST allow visitors to self-register, confirm accounts via email, and log in via Keycloak-issued JWT.
- **FR-002**: System MUST guide new users through profile completion including required demographics, interests, location, relationship goals, and at least one profile photo.
- **FR-003**: System MUST process photo uploads with ML moderation, blur generation, and privacy labels before they appear to other users.
- **FR-004**: System MUST provide swipe-style match discovery with compatibility scoring, daily queue limits, and deterministic ordering for fairness.
- **FR-005**: System MUST create persistent match records and notify both parties within 1 second of mutual interest.
- **FR-006**: System MUST enable real-time chat between matched users with read receipts, typing indicators, and offline delivery guarantees.
- **FR-007**: System MUST expose privacy controls (photo visibility, block/report) and ensure enforcement across services and YARP gateway.
- **FR-008**: System MUST log critical actions (auth, profile updates, matches, messages, reports) with correlation IDs for monitoring.
- **FR-009**: System MUST deliver consistent REST/SignalR contracts consumed by the Flutter client, documented in API specs.
- **FR-010**: System MUST provide automated demo scripts that populate demo accounts and validate primary flows within 10 minutes.

*Placeholder clarifications to resolve during `/speckit.clarify` phase:*

- **FR-011**: System MUST define retention policy for chat transcripts [NEEDS CLARIFICATION: regulatory requirements pending].
- **FR-012**: System SHOULD specify push notification strategy for mobile apps [NEEDS CLARIFICATION: dependent on Firebase enablement].

### Key Entities *(include if feature involves data)*

- **Member Profile**: Represents the fully onboarded user; includes identity (Keycloak ID), demographics, preferences, photo catalog, and privacy settings.
- **Photo Asset**: Stores metadata for each uploaded photo including storage URI, moderation scores, blur variants, privacy scope, and audit trail.
- **Match**: Records mutual interest between two members with created timestamp, compatibility score snapshot, and status (active, blocked, archived).
- **Message**: Represents chat events tied to a match with sender ID, content payload, delivery status, and moderation flags.
- **Report**: Captures safety escalations referencing offending user, context (photo, message, profile), resolution state, and timestamps.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 90% of new users complete profile creation (including first photo) within 12 minutes using guided flow and demo scripts.
- **SC-002**: Match discovery requests respond in ≤350ms P95 under demo load of 500 concurrent users.
- **SC-003**: 80% of active users generate at least one mutual match within 48 hours of signup using seeded cohorts.
- **SC-004**: 95% of chat messages deliver within 1 second when both parties online; offline deliveries catch up within 30 seconds of reconnection.
- **SC-005**: All safety reports route to moderation queue with audit logs and acknowledgement within 2 minutes.

## Clarifications & Decisions
- MVP verification uses email confirmation backed by Keycloak; SMS verification is deferred to a post-MVP enhancement while maintaining hooks for secondary factors.
- Optional onboarding modules (profession, extended prompts, voice intro) are treated as progressive add-ons and must not block the minimum 4–6 step flow.
- Safety education cards ship in lightweight form (dismissible reminders) with a backlog item to expand them into richer content once messaging stability is proven.

