# Overnight AI Automation Prerequisites

**Status: ❌ NOT READY** - CI/CD is broken, must fix before attempting overnight runs

## Critical Finding

**All CI/CD workflows are FAILING** (last 5 runs across all repos):
```
STATUS  TITLE          WORKFLOW    BRANCH  EVENT  AGE       
X       Remove leg...  Dating ...  main    push   1 month ago
X       Remove leg...  Compreh...  main    push   1 month ago  
X       Remove leg...  Profess...  main    push   1 month ago
X       Fix: Add J...  Profess...  main    push   4 months ago
X       Fix: Add J...  Compreh...  main    push   4 months ago
```

**Why this matters**: Overnight AI runs generate 90-100 files across 9 repos. Without working CI/CD:
- ❌ No automated build verification (could ship broken code)
- ❌ No test validation (regressions go undetected)
- ❌ No coverage enforcement (quality degrades)
- ❌ No smoke tests (integration failures hidden until manual testing)
- ❌ **Result**: Morning review becomes 4-6 hours of manual debugging instead of 30-minute PR approval

## Philosophy: "Safety Over Speed"

> "I prefer work slowed and no problems then fast and spagetti code and messy" - User requirement

**Translation**: We need MULTIPLE validation gates BEFORE merging AI-generated code:

```
AI generates code (overnight)
    ↓
Gate 1: Build succeeds? ✅ or ❌ (CI/CD)
    ↓
Gate 2: Tests pass? ✅ or ❌ (CI/CD)
    ↓
Gate 3: Coverage >80%? ✅ or ❌ (CI/CD)
    ↓
Gate 4: Smoke tests pass? ✅ or ❌ (CI/CD)
    ↓
Gate 5: Human review? ✅ or ❌ (morning review)
    ↓
ONLY THEN: Merge to main
```

**Current state**: Gates 1-4 are BROKEN. Only Gate 5 (human review) works.

**Risk**: Human catches build errors at 8AM that CI/CD should have caught at 2AM → wastes 6 hours.

---

## Phase 1: Fix CI/CD Foundation (BLOCKING - Must complete first)

### P1.1: Get Local Builds GREEN ⚠️ In Progress

**Current state**: 
- ✅ UserService builds (5 warnings, 0 errors)
- ⏳ Other 5 services untested
- ❌ Security vulnerabilities (OpenTelemetry 1.8.0 has CVE)

**Action items**:
```bash
# Test all service builds
cd ~/development/DatingApp
for service in UserService MatchmakingService swipe-service photo-service messaging-service; do
    echo "Building $service..."
    cd $service
    dotnet build --configuration Release 2>&1 | tee ../build-$service.log
    cd ..
done

# Check for build failures
grep -l "Build FAILED" build-*.log
```

**Success criteria**: All 5 services + dejting-yarp build with 0 errors

**Time estimate**: 1-2 hours (might reveal missing dependencies, DB connection configs)

---

### P1.2: Fix Security Vulnerabilities 🔐

**Found vulnerabilities**:
```
Package 'OpenTelemetry.Instrumentation.AspNetCore' 1.8.0 
  → CVE: https://github.com/advisories/GHSA-vh2m-22xx-q94f
  → Severity: MODERATE
  
Package 'OpenTelemetry.Instrumentation.Http' 1.8.0
  → CVE: https://github.com/advisories/GHSA-vh2m-22xx-q94f  
  → Severity: MODERATE
```

**Action items**:
```bash
# Update vulnerable packages (check latest stable version)
cd ~/development/DatingApp/UserService
dotnet add package OpenTelemetry.Instrumentation.AspNetCore --version 1.10.0
dotnet add package OpenTelemetry.Instrumentation.Http --version 1.10.0

# Repeat for all 5 services
# Test builds still work after upgrade
dotnet build --configuration Release
```

**Success criteria**: `dotnet build` shows 0 NU1902 warnings

**Time estimate**: 30 minutes

---

### P1.3: Get Local Tests GREEN 🧪

**Current state**:
- ✅ Test projects exist for all 6 services
- ⏳ Tests not run recently (unknown pass/fail state)
- ⏳ Coverage unknown

**Test projects found**:
```
UserService/UserService.Tests/
MatchmakingService/MatchmakingService.Tests/
swipe-service/SwipeService.Tests/
photo-service/PhotoService.Tests/
messaging-service/MessagingService.Tests/
dejting-yarp/src/dejting-yarp.Tests/
```

**Action items**:
```bash
# Run all tests locally
cd ~/development/DatingApp
for service in UserService MatchmakingService swipe-service photo-service messaging-service; do
    echo "Testing $service..."
    cd $service
    dotnet test --configuration Release --verbosity normal 2>&1 | tee ../test-$service.log
    cd ..
done

# Check for test failures
grep -E "Failed|Error" test-*.log
```

**Success criteria**: 
- All test projects run without errors
- Test pass rate >95% (some failures acceptable if documented)
- No crashes or connection timeouts

**Time estimate**: 1-2 hours (might need to fix broken tests, DB setup issues)

---

### P1.4: Fix CI/CD Workflow ⚙️

**Current state**: 
- ✅ [comprehensive-ci-cd.yml](/.github/workflows/comprehensive-ci-cd.yml) exists
- ❌ 100% failure rate (5/5 recent runs failed)
- ⏳ Failure cause unknown (404 error when querying run details)

**Likely issues**:
1. MySQL service not starting (health check timeout)
2. Keycloak service not starting (health check timeout)  
3. Services can't connect to databases (wrong ports, passwords)
4. Missing GitHub secrets (CODECOV_TOKEN)
5. Test projects not found (path issues)

**Action items**:
```bash
# Trigger new workflow run to see current error
cd ~/development/DatingApp
git commit --allow-empty -m "Test: Trigger CI/CD workflow"
git push origin main

# Watch workflow run
gh run watch

# Download logs if it fails
gh run view --log-failed > ci-cd-failure.log

# Fix common issues based on logs
```

**Common fixes**:
- MySQL health check timeout → increase timeout from 30s to 60s
- Service startup timeout → add `sleep 30` before smoke tests
- Missing secrets → add CODECOV_TOKEN to repo settings (or skip Codecov upload)
- Path issues → verify service names match directory names exactly

**Success criteria**: 
- Workflow completes without errors
- All 5 services build successfully in CI
- At least some tests run (even if some fail)

**Time estimate**: 2-4 hours (debugging CI is always slow)

---

### P1.5: Get Smoke Tests GREEN 🔥

**Current state**:
- ✅ [smoke-tests.py](/smoke-tests.py) exists (126 lines)
- ⏳ Tests 5 services: UserService (8082), MatchmakingService (8083), SwipeService (8084), PhotoService (8085), MessagingService (8086)
- ⏳ Checks `/health` endpoints
- ⏳ Unknown if tests pass (haven't run in months)

**Action items**:
```bash
# Start services locally
cd ~/development/DatingApp
./infrastructure/start.sh   # Keycloak + databases
./dev-start.sh              # All 7 services

# Wait for startup (30-60 seconds)
sleep 60

# Run smoke tests
python3 smoke-tests.py

# Check results
echo $?  # Should be 0 for success
```

**Common failures**:
- Services not responding → check ports with `netstat -tuln | grep 808`
- Health endpoint 404 → service doesn't have `/health` endpoint yet
- Connection refused → service crashed on startup (check logs)
- Database errors → migrations not run

**Success criteria**: `smoke-tests.py` returns exit code 0 (all 5 services healthy)

**Time estimate**: 1-2 hours (might need to add `/health` endpoints to services missing them)

---

### P1.6: Establish Coverage Baselines 📊

**Current state**:
- ✅ Coverage collection configured in [comprehensive-ci-cd.yml](/.github/workflows/comprehensive-ci-cd.yml#L93-L119)
- ✅ 80% threshold enforced
- ❌ No baseline measurements (don't know current coverage %)

**Action items**:
```bash
# Generate coverage report locally
cd ~/development/DatingApp/UserService
dotnet test \
    --configuration Release \
    --collect:"XPlat Code Coverage" \
    --results-directory ./coverage \
    -- DataCollectionRunSettings.DataCollectors.DataCollector.Configuration.Format=cobertura

# Extract coverage %
coverage_file=$(find coverage -name "coverage.cobertura.xml" | head -1)
line_rate=$(grep -oP 'line-rate="\K[0-9.]+' "$coverage_file" | head -1)
line_pct=$(echo "$line_rate * 100" | bc -l | xargs printf "%.1f")
echo "UserService coverage: ${line_pct}%"

# If <80%, temporarily lower threshold OR add tests
```

**Record baselines** (example):
```
UserService:         67% line, 54% branch  ⚠️ Below threshold
MatchmakingService:  82% line, 71% branch  ✅ Passes
SwipeService:        45% line, 38% branch  ❌ Needs work
PhotoService:        91% line, 85% branch  ✅ Excellent
MessagingService:    73% line, 65% branch  ⚠️ Below threshold
```

**Decision**: 
- Option A: Lower threshold to 60% temporarily, commit to increasing 5%/month
- Option B: Write tests NOW to hit 80% (2-3 days work per low-coverage service)

**Success criteria**: Know current coverage % for all services, have plan to reach 80%

**Time estimate**: 2-3 hours measurement + variable time for test writing

---

## Phase 2: Build Controller Repo Safety Net (After Phase 1 complete)

### P2.1: Create Controller Repository 🎮

**What it is**: Git repository with submodules tracking all 9 repos at specific commits

**Why needed**: 
- Snapshot entire project state before overnight run
- Rollback all 9 repos atomically if AI generates garbage
- Track dependencies between repos (SwipeService → MatchmakingService)

**Action items**:
```bash
# Create controller repo
cd ~/development
mkdir DatingAppController && cd DatingAppController
git init

# Add submodules for all 9 repos
git submodule add ../DatingApp DatingApp-Config
git submodule add ../DatingApp/UserService UserService
git submodule add ../DatingApp/MatchmakingService MatchmakingService
git submodule add ../DatingApp/swipe-service swipe-service
git submodule add ../DatingApp/photo-service photo-service
git submodule add ../DatingApp/messaging-service messaging-service
git submodule add ../DatingApp/dejting-yarp dejting-yarp
git submodule add ../DatingApp/safety-service safety-service
git submodule add ../mobile-apps/flutter/dejtingapp mobile-client

# Create initial snapshot
git commit -m "Initial snapshot: All repos at stable state"
git tag stable-baseline
```

**File structure**:
```
DatingAppController/
├── .git/
├── .gitmodules              ← Submodule configuration
├── DatingApp-Config/        ← Submodule @ commit abc123
├── UserService/             ← Submodule @ commit def456
├── MatchmakingService/      ← Submodule @ commit ghi789
├── ... (7 more submodules)
└── scripts/
    ├── snapshot.sh         ← Create snapshot before overnight run
    ├── rollback.sh         ← Restore to previous snapshot
    ├── status-all.sh       ← Show drift across all repos
    ├── update-all.sh       ← Pull latest from all repos
    └── run-ai-batch.sh     ← Queue overnight tasks
```

**Success criteria**: 
- `git submodule status` shows all 9 repos
- `git tag` shows `stable-baseline`
- Can checkout tag and all submodules restore to exact commits

**Time estimate**: 1-2 hours

---

### P2.2: Create Snapshot Scripts 📸

**snapshot.sh** - Save current state before overnight run:
```bash
#!/bin/bash
# Usage: ./scripts/snapshot.sh "Before AI batch - onboarding features"

set -e

DESC="$1"
if [ -z "$DESC" ]; then
    echo "Usage: $0 <description>"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
TAG="ai-batch-start-$TIMESTAMP"

cd "$(dirname "$0")/.."

# Update submodules to current commits
git submodule update --remote --merge

# Record state
git add .gitmodules
git add -A
git commit -m "Snapshot: $DESC" || echo "No changes to commit"

# Tag for easy rollback
git tag -a "$TAG" -m "$DESC"

echo "✅ Snapshot created: $TAG"
echo "📋 Submodule commits:"
git submodule status

echo ""
echo "To rollback later: ./scripts/rollback.sh $TAG"
```

**rollback.sh** - Restore to previous snapshot:
```bash
#!/bin/bash
# Usage: ./scripts/rollback.sh ai-batch-start-20260207-220000

set -e

TAG="$1"
if [ -z "$TAG" ]; then
    echo "Available snapshots:"
    git tag -l "ai-batch-start-*"
    exit 1
fi

cd "$(dirname "$0")/.."

echo "⚠️  Rolling back to snapshot: $TAG"
echo "This will reset ALL 9 repos to previous commits."
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Checkout tag
git checkout "$TAG"

# Update all submodules to tagged commits
git submodule update --init --recursive

echo "✅ Rollback complete. All repos restored to $TAG"
echo ""
echo "📋 Current state:"
git submodule status
```

**status-all.sh** - Show what changed across all repos:
```bash
#!/bin/bash
# Usage: ./scripts/status-all.sh

cd "$(dirname "$0")/.."

echo "📊 Multi-Repo Status Report"
echo "="

for submodule in DatingApp-Config UserService MatchmakingService swipe-service photo-service messaging-service dejting-yarp safety-service mobile-client; do
    echo ""
    echo "=== $submodule ==="
    cd "$submodule"
    
    # Git status
    if [ -n "$(git status --porcelain)" ]; then
        echo "📝 Changes detected:"
        git status --short
    else
        echo "✅ Clean (no changes)"
    fi
    
    # Ahead/behind
    branch=$(git rev-parse --abbrev-ref HEAD)
    ahead=$(git rev-list --count origin/$branch..$branch 2>/dev/null || echo "0")
    behind=$(git rev-list --count $branch..origin/$branch 2>/dev/null || echo "0")
    
    if [ "$ahead" -gt 0 ]; then
        echo "⬆️  $ahead commits ahead of origin"
    fi
    if [ "$behind" -gt 0 ]; then
        echo "⬇️  $behind commits behind origin"
    fi
    
    cd ..
done

echo ""
echo "="
echo "Use ./scripts/snapshot.sh to save current state"
```

**Success criteria**: 
- Can create snapshot, make changes, rollback successfully
- All 9 repos return to exact previous state
- No merge conflicts or orphaned changes

**Time estimate**: 2-3 hours (includes testing rollback scenarios)

---

### P2.3: Define Wave-Based Merge Strategy 🌊

**Philosophy**: Merge in dependency order to prevent cascade failures

**Wave 1: Foundation** (Must merge first - other waves depend on it)
```
Database migrations
Shared models (Contracts/, DTOs/)
Shared middleware (CorrelationIdMiddleware)
Configuration changes (appsettings.json)
```
**Dependencies**: None (safe to merge independently)
**Risk level**: LOW (if migration fails, roll back entire wave)
**Merge order**: 
1. DatingApp-Config (shared contracts)
2. Each service's migration (can run in parallel)
3. Verify: `dotnet ef migrations list` shows new migrations

---

**Wave 2: Backend APIs** (Depends on Wave 1 models/migrations)
```
Controllers (new endpoints)
Commands/Queries (MediatR handlers)
Services (business logic)
Repository changes
```
**Dependencies**: Wave 1 (needs models, DB schema)
**Risk level**: MEDIUM (logic bugs possible, but isolated per service)
**Merge order**:
1. UserService backend changes
2. MatchmakingService backend changes
3. swipe-service, photo-service, messaging-service (parallel OK)
4. Verify: `dotnet test` passes, `/health` endpoints return 200

---

**Wave 3: Frontend** (Depends on Wave 2 APIs)
```
Flutter UI screens
State management (Riverpod)
API client code
Navigation updates
```
**Dependencies**: Wave 2 (needs working API endpoints)
**Risk level**: HIGH (UI bugs, integration issues, user-visible)
**Merge order**:
1. mobile-client API client updates (calling new endpoints)
2. mobile-client UI screens
3. Verify: Manual testing of new flows

---

**Wave 4: Tests** (Depends on Wave 1-3 being stable)
```
Integration tests
E2E tests
Test fixtures
```
**Dependencies**: Waves 1-3 (testing complete features)
**Risk level**: LOW (tests failing don't break production code)
**Merge order**:
1. Service integration tests (can merge in parallel)
2. E2E tests (mobile + backend)
3. Verify: Test suite passes end-to-end

---

**Enforcement rules**:
```bash
# In run-ai-batch.sh, enforce wave ordering
if [ "$WAVE" = "backend" ]; then
    # Check Wave 1 (foundation) is merged
    if ! git log --oneline | grep -q "Wave 1: Foundation"; then
        echo "❌ Cannot merge Wave 2 until Wave 1 is complete"
        exit 1
    fi
fi
```

**Morning review checklist**:
```
□ Wave 1 (Foundation) - All PRs reviewed?
  ├─ Migrations applied to test DB?
  ├─ Shared models compile without errors?
  └─ All services still build?

□ Wave 2 (Backend) - APIs functional?
  ├─ smoke-tests.py passes?
  ├─ Manual Postman testing?
  └─ No breaking changes to existing endpoints?

□ Wave 3 (Frontend) - UI working?
  ├─ `flutter build` succeeds?
  ├─ Manual testing on iOS simulator?
  └─ No crashes or blank screens?

□ Wave 4 (Tests) - Coverage maintained?
  ├─ Coverage still >80%?
  ├─ E2E tests pass?
  └─ No skipped/disabled tests?
```

**Time estimate**: 3-4 hours (document wave rules, create enforcement scripts)

---

## Phase 3: Configure Overnight AI Tasks (After Phase 2 complete)

### P3.1: Create Task Safety Classification 🚦

**Tier 1: 100% Safe for AI Autonomy** (Generate overnight, auto-approve if CI passes)
```
✅ Database migrations (from schema design docs)
✅ Model/DTO classes (from contracts)
✅ Test skeletons (arrange/act/assert structure)
✅ Reference data seeding (countries, genders, etc.)
✅ API client boilerplate (from OpenAPI specs)
✅ Documentation (code comments, README)
```
**Why safe**: Deterministic, low logic, well-specified, isolated
**Success rate**: 95-98%
**Review time**: 5-10 min per PR (quick sanity check)

---

**Tier 2: 90% Safe** (Generate overnight, human review required before merge)
```
⚠️ API endpoint implementations (from contracts + simple CRUD)
⚠️ MediatR command handlers (simple, no complex business logic)
⚠️ Repository methods (basic CRUD)
⚠️ Validation logic (from requirements docs)
⚠️ Configuration files (appsettings.json updates)
```
**Why caution needed**: Some logic, integration points, can have subtle bugs
**Success rate**: 85-90%
**Review time**: 15-20 min per PR (verify logic, test edge cases)

---

**Tier 3: NEVER Automate** (Human writes it during daytime)
```
❌ UI/UX design decisions (spacing, colors, layout)
❌ Complex business logic (matching algorithm, privacy rules)
❌ Security-critical code (auth, encryption, data access control)
❌ Payment processing
❌ Shared middleware (affects all services)
❌ Database connection strings, secrets
```
**Why prohibited**: Creative, context-heavy, high risk
**Success rate**: 40-60% (too low to justify automation)
**Review time**: Would take longer to fix than write from scratch

---

**Task classification example** (from ONBOARDING_IMPLEMENTATION_TASKS.md):
```
TASK-010: Phone entry screen UI
  → Tier 3 ❌ (UI/UX decisions)
  
TASK-014: Set up Twilio account
  → Tier 3 ❌ (manual account setup, secrets management)
  
TASK-020: Integrate CAPTCHA backend validation
  → Tier 2 ⚠️ (API endpoint, but simple validation logic)
  
TASK-030: OTP input screen models
  → Tier 1 ✅ (DTOs from contract)
  
TASK-040: SMS verification test suite
  → Tier 1 ✅ (test skeletons, AI can generate arrange/act/assert)
  
TASK-270: Privacy Policy (GDPR-compliant)
  → Tier 3 ❌ (legal work, requires attorney/human review)
```

**Time estimate**: 2-3 hours (review all 260 tasks, classify each)

---

### P3.2: Create AI Task Queue Configuration 📋

**File: `ai-autonomous-tasks.json`**
```json
{
  "metadata": {
    "created": "2026-02-07",
    "run_schedule": "Overnight (22:00-06:00)",
    "review_schedule": "Morning standup (08:00-09:00)",
    "max_concurrent_tasks": 5,
    "timeout_per_task_minutes": 30
  },
  "waves": [
    {
      "wave_number": 1,
      "name": "Foundation - Database & Models",
      "depends_on": [],
      "tasks": [
        {
          "id": "TASK-050",
          "title": "Create UserProfile model with onboarding fields",
          "tier": 1,
          "estimated_files": 3,
          "repos": ["UserService"],
          "ai_prompt": "Create UserProfile.cs model in UserService/Models/. Include: FirstName, DateOfBirth, Gender, Bio, Height, Location (City, Latitude, Longitude). Follow existing model conventions (BaseEntity, nullable reference types). Add EF Core configuration in UserProfileConfiguration.cs.",
          "acceptance_criteria": [
            "Model compiles without errors",
            "All properties have appropriate data annotations",
            "EF Core configuration includes indexes on UserId, Location"
          ]
        },
        {
          "id": "TASK-051",
          "title": "Create migration for UserProfile table",
          "tier": 1,
          "estimated_files": 1,
          "repos": ["UserService"],
          "ai_prompt": "Generate EF Core migration for UserProfile model: `dotnet ef migrations add AddUserProfileOnboarding --project UserService.csproj`. Verify migration creates table with correct columns, indexes, and foreign key to Users table.",
          "acceptance_criteria": [
            "Migration file created in Migrations/",
            "Up() method creates UserProfiles table",
            "Down() method drops table cleanly",
            "dotnet ef migrations list shows new migration"
          ]
        }
      ]
    },
    {
      "wave_number": 2,
      "name": "Backend - API Endpoints",
      "depends_on": [1],
      "tasks": [
        {
          "id": "TASK-052",
          "title": "Create SaveUserProfile API endpoint",
          "tier": 2,
          "estimated_files": 5,
          "repos": ["UserService"],
          "ai_prompt": "Implement POST /api/users/{userId}/profile endpoint using CQRS pattern. Create SaveUserProfileCommand, SaveUserProfileCommandHandler, validator, and controller action. Follow existing patterns in UpdateUserCommand.cs. Return 200 with ProfileDto on success, 400 if validation fails.",
          "acceptance_criteria": [
            "Builds without errors",
            "Unit tests for command handler pass",
            "Integration test verifies profile saved to DB",
            "Swagger doc generated correctly"
          ]
        }
      ]
    }
  ],
  "guardrails": {
    "require_ci_pass": true,
    "require_test_pass": true,
    "require_coverage_threshold": 80,
    "require_human_review_tier2": true,
    "auto_merge_tier1": false,
    "max_failed_tasks_before_abort": 3,
    "shared_code_freeze": [
      "Shared/",
      "Contracts/",
      "*.Common/"
    ]
  }
}
```

**Time estimate**: 4-6 hours (define first 20-30 tasks with detailed prompts)

---

### P3.3: Create Overnight Run Orchestration Script 🤖

**File: `scripts/run-ai-batch.sh`**
```bash
#!/bin/bash
# Overnight AI batch processor with safety guardrails
# Usage: ./scripts/run-ai-batch.sh ai-autonomous-tasks.json

set -e

TASK_FILE="$1"
BATCH_START=$(date +%Y%m%d-%H%M%S)
SNAPSHOT_TAG="ai-batch-start-$BATCH_START"

# Validate prerequisites
echo "🔍 Pre-flight checks..."

# Check 1: CI/CD is working
echo "  - Checking CI/CD status..."
last_ci_status=$(gh run list --limit 1 --json conclusion --jq '.[0].conclusion')
if [ "$last_ci_status" != "success" ]; then
    echo "❌ CI/CD not passing (last run: $last_ci_status)"
    echo "Fix CI/CD before running overnight batch!"
    exit 1
fi
echo "  ✅ CI/CD is green"

# Check 2: All repos are clean
echo "  - Checking repo cleanliness..."
./scripts/status-all.sh > /tmp/status.txt
if grep -q "Changes detected" /tmp/status.txt; then
    echo "❌ Uncommitted changes detected"
    echo "Commit or stash changes before overnight run!"
    cat /tmp/status.txt
    exit 1
fi
echo "  ✅ All repos clean"

# Check 3: Tests passing locally
echo "  - Running test suite..."
for service in UserService MatchmakingService swipe-service photo-service messaging-service; do
    cd ~/development/DatingApp/$service
    dotnet test --no-build --verbosity quiet > /tmp/test-$service.log 2>&1
    if [ $? -ne 0 ]; then
        echo "❌ Tests failing in $service"
        tail -20 /tmp/test-$service.log
        exit 1
    fi
done
echo "  ✅ All tests passing"

# Create snapshot
echo "📸 Creating snapshot..."
./scripts/snapshot.sh "Before overnight batch $BATCH_START"

# Load task configuration
echo "📋 Loading tasks from $TASK_FILE..."
# TODO: Parse JSON, extract Wave 1 tasks
# TODO: For each task, call AI agent with prompt
# TODO: Create branch, commit changes, create PR
# TODO: Trigger CI/CD on PR
# TODO: Track status in batch-results.json

echo ""
echo "✅ Pre-flight checks passed"
echo "🚀 Batch will run for ~8 hours (estimated)"
echo "📊 Results will be in: batch-results-$BATCH_START.json"
echo "🔍 Review in morning with: ./scripts/review-batch.sh $BATCH_START"
echo ""
echo "Starting batch in 10 seconds... (Ctrl+C to abort)"
sleep 10

# TODO: Implement actual batch execution
echo "🤖 AI batch processing started..."
echo "(Implementation pending - this is the shell framework)"
```

**Time estimate**: 6-8 hours (complex orchestration, error handling, status tracking)

---

### P3.4: Create Morning Review Script 📊

**File: `scripts/review-batch.sh`**
```bash
#!/bin/bash
# Morning review of overnight AI batch results
# Usage: ./scripts/review-batch.sh 20260207-220000

BATCH_ID="$1"
RESULTS_FILE="batch-results-$BATCH_ID.json"

if [ ! -f "$RESULTS_FILE" ]; then
    echo "❌ Results file not found: $RESULTS_FILE"
    exit 1
fi

echo "☕ Good morning! Here's your overnight batch report:"
echo "="

# Summary statistics
total_tasks=$(jq '.tasks | length' "$RESULTS_FILE")
completed=$(jq '[.tasks[] | select(.status=="completed")] | length' "$RESULTS_FILE")
failed=$(jq '[.tasks[] | select(.status=="failed")] | length' "$RESULTS_FILE")
pending=$(jq '[.tasks[] | select(.status=="pending")] | length' "$RESULTS_FILE")

echo "📊 Summary:"
echo "  - Total tasks: $total_tasks"
echo "  - ✅ Completed: $completed"
echo "  - ❌ Failed: $failed"
echo "  - ⏳ Pending: $pending"
echo ""

# Show PRs created
echo "📝 Pull Requests Created:"
jq -r '.tasks[] | select(.pr_url != null) | "  - [\(.id)] \(.title)\n    PR: \(.pr_url)\n    CI: \(.ci_status)"' "$RESULTS_FILE"
echo ""

# Show CI failures
echo "⚠️  CI Failures (needs attention):"
jq -r '.tasks[] | select(.ci_status=="failure") | "  - [\(.id)] \(.title) - \(.ci_error)"' "$RESULTS_FILE"
echo ""

# Show tasks ready to merge (Tier 1, CI passed)
echo "🎯 Ready to Merge (Tier 1, CI green):"
jq -r '.tasks[] | select(.tier==1 and .ci_status=="success") | "  - [\(.id)] \(.title) - PR: \(.pr_url)"' "$RESULTS_FILE"
echo ""

# Show tasks needing human review (Tier 2)
echo "👀 Needs Human Review (Tier 2):"
jq -r '.tasks[] | select(.tier==2 and .ci_status=="success") | "  - [\(.id)] \(.title) - PR: \(.pr_url)"' "$RESULTS_FILE"
echo ""

# Rollback decision
echo "="
echo "🤔 Decision Time:"
echo "  A) Merge ready PRs (Tier 1, green CI)"
echo "  B) Review Tier 2 PRs manually, then merge"
echo "  C) Rollback entire batch (something is very wrong)"
echo ""
read -p "Your choice (A/B/C): " choice

case $choice in
    A)
        echo "🚀 Auto-merging Tier 1 PRs with green CI..."
        # TODO: Implement auto-merge for Tier 1 tasks
        ;;
    B)
        echo "👀 Opening PRs for manual review..."
        # TODO: Open each Tier 2 PR in browser
        ;;
    C)
        echo "⏪ Rolling back entire batch..."
        ./scripts/rollback.sh "ai-batch-start-$BATCH_ID"
        ;;
    *)
        echo "Invalid choice. Exiting."
        ;;
esac
```

**Time estimate**: 3-4 hours

---

## Phase 4: Gradual Rollout (After Phase 3 complete)

### P4.1: Test Run Week 1 - Conservative (10-15 tasks)

**Goal**: Validate infrastructure works end-to-end with minimal risk

**Task selection**: 
- 10 Tier 1 tasks (database migrations, models, test skeletons)
- 5 Tier 2 tasks (simple CRUD endpoints)
- 0 Tier 3 tasks (humans write these)

**Expected results**:
- Files generated: 40-50
- Success rate: 80-85% (10-12 successful, 2-3 need fixes)
- Morning review time: 1-2 hours

**Rollback triggers**:
- More than 3 tasks fail CI → rollback entire batch
- Shared code modified unexpectedly → rollback immediately
- Any service crashes → rollback, investigate

**Time estimate**: 8 hours overnight + 1-2 hours morning review

---

### P4.2: Test Run Week 2 - Moderate (20-30 tasks)

**Goal**: Scale up cautiously, refine prompts based on Week 1 learnings

**Task selection**:
- 15 Tier 1 tasks
- 10 Tier 2 tasks
- 5 manual tasks (Tier 3, human does during daytime)

**Expected results**:
- Files generated: 70-90
- Success rate: 85-90% (improved prompts from Week 1 feedback)
- Morning review time: 2-3 hours

**Time estimate**: 8 hours overnight + 2-3 hours morning review

---

### P4.3: Full Production Week 3+ - Aggressive (40-60 tasks)

**Goal**: Maximize velocity while maintaining quality

**Task selection**:
- 25 Tier 1 tasks
- 20 Tier 2 tasks
- 15 Tier 3 tasks (manual)

**Expected results**:
- Files generated: 90-120
- Success rate: 90-95% (after 2 weeks of prompt refinement)
- Morning review time: 3-4 hours
- Net time saved: 5-7 working days per week

**Time estimate**: 8 hours overnight + 3-4 hours morning review

---

## Prerequisites Checklist (Print This!)

Before attempting first overnight AI run, verify ALL boxes checked:

### Phase 1: CI/CD Foundation ✅ = ALL GREEN
```
□ All 6 services build without errors (UserService, MatchmakingService, swipe-service, photo-service, messaging-service, dejting-yarp)
□ Security vulnerabilities fixed (OpenTelemetry packages updated to 1.10.0+)
□ All test projects run without crashes
□ Test pass rate >95% (or failures documented + acceptable)
□ CI/CD workflow runs and completes (even if some tests fail)
□ smoke-tests.py passes (all 5 services return healthy)
□ Coverage measured for all services (know baseline %, even if <80%)
```

### Phase 2: Controller Repo ✅ = SAFETY NET READY
```
□ Controller repo created with 9 submodules
□ `stable-baseline` tag exists
□ snapshot.sh tested (creates tag, records commit hashes)
□ rollback.sh tested (restores all repos to previous snapshot)
□ status-all.sh shows unified view across repos
□ Wave-based merge strategy documented (Foundation → Backend → Frontend → Tests)
□ Shared code freeze policy enforced (no changes to Shared/ during overnight runs)
```

### Phase 3: Task Configuration ✅ = GUARDRAILS ACTIVE
```
□ All 260 tasks classified into Tier 1/2/3 (100%/90%/NEVER automate)
□ ai-autonomous-tasks.json created with Wave 1 tasks (first 10-15 tasks)
□ run-ai-batch.sh pre-flight checks working (CI green, repos clean, tests pass)
□ review-batch.sh generates morning report (PRs, CI status, merge recommendations)
□ Guardrails configured (require CI pass, coverage >80%, human review Tier 2)
```

### Phase 4: Test Run ✅ = FIRST RUN SUCCESSFUL
```
□ Test run Week 1 completed (10-15 tasks)
□ Morning review <2 hours
□ Success rate >80%
□ No rollbacks needed
□ Team confident in process
```

**Only when ALL phases complete → proceed to production overnight runs**

---

## Estimated Timeline to "Ready for Overnight Runs"

| Phase | Tasks | Time Estimate | Blocking? |
|-------|-------|---------------|-----------|
| **Phase 1: CI/CD** | Fix builds, tests, security, smoke tests, coverage | **8-12 hours** | ✅ YES - MUST complete first |
| **Phase 2: Controller Repo** | Create, test snapshot/rollback, document waves | **6-9 hours** | ✅ YES - Safety net required |
| **Phase 3: Task Config** | Classify tasks, write prompts, create scripts | **12-18 hours** | ✅ YES - Automation infrastructure |
| **Phase 4: Test Run** | First conservative batch, review, refine | **10-12 hours** | ⚠️ PARTIAL - Can iterate |
| **Total** | End-to-end infrastructure | **36-51 hours** | **~ 5-7 working days** |

**Reality check**: Before running 8-hour overnight batches that generate 90-100 files, we need 5-7 days of infrastructure work.

**Alternative**: Skip overnight runs entirely, use AI assistant interactively during daytime. Generate 10-15 files per session, review immediately, iterate. Slower but safer for solo developer.

---

## Recommendations

### Option A: Full Overnight Automation (Complex, High ROI)

**Pros**:
- Save 5-7 days per week (after infrastructure complete)
- Maximize AI leverage
- Systematic, repeatable process

**Cons**:
- 5-7 days setup time before first run
- Complex infrastructure (controller repo, wave merging, orchestration)
- Single point of failure (if orchestration breaks at 3AM)

**Best for**: Teams of 2-3 developers, aggressive timelines

---

### Option B: Daytime Interactive (Simple, Immediate Start)

**Pros**:
- Start TODAY (no infrastructure needed)
- Immediate feedback loop (see AI output, correct mistakes instantly)
- Simpler mental model (no overnight surprises)

**Cons**:
- Slower (10-15 tasks per day vs 40-60 overnight)
- Requires continuous attention (can't "set it and forget it")
- Still saves time (AI generates first draft), just not overnight

**Best for**: Solo developers, learning phase, rapid iteration

**Process**:
```
09:00 - Morning standup: Pick 3 Tier 1 tasks
09:30 - AI generates Task 1 (models) - Review + merge (15 min)
10:00 - AI generates Task 2 (migration) - Review + merge (15 min)
10:30 - AI generates Task 3 (test skeleton) - Review + merge (15 min)
11:00 - Pick 2 Tier 2 tasks
11:30 - AI generates Task 4 (API endpoint) - Review + test (30 min)
12:30 - AI generates Task 5 (validation) - Review + test (30 min)
---
Result: 5 tasks/day × 5 days = 25 tasks/week
Compare: Overnight = 40-60 tasks/week (but requires 5-7 days setup)
```

---

### Option C: Hybrid (Recommended for Solo Dev)

**Phase 1 (Week 1-2)**: Build CI/CD foundation while working interactively
- Fix CI/CD (2 days)
- Use AI daytime for Tier 1 tasks while CI/CD builds (3 days)
- Establish green baseline

**Phase 2 (Week 3-4)**: Add controller repo, test small overnight runs
- Create controller repo (1 day)
- Test 10-task overnight run (1 day)
- Refine based on learnings (3 days)

**Phase 3 (Week 5+)**: Full production overnight runs
- 40-60 tasks per overnight run
- 3-4 hour morning reviews
- Net save 5-7 days/week

**Total time to full automation**: 3-4 weeks
**Progressive value**: Start saving time Week 1 (daytime AI), maximize Week 5+ (overnight)

---

## Next Steps

**IMMEDIATE (Today)**: Fix CI/CD foundation
```bash
# Step 1: Build all services, capture errors
cd ~/development/DatingApp
for service in UserService MatchmakingService swipe-service photo-service messaging-service; do
    echo "Building $service..."
    cd $service
    dotnet build --configuration Release 2>&1 | tee ../build-$service.log
    cd ..
done

# Step 2: Update vulnerable packages
cd UserService
dotnet add package OpenTelemetry.Instrumentation.AspNetCore --version 1.10.0
dotnet add package OpenTelemetry.Instrumentation.Http --version 1.10.0
# Repeat for other services

# Step 3: Trigger CI/CD run
git add -A
git commit -m "fix: Update OpenTelemetry packages for CVE GHSA-vh2m-22xx-q94f"
git push origin main
gh run watch  # Watch it hopefully turn green
```

**SHORT TERM (This week)**: Get tests passing, smoke tests green
**MEDIUM TERM (Next 2 weeks)**: Controller repo + test run
**LONG TERM (3-4 weeks)**: Full overnight automation

---

**Bottom line**: You were 100% right to question overnight runs before CI/CD works. Let's fix the foundation first (5-7 days), then we'll have a bulletproof system for safe overnight automation. 🎯
