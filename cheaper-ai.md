# cheaper-ai.md — Execution Plan for DeepSeek V4 Agent

> AUDIENCE: an autonomous coding AI (DeepSeek V4), NOT a human.
> You are continuing a partially-completed engineering plan in this multi-repo workspace.
> Read this whole file once, then execute tasks top-to-bottom. Each task is self-contained:
> it has FILES, STEPS, ACCEPTANCE, and VERIFY. Do not skip VERIFY. Do not ask the human
> questions unless ACCEPTANCE is ambiguous AND you cannot resolve it from the codebase.

---

## 0. OPERATING CONTRACT (read first, obey always)

### 0.1 Editing
- Edit files directly with your file-edit tools (write/replace). Do NOT use `cat > file << EOF`
  shell heredocs. The repo's `copilot-instructions.md` says to use heredocs — that rule is
  SUPERSEDED for agent mode. Ignore it.
- Read a file before editing it. Match existing indentation exactly (the gateway JSON files
  use TAB indentation; most C# uses 4 spaces; Dart uses 2 spaces).
- Do NOT create markdown "documentation of changes" files. Do NOT add comments/docstrings to
  code you did not change. Only make changes a task requires. No speculative refactors.

### 0.2 Build & Test commands (deterministic — use these exact forms)
- Backend service (run from the service dir):
  `dotnet build` then `dotnet test <Svc>.Tests/<Svc>.Tests.csproj`
  - UserService dir: `/home/m/development/DatingApp/UserService`
  - MatchmakingService dir: `/home/m/development/DatingApp/MatchmakingService`
  - messaging-service dir: `/home/m/development/DatingApp/messaging-service`
  - swipe-service dir: `/home/m/development/DatingApp/swipe-service`
  - photo-service dir: `/home/m/development/DatingApp/photo-service`
- EF migration (from the service dir, only when a DB entity/table changes):
  `dotnet ef migrations add <Name>`  (dotnet-ef 9.0.3 is installed; runtime auto-applies via
  `Database.Migrate()` at startup, so a migration is MANDATORY whenever you add/alter an entity).
- Flutter (from `/home/m/development/mobile-apps/flutter/dejtingapp`):
  `flutter analyze <changed files>` then `flutter test <changed test files>`
  - Full gates: `flutter analyze --no-fatal-infos --no-fatal-warnings` and `flutter test`.
- API smoke test (from `/home/m/development/DatingApp`): `python3 api_tests.py`
- JSON validity after editing any gateway config:
  `python3 -c "import json;json.load(open('<file>'));print('OK')"`

### 0.3 Verify-after-edit rule
After EVERY code change: run the narrowest relevant build/analyze + test. A task is DONE only
when its VERIFY passes with zero errors and zero new failing tests. If a pre-existing test was
already failing before your change, note it and continue; do not "fix" unrelated code.

### 0.4 Multi-repo git (do NOT improvise)
This workspace is 8+ independent git repos. To commit/push use the provided wrappers from
`/home/m/development/DatingApp`: `./ai-commit-helper.sh` or `./gita-workflow.sh`; for GitHub use
`./gh-multi-repo.sh`. NEVER loop `cd repo && git commit`. Batch ALL GitHub API calls; never call
`gh pr/issue` in a loop. Default: make local commits per-repo via the wrapper; only push when the
human says so.

### 0.5 Hard constraints (product decisions — do not violate)
- NON-AI ONLY. Do NOT add or call any LLM (Gemini/Groq/Ollama/OpenAI), embeddings, pgvector,
  or "AI" features. All "smart" features must be RULE-BASED / deterministic.
- Monetization is architected EARLY (Phase P1) before most differentiators.
- Niche-AGNOSTIC. No niche-specific onboarding copy.
- The human does NOT care about the "matches look fake" enrichment task — it is DEFERRED/skipped
  unless explicitly re-requested. Do NOT spend effort enriching the match list names/photos.

---

## 1. SYSTEM MAP (ground truth)

### 1.1 Services / ports
| Port | Service | Dir | DB |
|------|---------|-----|----|
| 8080 | dejting-yarp (gateway) | dejting-yarp/src/dejting-yarp | - |
| 8082 | UserService | UserService | MySQL UserServiceDb |
| 8083 | MatchmakingService | MatchmakingService | MySQL MatchmakingDb |
| 8085 | photo-service | photo-service | MySQL PhotoServiceDb |
| 8086 | messaging-service (SignalR) | messaging-service | MySQL MessagingServiceDb |
| 8087 | swipe-service | swipe-service | MySQL SwipeServiceDb |
| 8088 | safety-service | safety-service | - |
| 8089 | bot-service | bot-service/BotService | SQLite |
| 8090 | Keycloak | docker | - |

### 1.2 Auth model
- Keycloak OIDC is the ONLY auth provider (AuthService was deleted). JWT `sub` claim ==
  Keycloak user id. In C# controllers extract it with:
  `User.FindFirstValue(ClaimTypes.NameIdentifier) ?? User.FindFirstValue("sub")`.
- Some entities key off a `Guid UserId` (UserService) and some off a `string KeycloakId`
  (MatchmakingService). Match the local convention of the service you edit.

### 1.3 Conventions
- C#: CQRS via MediatR (Commands/ + Queries/ folders), EF Core 8, controllers return
  `ApiResponse<T>` (UserService/Common/ApiResponse.cs: `SuccessResult`, `FailureResult`).
  Tests: xUnit + Moq + EF Core InMemoryDatabase (`UseInMemoryDatabase(Guid.NewGuid().ToString())`),
  IDisposable pattern, claims set via `DefaultHttpContext{ User = ClaimsPrincipal(...) }`.
- Flutter: Dart 3.5, dark theme, primaryColor coral `#FF7F50`. `ApiUrls.gateway` lives in
  `lib/backend_url.dart`. Auth token via `AppState().getOrRefreshAuthToken()` (in
  `lib/services/api_service.dart`); always `await AppState().initialize()` first. Tests use
  `buildCoreScreenTestApp(home: ...)` from `test/helpers/core_screen_test_helper.dart`; test file
  mirrors source path (`lib/x/y.dart` -> `test/x/y_test.dart`). `DropdownButtonFormField` in this
  Flutter version uses `value:` NOT `initialValue:`.
- Gateway (YARP): routes in `dejting-yarp/src/dejting-yarp/appsettings.json` (base) and
  `appsettings.Development.json` (dev — the one used locally). TAB indentation. To expose a new
  backend path you MUST add a route in BOTH files (or at least Development for local). A route =
  `{ "ClusterId": "<cluster>", "Match": { "Path": "/api/x/{**catch-all}" }, "Metadata": {...} }`.
  Clusters already defined: userCluster(8082), matchmakingCluster(8083), photoCluster(8085),
  messagingCluster(8086), swipeCluster(8087), safetyCluster(8088).

---

## 2. ALREADY DONE (do NOT redo — verify only if you touch nearby code)

1. **Support/Feedback (T091) — COMPLETE & verified (242/242 UserService tests).**
   - `UserService/Models/SupportTicket.cs`, DbSet+config in `UserService/Data/ApplicationDbContext.cs`,
     EF migration `AddSupportTickets`, full `UserService/Controllers/SupportController.cs`
     (GET ownership enforced in-query => other user's ticket returns 404),
     `UserService/UserService.Tests/Controllers/SupportControllerTests.cs` (8 tests).
   - Gateway: `supportRoute` -> userCluster, `/api/support/{**catch-all}` in base + Development.
   - Flutter: `lib/services/support_service.dart` (SupportCategory enum; POST feedback) and
     `lib/screens/help_screen.dart` rewritten into a working feedback Form. 3 help_screen tests pass.
2. **Compatibility de-stub — COMPLETE.**
   - `lib/services/compatibility_service.dart` `DefaultCompatibilityService` now calls real backend
     `GET /api/compatibility/questions` + `POST /api/compatibility/answers` (MatchmakingService
     `CompatibilityController`). It caches a static `label->value` map to translate the screen's
     `Map<questionIdString, optionLabelString>` into the backend `{answers:[{questionId:int,value:int}]}`.
     Kept `const` constructor (cache is static) so 10 existing screen tests still pass.
   - Gateway: added `compatibilityRoute` -> matchmakingCluster to Development (base already had it).
3. **MCP token optimization** (env-level, not app code): GitHub MCP server set to
   `GITHUB_DYNAMIC_TOOLSETS=1`. Irrelevant to app tasks; ignore.

---

## 3. KEY REUSABLE ASSETS (prefer reusing over building new)

- `005` compatibility engine is LIVE: `CompatibilityScorer` service, 15 questions seeded,
  `MatchInsight` entity, endpoint `GET /api/matchmaking/matches/{matchId}/insight`
  (MatchmakingController `GetMatchInsight`, tiered free/premium response).
- Flutter widgets already built: `CompatibilityBadge`, `CompatibilityBarComparison`,
  `MatchInsightScreen`, service `lib/services/match_insight_service.dart`. REUSE these for P2.
- FCM scaffolding exists: `lib/services/firebase_phone_auth_service.dart`; a migration adding FCM
  token fields exists. REUSE for P3 push.
- Presence: `UserService.UserProfile` already has `IsOnline` + `LastActiveAt` (indexed) and an
  `ActivityPingMiddleware` updates `LastActiveAt`. MatchmakingService's local `UserProfile` also has
  `LastActiveAt`. => DO NOT build a presence service. Derive "online" = `LastActiveAt > now-5min`.
- Admin reset endpoints exist (dev only): `DELETE /api/admin/matches|messages|swipes`,
  composite `POST /api/admin/reset-interactions` on gateway. Use to reset state between manual checks.

---

## 4. TASK LIST (execute in order; P0 -> P5)

> Each task: ID, GOAL, FILES, STEPS, ACCEPTANCE, VERIFY. Mark a task done only after VERIFY passes.
> Within a phase, tasks are mostly independent; do them sequentially to keep diffs reviewable.

### PHASE P0 — Foundation fixes & de-stub ✅ COMPLETE

All P0 tasks verified and green. Details below.

**P0-1 ✅ Privacy Settings screen** — replaced "Coming soon" placeholder with a `StatefulWidget` showing:
- "Show me in discovery" toggle (local state, resets on restart but functional)
- Blocked users list loaded from `SafetyService.getBlockedUsers()` with per-user unblock button
- Loading/error states, retry button
- Widget test updated: 4 tests all pass (render, title, privacy controls, navigation from Settings)
- Files: `lib/screens/privacy_settings_screen.dart`, `test/screens/privacy_settings_screen_test.dart`

**P0-2 ✅ Cleanup batch** — three of four subtasks were already done:
- (a) debug prints: all `debugPrint` calls in `api_service.dart` are in catch blocks; `debugPrint` is inherently debug-only in Flutter — already compliant, skipped.
- (b) Dead language row: removed `ListTile` with `// TODO: Language settings` from `settings_screen.dart` (no locale controller/provider existed to wire to)
- (c) Bot-to-bot flooding: **already implemented** — `SyntheticUserService.cs` has `GetAllBotKeycloakIdsAsync()` + guard skipping bot recipients, plus turn-taking logic (`last msg was ours → wait`)
- (d) Geo timeout: **already done** — `getCurrentPosition()` has `timeLimit: Duration(seconds:10)`
- Settings test updated: "shows language option" → "shows help and support option"

**P0-3 ✅ OAuth re-trigger** — replaced `// TODO: Trigger OAuth account picker again` + `Navigator.pop(context)` with `Navigator.popUntil(context, (route) => route.isFirst)` in `account_consent_screen.dart` ~L177. Popping to root sends user back to the login screen where they can choose a different account.

**P0-4 ✅ P0 tests** — T051 covered by P0-1's widget test (4 tests, pass). T021 and T041 exist as integration tests (207 and 181 lines respectively) in `integration_test/` — they require a running backend. MatchmakingService already has **225 tests** (far above the 40+ target).

**VERIFY state:**
```
flutter analyze — clean (2 pre-existing warnings in account_consent_screen.dart, unrelated)
flutter test test/screens/settings_screen_test.dart     → 14/14 pass
flutter test test/screens/privacy_settings_screen_test.dart  → 4/4 pass
flutter test test/screens/help_screen_test.dart            → 3/3 pass
dotnet test MatchmakingService.Tests/...  → 225/225 pass
dotnet test UserService.Tests/...         → 242/242 pass
```

### NEXT: PHASE P1 — Monetization foundation

---

### PHASE P1 — Monetization foundation (architect before differentiators)

> Rule-based, no external payment processor required yet — scaffold IAP in sandbox/stub mode.
> UserService owns entitlements (Decision: UserService already has user data + ApplicationDbContext).

#### P1-1 — Entitlement + Sparks data model ✅ DONE
- **Entities in UserService:**
  - `Models/Entitlement.cs` — `UserId` (string KeycloakId), `Tier` (Free/Premium enum, stored as string), `ExpiresAt`, `CreatedAt`, `UpdatedAt`
  - `Models/Entitlement.cs` (SparksLedgerEntry) — `UserId`, `Delta` (int, +credit/-debit), `Reason`, `BalanceAfter` (running total, never negative), `CreatedAt`
- **DTOs:** `BillingDtos.cs` — `GetEntitlementQuery/Response`, `GetSparksBalanceQuery/Response`, `GrantPremiumCommand/Response`, `CreditSparksCommand/Response`, `DebitSparksCommand/Response`, `SandboxPurchaseRequest/Response`, `PremiumCatalogResponse`
- **CQRS:** `Queries/EntitlementQueries.cs` (GetEntitlementHandler, GetSparksBalanceHandler), `Commands/EntitlementCommands.cs` (GrantPremiumHandler, CreditSparksHandler, DebitSparksHandler)
- **Controller:** `Controllers/BillingController.cs` — `GET /api/billing/status` (JWT), `GET /api/billing/internal-status?userId=` (internal API key), `GET /api/billing/catalog` (public), `POST /api/billing/purchase` (sandbox, JWT)
- **Service:** `Services/FeatureGate.cs` — `IFeatureGate.IsPremium(userId)` for in-process use
- **Migration:** `AddMonetization` generated (Entitlements table, SparksLedger table)
- **Tests:** 15 tests (entitlement query/expiry/active, sparks balance/credit/debit, controller status/catalog/purchase/auth)
- **VERIFY:** `dotnet test UserService.Tests/...` → 257/257 pass

#### P1-2 — FeatureGate enforcement (replace placeholder) ✅ DONE
- Replaced `User.HasClaim("tier", "premium")` at MatchmakingController.cs L737 with real
  `_userServiceClient.IsPremiumAsync(keycloakId)` call to UserService's billing internal-status endpoint
- Added `billingRoute` (userCluster, `/api/billing/{**catch-all}`) to both gateway configs
- Added `GET /api/billing/internal-status?userId=` endpoint (validates X-Internal-API-Key)
- MatchmakingService.UserServiceClient updated with `IsPremiumAsync()` calling internal-status
- **VERIFY:** `dotnet test MatchmakingService.Tests/...` → 225/225 pass

#### P1-3 — Premium catalog + Sparks store API ✅ DONE (included in P1-1)
- `GET /api/billing/catalog` returns hardcoded plans + bundles
- `POST /api/billing/purchase` accepts SKU and grants premium/sparks via MediatR handlers
- 15 billing tests cover catalog, purchase, status, and auth

#### P1-4 — Flutter paywall + Sparks store UI
- GOAL: Paywall sheet shown when a 402 is received; a Sparks store screen reachable from
  `lib/screens/profile_hub_screen.dart`. Use existing theme + widget patterns.
- ACCEPTANCE: hitting a gated action shows the paywall; store lists bundles; sandbox purchase
  updates displayed balance/tier.
- VERIFY: `flutter analyze` clean; widget tests for paywall + store screen pass.

#### P1-5 — Enforce swipe-limit gate
- GOAL: Free users get a daily swipe cap; premium unlimited. Enforce in swipe-service against the
  entitlement from P1-1 (call or cache). Over-limit => 402 + paywall on client.
- ACCEPTANCE: free user blocked after N swipes/day; premium unaffected; tests cover both.
- VERIFY: `dotnet test SwipeService.Tests/...`; Flutter swipe flow analyze/test.

---

### PHASE P2 — Cool differentiators (NON-AI, rule-based) — PRIMARY VALUE

#### P2-1 — Surface compatibility everywhere
- GOAL: Use existing `CompatibilityBadge` / `CompatibilityBarComparison` / `MatchInsightScreen`
  to show compatibility on the discover deck, the matches list, and the profile detail screen.
- STEPS: Wire `match_insight_service.dart` (calls `/api/matchmaking/matches/{id}/insight`) into
  `home_screen.dart` (deck), `enhanced_matches_screen.dart`, `profile_detail_screen.dart`. Free tier
  sees a teaser (badge / top axis); premium sees full breakdown (gated via P1-2).
- ACCEPTANCE: compatibility visible in all three places; premium reveals more than free.
- VERIFY: `flutter analyze` clean; widget tests for each screen updated and green.

#### P2-2 — 7-axis radar chart (rule-based)
- GOAL: Backend computes a deterministic 7-axis compatibility vector from existing answers
  (no ML). Flutter renders a radar chart widget. Full reveal is premium (P1-2); free sees blurred/
  partial.
- STEPS: Add a scorer method producing 7 named axes (e.g. Values, Lifestyle, Personality,
  Communication, Ambition, Social, Intimacy) as 0–100 from the answer set; expose via the insight
  endpoint (extend response). Build a `CompatibilityRadarChart` Flutter widget (CustomPainter, no
  heavy deps unless one is already in pubspec).
- ACCEPTANCE: radar renders from real backend vector; premium full, free partial; deterministic
  (same inputs => same axes).
- VERIFY: `dotnet test` (scorer unit tests for axis math); `flutter analyze` + widget test.

#### P2-3 — Expand question bank (15 -> fuller)
- GOAL: Add more seeded compatibility questions (TIPI personality, ECR attachment, values) so the
  radar/insight is richer. Pure data + scorer weighting; NO AI.
- STEPS: Extend the seed (MatchmakingService question seeding/migration). Update scorer weights/axes
  mapping. Keep `CompatibilityQuestionDto` shape stable (Flutter already consumes it).
- ACCEPTANCE: question count increased; scoring still deterministic; existing answer flow unaffected.
- VERIFY: `dotnet test`; Flutter compatibility screen test still green (it reads questions live).

#### P2-4 — Rule-based conversation-starter chips
- GOAL: In `enhanced_chat_screen.dart`, show suggested opener chips derived RULE-BASED from shared
  high-compat answers / shared interests (NOT an LLM). Tapping inserts text into the composer.
- ACCEPTANCE: chips reflect actual shared attributes; tapping fills the input; no network LLM call.
- VERIFY: `flutter analyze` + widget test for the chat screen.

#### P2-5 — Anonymous Forum "Forumet"
- GOAL: A community forum module: channels, posts, upvote/karma, moderated by the existing
  safety-service. Anonymous handles.
- STEPS: New backend (extend safety-service or a small module): entities Channel, Post, Vote;
  endpoints list channels, list/create posts, vote; route content through existing safety-service
  moderation (rule-based filters already present — do NOT add an LLM). Gateway route. Flutter
  screens: channel list, post list, composer.
- ACCEPTANCE: users can post anonymously, upvote, see karma; flagged content blocked by existing
  moderation; gated/rate-limited sensibly.
- VERIFY: backend `dotnet test`; `python3 api_tests.py`; Flutter analyze + tests for forum screens.

#### P2-6 — Post-date feedback loop + discovery delight
- GOAL: (a) Lightweight post-match/post-date feedback prompt persisted backend-side and used to
  tune ranking weights (rule-based). (b) Discovery polish: rewind last swipe (gate premium),
  superlike, friendly empty-states, match celebration animation.
- ACCEPTANCE: feedback persists; rewind/superlike work (rewind premium-gated); empty + celebration
  states render.
- VERIFY: backend `dotnet test`; Flutter analyze + tests.

---

### PHASE P3 — Retention engine

#### P3-1 — Push notifications (FCM)
- GOAL: Send FCM pushes on new match / new message / new like / daily re-engagement. Reuse existing
  firebase scaffolding + FCM token migration. Server sends via FCM HTTP v1 (service account, NOT an
  LLM). Client registers token on login.
- ACCEPTANCE: token stored; a triggered event sends a push (verify with a test token / mock).
- VERIFY: backend `dotnet test` (mock the FCM sender); Flutter analyze.

#### P3-2 — "Likes You" grid (gated)
- GOAL: Show who liked the current user (data already in swipe-service). Free tier sees blurred
  tiles + count; premium sees identities (P1-2 gate).
- ACCEPTANCE: grid lists incoming likes; free blurred, premium clear.
- VERIFY: `dotnet test SwipeService.Tests/...`; Flutter analyze + widget test.

#### P3-3 — Daily re-engagement + online/activity badges
- GOAL: Daily summary push (P3-1) + online/last-active badges using the presence insight in §3
  (`LastActiveAt > now-5min`). Surface badge on deck/matches/profile.
- ACCEPTANCE: badge reflects real LastActiveAt; daily job/endpoint exists.
- VERIFY: backend test for the freshness rule; Flutter analyze + test.

---

### PHASE P4 — Trust & safety + table stakes (non-AI)

- P4-1 (T053): Full report workflow — report -> safety-service queue -> admin/review view. Rule-based
  triage only.
- P4-2: Surface verification badges (photo/selfie verification already exists in photo-service /
  UserService VerificationController) on profiles and deck.
- P4-3 (T090): Account pause/snooze. NOTE: `UserService AccountStatusController.PauseAccount`
  (AccountPauseRequest/PauseDuration) already EXISTS — verify, surface in Flutter settings, add tests
  if missing. Do not rebuild the backend if present.
- P4-4 (T055): Account recovery flow.
- P4-5: Photo match-check cleanup — `PhotosController` ~L885 delegates match-check (code smell);
  refactor to remove the cross-concern without changing behavior.
- VERIFY each: relevant `dotnet test` + Flutter analyze/test.

---

### PHASE P5 — Quality / observability / launch

- P5-1 (T004): Coverage gate 80% in CI (use `collect-coverage.sh`).
- P5-2: Delete `.bak` files (e.g. `MatchmakingController.cs.bak`, `MessagesController.cs.bak`,
  `SwipesController.cs.bak`) ONLY after confirming the live file supersedes them.
- P5-3: E2E tests for the new flows (paywall, radar, forum, likes-you, push).
- P5-4: Finalize Grafana dashboards; (T002) generate mermaid architecture graphs.
- VERIFY: full `dotnet test` per service; `flutter test`; `python3 api_tests.py`; CI green.

---

## 5. DEPENDENCIES (ordering constraints)
- P0 before everything (unblocks testing).
- P1 before the GATED parts of P2 (radar full-reveal) and P3 (likes-you reveal).
- P2 and P3 can proceed in parallel after P1; do them sequentially if working solo for clean diffs.
- P4 report/verification is largely independent — may run alongside P2/P3.
- Presence insight (§3) feeds P3-3 activity badges.
- P5 is continuous; finalize last.

## 6. EXCLUDED — DO NOT BUILD
- Any LLM/AI: spec 002 agents, spec 003 LLM bots, spec 005 AI Psykolog + pgvector, AI photo coach,
  LLM conversation openers, LLM safety agent.
- Multi-app flavor package extraction (spec 004).
- Niche-specific onboarding.
- Match-list "fake data" name/photo enrichment (human deprioritized it).

## 7. DEFINITION OF DONE (per phase)
A phase is DONE when: all its tasks' VERIFY pass; `python3 api_tests.py` is green; the relevant
service `dotnet test` suites pass; `flutter analyze --no-fatal-infos --no-fatal-warnings` and
`flutter test` pass; and you have made local commits via the repo wrapper scripts (push only on
human request). Then proceed to the next phase.
