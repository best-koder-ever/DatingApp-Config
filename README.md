# DatingApp Platform

A production-style, microservices dating platform built with .NET 8 backend services and a Flutter client.

This repository is the platform orchestration and configuration hub. It ties together service repos, local infrastructure, scripts, and integration flows.

## Why This Repo Exists

This is the control plane for local/dev environments and cross-repo workflows.

It contains:
- Local infrastructure startup and shutdown scripts
- Platform-level test orchestration
- Development automation and quality scripts
- High-level architecture, specs, and docs

It does **not** contain all feature code for every service. Core implementation lives in the service-specific repositories listed below.

## Repository Map

Core repos in this platform:

- `best-koder-org/mobile_dejtingapp` - Flutter app (mobile/web client)
- `best-koder-org/UserService` - Profiles, onboarding state, preferences
- `best-koder-org/MatchmakingService` - Candidate scoring and match logic
- `best-koder-org/swipe-service` - Swipe ingestion and behavior analytics
- `best-koder-org/messaging-service` - SignalR + REST messaging stack
- `best-koder-org/photo-service` - Media storage, image processing, moderation
- `best-koder-org/dejting-yarp` - API gateway and traffic/routing policies
- `best-koder-org/DatingAppController` - Multi-repo automation/orchestration
- `best-koder-ever/DatingApp-Config` (this repo)

## Architecture Snapshot

### Backend Services
- UserService
- MatchmakingService
- swipe-service
- messaging-service
- photo-service
- dejting-yarp (gateway)
- safety-service
- bot-service

### Client
- Flutter 3.32.1 + Dart 3.5

### Infrastructure
- Keycloak (OIDC)
- MySQL
- YARP gateway
- Python-based smoke tests

## Quick Start

```bash
# 1) Start shared infrastructure (Keycloak + DB)
./infrastructure/start.sh

# 2) Start backend services
./dev-start.sh

# 3) Run API smoke tests
python3 api_tests.py

# 4) Stop everything
./dev-stop.sh
./infrastructure/stop.sh
```

## Platform Validation

```bash
python3 api_tests.py
```

What this validates:
- Auth/login flows
- Profile and onboarding API paths
- Match and swipe API behavior
- Messaging API basics

## Multi-Repo Workflow

This platform is intentionally multi-repo. Use provided helpers instead of manual loops:

```bash
# Commit/push helper for many repos
./gita-workflow.sh

# Multi-repo GitHub operations
./gh-multi-repo.sh
```

## Tech Stack

- .NET 8 / ASP.NET Core
- EF Core 8 + MySQL
- SignalR
- Flutter (mobile + web)
- Keycloak OIDC
- Python 3.12 tooling

## For Recruiters / Hiring Managers

Start here, then inspect these repos for deeper examples:

1. `best-koder-org/mobile_dejtingapp` (frontend architecture + testable services)
2. `best-koder-org/MatchmakingService` (domain logic and scoring)
3. `best-koder-org/dejting-yarp` (gateway architecture)
4. `best-koder-org/messaging-service` (real-time systems)

Each repo includes a dedicated README with architecture and run/test instructions.

## License

Proprietary unless stated otherwise.
