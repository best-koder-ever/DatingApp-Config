# DatingApp MVP Constitution

## Core Principles

### I. Trust & Safety First
Protect user privacy, consent, and safety in every interaction; align security, moderation, and access controls with Keycloak-authenticated sessions.

### II. MVP Scope Discipline
Ship only the critical matching, messaging, and photo flows needed for the first market launch; defer advanced personalization or automation until post-MVP.

### III. Evidence-Backed Delivery
Every change must include automated verification (unit, integration, or scripted demo) and be reproducible via `dev-start.sh` plus published test scripts.

### IV. Cohesive Experience
All surface areas (API Gateway, services, Flutter client) must expose consistent DTOs, error codes, and latency budgets to keep the experience smooth on mid-tier devices.

### V. Operability & Observability
Logs, health checks, and config must support 24/7 monitoring; any new component needs structured logging and readiness probes before it routes real traffic.

## Delivery Guardrails
- Backend remains .NET 8 with PostgreSQL, Redis optional only if justified with load data.
- Flutter web/mobile client must function offline-aware for core profile viewing and retry uploads automatically.
- No new infrastructure dependencies beyond existing docker-compose unless approved in writing within the spec.
- Performance targets: P95 API < 350ms, image uploads < 2MB, SignalR message fan-out < 1s.

## Workflow Expectations
1. Start every initiative with `/speckit.specify`, `/speckit.plan`, `/speckit.tasks` artifacts stored under `specs/<feature>/`.
2. Use `create-new-feature.sh` to branch and track features; keep specs updated as implementation evolves.
3. PRs must reference the spec tasks and include demo evidence (logs, screenshots, or test output).
4. Weekly review ensures constitution alignment; unresolved violations block release candidates.

## Governance
The constitution guides all MVP decisions. Amendments require consensus from product lead + tech lead, documented in `AI_CONTEXT.md` changelog and version bump below.

**Version**: 1.0.0 | **Ratified**: 2025-10-20 | **Last Amended**: 2025-10-20
