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
