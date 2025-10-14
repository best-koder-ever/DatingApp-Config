# Space Context Snapshot (2025-10-10)

Use this snippet as a drop-in context block when opening a GitHub Space thread for DatingApp.

## Current Focus
- All backend services migrated to Keycloak authentication; RSA key files removed.
- PostgreSQL live for PhotoService; other services still on in-memory stores pending migration.
- Flutter client uses AppState-based session persistence and awaits multi-photo upload improvements.

## Active Priorities
1. Finish PostgreSQL migration for AuthService, UserService, MatchmakingService, MessagingService, SwipeService.
2. Validate photo grid flow end-to-end (multi-upload, blurred image variants, 404 fixes).
3. Introduce background processing (Hangfire/RabbitMQ) for photo moderation + matchmaking events.
4. Plan production infra upgrades (cloud storage, CDN, monitoring).

## Useful Paths
- `AI_CONTEXT.md` – master architecture + migration record.
- `API_DOCUMENTATION.md` – REST endpoints reference.
- `PhotoService/Program.cs` – Keycloak auth + PostgreSQL wiring.
- `Flutter/dejtingapp/lib/services/*.dart` – client integrations.

Drag this file into a Space thread or paste the sections you need so Copilot has the latest project state instantly.
