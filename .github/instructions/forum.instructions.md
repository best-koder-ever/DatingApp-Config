---
description: "Forum (Community) rules: canonical service, frozen API contract, anonymity, limits and known drift. Load whenever touching forum code."
applyTo: "**/forum-service/**"
---

# Forum (Community) — working rules

> Full detail: `specs/006-anonymous-forum/` (spec.md, plan.md, data-model.md,
> contracts/forum-api.md, tasks.md). This file is the short version that must stay true.

## 1. One backend, and it is forum-service

`forum-service` (:8092) is the **only** forum backend. YARP routes
`/api/forum/{**catch-all}` → `forumCluster` → `http://localhost:8092/`.

- **Do not** add forum code to `safety-service`, `MatchmakingService` or `UserService`.
  A duplicate safety-service `ForumController` existed, was unreachable, and was deleted
  2026-09-12. Do not recreate it.
- The forum has its own database (`forum-db`, port 3313, `ForumDb`). Do not put forum tables
  in another service's database.
- Schema changes go through **EF migrations** (`dotnet ef migrations add …`).
  `EnsureCreated()` was removed deliberately — do not bring it back.

## 2. Anonymity is not optional

- Author identity is `KeycloakId`, stored server-side for ownership, moderation and banning.
  **It must never appear in a response body.** The controller returns response *records*
  (`TopicResponse` / `AnswerResponse`) precisely so it cannot be serialized accidentally.
- Clients see only `colorHex` + `pseudonym`, derived by `PseudonymService` from
  `SHA256(keycloakId + ":" + topicId)`. Stable within one topic, unlinkable across topics.
- Use `isOwn` to tell the client whether the viewer wrote it. Never expose why.
- Use big-endian reads in any hashing so the identity is identical on every architecture.

## 3. The contract is frozen

`specs/006-anonymous-forum/contracts/forum-api.md` is authoritative. Before changing either
side, run:

```bash
bash scripts/check-forum-contract.sh
```

It asserts every field the Flutter models read exists in the backend response records. This
contract **drifted twice** before, once in each direction — that is why the check exists.

Rules that are easy to get wrong:
- **Create returns 201, not 200.** `apiTests` and the Dart client both assert it.
- **List endpoints return `{ total, page, pageSize, items }`**, not a bare array.
- Timestamps are UTC and serialized with a trailing `Z`. Use the controller's `AsUtc` helper.
- Channel slugs are wire format: `feedback`, `first-dates`, `red-flags`, `vent`,
  `success-stories`, `ask`. Renaming one is a breaking client change.

## 4. A topic has no title

A topic is one text of 1–200 characters plus a channel. Answers are also 1–200. Do not add a
title field, and do not raise the limit without changing all four places at once:
`ForumLimits.MaxTextLength`, the API validation, the DB `HasMaxLength`, and
`ForumService.maxTextLength` in Dart.

## 5. Moderation holds, it does not delete

`IsModerated` hides a post from the feed so a human can reverse a false positive. Never
hard-delete user content on a heuristic. Held content stays in the database.

## 6. Limits live in one place

`Models/ForumLimits.cs` is the single source of truth (3 topics/day, 15 answers/day, 30s
cooldown, 24h duplicate window, 3 duplicates, 48h expiry, 50 transcriptions/day). If you
change a value there, mirror it in `lib/services/forum_service.dart` and the spec.

## 7. Known environment gotchas

- **`/api/forum/**` returns 502 locally if forum-service was not started.** `dev-start.sh`
  launches it; use it rather than starting services by hand.
- **The gateway requires a token on every path** outside `/api/auth`, `/auth`,
  `/api/userfeedback` — so `/channels` needs one even though the controller allows anonymous.
- **YARP drops the terminating chunk.** Strict HTTP clients report a short read on chunked
  responses; the payload is intact. curl and Dart are fine. See the note in `api_tests.py`.
- **CPU transcription is very slow** (measured 185s for a 9.8s clip). `Whisper:Provider`
  defaults to `groq` so a `GROQ_API_KEY` switches to the fast path with no code change.
- Do **not** set a route-level `Timeout` in the YARP config: it maps to `TimeoutPolicy`, which
  needs `UseRequestTimeouts()` middleware this gateway does not install, and every forum
  request then 500s. Use the cluster's `HttpRequest.ActivityTimeout`.
