# Feature Specification: Anonymous Forum ("Community")

**Feature**: Jodel-style anonymous forum for short topics and short answers
**Owner service**: `forum-service` (:8092) — the only forum backend
**Client**: `lib/services/forum_service.dart` + `lib/screens/forum_feed_screen.dart`
**Status**: implemented (2026-09-12)

## Why

People want to read and share short, low-stakes thoughts about dating — first dates, red
flags, venting, asking the community — and to leave feedback about the app that others can
read. Identity gets in the way of that, so the forum is anonymous by design and separate
from dating identity.

## User Stories

### US1 — Read the feed (P1)
As a user I open Community and see a feed of recent short topics, newest and most-liked
first, so there is always something to read.

**Acceptance**
- Feed loads without a filter and with a channel filter.
- Each topic shows its text, an anonymous colour + pseudonym, a vote score, an answer count.
- Expired (48h), soft-deleted and moderation-held topics never appear.
- No response ever contains the author's Keycloak id.
- Paging works; page size is clamped server-side.

### US2 — Start a topic (P1)
As a user I start a topic by writing one short text and picking a channel, so sharing takes
seconds.

**Acceptance**
- A topic is a single field of 1–200 characters plus a channel. There is no title.
- Text is validated after trimming, both in the client and the API, and the column is capped.
- Success returns 201.
- Refusal is explained: 400 for bad input, 429 for the cooldown or daily cap, 422 when held
  for review.
- The composer stays open on refusal so the text is not lost.

### US3 — Answer a topic (P1)
As a user I write a short answer under a topic, so I can react without starting a new topic.

**Acceptance**
- Answers are 1–200 characters and hang under exactly one topic.
- Answers are listed oldest-first and paged.
- The same author keeps one colour + pseudonym for every answer inside one topic, but differs
  across topics.

### US4 — Vote (P1)
As a user I give a topic +1 or -1, so the best topics rise.

**Acceptance**
- One vote per user per topic, enforced by a unique index.
- Sending the same value again removes the vote; sending the opposite changes it.
- You cannot vote on your own topic (422).
- Values other than +1/-1 are rejected (400).
- Sorting supports `hot` (default), `top` and `new`.

### US5 — Voice input (P2)
As a user I record a short voice note and get editable text in the composer, so I can post
without typing.

**Acceptance**
- The mic produces text in a field the user can edit before posting; nothing is submitted
  automatically.
- Recordings are capped at 20s and 2 MB, with an extension allowlist.
- Transcription is capped per user per day; it is exempt from the posting cooldown.
- When the engine is unavailable the client says so and the user types instead (503).

### US6 — Moderation and reporting (P2)
As the platform I must be able to act on abuse even though users are anonymous, and as a user
I must be able to report something.

**Acceptance**
- Prohibited language, contact details and personal numbers hold a post for review; nothing
  is silently deleted.
- Reporting a topic or answer forwards an accountable report to safety-service while keeping
  the author hidden from the reporter.
- Self-reporting is refused (422); an unreachable safety service returns 503 rather than
  claiming success.

### US7 — Anti-spam (P1)
As the platform I must stop one person flooding the forum.

**Acceptance**
- 3 topics per user per UTC day, 15 answers per day, 30s between posts.
- The same text posted three times within 24h is refused.
- Counters persist across restarts and are per user.
- Limits are communicated with 429 and a `Retry-After` header where a wait is known.

## Out of scope
Subforums, titles, images, nested replies, direct messages between forum users, translation,
summarisation, realtime updates, a separate moderation UI.

## Related
- `specs/005-core-differentiation/tasks.md` Phase 10/11 — the superseded safety-service plan
- `specs/001-mvp-foundation/plan.md` — recorded the original contract mismatch
