# Implementation Plan: DatingApp MVP Foundation

**Branch**: `001-mvp-foundation` | **Date**: 2025-10-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mvp-foundation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Deliver a production-ready MVP that covers the first-time profile journey, daily match discovery, real-time messaging, and foundational safety controls. We will harden the existing .NET microservices and Flutter client, enforce privacy workflows, and provide scripted demo coverage so stakeholders can validate the full loop end-to-end. Registration and verification now flow entirely through Keycloak; the legacy AuthService remains only as retired scaffolding until we remove it post-MVP.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: .NET 8 (backend services), Flutter 3.32.1 + Dart 3.5 (client), Python 3.12 (tooling)  
**Primary Dependencies**: ASP.NET Core, Entity Framework Core 8, SignalR, Keycloak OIDC (primary auth), ImageSharp, ML.NET, Flutter core libs, Riverpod-lite state helpers  
**Storage**: PostgreSQL (primary), Redis (optional cache if needed), Azure blob-compatible storage (local filesystem for dev), Keycloak DB  
**Testing**: xUnit + FluentAssertions, integration tests via docker-compose, Flutter integration_test, Python API harness (`api_tests.py`)  
**Target Platform**: Linux containers for services, Android/iOS/Web for Flutter client  
**Project Type**: Multi-service backend + Flutter client  
**Performance Goals**: P95 API latency ≤350ms, SignalR delivery ≤1s, photo processing <10s per batch  
**Constraints**: Offline-aware client caching, <2MB photo limit, limit new infra dependencies, reuse existing docker-compose  
**Scale/Scope**: Initial launch cohort 5k users, concurrent demo load 500, 6 primary screens + admin tooling TBD

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance Status | Notes |
|-----------|-------------------|-------|
| Trust & Safety First | ✅ Planned ML moderation, privacy controls, audit logging | Ensure report workflow ties into moderation notifications |
| MVP Scope Discipline | ✅ Focused on onboarding, matching, messaging, safety | Defer advanced personalization, premium upsells |
| Evidence-Backed Delivery | ⚠️ Pending | Legacy signup-to-match automation validated via TestDataGenerator; T029 will deliver Keycloak-first replacement before MVP ship; messaging loop coverage still outstanding |
| Cohesive Experience | ✅ Shared DTO definitions through Contracts folder & YARP gateway tests | Maintain compatibility matrix with Flutter models |
| Operability & Observability | ⚠️ Pending | Must add structured logging + health probes for new endpoints |

Mitigations: incorporate test automation tasks (Phase 2) and logging enhancements in each service change.

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
AuthService/ *(legacy shell; Keycloak handles auth after Oct 22 2025 migration)*
MatchmakingService/
MessagingService/
photo-service/
swipe-service/
UserService/
YARP gateway: dejting-yarp/
Flutter app: mobile-apps/flutter/dejtingapp/
Infrastructure scripts: infrastructure/, dev-start.sh, dev-stop.sh
Shared tooling: scripts/, TestDataGenerator/, api_tests.py
Specs: specs/001-mvp-foundation/
```

**Structure Decision**: Retain existing multi-service layout. Specs live in `specs/001-mvp-foundation`. Backend services updated in place; no new projects. Flutter app receives new feature modules under `lib/`. Shared contracts documented in `specs/001-mvp-foundation/contracts/` and enforced via YARP + DTO updates.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | | |

