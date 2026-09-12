# Tasks: Anonymous Forum

**Input**: `specs/006-anonymous-forum/`
**Format**: `[ID] [P?] [Story] Description` — `[P]` = safe to implement in parallel
**PR rule**: one task, one PR, CI + Copilot review on each.

Status legend: `[x]` done · `[ ]` not started · `[~]` partially done

## Phase 0 — Remove the duplicates (blocking)

- [x] T001 Delete the unreachable safety-service forum implementation (`ForumController.cs`,
      `Models/ForumPost.cs`, `Models/ForumVote.cs`, `SafetyService.Tests/Controllers/ForumControllerTests.cs`)
      and strip the forum entities from `SafetyDbContext`. *22/22 tests still pass.*
- [x] T002 [P] Mark `specs/005-core-differentiation/tasks.md` Phase 10/11 superseded; correct
      T606, which claimed `/api/forum/**` routes to SafetyService.
- [x] T003 [P] Record forum-service as canonical in `.github/copilot-instructions.md`; emit it
      from `scripts/generate-ai-context.sh`.

## Phase 1 — forum-service becomes real

- [x] T010 Models: `ForumTopic`, `ForumAnswer`, `ForumVote`, `ForumPostQuota`, `ForumChannels`,
      `ForumLimits`. Delete `ForumPost`/`ForumComment`.
- [x] T011 EF migrations + package alignment (Pomelo 8.0.3) + pinned `ServerVersion` +
      `Database.Migrate()`.
- [x] T012 `ForumDbContext` fluent config: length caps, indexes, unique vote and quota keys.
- [x] T013 [US1][US2][US3][US4] `ForumController` implementing the frozen contract.
- [x] T014 [P] [US1] `PseudonymService` — deterministic per-topic colour + pseudonym.
- [x] T015 [P] [US7] `ForumQuotaService` — daily caps, cooldown, duplicate detection.
- [x] T016 [P] [US6] `ForumModerationService` — hold for review, never delete.
- [x] T017 [US5] `POST /api/forum/transcribe` + `WhisperClient` + daily transcription cap.
- [x] T018 `ForumService.Tests` — 62 tests.
- [x] T019 `.github/workflows/ci.yml` + `.dockerignore`.

## Phase 2 — Gateway and test tooling

- [x] T020 `dev-start.sh` / `dev-stop.sh` start, health-check and stop forum-service
      (fixes `/api/forum/**` returning 502 locally).
- [x] T021 YARP: raise the forum cluster activity timeout to 5 minutes for `/transcribe`.
- [x] T022 Repoint the ai-tester-service probes from `/posts` to `/topics` + `/answers`.
- [x] T023 `api_tests.py --forum` — end-to-end scenario through the gateway.

## Phase 3 — Flutter Community tab

- [x] T030 [US1] Rewrite `lib/services/forum_service.dart` to the contract, with `ForumResult`.
- [x] T031 [US1][US4] Rewrite `lib/screens/forum_feed_screen.dart` as the feed.
- [x] T032 [US2] `forum_compose_sheet.dart` — one capped field, channel picker.
- [x] T033 19 service tests + 7 widget tests.
- [x] T034 25 l10n strings (en + sv), including channel names.

## Phase 4 — Voice input

- [x] T040 `ForumService.transcribe` — multipart upload, 300s timeout, 503 handling.
- [x] T041 [US5] Mic in the composer. Tap to record, tap to stop, transcript lands in the
      same 200-char field for editing before posting. Auto-stops at 20s so a forgotten
      recording cannot run on. Hidden on web, where the `record` plugin has no implementation.
      *The latency blocker turned out to be a non-issue: see the Groq note below.*
- [ ] T042 [US5] Server-side duration probe (bot-service's `IAudioInspector`/ffprobe pattern);
      `MaxVoiceSeconds` is currently only enforced client-side.

## Phase 5 — Reporting

- [x] T050 [US6] `POST /api/forum/report` + `SafetyReportForwarder` to safety-service.
- [x] T051 [US6] Report action on topic cards + outcome snackbar.
- [ ] T052 [P] [US6] Report action on individual answers (the API already supports it).

## Transcription latency — resolved

Local CPU whisper measured **185s for a 9.8s clip** (`ggml-small`, 4 threads), which is why
this phase looked blocked. It is not:

- `GROQ_API_KEY` is already set in the project's `.env`.
- `dev-start.sh` already loads `.env` with `set -a`, so services it starts inherit the key.
- `WhisperOptions.Provider` defaults to `groq`, and `WhisperClient` reads `GROQ_API_KEY`
  straight from the environment.

Measured through `POST /api/forum/transcribe`: **2.27s end to end**, ~80x faster than local,
with an equally accurate transcript. **No code change was required.**

The remaining gap was docker: `docker-compose.yml` passed no API keys to any service, so the
whole Groq fast path was dormant in containers. `GROQ_API_KEY` (and `GEMINI_API_KEY` for
bot-service) are now passed through, defaulting to empty so nothing breaks without a key.

## Phase 6 — Verification and review

- [x] T060 `spec.md` with user stories and acceptance criteria.
- [x] T061 `plan.md`, `data-model.md`, `contracts/forum-api.md`.
- [x] T062 `tasks.md` (this file).
- [ ] T063 `.github/agents/verify-forum.agent.md` — run it after any forum change.
- [ ] T064 Wire the forum PRs to CI + Copilot review across the four repos.

## Phase 7 — AI context (so this cannot drift again)

- [x] T070 `.github/instructions/forum.instructions.md` with `applyTo` globs.
- [x] T071 `forum-service/.github/copilot-instructions.md`, committed inside the submodule repo
      so it travels with that repo.
- [x] T072 `.github/skills/forum-feature/SKILL.md` + `scripts/forum-smoke.sh` +
      `scripts/check-forum-contract.sh`.

## Suggested PR slicing

| PR | Tasks | Repo |
|---|---|---|
| 1 | T001–T003 | `safety-service`, root |
| 2 | T010–T014 | `forum-service` |
| 3 | T015–T018 | `forum-service` |
| 4 | T017, T019 | `forum-service` |
| 5 | T020–T023 | root, `dejting-yarp`, `ai-tester-service` |
| 6 | T030–T034 | `dejtingapp` |
| 7 | T050–T051 | `forum-service`, `dejtingapp` |
| 8 | T041–T042 | `dejtingapp`, `forum-service` (after the latency decision) |
