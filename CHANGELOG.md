# Changelog

All notable changes to the DatingApp MVP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (Features)
- Photo upload with 4-tier privacy system (Public, Private, MatchOnly, VIP)
- ML.NET content moderation for photos
- Matchmaking scoring algorithm with distance + interests + demographics
- Swipe recording with mutual match detection
- SignalR real-time messaging hub (basic)

### In Progress
- Keycloak OIDC integration (replacing legacy AuthService)
- Flutter onboarding wizard UI
- Message persistence layer

### Not Started
- Match notifications
- Reporting + blocking system
- Account recovery flows

---

## [0.14.9] - 2026-02-14

### Added 🚀 (Swipe Abuse Detection — Phase 14.9)
- SwipeBehaviorStats model with trust score tracking (SwipeService)
- SwipeBehaviorAnalyzer service — composite trust score formula (ratio/velocity/streak penalties)
- Real-time swipe velocity tracking integrated into RecordSwipeHandler
- Consecutive-like circuit breaker (30 likes → 15min cooldown)
- SwipeBehaviorRecalcService background job (6h periodic recalculation)
- BotDetectionHeuristics — 4-signal bot detection (clock regularity, 24/7 activity, monotonic patterns, device fingerprint)
- Internal SwipeBehaviorController (trust-score, report, recalc, batch, bot-check endpoints)
- Shadow restrict in MatchmakingService — trust score multiplier in candidate ranking
- 22 new unit tests (16 SwipeBehaviorAnalyzer + 6 BotDetection), all passing
- EF migration for SwipeBehaviorStats table

### Technical
- SwipeService: 60/60 tests passing (was 38)
- MatchmakingService: 81/81 tests passing
- Trust score formula: 100 - ratioPenalty - velocityPenalty - streakPenalty, clamped [0,100]
- Shadow restrict formula: finalScore *= (0.5 + trustScore/200)
- Graceful degradation: MatchmakingService defaults to trust=100 on HTTP failure

## [0.1.0-alpha] - 2026-01-24

### Added
- Initial project structure with 8 microservices
- UserService: Profile CRUD APIs
- MatchmakingService: Compatibility scoring
- swipe-service: Swipe recording + match detection
- photo-service: Enterprise photo privacy system
- messaging-service: SignalR hub infrastructure
- dejting-yarp: API gateway with YARP
- Keycloak: OIDC authentication server
- GitHub Projects automation (sync_mvp_project.sh)
- Auto-generated dashboard (DASHBOARD.md)
- Living documentation structure (docs/)

### Changed
- Migrated from legacy AuthService to Keycloak (in progress)
- Consolidated microservices into multi-repo structure

### Technical
- .NET 8 backend services
- Flutter 3.32.1 client
- Post

greSQL + MySQL databases (consolidation pending)
- Docker Compose orchestration

---

## Release Template

```markdown
## [X.X.X] - YYYY-MM-DD

### Added �� (User-Facing Features)
- New feature description

### Changed 🔄 (Breaking Changes)
- API endpoint changed from X to Y

### Fixed 🐛 (Bug Fixes)
- Fixed issue where...

### Deprecated ⚠️ (Will be Removed)
- Feature X is deprecated, use Y instead

### Removed ❌
- Removed legacy feature

### Security 🔒
- Fixed vulnerability in...
```

---

*Keep this updated after every release!*
