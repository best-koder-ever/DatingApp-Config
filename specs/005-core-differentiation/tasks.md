# Tasks: 005 — Core Differentiation

**Input**: SCOPE.md, product-vision.md (repo memory), existing MatchmakingService + UserService codebase
**Prerequisites**: 001-mvp-foundation shipped (profiles, matching, messaging, swipes, wizard), 003-bot-swarm LLM infrastructure

---

## Phase 1: Compatibility Question Schema (Week 1)

**Goal**: Create the question/answer data model and seed 32 psychology-backed questions. This is the foundation everything else builds on.

> **⚠️ DEVIATION NOTE (2026-04-30 reconciliation)**
> Phase 1 entities were built with a **categorical multi-choice + voice-hybrid schema** instead of the spec's 7-point Likert + BigFive/Attachment axes. Actual fields: `Emoji`, `OptionsJson`, `Weight`, `VoiceEligible`, `VoicePromptText[Sv]` on `CompatibilityQuestion`; `AnswerType`, `VoiceTranscript`, `DepthScore`, `QualityBreakdown`, `VoiceDurationSeconds` on `UserQuestionAnswer`. **15 questions** seeded (5 Personality, 4 Values, 3 Attachment, 3 Lifestyle) — not 32 TIPI-10/ECR-S. Phase 3+ scoring must work against this schema. T504/T505/T506 are superseded; expanding the question bank is future work.


### Entity & Storage
- [x] T500 [P0] [Infra] Create `CompatibilityQuestion` entity — `Id (int)`, `Category (enum: BigFive, Attachment, Values)`, `QuestionText (string)`, `QuestionTextSv (string)`, `ScaleMin (int)`, `ScaleMax (int)`, `ScaleMinLabel (string)`, `ScaleMaxLabel (string)`, `Weight (double)`, `SortOrder (int)`, `IsActive (bool)`, `BigFiveAxis (enum?: E, A, C, N, O)`, `AttachmentAxis (enum?: Anxiety, Avoidance)`
- **Estimate**: 2h
- **File**: `MatchmakingService/Models/CompatibilityQuestion.cs`
- **Evidence**: `dotnet build` succeeds, entity has all fields

- [x] T501 [P0] [Infra] Create `UserQuestionAnswer` entity — `Id (int)`, `KeycloakId (string)`, `QuestionId (int FK → CompatibilityQuestion)`, `Value (int, 1-7 Likert)`, `AnsweredAt (DateTime)`, unique constraint on (KeycloakId, QuestionId)
- **Estimate**: 1h
- **File**: `MatchmakingService/Models/UserQuestionAnswer.cs`
- **Depends on**: T500
- **Evidence**: `dotnet build` succeeds, FK relationship defined

- [x] T502 [P0] [Infra] Register entities in `MatchmakingDbContext` — add `DbSet<CompatibilityQuestion>`, `DbSet<UserQuestionAnswer>`, configure relationships and indexes in `OnModelCreating`
- **Estimate**: 1h
- **File**: `MatchmakingService/Data/MatchmakingDbContext.cs`
- **Depends on**: T500, T501
- **Evidence**: `dotnet ef migrations add AddCompatibilityQuestions` succeeds

- [x] T503 [P0] [Infra] Create EF migration — `AddCompatibilityQuestions` migration with tables, indexes, FK constraints
- **Estimate**: 30m
- **File**: `MatchmakingService/Migrations/` (auto-generated)
- **Depends on**: T502
- **Evidence**: `dotnet ef database update` applies cleanly

### Question Seeding
- [ ] T504 [P0] [Data] Seed 10 TIPI-10 questions (Big Five personality) — standard validated instrument: 2 items each for Extraversion, Agreeableness, Conscientiousness, Neuroticism (inv→Emotional Stability), Openness. 7-point Likert. Swedish translations. Reverse-scored items marked.
- **Estimate**: 2h
- **File**: `MatchmakingService/Data/SeedData/CompatibilityQuestionSeed.cs`
- **Depends on**: T503
- **Evidence**: Seed runs, 10 questions in DB, text matches published TIPI-10

- [ ] T505 [P0] [Data] Seed 12 ECR-S questions (Attachment style) — Experiences in Close Relationships Short Form: 6 Anxiety items + 6 Avoidance items. 7-point Likert. Swedish translations.
- **Estimate**: 2h
- **File**: `MatchmakingService/Data/SeedData/CompatibilityQuestionSeed.cs`
- **Depends on**: T503
- **Evidence**: 12 questions in DB, covers both attachment axes

- [ ] T506 [P0] [Data] Seed 10 values/dealbreaker questions — custom items covering: children (want/have), religion importance, political alignment, lifestyle (smoking, drinking, exercise), long-distance willingness, marriage views, financial values. 7-point Likert where applicable, binary where needed.
- **Estimate**: 2h
- **File**: `MatchmakingService/Data/SeedData/CompatibilityQuestionSeed.cs`
- **Depends on**: T503
- **Evidence**: 10 questions in DB, covers key dealbreaker dimensions

- [x] T507 [P0] [Infra] Auto-run seed on startup — call `SeedCompatibilityQuestions()` from `Program.cs` on first run (idempotent, checks if questions exist)
- **Estimate**: 1h
- **File**: `MatchmakingService/Program.cs`, `MatchmakingService/Data/SeedData/CompatibilityQuestionSeed.cs`
- **Depends on**: T504, T505, T506
- **Evidence**: Service starts clean, questions seeded, restart doesn't duplicate

**Phase 1 Total: ~12h / 8 tasks**

---

## Phase 2: Question API & Flutter Screen (Week 1-2)

**Goal**: Users can answer compatibility questions during onboarding or from profile settings. Answers stored in MatchmakingService.

### Backend API
- [x] T510 [P0] [API] Create `CompatibilityController` — `GET /api/compatibility/questions` returns all active questions grouped by category. `POST /api/compatibility/answers` accepts `{ answers: [{ questionId, value }] }` and upserts UserQuestionAnswers. `GET /api/compatibility/answers/{keycloakId}` returns user's answers. Auth required.
- **Estimate**: 4h
- **File**: `MatchmakingService/Controllers/CompatibilityController.cs`
- **Depends on**: T507
- **Evidence**: API returns 32 questions, accepts answers, persists to DB

- [x] T511 [P0] [API] Create DTOs — `CompatibilityQuestionDto`, `CompatibilityAnswerDto`, `SubmitAnswersRequest`, `SubmitAnswersResponse`, `UserAnswersSummaryDto`
- **Estimate**: 1h
- **File**: `MatchmakingService/DTOs/CompatibilityDtos.cs`
- **Evidence**: DTOs compile, used by controller

- [ ] T512 [P1] [API] Create CQRS commands/queries — `GetQuestionsQuery`, `SubmitAnswersCommand`, `GetUserAnswersQuery` with MediatR handlers
- **Estimate**: 3h
- **File**: `MatchmakingService/Commands/SubmitAnswersCommand.cs`, `MatchmakingService/Queries/GetQuestionsQuery.cs`, `MatchmakingService/Queries/GetUserAnswersQuery.cs`
- **Depends on**: T510, T511
- **Evidence**: Handlers unit tested with InMemoryDatabase

- [x] T513 [P1] [API] Add YARP route — `/api/compatibility/**` → MatchmakingService:8083
- **Estimate**: 30m
- **File**: `dejting-yarp/src/dejting-yarp/appsettings.json`
- **Depends on**: T510
- **Evidence**: curl through YARP gateway returns questions

### Flutter Onboarding
- [x] T514 [P0] [Flutter] Create `CompatibilityService` — API client for compatibility endpoints: `getQuestions()`, `submitAnswers()`, `getUserAnswers()`. Uses existing `ApiService` HTTP client.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/services/compatibility_service.dart`
- **Depends on**: T510
- **Evidence**: Service compiles, mock test passes

- [x] T515 [P0] [Flutter] Create `compatibility_questions_screen.dart` — wizard step 6 screen. Shows questions grouped by category (Big Five → Attachment → Values). 7-point Likert slider per question. Swedish text. Progress indicator. Submits all answers on completion.
- **Estimate**: 6h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/wizard/compatibility_questions_screen.dart`
- **Depends on**: T514
- **Evidence**: Screen renders, questions display, slider works, submits to API

- [ ] T516 [P1] [Flutter] Integrate into onboarding flow — add compatibility screen after current step 5 (preferences). Update `OnboardingCoordinator` to include new step. Make skippable but encouraged.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/services/onboarding_coordinator.dart`
- **Depends on**: T515
- **Evidence**: Full onboarding flow includes questions step, skip button works

- [ ] T517 [P1] [Flutter] Create compatibility settings screen — accessible from profile/settings, allows re-answering questions anytime. Shows current answers with edit capability.
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/compatibility_settings_screen.dart`
- **Depends on**: T514
- **Evidence**: Screen accessible from settings, loads current answers, saves updates

### Tests
- [ ] T518 [P0] [Test] Unit tests for CompatibilityController — test all 3 endpoints, auth enforcement, validation (value range 1-7), upsert behavior, missing question ID handling
- **Estimate**: 3h
- **File**: `MatchmakingService/MatchmakingService.Tests/Controllers/CompatibilityControllerTests.cs`
- **Depends on**: T510
- **Evidence**: `dotnet test` passes, all endpoints covered

- [ ] T519 [P0] [Test] Widget tests for compatibility_questions_screen — test question rendering, slider interaction, category grouping, submit flow, skip behavior
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/test/screens/wizard/compatibility_questions_screen_test.dart`
- **Depends on**: T515
- **Evidence**: `flutter test` passes

**Phase 2 Total: ~28h / 10 tasks**

---

## Phase 3: Compatibility Scoring Engine (Week 2-3)

**Goal**: Calculate pairwise compatibility scores from question answers. Power the matching algorithm.

### Scoring Logic
- [x] T520 [P0] [Core] Create `CompatibilityScorer` service — calculates compatibility between two users from their answers. Big Five: inverse-distance on paired items (reverse-scored items handled). Attachment: anxiety-avoidance 2D distance (secure-secure = highest). Values: exact-match weighted by importance. Returns `CompatibilityResult { OverallScore (0-100), BigFiveScore, AttachmentScore, ValuesScore, TopReasons[], FrictionPoints[] }`
- **Estimate**: 6h
- **File**: `MatchmakingService/Services/CompatibilityScorer.cs`
- **Depends on**: T507
- **Evidence**: Unit tests: identical answers = 100%, opposite = low, partial overlap = proportional

- [x] T521 [P0] [Core] Create `CompatibilityScore` entity — `Id`, `KeycloakId1`, `KeycloakId2` (alphabetically sorted), `OverallScore`, `BigFiveScore`, `AttachmentScore`, `ValuesScore`, `TopReasonsJson`, `FrictionPointsJson`, `CalculatedAt`, unique constraint on (KeycloakId1, KeycloakId2)
- **Estimate**: 1h
- **File**: `MatchmakingService/Models/CompatibilityScore.cs`
- **Evidence**: Entity compiles, added to DbContext

- [x] T522 [P0] [Core] Register `CompatibilityScore` in DbContext + migration
- **Estimate**: 30m
- **File**: `MatchmakingService/Data/MatchmakingDbContext.cs`
- **Depends on**: T521
- **Evidence**: Migration applies cleanly

- [x] T523 [P0] [API] Add `GET /api/compatibility/score/{otherKeycloakId}` — returns cached score or calculates on-demand. Caches in CompatibilityScore table. Invalidates when either user updates answers.
- **Estimate**: 3h
- **File**: `MatchmakingService/Controllers/CompatibilityController.cs`
- **Depends on**: T520, T522
- **Evidence**: API returns score, second call returns cached, answer update invalidates

- [ ] T524 [P0] [Core] Background pre-computation — background service that pre-calculates compatibility scores for users in same geographic area who both have answers. Runs on schedule or triggered by new answer submission.
- **Estimate**: 4h
- **File**: `MatchmakingService/Services/Background/CompatibilityPrecomputeService.cs`
- **Depends on**: T520, T522
- **Evidence**: Scores pre-calculated for test users, cold-start handled gracefully

### Tests
- [x] T525 [P0] [Test] Unit tests for CompatibilityScorer — test Big Five scoring (normal + reverse items), attachment 2D distance, values exact-match, overall weighted score, edge cases (one user has no answers, partial answers)
- **Estimate**: 4h
- **File**: `MatchmakingService/MatchmakingService.Tests/Services/CompatibilityScorerTests.cs`
- **Depends on**: T520
- **Evidence**: `dotnet test` passes, all scoring paths covered

**Phase 3 Total: ~19h / 6 tasks**

---

## Phase 4: Scoring Integration (Week 3)

**Goal**: Wire compatibility scores into the matching algorithm. Matches ranked by multi-dimensional score, not just desirability.

### AdvancedMatchingService Integration
- [x] T530 [P0] [Core] Add compatibility score to `AdvancedMatchingService.ScoreCandidateAsync()` — inject `CompatibilityScorer`, look up cached score, include as weighted component (30% weight). Fall back gracefully if either user has no answers (use average).
- **Estimate**: 4h
- **File**: `MatchmakingService/Services/AdvancedMatchingService.cs`
- **Depends on**: T520
- **Evidence**: Candidate scores include compatibility, users with answers rank higher

- [x] T531 [P1] [Core] Update `ScoringConfiguration` — add `CompatibilityWeight (double, default 0.30)`, adjust other weights to sum to 1.0. Make configurable via appsettings.
- **Estimate**: 1h
- **File**: `MatchmakingService/Models/ScoringConfiguration.cs`, `MatchmakingService/appsettings.json`
- **Depends on**: T530
- **Evidence**: Weights configurable, default weights sum to 1.0

- [ ] T532 [P1] [Core] Generate "Why You Matched" reasons during scoring — when `AdvancedMatchingService` creates a match, generate top-3 positive reasons and top-2 friction points from `CompatibilityResult`. Store as JSON in `MatchInsight` entity.
- **Estimate**: 4h
- **File**: `MatchmakingService/Services/AdvancedMatchingService.cs`, `MatchmakingService/Models/MatchInsight.cs`
- **Depends on**: T530, T520
- **Evidence**: New matches have populated MatchInsight records

- [ ] T533 [P0] [Infra] Create `MatchInsight` entity + migration — `Id`, `MatchId (FK)`, `ForKeycloakId (string)`, `ReasonsJson` (top positive signals), `FrictionJson` (areas of difference), `GrowthJson` (complementary strengths), `OverallScore`, `CreatedAt`
- **Estimate**: 2h
- **File**: `MatchmakingService/Models/MatchInsight.cs`, `MatchmakingService/Data/MatchmakingDbContext.cs`
- **Evidence**: Migration applies, entity registered

- [ ] T534 [P1] [API] Add `GET /api/matchmaking/matches/{matchId}/insight` — returns MatchInsight for authenticated user. Tiered: free users get score + top 2 reasons. Premium (future) gets full 4-section card.
- **Estimate**: 3h
- **File**: `MatchmakingService/Controllers/MatchmakingController.cs`
- **Depends on**: T533
- **Evidence**: API returns insight data, tiered response based on placeholder premium flag

- [ ] T535 [P1] [Core] Update DailyPick generation — `DailyPickGenerationService` uses compatibility-enhanced scoring to select daily picks. Higher compatibility = more likely to be picked.
- **Estimate**: 3h
- **File**: `MatchmakingService/Services/Background/DailyPickGenerationService.cs`
- **Depends on**: T530
- **Evidence**: Daily picks favor users with high compatibility scores

### Tests
- [ ] T536 [P0] [Test] Integration tests for scoring integration — verify AdvancedMatchingService uses compatibility, verify fallback when no answers, verify weight configuration works
- **Estimate**: 4h
- **File**: `MatchmakingService/MatchmakingService.Tests/Services/AdvancedMatchingServiceTests.cs`
- **Depends on**: T530, T531
- **Evidence**: `dotnet test` passes, scoring weights verified

- [ ] T537 [P0] [Test] Unit tests for MatchInsight generation — verify reasons generated, JSON format valid, asymmetric insights (user A and user B get different reasons)
- **Estimate**: 3h
- **File**: `MatchmakingService/MatchmakingService.Tests/Services/MatchInsightTests.cs`
- **Depends on**: T532
- **Evidence**: `dotnet test` passes

**Phase 4 Total: ~24h / 8 tasks**

---

## Phase 5: Match Insight Card — Flutter UI (Week 3-4)

**Goal**: Show users WHY they matched. Progressive disclosure from discover card to full insight.

### Flutter Components
- [ ] T540 [P0] [Flutter] Create `MatchInsightService` — API client for `/api/matchmaking/matches/{matchId}/insight`. Caches insight data locally.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/services/match_insight_service.dart`
- **Depends on**: T534
- **Evidence**: Service compiles, returns parsed insight data

- [ ] T541 [P0] [Flutter] Create compatibility badge widget — circular gradient badge showing overall % score. Coral→teal gradient. Used on discover card and match list.
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/lib/widgets/discovery/compatibility_badge.dart`
- **Evidence**: Badge renders with score, gradient correct, responsive to different sizes

- [ ] T542 [P0] [Flutter] Create compatibility bar comparison widget — horizontal bars comparing user vs match on Big Five, Attachment, Values dimensions. Used on profile preview.
- **Estimate**: 4h
- **File**: `mobile-apps/flutter/dejtingapp/lib/widgets/discovery/compatibility_bars.dart`
- **Evidence**: Bars render, coral/teal colors, responsive layout

- [ ] T543 [P0] [Flutter] Create Match Insight Card screen — full 4-section card: "Why You Connected" ✅ (top reasons), "Areas of Difference" ⚠️ (friction, max 3), "Where This Could Go" 🌱 (growth), "What You Could Learn" 📚 (premium). Navigate from match detail.
- **Estimate**: 6h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/match_insight_screen.dart`
- **Depends on**: T540, T541, T542
- **Evidence**: Full card renders with all 4 sections, premium section shows lock icon for free users

- [ ] T544 [P1] [Flutter] Integrate badge into discover card — add compatibility badge to existing `profile_card.dart`. Show only when score available.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/widgets/discovery/profile_card.dart`
- **Depends on**: T541
- **Evidence**: Badge visible on discover card when compatibility data exists

- [ ] T545 [P1] [Flutter] Integrate insight into matches screen — add compatibility % to match list items in `enhanced_matches_screen.dart`. Tap navigates to Match Insight Card.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/enhanced_matches_screen.dart`
- **Depends on**: T540, T543
- **Evidence**: Matches show %, tap opens insight card

### Tests
- [ ] T546 [P0] [Test] Widget tests for Match Insight Card — test all 4 sections render, premium gating, navigation, empty state
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/test/screens/match_insight_screen_test.dart`
- **Depends on**: T543
- **Evidence**: `flutter test` passes

- [ ] T547 [P0] [Test] Widget tests for compatibility badge and bars — test rendering, score display, gradient, responsive
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/test/widgets/discovery/compatibility_widgets_test.dart`
- **Depends on**: T541, T542
- **Evidence**: `flutter test` passes

**Phase 5 Total: ~24h / 8 tasks**

---

## Phase 6: AI Psykolog — Backend (Week 4-5)

**Goal**: LLM-powered Swedish reflection conversations. NOT therapy — "reflection coach." Sessions stored, themes extracted.

### Service Setup
- [ ] T550 [P0] [Infra] Create `PsykologSession` entity in UserService — `Id`, `KeycloakId`, `StartedAt`, `EndedAt`, `ThemeCount (int)`, `Status (enum: Active, Completed, Expired)`, `SessionNumber (int, per user)`
- **Estimate**: 1h
- **File**: `UserService/Models/PsykologSession.cs`
- **Evidence**: Entity compiles

- [ ] T551 [P0] [Infra] Create `PsykologMessage` entity — `Id`, `SessionId (FK)`, `Role (enum: User, Assistant)`, `Content (string)`, `CreatedAt`. Messages stored temporarily for context within session, purged after theme extraction.
- **Estimate**: 1h
- **File**: `UserService/Models/PsykologMessage.cs`
- **Depends on**: T550
- **Evidence**: Entity compiles, FK configured

- [ ] T552 [P0] [Infra] Register psykolog entities in `ApplicationDbContext` + migration
- **Estimate**: 1h
- **File**: `UserService/Data/ApplicationDbContext.cs`
- **Depends on**: T550, T551
- **Evidence**: Migration applies cleanly

- [ ] T553 [P0] [Core] Create `PsykologService` — manages session lifecycle: `StartSession()` (checks monthly limit for free users), `SendMessage()` (builds conversation context, calls LLM, stores response), `EndSession()` (triggers theme extraction). Uses LLM via HTTP to bot-service or direct LLM provider.
- **Estimate**: 8h
- **File**: `UserService/Services/PsykologService.cs`
- **Depends on**: T552
- **Evidence**: Session starts, messages round-trip through LLM, session ends

- [ ] T554 [P0] [AI] Design psykolog system prompt — Swedish-first, warm but professional tone. Focus on: relationship patterns, attachment awareness, values clarification, self-reflection. Explicit guardrails: never diagnose, never prescribe medication, redirect crisis to 112/Mind, never reveal being AI unless directly asked, never discuss other users.
- **Estimate**: 3h
- **File**: `UserService/Services/PsykologPrompts.cs`
- **Evidence**: 10 sample conversations reviewed for tone, safety, Swedish naturalness

- [ ] T555 [P0] [AI] Create theme extraction pipeline — after session ends, send full conversation to LLM with extraction prompt. Extract 3-7 themes as structured JSON: `{ themes: [{ label, intensity (0-1), axis (BigFive/Attachment/Values) }] }`. Store in `UserTheme` entity. Original messages deleted after extraction.
- **Estimate**: 6h
- **File**: `UserService/Services/ThemeExtractor.cs`, `UserService/Models/UserTheme.cs`
- **Depends on**: T553
- **Evidence**: Session ends → themes extracted → messages purged → themes stored

### API
- [ ] T556 [P0] [API] Create `PsykologController` — `POST /api/psykolog/sessions` (start session), `POST /api/psykolog/sessions/{id}/messages` (send message, get response), `POST /api/psykolog/sessions/{id}/end` (end session), `GET /api/psykolog/sessions` (list user's sessions), `GET /api/psykolog/themes` (user's extracted themes)
- **Estimate**: 4h
- **File**: `UserService/Controllers/PsykologController.cs`
- **Depends on**: T553
- **Evidence**: Full API works end-to-end

- [ ] T557 [P1] [API] Add YARP routes for psykolog — `/api/psykolog/**` → UserService:8082
- **Estimate**: 30m
- **File**: `dejting-yarp/src/dejting-yarp/appsettings.json`
- **Depends on**: T556
- **Evidence**: curl through gateway works

- [ ] T558 [P1] [Core] Rate limiting — free users: 1 session/month (30 messages max per session). Premium: unlimited sessions (50 messages max per session). Track via monthly counter.
- **Estimate**: 2h
- **File**: `UserService/Services/PsykologService.cs`
- **Depends on**: T553
- **Evidence**: Free user blocked after 1 session/month, premium unlimited

### Tests
- [ ] T559 [P0] [Test] Unit tests for PsykologService — test session lifecycle, message flow, theme extraction, rate limiting, graceful LLM failure handling
- **Estimate**: 4h
- **File**: `UserService/UserService.Tests/Services/PsykologServiceTests.cs`
- **Depends on**: T553
- **Evidence**: `dotnet test` passes

- [ ] T560 [P0] [Test] Unit tests for ThemeExtractor — test JSON parsing, axis mapping, edge cases (LLM returns garbage, empty session)
- **Estimate**: 2h
- **File**: `UserService/UserService.Tests/Services/ThemeExtractorTests.cs`
- **Depends on**: T555
- **Evidence**: `dotnet test` passes

**Phase 6 Total: ~33h / 11 tasks**

---

## Phase 7: AI Psykolog — Flutter UI (Week 5)

**Goal**: Chat-style reflection UI. Warm, calming, distinct from dating chat.

### Flutter Screens
- [ ] T565 [P0] [Flutter] Create `PsykologService` — API client for psykolog endpoints: `startSession()`, `sendMessage()`, `endSession()`, `getSessions()`, `getThemes()`
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/services/psykolog_service.dart`
- **Depends on**: T556
- **Evidence**: Service compiles, mock test passes

- [ ] T566 [P0] [Flutter] Create `psykolog_chat_screen.dart` — chat UI with distinct theme (softer colors, no dating branding). Message bubbles, typing indicator, session timer, "End Session" button. Swedish UI.
- **Estimate**: 6h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/psykolog_chat_screen.dart`
- **Depends on**: T565
- **Evidence**: Chat works, messages render, LLM responses displayed

- [ ] T567 [P0] [Flutter] Create `psykolog_home_screen.dart` — session history, start new session button, monthly session counter (free), themes summary. Entry point from profile hub.
- **Estimate**: 4h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/psykolog_home_screen.dart`
- **Depends on**: T565
- **Evidence**: Screen shows session history, navigates to chat

- [ ] T568 [P1] [Flutter] Integrate psykolog into navigation — add psykolog tab/button to `home_screen.dart` or `profile_hub_screen.dart`. Show session count badge.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/home_screen.dart`
- **Depends on**: T567
- **Evidence**: Psykolog accessible from main navigation

- [ ] T569 [P1] [Flutter] Create theme visualization widget — show extracted themes as tag cloud or categorized list (Big Five, Attachment, Values). Shows confidence and evolution.
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/lib/widgets/psykolog/theme_visualization.dart`
- **Depends on**: T565
- **Evidence**: Themes display with categories and intensity

### Tests
- [ ] T570 [P0] [Test] Widget tests for psykolog screens — test chat rendering, message sending, session lifecycle UI, theme display
- **Estimate**: 4h
- **File**: `mobile-apps/flutter/dejtingapp/test/screens/psykolog_chat_screen_test.dart`
- **Depends on**: T566
- **Evidence**: `flutter test` passes

**Phase 7 Total: ~21h / 6 tasks**

---

## Phase 8: Vector Matching (Week 5-6)

**Goal**: Convert psykolog themes into vector embeddings. Feed into matching as deep compatibility signal.

### Vector Infrastructure
- [ ] T575 [P0] [Infra] Add pgvector extension to UserService database — `CREATE EXTENSION IF NOT EXISTS vector;` in migration. Configure EF Core with `Npgsql.EntityFrameworkCore.PostgreSQL.Pgvector` (or store as float[] if MySQL).
- **Estimate**: 3h
- **File**: `UserService/Data/ApplicationDbContext.cs`, new migration
- **Evidence**: Vector extension active, can store/query vectors

- [ ] T576 [P0] [Core] Create `ReflectionVector` entity — `Id`, `KeycloakId`, `Vector (float[128])`, `SessionCount (int, how many sessions contributed)`, `Confidence (double, 0-1)`, `UpdatedAt`. One row per user, updated after each theme extraction.
- **Estimate**: 2h
- **File**: `UserService/Models/ReflectionVector.cs`
- **Depends on**: T575
- **Evidence**: Entity compiles, vector column created

- [ ] T577 [P0] [Core] Create `VectorEmbeddingService` — takes user's accumulated themes, generates 128-d embedding via LLM embedding API (OpenAI-compatible endpoint or sentence-transformers). Updates `ReflectionVector`. Calculates confidence based on session count (1 session=0.4, 3=0.7, 10+=0.95).
- **Estimate**: 6h
- **File**: `UserService/Services/VectorEmbeddingService.cs`
- **Depends on**: T576, T555
- **Evidence**: Themes → vector generated, stored, confidence correct

- [ ] T578 [P0] [Core] Create vector similarity endpoint — `GET /api/psykolog/vector-similarity/{otherKeycloakId}` returns cosine similarity between two users' reflection vectors. Returns null if either user has no vector.
- **Estimate**: 2h
- **File**: `UserService/Controllers/PsykologController.cs`
- **Depends on**: T577
- **Evidence**: API returns similarity score (0-1), null handling works

- [ ] T579 [P0] [Core] Wire vector similarity into MatchmakingService — MatchmakingService calls UserService for vector similarity during scoring. Weight: 40% when both users have vectors, 0% otherwise (redistributed to other signals).
- **Estimate**: 4h
- **File**: `MatchmakingService/Services/AdvancedMatchingService.cs`, `MatchmakingService/Services/UserServiceClient.cs`
- **Depends on**: T578, T530
- **Evidence**: Candidates with vector similarity ranked higher, graceful fallback

- [ ] T580 [P1] [Core] Privacy pipeline — ensure original psykolog message text is deleted after theme extraction (max 24h retention). Vectors are anonymous (no reversible mapping to text). User can request full vector deletion.
- **Estimate**: 3h
- **File**: `UserService/Services/ThemeExtractor.cs`, `UserService/Services/PsykologService.cs`
- **Depends on**: T555, T577
- **Evidence**: Messages deleted post-extraction, vector deletion endpoint works

### Tests
- [ ] T581 [P0] [Test] Unit tests for VectorEmbeddingService — test embedding generation, confidence calculation, update behavior, error handling
- **Estimate**: 3h
- **File**: `UserService/UserService.Tests/Services/VectorEmbeddingServiceTests.cs`
- **Depends on**: T577
- **Evidence**: `dotnet test` passes

- [ ] T582 [P0] [Test] Integration test for vector matching pipeline — end-to-end: psykolog session → theme extraction → vector generation → similarity query → matching score impact
- **Estimate**: 4h
- **File**: `UserService/UserService.Tests/Integration/VectorMatchingPipelineTests.cs`
- **Depends on**: T579
- **Evidence**: Full pipeline verified

**Phase 8 Total: ~27h / 8 tasks**

---

## Phase 9: 7-Axis Radar Chart (Week 6)

**Goal**: Visual personality/compatibility representation. Living chart that evolves with sessions.

### Backend
- [ ] T585 [P0] [Core] Create `RadarProfile` entity — `KeycloakId`, 7 axis values (0.0-1.0): `EmotionalStability`, `SocialEnergy`, `Openness`, `Warmth`, `LifeStructure`, `IntimacyComfort`, `ConflictStyle`. Plus `Confidence (double)`, `UpdatedAt`. Computed from questions (60%) + themes/vectors (40%).
- **Estimate**: 2h
- **File**: `MatchmakingService/Models/RadarProfile.cs`
- **Evidence**: Entity compiles, all 7 axes present

- [ ] T586 [P0] [Core] Create `RadarProfileCalculator` service — computes 7 axes from: TIPI-10 answers (maps to 5 Big Five axes), ECR-S answers (maps to IntimacyComfort + partial ConflictStyle), Values answers (partial Warmth, LifeStructure), psykolog themes (refines all axes). Blends sources by confidence.
- **Estimate**: 6h
- **File**: `MatchmakingService/Services/RadarProfileCalculator.cs`
- **Depends on**: T585, T520
- **Evidence**: Calculator produces valid axis values, confidence-weighted blend works

- [ ] T587 [P0] [API] Add `GET /api/compatibility/radar/{keycloakId}` — returns radar profile for user. `GET /api/compatibility/radar/compare/{otherKeycloakId}` returns both profiles for overlay comparison (premium).
- **Estimate**: 3h
- **File**: `MatchmakingService/Controllers/CompatibilityController.cs`
- **Depends on**: T586
- **Evidence**: API returns 7-axis data, compare endpoint returns both profiles

- [ ] T588 [P1] [Core] Radar profile auto-update — recalculate when user completes questions, finishes psykolog session, or submits post-date feedback. Background service or event-driven.
- **Estimate**: 3h
- **File**: `MatchmakingService/Services/Background/RadarProfileUpdateService.cs`
- **Depends on**: T586
- **Evidence**: Profile updates on trigger events

### Flutter
- [ ] T589 [P0] [Flutter] Create `RadarChartWidget` — 7-axis radar chart with CustomPainter. Coral polygon (user) + teal polygon (match, optional). 30% opacity fill. Axis labels. Progressive disclosure: faded at low confidence, vivid at high.
- **Estimate**: 8h
- **File**: `mobile-apps/flutter/dejtingapp/lib/widgets/compatibility/radar_chart_widget.dart`
- **Evidence**: Chart renders with 7 axes, two overlaid polygons, opacity based on confidence

- [ ] T590 [P1] [Flutter] Create `radar_profile_screen.dart` — full-screen radar chart with narrative annotations. "Strong alignment" / "Interesting difference" / "Worth discussing" labels per axis. Shows confidence level and data sources.
- **Estimate**: 4h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/radar_profile_screen.dart`
- **Depends on**: T589
- **Evidence**: Screen renders full chart with annotations

- [ ] T591 [P1] [Flutter] Integrate radar into Match Insight Card — add radar chart overlay (user vs match) to the Match Insight screen. Premium section.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/match_insight_screen.dart`
- **Depends on**: T589, T543
- **Evidence**: Radar visible in insight card for premium users

- [ ] T592 [P1] [Flutter] Integrate radar into profile hub — show own radar chart on profile page. "Your Compatibility Profile" section.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/profile_hub_screen.dart`
- **Depends on**: T589
- **Evidence**: Radar chart visible on profile hub

### Tests
- [ ] T593 [P0] [Test] Unit tests for RadarProfileCalculator — test axis calculations from questions, theme integration, confidence blending, edge cases
- **Estimate**: 4h
- **File**: `MatchmakingService/MatchmakingService.Tests/Services/RadarProfileCalculatorTests.cs`
- **Depends on**: T586
- **Evidence**: `dotnet test` passes

- [ ] T594 [P0] [Test] Widget tests for RadarChartWidget — test 7-axis rendering, two-polygon overlay, confidence opacity, responsive sizing
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/test/widgets/compatibility/radar_chart_widget_test.dart`
- **Depends on**: T589
- **Evidence**: `flutter test` passes

**Phase 9 Total: ~37h / 10 tasks**

---

## Phase 10: Anonymous Forum "Forumet" — Backend (Week 7)

**Goal**: Jodel-style anonymous posting about dating life. Separate from dating identity.

### Data Model
- [ ] T600 [P0] [Infra] Create forum entities — `ForumPost { Id, AnonymousColorHex, Channel (enum: FirstDates, RedFlags, Vent, SuccessStories, AskCommunity), Content (string, max 500), Karma (int), CreatedAt, ExpiresAt (48h default), IsModerated (bool), ModeratedAt, KeycloakIdHash (SHA256, for rate limits only — not reversible to identity) }`. `ForumVote { Id, PostId (FK), VoterKeycloakIdHash, VoteType (Up/Down), CreatedAt }`. Unique constraint on (PostId, VoterKeycloakIdHash).
- **Estimate**: 3h
- **File**: `safety-service/SafetyService/Models/ForumPost.cs`, `safety-service/SafetyService/Models/ForumVote.cs`
- **Evidence**: Entities compile, relationships configured

- [ ] T601 [P0] [Infra] Register forum entities in `SafetyDbContext` + migration
- **Estimate**: 1h
- **File**: `safety-service/SafetyService/Data/SafetyDbContext.cs`
- **Depends on**: T600
- **Evidence**: Migration applies, tables created

### API
- [ ] T602 [P0] [API] Create `ForumController` — `GET /api/forum/posts?channel=X&sort=hot|new&page=N` (paginated feed), `POST /api/forum/posts` (create post, assigns random color), `POST /api/forum/posts/{id}/vote` (upvote/downvote, toggle), `DELETE /api/forum/posts/{id}` (author only, by hash match). Rate limit: 5 posts/day, 50 votes/day per user.
- **Estimate**: 6h
- **File**: `safety-service/SafetyService/Controllers/ForumController.cs`
- **Depends on**: T601
- **Evidence**: Full CRUD works, rate limits enforced

- [ ] T603 [P0] [Core] Forum DTOs — `ForumPostDto`, `CreatePostRequest`, `VoteRequest`, `ForumFeedResponse` with pagination
- **Estimate**: 1h
- **File**: `safety-service/SafetyService/DTOs/ForumDtos.cs`
- **Evidence**: DTOs compile

- [ ] T604 [P0] [Core] "Hot" sorting algorithm — score = upvotes - downvotes, decayed by age (Wilson score or Reddit-style). New posts get initial boost. Posts expire after 48h by default.
- **Estimate**: 3h
- **File**: `safety-service/SafetyService/Services/ForumScoringService.cs`
- **Depends on**: T602
- **Evidence**: Hot feed sorts by decayed score, new posts visible

- [ ] T605 [P1] [Core] Forum content moderation — auto-moderate via existing safety-service LLM pipeline. Flag posts containing personal info, harassment, or dating profile references. Hold for review rather than auto-delete.
- **Estimate**: 3h
- **File**: `safety-service/SafetyService/Services/ForumModerationService.cs`
- **Depends on**: T602
- **Evidence**: Offensive post flagged, personal info detected

- [ ] T606 [P1] [API] Add YARP route — `/api/forum/**` → SafetyService:8088
- **Estimate**: 30m
- **File**: `dejting-yarp/src/dejting-yarp/appsettings.json`
- **Depends on**: T602
- **Evidence**: curl through gateway works

### Tests
- [ ] T607 [P0] [Test] Unit tests for ForumController — test CRUD, voting (toggle, one-per-user), rate limits, channel filtering, pagination, author deletion
- **Estimate**: 4h
- **File**: `safety-service/SafetyService.Tests/Controllers/ForumControllerTests.cs`
- **Depends on**: T602
- **Evidence**: `dotnet test` passes

- [ ] T608 [P0] [Test] Unit tests for ForumScoringService — test hot sort, time decay, initial boost, edge cases (0 votes, all downvotes)
- **Estimate**: 2h
- **File**: `safety-service/SafetyService.Tests/Services/ForumScoringServiceTests.cs`
- **Depends on**: T604
- **Evidence**: `dotnet test` passes

**Phase 10 Total: ~24h / 9 tasks**

---

## Phase 11: Anonymous Forum — Flutter UI (Week 7-8)

**Goal**: Anonymous, Jodel-inspired feed in the app. Warm community vibe. Completely separated from dating identity.

### Flutter Screens
- [ ] T610 [P0] [Flutter] Create `ForumService` — API client for forum endpoints: `getPosts()`, `createPost()`, `vote()`, `deletePost()`
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/services/forum_service.dart`
- **Depends on**: T602
- **Evidence**: Service compiles, mock test passes

- [ ] T611 [P0] [Flutter] Create `forum_feed_screen.dart` — main forum screen. Channel tabs (First Dates, Red Flags, Vent, Success Stories, Ask). Card list with anonymous color bar, content, karma count, vote buttons. Pull-to-refresh. Infinite scroll pagination.
- **Estimate**: 6h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/forum_feed_screen.dart`
- **Depends on**: T610
- **Evidence**: Feed renders, channels switch, voting works

- [ ] T612 [P0] [Flutter] Create `forum_compose_screen.dart` — post creation. Channel selector, text input (500 char limit), random color preview, submit. Warning: "Posts are anonymous — no one can see your identity."
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/forum_compose_screen.dart`
- **Depends on**: T610
- **Evidence**: Compose works, character limit enforced, posts appear in feed

- [ ] T613 [P1] [Flutter] Integrate forum into navigation — add forum tab to `home_screen.dart` bottom navigation. Badge for new posts since last visit.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/home_screen.dart`
- **Depends on**: T611
- **Evidence**: Forum tab visible, navigates to feed

### Tests
- [ ] T614 [P0] [Test] Widget tests for forum screens — test feed rendering, channel switching, voting, compose flow, empty states
- **Estimate**: 4h
- **File**: `mobile-apps/flutter/dejtingapp/test/screens/forum_feed_screen_test.dart`
- **Depends on**: T611
- **Evidence**: `flutter test` passes

**Phase 11 Total: ~17h / 5 tasks**

---

## Phase 12: Post-Date Feedback Loop (Week 8)

**Goal**: After dates, users reflect → radar recalibrates → matching improves. The "Living Profile" engine.

### Backend
- [ ] T620 [P0] [Core] Create `PostDateFeedback` entity — `Id`, `KeycloakId`, `MatchId`, `OverallRating (1-5)`, `ChemistryRating (1-5)`, `ConversationRating (1-5)`, `WouldMeetAgain (bool)`, `FreeformReflection (string, optional)`, `CreatedAt`
- **Estimate**: 2h
- **File**: `MatchmakingService/Models/PostDateFeedback.cs`
- **Evidence**: Entity compiles, registered in DbContext

- [ ] T621 [P0] [API] Create `POST /api/matchmaking/matches/{matchId}/feedback` — accepts post-date feedback. Triggers radar recalibration for the user. Feeds back into matching quality metrics.
- **Estimate**: 3h
- **File**: `MatchmakingService/Controllers/MatchmakingController.cs`
- **Depends on**: T620
- **Evidence**: Endpoint accepts feedback, triggers recalibration event

- [ ] T622 [P0] [Core] Feedback → radar recalibration — post-date ratings adjust radar axes. Low chemistry + high conversation = recalibrate IntimacyComfort axis. Low overall = reduce confidence in match signals.
- **Estimate**: 4h
- **File**: `MatchmakingService/Services/RadarProfileCalculator.cs`
- **Depends on**: T621, T586
- **Evidence**: Radar axes shift after feedback, changes reflected in next match scores

- [ ] T623 [P1] [Flutter] Create `post_date_feedback_screen.dart` — prompted after a match (timing: 24h after last message exchange > N messages). Star ratings, toggle, optional text. "Help us match you better."
- **Estimate**: 4h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/post_date_feedback_screen.dart`
- **Depends on**: T621
- **Evidence**: Screen renders, submits feedback, shows confirmation

### Tests
- [ ] T624 [P0] [Test] Unit tests for feedback recalibration — test axis adjustments, edge cases (no previous radar), confidence changes
- **Estimate**: 3h
- **File**: `MatchmakingService/MatchmakingService.Tests/Services/RadarRecalibrationTests.cs`
- **Depends on**: T622
- **Evidence**: `dotnet test` passes

- [ ] T625 [P0] [Test] Widget tests for post-date feedback — test rating input, submission, timing trigger
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/test/screens/post_date_feedback_screen_test.dart`
- **Depends on**: T623
- **Evidence**: `flutter test` passes

**Phase 12 Total: ~18h / 6 tasks**

---

## Phase 13: Polish & Living Profile (Week 8-9)

**Goal**: Progressive confidence visualization, before/after comparisons, and flywheel messaging.

- [ ] T630 [P1] [Flutter] Radar chart confidence visualization — faded/dotted lines at <60% confidence, soft colors at 60-80%, vivid at 80-90%, gold ring at 95%+. Animate transitions.
- **Estimate**: 4h
- **File**: `mobile-apps/flutter/dejtingapp/lib/widgets/compatibility/radar_chart_widget.dart`
- **Depends on**: T589
- **Evidence**: Chart visually different at each confidence tier

- [ ] T631 [P1] [Flutter] Before/after radar comparison — show how user's radar has evolved: "3 months ago → now". Side-by-side or animated morph.
- **Estimate**: 4h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/radar_profile_screen.dart`
- **Depends on**: T589
- **Evidence**: Before/after comparison visible, animation smooth

- [ ] T632 [P1] [Flutter] Match quality metric — show "Your match quality improved X% since you started" on profile/psykolog home. Calculated from post-date feedback trends.
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/psykolog_home_screen.dart`
- **Depends on**: T567, T620
- **Evidence**: Metric displays, updates after feedback

- [ ] T633 [P2] [Core] Psykolog axis-based suggestions — psykolog suggests conversation topics based on user's weakest radar axes. "I notice you haven't explored much about how you handle disagreements..."
- **Estimate**: 4h
- **File**: `UserService/Services/PsykologService.cs`
- **Depends on**: T553, T586
- **Evidence**: Psykolog references radar axes in conversation

- [ ] T634 [P2] [Flutter] Forum-to-axis mapping — forum channels subtly relate to radar axes. "Red Flags" → Conflict Style. "First Dates" → Social Energy. Shows as "You might find this interesting" recommendations.
- **Estimate**: 3h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/forum_feed_screen.dart`
- **Depends on**: T611, T586
- **Evidence**: Recommendations shown based on radar profile

- [ ] T635 [P2] [Flutter] Onboarding confidence messaging — during wizard, after completing compatibility questions, show: "You now have 60% confidence. Complete 1 psykolog session to reach 80%." Motivate progression.
- **Estimate**: 2h
- **File**: `mobile-apps/flutter/dejtingapp/lib/screens/wizard/compatibility_questions_screen.dart`
- **Depends on**: T515
- **Evidence**: Confidence message shows after questions

**Phase 13 Total: ~20h / 6 tasks**

---

## Summary

| Phase | Tasks | Estimate | Depends On |
|-------|-------|----------|------------|
| 1: Question Schema | T500-T507 | ~12h | - |
| 2: Question API & Flutter | T510-T519 | ~28h | Phase 1 |
| 3: Scoring Engine | T520-T525 | ~19h | Phase 1 |
| 4: Scoring Integration | T530-T537 | ~24h | Phase 3 |
| 5: Match Insight Flutter | T540-T547 | ~24h | Phase 4 |
| 6: AI Psykolog Backend | T550-T560 | ~33h | - (parallel with 1-5) |
| 7: AI Psykolog Flutter | T565-T570 | ~21h | Phase 6 |
| 8: Vector Matching | T575-T582 | ~27h | Phase 6 |
| 9: Radar Chart | T585-T594 | ~37h | Phase 3, 8 |
| 10: Forum Backend | T600-T608 | ~24h | - (parallel) |
| 11: Forum Flutter | T610-T614 | ~17h | Phase 10 |
| 12: Post-Date Feedback | T620-T625 | ~18h | Phase 4, 9 |
| 13: Polish & Living Profile | T630-T635 | ~20h | Phase 9, 11, 12 |
| **Total** | **85 tasks** | **~304h** | |

### Critical Path
```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 (Questions → Scoring → Insight Card)
                                    ↓
Phase 6 → Phase 7 → Phase 8 → Phase 9 (Psykolog → Vectors → Radar)
                                    ↓
                              Phase 12 → Phase 13 (Feedback → Polish)

Phase 10 → Phase 11 (Forum, can run in parallel with above)
```

### Build Order (Recommended)
1. **Start with Phase 1 + Phase 10** (independent, can parallel)
2. **Phase 2 + Phase 6** (API layer, can parallel)
3. **Phase 3** (scoring engine — unlocks everything)
4. **Phase 4 + Phase 7 + Phase 11** (integration + Flutter UIs)
5. **Phase 5 + Phase 8** (insight card + vectors)
6. **Phase 9** (radar chart — needs all data sources)
7. **Phase 12 → Phase 13** (feedback loop + polish)
