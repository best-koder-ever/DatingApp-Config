# DatingApp Development Guidelines

**⚠️ BEFORE DOING ANYTHING: Check [RUNBOOK.md](../RUNBOOK.md) for operational commands and workflows**

Auto-generated from Spec Kit feature plans. Last updated: 2025-10-20

## Active Technologies
- .NET 8 + ASP.NET Core + Entity Framework Core 8 (backend services)
- SignalR, Keycloak OIDC, ImageSharp, ML.NET, OpenCvSharp (real-time & media)
- Flutter 3.32.1 + Dart 3.5 (web + mobile client)
- Python 3.12 (tooling, API smoke tests)

## Project Structure
```
AuthService/                 # Authentication, JWT issuance
UserService/                 # Profile management & photo metadata
MatchmakingService/          # Candidate scoring, swipe processing
messaging-service/           # SignalR messaging hub
photo-service/               # Photo storage, moderation, privacy pipeline
swipe-service/               # Swipe ingestion + matchmaking hooks
dejting-yarp/                # YARP gateway, routing config
mobile-apps/flutter/dejtingapp/  # Flutter client
specs/001-mvp-foundation/    # Spec Kit artifacts for current MVP feature
infrastructure/, dev-*.sh    # Environment and orchestration scripts
TestDataGenerator/, api_tests.py  # Legacy demo seeding (avoid new usage); rely on Keycloak-first automation instead
```

## Commands
- `./infrastructure/start.sh` → start Keycloak + shared databases
- `./dev-start.sh` → run services (TestDataGenerator no longer auto-started; replace with Keycloak automation when ready)
- `python3 api_tests.py` → verify auth/profile/match/messaging APIs
- `cd mobile-apps/flutter/dejtingapp && flutter test integration_test/visual_photo_upload_test.dart`
- `./dev-stop.sh` and `./infrastructure/stop.sh` → clean shutdown

## Code Style
- Follow .NET 8 conventions with analyzers enabled per service
- Flutter uses `analysis_options.yaml` (pedantic + lint) and Riverpod-lite patterns
- Python tooling adheres to `ruff` defaults when run locally (`ruff check .`)

## Recent Changes
- 001-mvp-foundation: Captured MVP constitution, user stories, implementation plan, and API/message contracts

<!-- MANUAL ADDITIONS START -->

## Multi-Repo Workflow (CRITICAL - READ FIRST!)
**This project has 8+ Git repositories.** Use these tools, don't manually iterate:
- **For commits/pushes:** `./gita-workflow.sh` or `./ai-commit-helper.sh`
- **For GitHub operations:** `./gh-multi-repo.sh`
- **Never:** Loop through repos with manual `cd repo && git commit && cd ..` patterns

Why: User set up gita and helper scripts specifically to avoid tedious manual operations. Always check for and use these tools first.

<!-- MANUAL ADDITIONS END -->
