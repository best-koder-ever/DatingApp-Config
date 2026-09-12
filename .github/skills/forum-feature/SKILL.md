---
name: forum-feature
description: "Work on the anonymous Community forum end to end — add or change a forum feature across forum-service, the YARP gateway and the Flutter client, then verify the contract has not drifted. USE FOR: forum, Community tab, topics, answers, votes, channels, anonymous posts, pseudonym, forum rate limits, forum voice input, forum reporting, change the forum API. DO NOT USE FOR: general Flutter or .NET questions, other services, or moderation outside the forum."
---

# Forum feature workflow

Use this when changing anything under `/api/forum`, the Community tab, or the forum database.
The forum has four moving parts in four repositories, and its contract has drifted twice, so
work the sequence rather than editing one side.

## Before you start

1. Read `specs/006-anonymous-forum/spec.md` and `contracts/forum-api.md`.
2. Run `bash scripts/check-forum-contract.sh` and confirm it currently passes. If it fails,
   you are fixing drift, not adding a feature — say so before proceeding.
3. Decide which of the four layers changes. Most features touch one or two, not all four:

| Layer | Repo | Path |
|---|---|---|
| API + rules | `forum-service` | `Controllers/`, `Services/`, `Models/ForumLimits.cs` |
| Routing | `dejting-yarp` | `src/dejting-yarp/appsettings.Development.json` |
| Client | `dejtingapp` | `lib/services/forum_service.dart`, `lib/widgets/forum/`, `lib/screens/forum_feed_screen.dart` |
| Spec | root | `specs/006-anonymous-forum/` |

## The sequence

1. **Contract first.** Update `contracts/forum-api.md` before writing code. If the change is
   breaking, say so explicitly — the Flutter client ships separately and the two can be out of
   step in the field.
2. **Limits in one place.** Any new cap or length goes in `Models/ForumLimits.cs`, is mirrored
   in `lib/services/forum_service.dart`, and is documented in the spec. Three copies, one
   source of truth.
3. **Backend.** Add the endpoint or rule, then a unit test in `ForumService.Tests`. Follow the
   established shapes: `PagedResponse<T>`, response *records* that never carry `KeycloakId`,
   `AsUtc` for timestamps, and 201 for creates.
4. **Migration if the schema changed.** `dotnet ef migrations add <Name> --output-dir Migrations`
   then `dotnet ef database update`. Never edit an applied migration.
5. **Client.** `ForumService` returns `ForumResult<T>` — carry the backend's own `error`
   message so the UI can distinguish 429 (cooldown vs daily cap), 422 (held for review) and
   503 (unavailable). Do not swallow errors and return null.
6. **Verify.** Run, in order:
   ```bash
   cd forum-service && dotnet test ForumService.Tests/ForumService.Tests.csproj
   bash scripts/check-forum-contract.sh
   ./dev-start.sh                     # if not already running
   python3 api_tests.py --forum
   cd mobile-apps/flutter/dejtingapp && flutter test test/services/forum_service_test.dart test/screens/forum_feed_screen_test.dart
   ```
   Then run the `verify-forum` agent for the full pass/fail report.

## Rules that are easy to break

- A topic has **no title** — one ≤200-char text plus a channel.
- Create returns **201**; lists return a paged object, not an array.
- Never serialize `KeycloakId`. Return `isOwn` instead.
- Moderation **holds** content for review; it never deletes it.
- Votes are unique per `(topicId, voterId)` at the database level, and self-votes are refused.
- Cache-busting the feed after a post is the screen's job — the composer only reports the
  result.

## Reporting back

State which of the four layers changed, paste the `check-forum-contract.sh` output, and give
the test counts before and after. If you changed DDL, say whether the change is additive
(safe) or needs the dev `ForumDb` recreated.
