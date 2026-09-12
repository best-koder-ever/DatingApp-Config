# Data model — anonymous forum

Database: MySQL `ForumDb` on port 3313 (container `forum-db`). Schema is owned by EF Core
migrations in `forum-service/Migrations/`; `EnsureCreated()` is no longer used.

## ForumTopic
| Column | Type | Notes |
|---|---|---|
| Id | int PK | |
| KeycloakId | varchar(64) | Author. **Server-side only — never serialized.** |
| Text | varchar(200) | The whole topic; there is no title. |
| Channel | varchar(32) | Slug from `ForumChannels`. |
| CreatedAt | datetime(6) | UTC. |
| ExpiresAt | datetime(6) | `CreatedAt + 48h`. Expired topics drop out of the feed. |
| IsDeleted | tinyint(1) | Soft delete; author-initiated. |
| IsModerated | tinyint(1) | Held for review; hidden from the feed, never destroyed. |
| ModeratedAt | datetime(6) null | |
| VoteScore | int | Denormalised sum of votes. Updated in the vote transaction. |

Indexes: `(Channel, CreatedAt)`, `(IsDeleted, IsModerated, ExpiresAt)`, `VoteScore`, `KeycloakId`.

## ForumAnswer
| Column | Type | Notes |
|---|---|---|
| Id | int PK | |
| TopicId | int FK → ForumTopic | Cascade delete. |
| KeycloakId | varchar(64) | **Server-side only.** |
| Text | varchar(200) | |
| CreatedAt | datetime(6) | |
| IsDeleted | tinyint(1) | |
| IsModerated | tinyint(1) | |
| ModeratedAt | datetime(6) null | |

Indexes: `(TopicId, CreatedAt)`, `KeycloakId`.
*Answer count is computed on read, not denormalised, so it cannot drift.*

## ForumVote
| Column | Type | Notes |
|---|---|---|
| Id | int PK | |
| TopicId | int FK → ForumTopic | Cascade delete. |
| VoterId | varchar(64) | **Server-side only.** |
| Value | int | +1 or -1. |
| VotedAt | datetime(6) | |

Index: **unique** `(TopicId, VoterId)` — the database, not application code, prevents a
concurrent double-vote.

## ForumPostQuota
| Column | Type | Notes |
|---|---|---|
| Id | int PK | |
| KeycloakId | varchar(64) | |
| Date | date | UTC date; a new row per day is the reset mechanism. |
| TopicCount | int | |
| AnswerCount | int | |
| TranscribeCount | int | Added by `AddTranscribeQuota`. |
| LastPostedAt | datetime(6) null | Drives the 30s cooldown. |

Index: **unique** `(KeycloakId, Date)`.

## Anonymous identity (derived, not stored)
`SHA256(keycloakId + ":" + topicId)` → colour from a fixed palette + pseudonym from Swedish
adjective/noun lists (definite form, e.g. "Gröna Duvan"). Big-endian reads so the identity is
identical on every architecture. Scoped to one topic: unlinkable across topics, stable within
one.

## Limits (single source of truth: `Models/ForumLimits.cs`)
`MaxTextLength` 200 · `TopicsPerDay` 3 · `AnswersPerDay` 15 · `PostCooldownSeconds` 30 ·
`DuplicateWindowHours` 24 · `MaxDuplicateCount` 3 · `PostLifetime` 48h · `MaxPageSize` 50 ·
`MaxVoiceBytes` 2 MB · `MaxVoiceSeconds` 20 · `TranscriptionsPerDay` 50
