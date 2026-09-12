# Plan — anonymous forum

## Where it lives

`forum-service` is the **only** forum backend. It has its own repo
(`github.com/best-koder-org/forum-service`), its own MySQL database (`forum-db`, port 3313)
and the YARP route `/api/forum/{**catch-all}` → `forumCluster` → `http://localhost:8092/`.

Before this work there were three overlapping implementations. The safety-service
`ForumController` + `ForumPost`/`ForumVote` were **unreachable** (nothing routed to them) and
were deleted. `specs/005-core-differentiation/tasks.md` Phase 10/11 described a
safety-service forum and is marked superseded.

## Layering

```
Flutter screen  →  ForumService  →  gateway :8080  →  forum-service :8092
                                       │                    │
                                       │                    ├─ ForumDbContext (ForumDb)
                                       │                    ├─ PseudonymService      (derived identity)
                                       │                    ├─ ForumQuotaService      (caps, cooldown, duplicates)
                                       │                    ├─ ForumModerationService (hold, don't delete)
                                       │                    ├─ WhisperClient          (→ whisper-service :8095)
                                       │                    └─ SafetyReportForwarder  (→ safety-service :8088)
```

## Key decisions (and why)

1. **No titles.** A topic is one ≤200-character text plus a channel. Titles add friction and
   a second thing to moderate, and Jodel has none.
2. **Anonymous identity is derived, not stored.** `SHA256(keycloakId + ":" + topicId)` gives a
   colour and a Swedish pseudonym. Stable inside one topic, unlinkable across topics. Nothing
   is reversible, so a leaked database row cannot de-anonymise a post.
3. **The raw `KeycloakId` stays server-side.** It is needed for ownership, moderation and
   banning, and is never serialized. The forum is anonymous to its *users*, not to the
   platform — which is what makes reporting and banning possible at all.
4. **Moderation holds, never deletes.** `IsModerated` hides a post from the feed so a human can
   reverse a false positive. Deleting anonymous content on a heuristic is irreversible.
5. **Caps are persisted, not in-memory.** `ForumPostQuota` survives restarts and works across
   instances; the unique `(KeycloakId, Date)` index makes the daily reset free.
6. **Votes are unique at the database level.** A unique `(TopicId, VoterId)` index means a
   concurrent double-tap cannot create two rows, rather than relying on application locking.
7. **`AnswerCount` is computed on read; `VoteScore` is stored.** Counts cannot drift; the score
   is stored because feed sorting and filtering must stay index-friendly.
8. **Hot sort uses 6-hour buckets, not exponential decay.** Chosen deliberately: it is
   guaranteed to translate to SQL on any provider, unlike provider-specific date arithmetic.
   Swapping in real decay is a one-line change once there is a MySQL-backed test.
9. **Moderation lives in forum-service, not a new `shared/DatingApp.Moderation`.** A project
   reference from forum-service into `../shared/` would break its standalone build and CI, and
   `shared/DatingApp.Llm` is not actually referenced by any service today. Extraction is the
   right move once there is a real distribution mechanism (own repo + submodule, or a package).
10. **Reporting is delegated to safety-service**, forwarding the reporter's own token, so there
    is one canonical report store and moderators see forum reports alongside the rest.

## Migrations

`EnsureCreated()` was replaced by `Database.Migrate()`. The schema now evolves:
`InitialCreate` then `AddTranscribeQuota`. The abandoned `ForumPosts`/`ForumComments` tables
(the old `EnsureCreated` shape) were empty and incompatible, so they were dropped rather than
migrated.

## Two pre-existing defects fixed on the way

- `Pomelo.EntityFrameworkCore.MySql` 9.0.0 (EF Core 9) was paired with
  `EntityFrameworkCore.Design` 8.0.0, which made `dotnet ef` unreliable. Aligned to 8.0.3.
- `ServerVersion.AutoDetect()` opened a live connection during startup, so the service would
  not boot while MySQL was down. Replaced with a pinned version.

## Verification
- `cd forum-service && dotnet test ForumService.Tests/ForumService.Tests.csproj` — 62 tests
- `python3 api_tests.py --forum` — end-to-end through the gateway
- `cd mobile-apps/flutter/dejtingapp && flutter test test/services/forum_service_test.dart test/screens/forum_feed_screen_test.dart` — 30 tests
- `bash scripts/forum-smoke.sh` — contract assertions
