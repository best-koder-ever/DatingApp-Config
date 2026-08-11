# 004 — Multi-App Architecture Foundation

## One-Liner
Extract shared Flutter packages and add per-flavor backend config so a second app can launch without duplicating code.

## In Scope
- Extract `packages/mobile_core/` (auth, API, models, JWT, env config)
- Extract `packages/mobile_ui_kit/` (shared widgets, theme base)
- Migrate `dejtingapp/` imports to use packages
- Document API classification (platform vs. product-specific)
- Add `Flavors:{flavorId}:*` config sections to backend services
- Separate Flutter build targets with distinct applicationId per flavor

## Out of Scope
- Building app #2 (that's spec 005+)
- Push notifications, geolocation, advanced security hardening
- App store listing preparation
- Repo-split (mono-repo → multi-repo) — deferred pending scale
- Any extraction of discovery, onboarding wizard, or matchmaking UI into shared code (Rule of 2)

## Depends On
- ✅ 001-mvp-foundation (core services, auth, profiles, matching, messaging)
- ✅ Flavor system (FlavorConfig, entry points, FlavorId backend column)
- ✅ Feature flags wired into UI screens

## Key Decisions
- **Rule of 2**: only extract when 2+ apps need it
- **Ports & Adapters**: packages expose interfaces, apps provide implementations
- **Config over code**: flavor diffs in FlavorConfig (client) + appsettings (server)
- **FR-008 TBD**: cross-app matching isolation policy needs user input
