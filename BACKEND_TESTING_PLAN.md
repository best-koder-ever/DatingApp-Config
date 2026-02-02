# Backend Testing & Quality Plan

**Date**: 2026-02-02  
**Decision**: Deprioritize Flutter UI, focus on backend reliability
**Rationale**: Better ROI to have rock-solid backend before UI polish

---

## ✅ Current Backend State (Verified)

### Services Running
- ✅ **UserService** (port 8082)
- ✅ **MatchmakingService** (port 8083)
- ✅ **SwipeService** (port 8084)
- ✅ **MessagingService** (port 8086)
- ❓ **PhotoService** (not detected in ps, may need restart)

### Database Status
**SwipeServiceDb** (Port 3310) - ✅ OPERATIONAL
- UserProfileMappings: 5 records (fixture users)
- Swipes: 12 records
- Matches: 5 active matches

**Other Databases** - ❌ NOT ACCESSIBLE via external ports
- UserServiceDb (Port 3308): Cannot connect
- MatchmakingDb (Port 3309): Cannot connect
- PhotoDb (Port 3311): Cannot connect
- MessagingServiceDb (Port 3306): Cannot connect

**Root Cause**: Likely not exposed in docker-compose or services using local MySQL

### Existing Test Projects
```
UserService.Tests/         5 test files
MatchmakingService.Tests/  4 test files
SwipeService.Tests/        1 test file
MessagingService.Tests/    4 test files
```

**Total**: ~14 test files across 4 services

---

## 🎯 Priority 1: Run & Measure Current Tests (Today - 2 hours)

### Goal
Understand what test coverage we ALREADY have before writing more.

### Tasks

#### 1. Run All Backend Unit Tests
```bash
cd /home/m/development/DatingApp

# Run tests for each service
dotnet test UserService/UserService.Tests/UserService.Tests.csproj --logger "console;verbosity=detailed"
dotnet test MatchmakingService/MatchmakingService.Tests/MatchmakingService.Tests.csproj --logger "console;verbosity=detailed"
dotnet test SwipeService/SwipeService.Tests/SwipeService.Tests.csproj --logger "console;verbosity=detailed"  
dotnet test MessagingService/MessagingService.Tests/MessagingService.Tests.csproj --logger "console;verbosity=detailed"
```

**Expected Output**:
- How many tests pass/fail?
- Which tests are skipped (marked with T003)?
- What's covered vs not covered?

#### 2. Add coverlet.collector for Code Coverage
```bash
# Add to each *.Tests.csproj:
dotnet add UserService/UserService.Tests package coverlet.collector
dotnet add MatchmakingService/MatchmakingService.Tests package coverlet.collector
dotnet add SwipeService/SwipeService.Tests package coverlet.collector
dotnet add MessagingService/MessagingService.Tests package coverlet.collector
```

**Run with coverage**:
```bash
dotnet test --collect:"XPlat Code Coverage" --results-directory ./TestResults
```

**View results**:
```bash
# Install reportgenerator
dotnet tool install -g dotnet-reportgenerator-globaltool

# Generate HTML report
reportgenerator -reports:"./TestResults/*/coverage.cobertura.xml" -targetdir:"./CoverageReport" -reporttypes:Html

# View in browser
xdg-open ./CoverageReport/index.html
```

#### 3. Document Current Coverage
Create `COVERAGE_BASELINE.md`:
```
UserService:        X% coverage (Y/Z lines)
MatchmakingService: X% coverage
SwipeService:       X% coverage
MessagingService:   X% coverage

Critical gaps:
- [ ] ProfileController methods not tested
- [ ] Exception handling not covered
- [ ] Validation logic incomplete
```

---

## 🎯 Priority 2: Fix Database Access for Testing (1 hour)

### Problem
Cannot connect to most databases from test scripts. This blocks:
- Integration tests
- Data seeding verification
- AI helper scripts (ai-verify-state.py)

### Solutions

**Option A: Use Services' Internal Databases** (RECOMMENDED)
Services are running and using MySQL. Check their connection strings:
```bash
# Check each service's appsettings
cat UserService/appsettings.Development.json | grep ConnectionString
cat MatchmakingService/appsettings.Development.json | grep ConnectionString
cat messaging-service/appsettings.Development.json | grep ConnectionString
```

**Option B: Start Docker Databases**
```bash
# Check if docker-compose defines databases
cat docker-compose.yml | grep -A 5 "UserService-db"

# If defined, start them:
docker-compose up -d UserService-db MatchmakingService-db MessagingService-db PhotoService-db
```

**Option C: Use In-Memory Databases for Tests**
- Update test projects to use `Microsoft.EntityFrameworkCore.InMemory`
- Tests create their own isolated databases
- No external dependencies

**Decision**: Start with Option A (use existing databases), then add Option C for fast unit tests.

---

## 🎯 Priority 3: Complete T004 (CI/CD Coverage Gates) (2 hours)

### Current Status
- ✅ CI/CD workflow exists (.github/workflows/comprehensive-ci-cd.yml)
- ✅ Badge added to README.md
- ⏳ Coverage gates NOT enforced (80% threshold)

### Implementation

#### Step 1: Update CI/CD Workflow
Add coverage requirements to `.github/workflows/comprehensive-ci-cd.yml`:

```yaml
- name: Run tests with coverage
  run: dotnet test --collect:"XPlat Code Coverage" --results-directory ./TestResults

- name: Check coverage threshold
  run: |
    dotnet tool install -g dotnet-reportgenerator-globaltool
    reportgenerator -reports:"./TestResults/*/coverage.cobertura.xml" -targetdir:"./CoverageReport" -reporttypes:Html
    
    # Parse coverage percentage
    COVERAGE=$(grep -oP 'Line coverage: \K[0-9.]+' ./CoverageReport/index.html | head -1)
    echo "Coverage: $COVERAGE%"
    
    if (( $(echo "$COVERAGE < 80" | bc -l) )); then
      echo "❌ Coverage $COVERAGE% is below 80% threshold"
      exit 1
    else
      echo "✅ Coverage $COVERAGE% meets threshold"
    fi
```

#### Step 2: Add Coverage Badge
```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./TestResults/*/coverage.cobertura.xml
    fail_ci_if_error: true
```

Update README.md:
```markdown
[![codecov](https://codecov.io/gh/yourusername/DatingApp/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/DatingApp)
```

#### Step 3: Configure per-service thresholds
Create `coverlet.runsettings`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<RunSettings>
  <DataCollectionRunSettings>
    <DataCollectors>
      <DataCollector friendlyName="XPlat Code Coverage">
        <Configuration>
          <Format>cobertura,opencover</Format>
          <Threshold>80</Threshold>
          <ThresholdType>line,branch</ThresholdType>
          <ThresholdStat>total</ThresholdStat>
        </Configuration>
      </DataCollector>
    </DataCollectors>
  </DataCollectionRunSettings>
</RunSettings>
```

Run with: `dotnet test --settings coverlet.runsettings`

---

## 🎯 Priority 4: Strategic Test Improvements (3-4 hours)

**NOT**: Write tests blindly
**DO**: Identify highest-risk, highest-value areas

### Risk-Based Testing Matrix

| Service          | Critical Paths                     | Current Coverage | Priority |
|------------------|------------------------------------|------------------|----------|
| UserService      | Profile creation, photo upload     | Unknown          | P1       |
| MatchmakingService | Scoring algorithm, candidate query | Unknown          | P1       |
| SwipeService     | Swipe processing, match detection  | Unknown          | P1       |
| MessagingService | Message delivery, read receipts    | Unknown          | P2       |
| PhotoService     | Moderation pipeline, storage       | Unknown          | P2       |

### Test Types Needed

**1. Unit Tests** (Fast, isolated)
- Controller action methods
- Business logic (scoring, matching)
- Validation rules
- Error handling

**2. Integration Tests** (Slower, database-backed)
- End-to-end user flows
- Database transactions
- Service-to-service calls
- Authentication/authorization

**3. Contract Tests** (API compatibility)
- Request/response schemas
- Error codes
- Versioning behavior

### Example: Matchmaking Service Test Plan

**High Priority**:
```csharp
// MatchmakingService.Tests/ScoringTests.cs
[Fact]
public void CalculateCompatibilityScore_SameNeighborhood_Adds20Points() {
    // Given two profiles in same neighborhood
    // When scoring
    // Then score includes +20 for proximity
}

[Fact]
public void CalculateCompatibilityScore_SharedInterests_AddsPerInterest() {
    // Given two profiles with overlapping interests
    // When scoring
    // Then score increases by 10 per shared interest
}

[Fact]
public void GetCandidates_ExcludesBlockedUsers_Always() {
    // Given blocked users exist
    // When fetching candidates
    // Then blocked users never appear
}
```

**Medium Priority**:
```csharp
[Fact]
public void GetCandidates_RespectsAgePreferences() {
    // Given age preferences set
    // When fetching candidates
    // Then only candidates in age range returned
}
```

---

## 🎯 Priority 5: Python Integration Test Improvements (2 hours)

### Current State
- ✅ api_tests.py exists (777 lines)
- ✅ Tests auth, profile, match, messaging
- ❌ No pytest framework
- ❌ No structured reporting
- ❌ No CI integration

### Improvements

#### 1. Convert to pytest
```python
# tests/integration/test_profile_flow.py
import pytest
import requests

@pytest.fixture
def api_base_url():
    return "http://localhost:8080"

@pytest.fixture
def authenticated_user(api_base_url):
    # Login and return token
    response = requests.post(f"{api_base_url}/auth/login", json={
        "username": "alice@test.com",
        "password": "password123"
    })
    return response.json()["access_token"]

def test_create_profile_success(api_base_url, authenticated_user):
    response = requests.post(
        f"{api_base_url}/api/profiles",
        headers={"Authorization": f"Bearer {authenticated_user}"},
        json={
            "firstName": "Alice",
            "age": 28,
            "movedToCity": "2024-01-15"
        }
    )
    assert response.status_code == 201
    assert response.json()["firstName"] == "Alice"

def test_create_profile_missing_required_field(api_base_url, authenticated_user):
    response = requests.post(
        f"{api_base_url}/api/profiles",
        headers={"Authorization": f"Bearer {authenticated_user}"},
        json={"firstName": "Alice"}  # Missing age
    )
    assert response.status_code == 400
    assert "age" in response.json()["errors"]
```

#### 2. Add to CI/CD
```yaml
- name: Run integration tests
  run: |
    pip install pytest requests
    pytest tests/integration/ --junitxml=test-results.xml
```

---

## 📋 Action Plan Summary

### Week 1: Measure & Fix (8-10 hours)
- [x] Day 1: Document backend state ✅
- [ ] Day 2: Run all tests, measure coverage (2h)
- [ ] Day 3: Fix database access for tests (1h)
- [ ] Day 3: Add coverage gates to CI/CD (2h)
- [ ] Day 4: Identify coverage gaps (1h)
- [ ] Day 5: Write high-priority missing tests (3h)

### Week 2: Strategic Testing (6-8 hours)
- [ ] Convert python API tests to pytest (2h)
- [ ] Add integration test suite for MatchmakingService (3h)
- [ ] Add contract tests for critical APIs (2h)
- [ ] Generate coverage reports for stakeholders (1h)

### Success Metrics
- ✅ All 4 backend services have >80% code coverage
- ✅ CI/CD pipeline enforces coverage gates
- ✅ Critical user paths have integration tests
- ✅ Can run all tests locally in <2 minutes
- ✅ Coverage reports visible in README badge

---

## 🚫 Deferred (NOT MVP Critical)

### Postponed Testing Features
- ❌ Load testing with Locust (Phase 8)
- ❌ E2E browser automation (Phase 8)
- ❌ Bot simulation framework (Phase 11)
- ❌ Grafana test dashboards (Phase 8)
- ❌ Allure reporting (nice-to-have)

**Rationale**: Better ROI to:
1. Get backend to 80% coverage
2. Launch beta with 10-50 users
3. Collect real usage data
4. THEN invest in comprehensive test automation

---

## 💡 Design Decision: Compatibility Score

**User Feedback**: "Maybe only as premium option, not default"

**Implications for Testing**:
- Core matching algorithm still needs tests (P1)
- Score calculation can be feature-flagged
- Premium vs free tier logic needs tests (P2)

**Recommended Approach**:
1. Build matching algorithm with scoring (testable)
2. Feature-flag score visibility: `showCompatibilityScore: isPremium` 3. Test both code paths (premium ON/OFF)
4. Launch MVP without showing score (reduces UI complexity)
5. A/B test score visibility with first 100 users

**Testing Impact**:
```csharp
[Theory]
[InlineData(true)]  // Premium user sees score
[InlineData(false)] // Free user doesn't see score
public void GetCandidates_CompatibilityScore_RespectsFeatureFlag(bool isPremium) {
    // Given user with premium status
    // When fetching candidates
    // Then score included/excluded based on premium status
}
```

---

**Next Action**: Run existing tests and measure coverage (2 hours)

```bash
cd /home/m/development/DatingApp

# Install coverage tool
dotnet add UserService/UserService.Tests package coverlet.collector
dotnet add MatchmakingService/MatchmakingService.Tests package coverlet.collector
dotnet add SwipeService/SwipeService.Tests package coverlet.collector
dotnet add MessagingService/MessagingService.Tests package coverlet.collector

# Run tests with coverage
dotnet test --collect:"XPlat Code Coverage" --results-directory ./TestResults

# Generate report
dotnet tool install -g dotnet-reportgenerator-globaltool
reportgenerator -reports:"./TestResults/*/coverage.cobertura.xml" -targetdir:"./CoverageReport" -reporttypes:Html

# View
xdg-open ./CoverageReport/index.html
```

**Last Updated**: 2026-02-02  
**Owner**: Solo developer focusing on backend quality before UI polish
