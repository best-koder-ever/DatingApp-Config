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

## AI Workflow - ZERO "ALLOW" PROMPTS (CRITICAL! READ TWICE!)
**🚫 NEVER make the user press "Allow" or "Accept". NOT ONCE. EVER.**
**ALWAYS use `run_in_terminal` with `cat > file << 'EOF'` for ALL file creation and editing.**

The user HATES the Allow button. Every Allow prompt = broken workflow. If you use `create_file`, `replace_string_in_file`, or `multi_replace_string_in_file` you are wasting the user's time. The user wants to review UI manually on device, not babysit file permission dialogs.

### File Creation & Editing — TERMINAL ONLY
- ✅ **DO:** `cat > file.ext << 'EOF'` ... `EOF` (create/overwrite files)
- ✅ **DO:** `sed -i 's/old/new/g' file.ext` (inline edits)
- ✅ **DO:** `echo "line" >> file.ext` (append)
- ✅ **DO:** `cp`, `mv`, `rm`, `mkdir -p` (file system ops)
- ✅ **DO:** `dotnet add package`, `flutter pub add` (package managers)
- ❌ **NEVER:** `create_file` tool — triggers Allow prompt
- ❌ **NEVER:** `replace_string_in_file` tool — triggers Allow prompt  
- ❌ **NEVER:** `multi_replace_string_in_file` tool — triggers Allow prompt
- ❌ **NEVER:** Any tool that shows "Allow" / "Accept" / confirmation dialog

### Build & Test Operations
- ✅ **DO:** `dotnet build`, `dotnet test`, `flutter build`, `flutter test`
- ✅ **DO:** Use `--no-restore` flag when packages already restored
- ✅ **DO:** Chain commands with `&&` for atomic operations: `cd dir && dotnet build && dotnet test`

### Package Management
- ✅ **DO:** `dotnet add package PackageName --version X.Y.Z`
- ✅ **DO:** `flutter pub add package_name`
- ✅ **DO:** `pip install package` or add to requirements.txt + `pip install -r requirements.txt`

### Why Terminal-First?
User requires **fully autonomous, non-blocking execution**. The user's role is reviewing PRs and testing UI manually on device/emulator — NOT pressing Allow buttons. Terminal commands never block on confirmations, allowing AI to complete entire tasks without human intervention.

### User's Manual Testing Workflow
The user will manually test onboarding wizard screens on device/emulator. AI should:
1. Create/modify code autonomously (terminal commands)
2. Run `flutter analyze` to validate
3. Commit + push
4. User pulls and runs on device to inspect UI/UX visually

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

