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

## AI Workflow - Non-Breaking Automation (CRITICAL!)
**ALWAYS use terminal commands for file operations.** Never use interactive tools that require user confirmation.

### File Creation & Editing
- ✅ **DO:** Use `cat > file.ext << 'EOF'`, `echo "content" > file.ext`, `sed`, `awk`
- ✅ **DO:** Use `dotnet add package`, `dotnet remove package` for NuGet operations
- ✅ **DO:** Use `mkdir -p`, `cp`, `mv`, `rm` for file system operations
- ❌ **DON'T:** Use tools that require "accept/allow" prompts or user interaction
- ❌ **DON'T:** Use `create_file` or `replace_string_in_file` if stuck - switch to terminal commands

### Build & Test Operations
- ✅ **DO:** `dotnet build`, `dotnet test`, `flutter build`, `flutter test`
- ✅ **DO:** Use `--no-restore` flag when packages already restored
- ✅ **DO:** Chain commands with `&&` for atomic operations: `cd dir && dotnet build && dotnet test`

### Package Management
- ✅ **DO:** `dotnet add package PackageName --version X.Y.Z`
- ✅ **DO:** `flutter pub add package_name`
- ✅ **DO:** `pip install package` or add to requirements.txt + `pip install -r requirements.txt`

### Why Terminal-First?
User requires **autonomous, non-breaking execution**. Terminal commands never block on confirmations, allowing AI to complete entire tasks without human intervention.

<!-- MANUAL ADDITIONS END -->

## AI Helper Tools (CRITICAL - USE IN EVERY CONVERSATION!)
**Philosophy**: "Make the Invisible Visible" - AI can verify state WITHOUT asking user

### 🚨 BEFORE Starting ANY Work
```bash
# Read cheatsheet (60 seconds):
cat AI_HELPERS_CHEATSHEET.md

# Check database state (1 second vs asking user):
python3 scripts/ai-verify-state.py
```

### ✅ IN EVERY Flutter Test
```dart
import 'helpers/test_assertions.dart';
import 'helpers/database_queries.dart';

setUpAll(() async {
  await TestAssertions.assertFixturesLoaded(); // ← ALWAYS include!
});
```

### 🔧 Quick Reference
- **Fixture users**: alice, bob, charlie, diana, erik
- **Known matches**: bob↔charlie, diana→erik
- **Check state**: `python3 scripts/ai-verify-state.py` (BEFORE asking user!)
- **Get user**: `await TestDatabaseQueries.getFixtureUser('bob')`
- **Reset**: `make test-clean` (1 command vs 6 steps)

### 📚 Full Context Files
1. **[START_HERE_AI.md](../START_HERE_AI.md)** ← Read first in new conversations (1 min)
2. **[.ai-context.json](../.ai-context.json)** ← Machine-readable context (parse this!)
3. **[AI_HELPERS_CHEATSHEET.md](../AI_HELPERS_CHEATSHEET.md)** ← Quick reference (60 sec)
4. **[AI_HELPER_STRATEGIES.md](../AI_HELPER_STRATEGIES.md)** ← Complete guide (30 min)

**Impact**: 10x faster AI development - no guessing, no asking user for basic info!

