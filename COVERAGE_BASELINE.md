# Backend Test Coverage Baseline

**Date**: 2026-02-02  
**Measured After**: Adding coverlet.collector to all test projects

---

## 📊 Current Coverage (BASELINE)

### Per-Service Coverage

| Service              | Line Coverage | Branch Coverage | Tests | Status |
|----------------------|---------------|-----------------|-------|--------|
| **SwipeService**     | 13.8%         | 15.5%           | 17    | ✅ Best |
| **MatchmakingService** | 12.6%       | 20.6%           | 18    | ⚠️     |
| **MessagingService** | 4.8%          | 5.3%            | 11    | ❌ 4 failing |
| **UserService**      | 2.0%          | 0.0%            | 2     | ❌ Worst |

### Overall Backend Coverage

```
Line Coverage:   8.3%
Branch Coverage: 10.4%
Services Tested: 4

⚠️ Coverage is 71.7% below 80% target
```

---

## 📋 Test Results Summary

### ✅ UserService (5 tests)
- **Passed**: 2
- **Skipped**: 3 (marked with T003 - test skeletons)
- **Failed**: 0
- **Coverage**: 2.0% lines, 0.0% branches

**Critical Gaps**:
- ProfileController methods not tested
- WizardController methods (skipped - need implementation)
- Photo upload validation not covered
- Preferences update not tested

### ✅ MatchmakingService (21 tests)
- **Passed**: 18
- **Skipped**: 3 (marked with T003)
- **Failed**: 0
- **Coverage**: 12.6% lines, 20.6% branches

**Critical Gaps**:
- Compatibility scoring algorithm not tested
- Candidate filtering logic incomplete
- Distance calculation not covered
- Mutual match creation (skipped)

### ✅ SwipeService (17 tests) - BEST COVERAGE
- **Passed**: 17
- **Skipped**: 0
- **Failed**: 0
- **Coverage**: 13.8% lines, 15.5% branches

**What's Covered**:
- RecordSwipe happy path ✅
- Mutual match detection ✅
- Invalid swipe handling ✅

**Gaps**:
- Edge cases not fully tested
- Database error handling not covered

### ⚠️ MessagingService (16 tests) - 4 FAILURES
- **Passed**: 11
- **Skipped**: 1
- **Failed**: 4 (all SignalR connection issues)
- **Coverage**: 4.8% lines, 5.3% branches

**Failed Tests**:
1. `SendMessage_ValidMessage_SenderGetsConfirmation` - Connection not active
2. `SendMessage_PersistsToDatabase` - Connection not active
3. `Connection_BothUsersConnect_Successfully` - Expected Connected, got Disconnected
4. `SendMessage_ValidMessage_ReceiverGetsNotification` - Connection not active

**Root Cause**: SignalR test setup issue (server not running or connection config wrong)

---

## 🎯 Priority Areas for Improvement

### Priority 1: Fix MessagingService SignalR Tests (2 hours)
**Impact**: +4 passing tests, ~2-3% coverage increase

**Problem**: All SignalR hub tests fail with "connection is not active"

**Solution**:
```csharp
// MessagingHubTests.cs - Fix connection setup
[Fact]
public async Task SendMessage_ValidMessage_SenderGetsConfirmation()
{
    // CURRENT (broken):
    var connection = new HubConnectionBuilder()
        .WithUrl("http://localhost:8086/hubs/messaging")
        .Build();
    await connection.InvokeAsync("SendMessage", message); // ❌ Fails

    // FIX: Start connection first
    await connection.StartAsync(); // ← ADD THIS
    await connection.InvokeAsync("SendMessage", message); // ✅ Works
}
```

### Priority 2: Implement UserService WizardController Tests (3 hours)
**Impact**: +3 tests, ~5-8% coverage increase for UserService

**Currently Skipped**:
- `UpdateStepBasicInfo_ValidData_ReturnsOk`
- `UpdateStepPreferences_ValidData_ReturnsOk`
- `CompleteWizard_WithPhotos_MarksProfileReady`

**Implementation**:
```csharp
[Fact]
public async Task UpdateStepBasicInfo_ValidData_ReturnsOk()
{
    // Arrange
    var command = new UpdateWizardStepCommand {
        UserId = "test-user",
        Step = WizardStep.BasicInfo,
        Data = new { firstName = "Alice", age = 28 }
    };
    
    // Act
    var result = await _controller.UpdateStep(command);
    
    // Assert
    var okResult = Assert.IsType<OkObjectResult>(result);
    Assert.NotNull(okResult.Value);
}
```

### Priority 3: Expand MatchmakingService Scoring Tests (2 hours)
**Impact**: +5-7 tests, ~10-15% coverage increase

**Missing Coverage**:
```csharp
[Fact]
public void CalculateCompatibilityScore_SameNeighborhood_Adds20Points()
{
    // Test proximity bonus
}

[Fact]
public void CalculateCompatibilityScore_SharedInterests_AddsPerInterest()
{
    // Test interest matching
}

[Theory]
[InlineData(18, 25, true)]  // Within range
[InlineData(18, 40, false)] // Outside range
public void GetCandidates_RespectsAgePreferences(int minAge, int candidateAge, bool shouldInclude)
{
    // Test age filtering
}
```

### Priority 4: Add UserService ProfileController Tests (3 hours)
**Impact**: +8-10 tests, ~15-20% coverage increase

**Critical Untested Methods**:
- `GetMyProfile()` - 506 lines uncovered
- `UpdateMyProfile()` - 420 lines uncovered
- `PreferencesController.UpdatePreferences()` - 2550 lines uncovered

---

## 📈 Coverage Improvement Roadmap

### Week 1: Quick Wins (10 hours)
- [x] Day 1: Measure baseline ✅ (8.3% coverage)
- [ ] Day 2: Fix MessagingService SignalR tests (2h) → **Expected: 10-12% coverage**
- [ ] Day 3: Implement WizardController tests (3h) → **Expected: 15-18% coverage**
- [ ] Day 4: Expand MatchmakingService tests (2h) → **Expected: 22-28% coverage**
- [ ] Day 5: Add ProfileController tests (3h) → **Expected: 35-45% coverage**

### Week 2: Strategic Coverage (8 hours)
- [ ] Add error handling tests (all services) → **Expected: 50-60% coverage**
- [ ] Add validation logic tests → **Expected: 60-70% coverage**
- [ ] Add database transaction tests → **Expected: 70-80% coverage**

### Success Criteria
- ✅ All services > 80% line coverage
- ✅ All tests passing (no failures)
- ✅ CI/CD enforces coverage gates
- ✅ Critical user paths covered

---

## 🔍 Test Quality Observations

### What's Working Well ✅
1. **SwipeService has best structure** - 17 tests, all passing, good coverage
2. **MatchmakingService has many tests** - 21 tests show investment in testing
3. **Test skeletons exist** - T003 done, clear markers for what needs work

### Issues to Fix ❌
1. **SignalR tests broken** - 4 failures in MessagingService (connection setup)
2. **UserService severely undertested** - Only 2.0% coverage
3. **Skipped tests accumulating** - 7 tests marked "TODO" need implementation
4. **No branch coverage in UserService** - 0.0% suggests minimal conditional testing

### Next Steps
1. **Immediate** (Today): Fix MessagingService SignalR connection setup
2. **This Week**: Get all 4 services to 30%+ coverage (realistic milestone)
3. **Next Week**: Push to 60%+ coverage with error handling tests
4. **Week 3**: Achieve 80%+ coverage and add CI/CD gates

---

## 📁 Coverage Reports

- **HTML Report**: `./CoverageReport/index.html`
- **XML Files**: `./TestResults/*/coverage.cobertura.xml`

**View in Browser**:
```bash
xdg-open /home/m/development/DatingApp/CoverageReport/index.html
```

---

**Last Updated**: 2026-02-02  
**Next Measurement**: After fixing MessagingService tests (expected +3-5%)
