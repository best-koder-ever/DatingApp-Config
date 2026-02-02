# Test Automation Guide

How to automate fixture loading and testing in the DatingApp project.

## Quick Start

```bash
# Install the Makefile (already done!)
# Now just use simple commands:

make test-clean    # Reset DB + seed + run tests (recommended)
make test          # Run tests with current data
make quick-reset   # Fast reset + seed (for development)
```

## 🎯 Professional Automation Methods

### Method 1: Makefile (Recommended for Development)

**What it does:** Provides simple commands that encapsulate complex workflows.

```bash
# Morning setup
make dev-start      # Start all services
make seed-minimal   # Load test data

# During development
make test           # Run tests
make quick-reset    # Quick cleanup + re-seed

# Before committing
make test-clean     # Full clean slate test
```

**Benefits:**
- ✅ Team consistency (everyone uses same commands)
- ✅ Documented workflows
- ✅ Quick iterations

**See:** `Makefile` in project root

---

### Method 2: Flutter Test Hooks (Automatic Setup)

**What it does:** Automatically loads fixtures when tests start.

```dart
// integration_test/my_test.dart
import 'helpers/test_environment.dart';

void main() {
  setUpAll(() async {
    // Automatically checks services + loads fixtures!
    await TestEnvironment.setupSuite(fixtureSet: 'minimal');
  });
  
  tearDownAll(() {
    TestEnvironment.teardownSuite();
  });
  
  testWidgets('My test', (tester) async {
    // Fixtures already loaded - just test!
  });
}
```

**Benefits:**
- ✅ No manual seeding needed
- ✅ Tests self-contained
- ✅ Automatic health checks

**See:** `integration_test/helpers/test_environment.dart`

---

### Method 3: GitHub Actions CI/CD (Automatic on Push)

**What it does:** Runs tests automatically on every push/PR.

**Workflow:**
1. Push code to GitHub
2. GitHub Actions starts
3. Spins up services
4. Seeds fixtures
5. Runs all tests
6. Reports results

**Benefits:**
- ✅ Catches issues before merge
- ✅ Fresh environment every time
- ✅ No local setup needed for reviewers

**See:** `.github/workflows/integration-tests.yml`

---

### Method 4: Docker Compose Test Profile

**What it does:** One command to start everything with fixtures.

```bash
# Start with automatic fixture loading
docker-compose --profile test up

# Everything is ready:
# - Services running
# - Databases created
# - Fixtures loaded
# - Health checks passing
```

**Benefits:**
- ✅ Fully automated environment
- ✅ Isolated from dev environment
- ✅ CI/CD compatible

**See:** `docker-compose.test.yml`

---

### Method 5: Pre-commit Hooks (Before Commit)

**What it does:** Automatically runs checks before you commit code.

```bash
# Enable the hook (one-time setup):
chmod +x .git/hooks/pre-commit

# Now every time you commit:
git commit -m "My changes"

# Hook automatically:
# - Checks for sensitive data
# - Runs API tests (if services running)
# - Validates code quality
```

**Benefits:**
- ✅ Prevents bad commits
- ✅ Catches issues early
- ✅ Enforces quality standards

**See:** `.git/hooks/pre-commit`

---

## 📊 Comparison: When to Use Each Method

| Method | Use Case | Speed | Automation Level |
|--------|----------|-------|------------------|
| **Makefile** | Day-to-day development | ⚡⚡⚡ Fast | Semi-automatic |
| **Flutter Hooks** | Writing new tests | ⚡⚡ Medium | Fully automatic |
| **GitHub Actions** | CI/CD, PR validation | ⚡ Slow (clean env) | Fully automatic |
| **Docker Profile** | Isolated testing | ⚡⚡ Medium | Fully automatic |
| **Pre-commit** | Before committing | ⚡⚡⚡ Fast | Fully automatic |

---

## 🏭 Industry Best Practices (What Professionals Do)

### Approach 1: Test Framework Integration (Most Common)

```dart
// What Netflix, Airbnb, Google do

class IntegrationTestSuite {
  @BeforeAll
  static void setupEnvironment() {
    // Load fixtures once before all tests
    loadFixtures('minimal');
  }
  
  @BeforeEach
  void resetState() {
    // Optional: reset between tests
  }
  
  @AfterAll
  static void cleanup() {
    // Optional: cleanup after tests
  }
}
```

**Used by:** Flutter's `setUpAll()`, Jest's `beforeAll()`, pytest's fixtures

---

### Approach 2: Database Seeder in Application Code

```csharp
// What Laravel, Rails, Django do

// Program.cs (SwipeService)
if (app.Environment.IsDevelopment() || app.Environment.IsStaging())
{
    using var scope = app.Services.CreateScope();
    var seeder = scope.ServiceProvider.GetRequiredService<DatabaseSeeder>();
    
    if (args.Contains("--seed"))
    {
        await seeder.SeedAsync("minimal");
    }
}
```

**Benefits:**
- Seeders are version-controlled with code
- Can be run as part of startup
- Type-safe (no external scripts)

---

### Approach 3: CI/CD Pipeline (Enterprise Standard)

```yaml
# What Microsoft, Amazon, Meta do

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
      - name: Start database
      - name: Run migrations
      - name: Seed test data  ← Automatic!
      - name: Run tests
      - name: Cleanup
```

**Benefits:**
- Runs on every PR
- Parallel test execution
- Matrix testing (multiple environments)

---

### Approach 4: Test Containers (Modern Approach)

```dart
// What Spring Boot, Testcontainers do

testWidgets('Integration test', (tester) async {
  // Automatically spins up containers with fixtures!
  await TestContainers.start(
    services: ['mysql', 'keycloak'],
    seed: 'minimal'
  );
  
  // Test code...
  
  await TestContainers.stop(); // Auto cleanup
});
```

**Benefits:**
- Isolated per test
- Parallel execution
- Clean state guaranteed

---

## 🚀 Recommended Setup for DatingApp

### For Daily Development:
```bash
# Once per morning:
make dev-start
make seed-minimal

# During development:
make test
```

### For Writing New Tests:
```dart
// Add to test file:
setUpAll(() async {
  await TestEnvironment.setupSuite();
});
```

### For CI/CD:
- GitHub Actions workflow already configured ✅
- Runs automatically on push/PR
- No manual intervention needed

### Before Committing:
```bash
# Pre-commit hook runs automatically
git commit -m "feat: my changes"

# Or manually:
make test-clean
```

---

## 💡 Migration Path: From Manual to Automatic

### Current State (Manual):
```bash
./infrastructure/start.sh
./scripts/seed-test-data.sh minimal
cd mobile-apps/flutter/dejtingapp
flutter test integration_test/
```

### Step 1: Use Makefile
```bash
make test-clean  # Encapsulates all above steps
```

### Step 2: Add to Tests
```dart
// Tests become self-contained
setUpAll(() async {
  await TestEnvironment.setupSuite();
});
```

### Step 3: Enable Pre-commit
```bash
chmod +x .git/hooks/pre-commit
# Now automatic on every commit
```

### Step 4: Push to GitHub
```bash
git push
# CI/CD runs tests automatically
```

---

## 🎓 Learning from Industry Leaders

### Google
- Uses Bazel for build + test orchestration
- Hermetic tests (fully isolated)
- Fixture data in code repositories

### Netflix
- Uses Buildkite for CI/CD
- Database snapshots for fixtures
- Parallel test execution (thousands of tests)

### Airbnb
- Jest + React Testing Library
- Mock Service Worker for API fixtures
- Storybook for component testing

### Our Approach (Best for Microservices)
- Makefile for developer workflows ✅
- Test framework hooks for automation ✅
- CI/CD for validation ✅
- Docker for isolation ✅
- Git hooks for quality gates ✅

---

## 📚 Further Reading

- [Martin Fowler: Testing Strategies](https://martinfowler.com/testing/)
- [Google Testing Blog](https://testing.googleblog.com/)
- [Flutter Integration Testing](https://docs.flutter.dev/testing/integration-tests)
- [Database Test Patterns](https://www.testcontainers.org/)

---

## 🤝 Contributing

When adding new tests:
1. Use `TestEnvironment.setupSuite()` in `setUpAll()`
2. Document required fixtures in test comments
3. Ensure tests pass with `make test-clean`
4. CI will validate automatically on PR
