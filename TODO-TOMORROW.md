# TODO — Current State

**Updated**: 2026-06-29
**Active track**: Premium Settings Section + Read Receipts

---

## ✅ COMPLETED (2026-06-25 session)

### Reputation Service (new microservice :8091)
- [x] Service scaffolded: .NET 8 + EF Core + MySQL + MediatR
- [x] ChatFeedback entity, ReputationScore entity, ReputationCalculator
- [x] Penalty caps, signal weighting, new account cooling, bot exclusion
- [x] JWT validation + rate limiting + internal API endpoints
- [x] Full admin control + ReputationAuditLog
- [x] 4 unit tests

### Phase 8-9: MatchmakingService Integration + Cross-Service Hooks
- [x] ReputationScoreCache + LiveScoringStrategy rep factor
- [x] safety-service → reputation on block/report
- [x] GhostDetectionService (runs every 6h) + 5 tests

### T630-T631: Radar Confidence + Before/After Comparison
- [x] 4-tier opacity in RadarChartWidget (gold at 95%+)
- [x] PreviousValuesJson on backend + grey overlay polygon in Flutter

### T623/T625: Post-Date Feedback Flutter (wired)
- [x] "Betygsätt er dejt" button in chat overflow menu

### T633: Psykolog Axis-Based Suggestions
- [x] WeakestAxesJson on PsykologSession, fetched from radar API
- [x] Dynamic system prompt with axis-specific suggestions

### Top Picks Backend Endpoint
- [x] `GET /api/matchmaking/top-picks/{userId}` — uses DailyPickStrategy
- [x] Flutter TopPicksScreen wired to real endpoint (mock fallback)

### Real Prices in Catalog
- [x] Backend: Premium plans now cost sparks (149/299/599 ⚡)
- [x] Backend: Spark bundles have real USD cent prices (.99-4.99)
- [x] Swedish names: Premium Månad, Kvartal, År
- [x] Flutter: PremiumPlan model gains priceSparks field
- [x] Flutter: Plan cards show spark price inline
- [x] Flutter: SEK conversion for spark bundles (19-149 kr)
- [x] Builds clean, analyze clean### AI Tester Service (new microservice :8093)
- [x] Service scaffolded: .NET 8 + SQLite + OWASP security probes
- [x] SecurityAuditor: SQLi, JWT manipulation, IDOR, rate limit, XSS, mass assignment checks
- [x] TestPersona model: NormalUser, Troll, Hacker, Scammer types
- [x] TestFinding model: severity, category, attack vector, evidence, reproducibility
- [x] TestRun model: phase tracking, findings aggregation
- [x] API: POST /api/tester/run, GET /api/tester/findings, GET /api/tester/report/daily
- [x] Admin-only access (Role=admin required)
- [x] Findings are READ-ONLY — human must accept/reject before any code change
- [x] Docker + YARP route configured
- [x] Builds clean — 0 errors, 0 warnings### Simple Forum (Jodel-inspired)
- [x] Backend: ForumPost + ForumComment models in UserService
- [x] Backend: GET/POST /api/forum/posts, GET/POST /api/forum/posts/{id}/comments
- [x] Backend: Anonymous posting option (IsAnonymous flag)
- [x] Flutter: forum_feed_screen.dart — single feed, posts + expandable comments
- [x] Flutter: Create post FAB + bottom sheet with anonymous toggle
- [x] Flutter: Comment input inline on expanded posts
- [x] Flutter analyze — 0 issues
- [x] UserService: 305/305 tests pass### Premium Settings + Read Receipts (2026-06-29)
- [x] Backend: `ReadReceiptsEnabled` field on UserProfile + PrivacySettingsDto
- [x] Backend: `PUT /api/userprofiles/{id}/privacy` handles read receipts
- [x] Flutter: `PremiumFeatureTile` widget — lock icon + gold badge for free users
- [x] Flutter: `PremiumUpgradeBanner` — gradient CTA for free users
- [x] Flutter: Settings screen reorganized — "Premium-funktioner" card with diamond icon
- [x] Flutter: Upgrade prompt dialog — lists premium benefits + navigates to plans
- [x] Flutter analyze — 0 errors
- [x] UserService: 305/305 tests pass

### Tests- [x] messaging-service: 147/147 | reputation-service: 4/4
- [x] UserService: 305/305 | MatchmakingService: 266 (1 pre-existing)
- [x] Flutter analyze — 0 issues across all changed files
- [x] All 6 microservices build clean

---

## 📋 Remaining Polish (Minor/Deferred)

- [x] Real prices in catalog ✅
- [x] Premium comparison screen with feature table ✅
- [ ] Push notifications for received sparks (needs FCM)
- [x] Spotlight scheduling screen with date/time/duration picker ✅
- [x] Read receipts toggle ✅
- [ ] Video clips

## 🔲 Next Available Tasks

| Task | Priority | Est. | Notes |
|------|----------|------|-------|
| T634: Forum-to-axis mapping | P2 | ~3h | Needs forum existing |
| Bot swarm T382-T384 (multi-lang, voice, admin UI) | P3 | ~15h | |
| Forum Phases 10-11 | P2 | ~41h | "Wait with forum" |
| Spotlight Scheduling | P3 | ~4h | Date/time picker |
| Read receipts toggle | P3 | ~2h | |

---

## Stability

| Service | Tests | Status |
|---------|-------|--------|
| messaging-service | 147/147 | ✅ |
| reputation-service | 4/4 | ✅ |
| UserService | 305/305 | ✅ |
| MatchmakingService | 266 (1 pre-existing) | ✅ |
| Flutter | 0 errors | ✅ |
