# Feature Specification: Multi-App Architecture Foundation

**Feature Branch**: `004-multi-app-architecture`  
**Created**: 2026-03-26  
**Status**: Draft  
**Input**: Extract shared platform from monolithic DatingApp so that a second app can reuse backend services and Flutter UI primitives without code duplication.

## Context — What Already Exists

The DatingApp has a **flavor system** that was built in the prior phase:

### Flutter (client)
- `FlavorConfig` abstract class with `featureFlags`, `copy`, `theme`, `flavorId`
- `HingeFlavorConfig` (serious dating) and `FleetFlavorConfig` (casual/social)
- `FlavorFeatureFlags`: `dailySwipeLimit`, `showCompatibilityScores`, `prominentVoicePrompts`, `showProfilePrompts`, `photoForwardDiscovery`
- `FlavorCopy`: welcome/discover text per flavor
- Entry points: `main_hinge.dart`, `main_fleet.dart`
- Feature flags are wired into 4 UI screens (home, profile_detail, welcome, profile_card)

### Backend (.NET 8)
- `FlavorId` column on `UserProfile` in UserService + MatchmakingService (with migration)
- 10% same-flavor scoring boost in `LiveScoringStrategy`
- All services share Keycloak OIDC, MySQL, SignalR infrastructure

### Gap
The current code is a **single Flutter project** (`dejtingapp/`) and a **single deployment** of 8 backend services. To launch app #2, we need:
1. Shared Flutter packages that both apps import
2. Clear API boundaries between platform-generic and product-specific behavior
3. Separate build targets and app identities

---

## User Scenarios & Testing

### User Story 1 — Extract Shared Flutter Packages (Priority: P1)

As a developer maintaining two dating apps, I can import `mobile_core` and `mobile_ui_kit` packages into a new app so that auth, API client, theme base, and common widgets are reused without copy-paste.

**Why this priority**: Without package extraction, any new app must duplicate auth, API, models, and shared widgets — creating immediate maintenance debt.

**Independent Test**: Create a minimal `app_two/` Flutter project that depends on `packages/mobile_core/` and `packages/mobile_ui_kit/`. Verify it compiles, can authenticate with Keycloak, and renders the `AuthenticatedAvatar` widget.

**Acceptance Scenarios**:

1. **Given** the extracted `packages/mobile_core/` package, **When** a new Flutter app adds it as a path dependency, **Then** the app can call `AuthService`, `ApiService`, and access all shared models without importing from `dejtingapp/lib/`.
2. **Given** the extracted `packages/mobile_ui_kit/` package, **When** a new Flutter app imports it, **Then** it can use `AuthenticatedAvatar`, `ConnectivityBanner`, `ErrorBoundary`, and `SkeletonLoaders` widgets.
3. **Given** the existing `dejtingapp/` app, **When** its imports are updated to reference packages instead of local paths, **Then** `flutter analyze` passes and all 659+ tests remain green.
4. **Given** both packages, **When** analyzed independently (`cd packages/mobile_core && flutter analyze`), **Then** zero errors and no imports from any app's `lib/`.

---

### User Story 2 — Backend API Classification (Priority: P2)

As a developer, I can consult a clear document classifying every backend API endpoint as "platform" (shared) or "product" (app-specific) so that I know which services app #2 can use as-is and which need flavor-specific configuration.

**Why this priority**: Backend services already work for one app. Before building app #2, the team needs clarity on what's shared vs. what needs per-flavor configuration.

**Independent Test**: Review the classification document against actual controller endpoints. Verify each endpoint is categorized and the reasoning is sound.

**Acceptance Scenarios**:

1. **Given** the `api-classification.md` document, **When** a developer reads it, **Then** every controller endpoint across all 8 services is categorized as platform-generic or product-specific.
2. **Given** endpoints marked product-specific, **When** they are examined, **Then** each has a note explaining what varies per flavor (e.g., scoring weights, swipe limits, copy text).
3. **Given** the FlavorId routing strategy, **When** the document describes isolation policy, **Then** it states whether flavors are hard-isolated (no cross-matching) or soft-preferenced (boost same, allow cross).

---

### User Story 3 — Per-Flavor Backend Configuration (Priority: P2)

As a backend developer, I can configure per-flavor values (swipe limits, scoring weights, feature toggles) via `appsettings.json` so that behavior differences live in config, not code.

**Why this priority**: Currently `dailySwipeLimit` is client-side only. Backend needs flavor-aware config so that the server enforces limits per flavor and new flavors can be added without code changes.

**Independent Test**: Set `Flavors:fleet:DailySwipeLimit = 0` and `Flavors:hinge:DailySwipeLimit = 10` in appsettings. Verify swipe-service reads and enforces the correct limit based on the user's FlavorId.

**Acceptance Scenarios**:

1. **Given** a `Flavors:{flavorId}:DailySwipeLimit` config section, **When** swipe-service receives a swipe from a user with FlavorId="hinge", **Then** it enforces the hinge-specific limit.
2. **Given** a new flavor "fleet" added to config, **When** services start, **Then** they read fleet-specific values without any code changes.
3. **Given** the MatchmakingService, **When** an admin configures `Flavors:fleet:SameFlavorBoost = 0.15`, **Then** the scoring strategy uses 15% boost for fleet-to-fleet matches instead of the hardcoded 10%.

---

### User Story 4 — Separate Build Targets (Priority: P3)

As a developer, I can build and sign app #1 and app #2 as completely separate APKs/IPAs with different application IDs, names, and icons.

**Why this priority**: Needed for app store submission but not for early development. Can use flavor entry points locally until CI/release pipeline is built.

**Independent Test**: Run `flutter build apk --target lib/main_hinge.dart` and `flutter build apk --target lib/main_fleet.dart`. Verify the outputs have different `applicationId`, app name, and launcher icon.

**Acceptance Scenarios**:

1. **Given** `main_hinge.dart` target, **When** built for Android, **Then** the APK has `applicationId = com.example.dejting` and the "Dejting" app name.
2. **Given** `main_fleet.dart` target, **When** built for Android, **Then** the APK has `applicationId = com.example.fleet` and the "Fleet" app name.
3. **Given** both build targets, **When** installed on same device, **Then** they coexist as separate apps.

---

### Edge Cases

- What if a user switches between apps with the same Keycloak identity? — Each app writes its own FlavorId to the user profile; the most recent one wins.
- What if a shared package needs a feature that only one app uses? — Don't add it to the shared package. Keep it in the app that needs it until a second app wants it (Rule of 2).
- What if package extraction breaks existing tests? — Tests run against the app which imports packages; zero regressions is a hard gate.
- What if backend services receive requests with an unknown FlavorId? — Fall back to "hinge" (default) config section.

## Requirements

### Functional Requirements

- **FR-001**: System MUST support extracting `packages/mobile_core/` as a pure Dart package containing auth, API client, environment config, JWT utilities, and shared models.
- **FR-002**: System MUST support extracting `packages/mobile_ui_kit/` as a Flutter package containing shared widgets (AuthenticatedAvatar, ConnectivityBanner, ErrorBoundary, SkeletonLoaders, VerificationBadge) and theme base utilities.
- **FR-003**: Extracted packages MUST NOT import from any app's `lib/` directory. Packages expose interfaces; apps provide implementations.
- **FR-004**: The existing `dejtingapp/` app MUST continue to work after migration to package imports, with all existing tests passing.
- **FR-005**: Backend services MUST read per-flavor configuration from `Flavors:{flavorId}:*` config sections in appsettings.
- **FR-006**: Backend services MUST fall back to default values when an unknown FlavorId is encountered.
- **FR-007**: Each Flutter app MUST be buildable as an independent APK/IPA with a unique applicationId/bundleId.
- **FR-008**: Cross-app matching policy MUST be configurable (hard-isolate vs. soft-preference) [NEEDS CLARIFICATION: user input required].

### Key Entities

- **FlavorConfig**: Per-app feature flags, copy, theme — lives in the app, not in shared packages.
- **mobile_core**: Shared Dart package — auth, API, models, environment, JWT.
- **mobile_ui_kit**: Shared Flutter package — common widgets, theme base.
- **Flavor Configuration Section**: Backend `appsettings.json` section `Flavors:{id}` with per-flavor overrides.
- **Build Target**: Flutter entry point (`main_{flavor}.dart`) paired with Android/iOS build variant.

## Success Criteria

### Measurable Outcomes

- **SC-001**: `packages/mobile_core/` and `packages/mobile_ui_kit/` each pass `flutter analyze` with zero errors independently.
- **SC-002**: After extraction, `dejtingapp/` still passes 659+ tests (zero regressions).
- **SC-003**: A skeleton second app can compile, authenticate, and render shared widgets by depending only on the extracted packages.
- **SC-004**: All 8 backend services build clean (`dotnet build`) after adding per-flavor config support.
- **SC-005**: Per-flavor config values are verifiable in integration tests (e.g., swipe limit test with different FlavorId headers).
- **SC-006**: No circular dependencies exist between packages (verified by `flutter analyze`).

## Design Principles

1. **Rule of 2**: Don't extract into a shared package until 2+ apps genuinely need it.
2. **Ports & Adapters**: Shared packages expose interfaces; apps provide implementations.
3. **No premature abstraction**: Only extract proven, stable code. Discovery, onboarding wizard, and matchmaking UI stay in the app.
4. **Thin app shell**: After extraction, each app is a thin shell that imports packages and adds product-specific screens + flavor config.
5. **Config over code**: Flavor-specific behavior differences live in `FlavorConfig` (client) and `appsettings.json` (server), not in `if/else` branches.

## Review & Acceptance Checklist

- [ ] Each user story is independently testable
- [ ] Acceptance scenarios use Given/When/Then format
- [ ] All requirements are specific and measurable
- [ ] Edge cases are documented
- [ ] Success criteria are objectively verifiable
- [ ] No implementation details leak into the spec (technology-agnostic where possible)
- [ ] NEEDS CLARIFICATION items are clearly marked
