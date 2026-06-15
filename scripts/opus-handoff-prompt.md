# DatingApp — Claude Model Handoff Prompt

> **Copy-paste this into a new chat when switching to a different model (e.g. Opus 4.6).**

## Project Overview

**DatingApp**: Multi-service .NET 8 dating platform with Flutter 3.32.1 mobile client.
Workspace root: `/home/m/development/DatingApp`
Instructions: `.github/copilot-instructions.md` (comprehensive — read it first)

### Services (all localhost)
| Port | Service | DB |
|------|---------|-----|
| 8080 | dejting-yarp (YARP gateway) | — |
| 8082 | UserService | MySQL :3310 UserServiceDb |
| 8083 | MatchmakingService | MySQL :3309 MatchmakingDb |
| 8085 | photo-service | MySQL :3310 PhotoServiceDb |
| 8086 | messaging-service (SignalR) | MySQL :3310 MessagingServiceDb |
| 8087 | swipe-service | MySQL :3310 SwipeServiceDb |
| 8088 | safety-service | — |
| 8089 | bot-service | SQLite |
| 8090 | Keycloak | Docker |
| 9100 | Dev Dashboard (NiceGUI) | — |

### What's Shipped
- ✅ Spec 005: Compatibility Engine + Match Insight UI (tagged `mvp-005-insight-v1`)
- ✅ Feedback FAB with Whisper transcription pipeline (tagged `mvp-tester-v0.2`)
- ✅ Tester APK via Tailscale Funnel (`https://fastdev.tail45c6a7.ts.net`)
- ✅ Keycloak tunnel hostname fix for OAuth issuer
- ✅ Swipe contract fix (TargetUserId changed from int → string)

### Current Task: AI & Costs Dashboard Panel
We just added a new **"AI & Costs"** tab to the NiceGUI dev dashboard (`dev_dashboard.py`) with:
- **Prompt cache controls**: Test Cache, Warm Cache (loads `copilot-instructions.md` into ephemeral cache)
- **Batch job management**: Submit/Check/Fetch batch jobs via Anthropic Batch API
- **Token cost calculator**: Compares Regular / Batch / Cache / Batch+Cache pricing
- **Model selector**: Claude Sonnet 4, 3.5 Sonnet, 3.5 Haiku
- Batch IDs persisted to `.ai-last-batch-id` for cross-session retrieval
- Results saved to `logs/batch-result-*.jsonl`

### Key Gotchas
- **SwipeRequest.TargetUserId** is `string`, not `int` (recent fix)
- **Keycloak hostname**: Must match Tailscale Funnel URL for tunnel token validation
- **Bot demo-user**: Same identity as Flutter dev login; keep paused to avoid message loops
- **Photo auth**: All image requests need `Authorization: Bearer <token>` header
- **ConversationId**: REST = alphabetically-sorted keycloak IDs joined by `_`; SignalR hub = matchId
- **Git discipline**: 8+ repos — use `gita-workflow.sh`; batch all `gh` API calls

### Commands
```bash
./infrastructure/start.sh          # Keycloak + DBs
./dev-start.sh                     # All backend services
./dashboard-start.sh               # NiceGUI dashboard at :9100
python3 api_tests.py               # Smoke tests
cd mobile-apps/flutter/dejtingapp && flutter test
```

### Architecture Patterns
- All services: EF Core 8 + MySQL, CQRS via MediatR, InMemoryDatabase + Moq for tests
- Auth: Keycloak OIDC → JWT; YARP validates tokens and routes
- All new code must have unit tests
