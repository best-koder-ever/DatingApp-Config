# DatingApp - Modern Dating Platform

[![Auto Tests](https://github.com/best-koder-ever/DatingApp-Config/actions/workflows/auto-test.yml/badge.svg)](https://github.com/best-koder-ever/DatingApp-Config/actions/workflows/auto-test.yml)
[![Comprehensive CI/CD](https://github.com/best-koder-ever/DatingApp-Config/actions/workflows/comprehensive-ci-cd.yml/badge.svg)](https://github.com/best-koder-ever/DatingApp-Config/actions/workflows/comprehensive-ci-cd.yml)

Modern microservices-based dating platform with .NET 8 backend and Flutter frontend.

**Auto-Testing**: Tests run automatically on every push + every 6 hours  
**Monitoring**: [View Dashboard](http://localhost:3000) • Run `./start-monitoring.sh`

## Architecture

### Backend Services
- **UserService** - User profile management, preferences, bio
- **MatchmakingService** - ML-powered candidate scoring & matching
- **SwipeService** - Swipe processing, match verification
- **PhotoService** - Photo storage, moderation, privacy enforcement
- **MessagingService** - Real-time messaging via SignalR
- **dejting-yarp** - API Gateway (YARP reverse proxy)

### Frontend
- **Flutter App** - Cross-platform mobile (iOS/Android) + web client

### Infrastructure
- **Keycloak** - OIDC authentication (port 9090)
- **MySQL 8.0** - All service databases
- **Seq** - Structured logging (port 5380)
- **Grafana** - Metrics & dashboards (port 3030)

## Visual QA

The project includes a browser-based visual QA environment powered by an Android emulator with a built-in noVNC web viewer.

### Start the Visual QA environment

```bash
# Start Android emulator + noVNC web viewer
make visual-qa-up
```

### Access the VNC viewer

Open your browser and navigate to:

```
http://localhost:6080
```

No VNC client is required — the noVNC viewer runs entirely in the browser.
The emulator may take ~2 minutes to fully boot on first launch.

### Generate a screenshot gallery

After running visual QA tests, generate a static HTML gallery that shows
captured screenshots, baselines, and diff overlays side-by-side:

```bash
make visual-qa-gallery
# → visual-qa/reports/gallery.html
```

The gallery is grouped by use-case and shows pass/fail badges for each test.
You can also browse it via the gallery server at `http://localhost:8099/gallery.html`
(served by the `gallery-server` container when `make visual-qa-up` is running).

### Stop the Visual QA environment

```bash
make visual-qa-down
```

### Directory layout

```
visual-qa/
├── docker-compose.visual-qa.yml   # Android emulator + noVNC compose
├── gallery.py                     # Gallery generator script
├── screenshots/                   # Captured test screenshots (by use-case)
├── baselines/                     # Baseline images          (by use-case)
└── reports/                       # Generated gallery HTML
```

## Quick Start

```bash
# Start infrastructure (Keycloak, MySQL, Seq, Grafana)
./infrastructure/start.sh

# Start all backend services
./dev-start.sh

# Run backend API tests
python3 api_tests.py

# Run Flutter app (development)
cd /home/m/development/mobile-apps/flutter/dejtingapp
flutter run -d chrome
```

**Detailed setup:** See [specs/001-mvp-foundation/quickstart.md](specs/001-mvp-foundation/quickstart.md)

## Development

### Technologies
- .NET 8 + ASP.NET Core + Entity Framework Core 8
- SignalR (real-time messaging)
- Keycloak OIDC (authentication)
- ImageSharp (photo processing)
- ML.NET (matchmaking scoring)
- Flutter 3.32.1 + Dart 3.5 (client)
- MySQL 8.0 (Pomelo EF Core provider)
- Python 3.12 (tooling & API tests)

### Code Style
- Follow .NET 8 conventions with analyzers enabled
- Flutter: `analysis_options.yaml` (pedantic + lint)
- Python: `ruff` defaults

### Multi-Repo Workflow
This project uses 8+ Git repositories. **Always use helper scripts:**
- **Commits/pushes:** `./gita-workflow.sh` or `./ai-commit-helper.sh`
- **GitHub operations:** `./gh-multi-repo.sh`

**Never manually iterate repos** - scripts exist to automate this.

## CI/CD

CI/CD pipeline runs on every push to `main`/`develop` branches:

- .NET unit tests (all services)
- Flutter unit & integration tests
- Service builds (Docker images)
- Security scanning (dependency checks)
- ~~Integration tests~~ (deferred pending service-to-service auth)
- ~~E2E tests~~ (deferred pending Flutter stabilization)

**Workflow:** [.github/workflows/comprehensive-ci-cd.yml](.github/workflows/comprehensive-ci-cd.yml)

## Project Status

**Current Focus:** Backend Solidification - Week 1 (001-mvp-foundation)

Recent completions:
- ✅ T052: PhotoService privacy enforcement (match verification)
- ✅ T007: Database consolidation (MySQL 8.0 standardization)
- ✅ T008: Remove AuthService (Keycloak sole auth)
- ✅ T065: Remove TestDataGenerator (api_tests.py automation)
- 🔨 T004: CI/CD green builds (in progress)

**Next priorities:**
- T004: Enable CI/CD green builds with coverage gates
- Service-to-service authentication (internal API keys)
- Performance & observability improvements
- Launch prep (Week 3)

**Roadmap:** See [specs/001-mvp-foundation/tasks.md](specs/001-mvp-foundation/tasks.md)

## Documentation

- **Quickstart:** [specs/001-mvp-foundation/quickstart.md](specs/001-mvp-foundation/quickstart.md)
- **Architecture:** [specs/001-mvp-foundation/guide.md](specs/001-mvp-foundation/guide.md)
- **Tasks:** [specs/001-mvp-foundation/tasks.md](specs/001-mvp-foundation/tasks.md)
- **API Contracts:** [specs/001-mvp-foundation/contracts/](specs/001-mvp-foundation/contracts/)
- **AI Collaboration:** [AI_COLLABORATION_GUIDE.md](AI_COLLABORATION_GUIDE.md)

## License

Proprietary - All rights reserved
