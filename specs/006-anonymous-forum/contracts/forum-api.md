# Contract — `/api/forum`

All endpoints require a bearer token, both at the gateway and at the service. `keycloakId` is
**never** part of any response body.

| Method | Path | Body | Success | Notes |
|---|---|---|---|---|
| GET | `/api/forum/channels` | – | 200 `["feedback",…]` | 6 slugs, display order |
| GET | `/api/forum/topics?channel=&sort=&page=&pageSize=` | – | 200 paged | `sort` = `hot` \| `top` \| `new` |
| GET | `/api/forum/topics/{id}` | – | 200 topic | |
| POST | `/api/forum/topics` | `{ text, channel? }` | **201** `{id}` | channel defaults to `vent` |
| DELETE | `/api/forum/topics/{id}` | – | 204 | author only, soft delete |
| POST | `/api/forum/topics/{id}/vote` | `{ value }` | 200 `{voteScore, myVote}` | `value` = +1 \| -1 |
| GET | `/api/forum/topics/{id}/answers?page=&pageSize=` | – | 200 paged | oldest first |
| POST | `/api/forum/answers/{id}/vote` | `{ value }` | 200 `{voteScore, myVote}` | `value` = +1 \| -1; toggle; not your own answer |
| POST | `/api/forum/topics/{id}/answers` | `{ text }` | **201** `{id}` | |
| DELETE | `/api/forum/answers/{id}` | – | 204 | author only, soft delete |
| POST | `/api/forum/transcribe` | multipart `audio` | 200 `{text}` | 503 when engine down |
| POST | `/api/forum/report` | `{ topicId? , answerId?, reason? }` | **201** `{id}` | exactly one target |
| GET | `/health` | – | 200 `{status, service, database}` | anonymous |

## Shapes

`PagedResponse<T>`: `{ total, page, pageSize, items[] }`

`TopicResponse`:
`{ id, text, channel, createdAt, expiresAt, voteScore, answerCount, isOwn, myVote, colorHex, pseudonym }`

`AnswerResponse`:
`{ id, topicId, text, createdAt, isOwn, colorHex, pseudonym }`

Timestamps are UTC and serialized with a trailing `Z`.

## Channels
`feedback` · `first-dates` · `red-flags` · `vent` · `success-stories` · `ask`
(default `vent`). **Renaming a slug is a breaking client change.**

## Errors
| Status | Meaning | Client behaviour |
|---|---|---|
| 400 | bad input (length, channel, vote value) | show the message |
| 401 | missing/expired token | re-authenticate |
| 404 | unknown topic/answer | refresh the feed |
| 422 | held for review, self-vote, self-report, duplicate text | explain, keep the composer open |
| 429 | cooldown or daily cap; `Retry-After` in seconds | back off, explain |
| 503 | safety service or speech engine unavailable | explain, offer the fallback |

## Gotchas
- **Going through the gateway requires a token even for `/channels`** — the gateway's inline
  auth middleware only whitelists `/api/auth`, `/auth`, `/api/userfeedback`.
- **YARP drops the terminating chunk**, so strict HTTP clients report a short read on chunked
  responses. Use the payload anyway; curl and Dart are unaffected.
- **`POST /transcribe` is slow on CPU whisper** (measured 185s for a 9.8s clip). The gateway
  activity timeout is raised to 5 minutes for this cluster; prefer the Groq fast path.
