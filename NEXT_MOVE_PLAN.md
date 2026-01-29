# Next Move Plan - Testing Infrastructure Transformation

**Created**: January 28, 2026  
**Priority**: CRITICAL - Foundation for Professional MVP  
**Timeline**: 3-4 weeks to transform testing approach

---

## 🎯 DECISION TIME: What to Build First?

You have **THREE viable paths**. I recommend Option 1.

### Option 1: Start with Test Infrastructure (RECOMMENDED) ⭐
**Timeline**: 1 week  
**Impact**: Highest - enables everything else  
**Risk**: Lowest - validates backend before UI work

**What you get**:
- Professional test data (no more hacky seeders)
- Confidence in backend APIs
- Foundation for all future testing
- CI/CD quality gates

**Start with**: Phase A tasks (test fixtures + API test suite)

### Option 2: Vanilla Flutter Harness First
**Timeline**: 1 week  
**Impact**: Medium - validates integration  
**Risk**: Medium - might discover backend issues late

**What you get**:
- Quick integration validation
- Debugging tool for API issues
- Foundation for integration tests

**Challenge**: Still need professional test data

### Option 3: Jump to Production UI
**Timeline**: 2-3 weeks  
**Impact**: Visible but risky  
**Risk**: HIGH - building on unvalidated foundation

**Not recommended because**:
- Backend APIs not proven
- No automated testing safety net
- Will waste time on debugging UI when issue is backend
- Hard to validate contracts

---

## ✅ RECOMMENDED: Start with Phase A (Test Infrastructure)

### Week 1: Foundation (Phase A tasks)

#### Day 1-2: Database Fixture Strategy
- [ ] **T-A1.1**: Design fixture system
  - Review current data models across services
  - Choose format (recommend: JSON for flexibility)
  - Create `infrastructure/test-fixtures/` structure
  - Document loading strategy

- [ ] **T-A1.2**: Create minimal fixture set (5 users, 2 matches)
  - Keycloak users (JSON)
  - UserService profiles (SQL/JSON)
  - MatchmakingService matches (SQL/JSON)
  - SwipeService swipes (SQL/JSON)
  - PhotoService metadata (SQL/JSON)

**Outcome**: Can load repeatable test data in <10 seconds

#### Day 3-4: Fixture Loader Tool
- [ ] **T-A1.3**: Build CLI tool
  - Language: Python (leverage existing patterns)
  - Commands: `load`, `reset`, `validate`
  - Supports: MySQL, Keycloak API
  - Error handling + rollback
  
**Outcome**: `./test-data load minimal` works reliably

#### Day 5: Docker Integration + Documentation
- [ ] **T-A1.4**: Test environment docker-compose
  - Create `docker-compose.test.yml`
  - Separate databases for test vs dev
  - Auto-load fixtures on startup
  - Network isolation

- [ ] **Documentation**: Update RUNBOOK.md with test data workflows

**Week 1 Checkpoint**: ✅ Professional test data infrastructure operational

---

### Week 2: API Testing + Vanilla Harness (Phase A2 + Phase B)

#### Day 6-8: Comprehensive API Tests
- [ ] **T-A2.1**: OpenAPI spec generation
  - Add Swashbuckle to all services
  - Generate specs automatically
  - Validate against contracts/api-spec.md

- [ ] **T-A2.2**: Backend API test suite
  - Framework: pytest + requests
  - Coverage: All endpoints (50+ tests)
  - Fixtures: Use new test data system
  - Assertions: Status codes, schemas, performance

**Outcome**: `pytest tests/api/` validates all backend services

#### Day 9-10: Vanilla Flutter Harness (Optional but Recommended)
- [ ] **T-B1.1**: Create vanilla-test-harness project
  - Minimal Flutter app
  - No styling, just functionality
  - Direct HTTP calls (no abstractions)

- [ ] **T-B1.2**: Basic screens
  - Login (Keycloak)
  - Profile form
  - Swipe buttons
  - Match list
  - Photo upload

**Week 2 Checkpoint**: ✅ Backend APIs proven + Integration harness ready

---

### Week 3: Bot Framework (Phase C1)

#### Day 11-13: Headless API Bot
- [ ] **T-C1.1**: Bot architecture
  - Python framework
  - YAML scenario configs
  - Multi-user orchestration

- [ ] **T-C1.2**: Core bot capabilities
  - User registration (Keycloak)
  - Profile creation
  - Swiping logic
  - Matching detection
  - Messaging

- [ ] **T-C1.3**: Happy path scenario
  - Full journey: Register → Match → Message
  - 10 synthetic users
  - Realistic timing

**Week 3 Checkpoint**: ✅ Automated user journey validation working

---

### Week 4: Production UI (Phase D) - Only After Validation

#### Day 14-18: Build Real Flutter App
- [ ] **T-D1.1**: Design system
  - Extract components from existing or start fresh
  - Widgetbook for component preview
  
- [ ] **T-D1.2**: Implement features
  - Use **validated** API contracts from Phase A
  - Reference patterns from vanilla harness
  - Add proper state management
  - Polish UI/UX

**Week 4 Checkpoint**: ✅ Production app built on solid foundation

---

## 🚀 IMMEDIATE ACTIONS (Today - Next 2 Hours)

### Action 1: Validate Strategy (30 min)
Read [TESTING_INFRASTRUCTURE_STRATEGY.md](TESTING_INFRASTRUCTURE_STRATEGY.md) and decide:
- ✅ Agree with 4-layer approach?
- ✅ Start with Phase A (test infrastructure)?
- ✅ Timeline acceptable (1 week per phase)?

### Action 2: Setup Test Fixtures Directory (15 min)

```bash
cd /home/m/development/DatingApp

# Create directory structure
mkdir -p infrastructure/test-fixtures/{minimal,standard,load,demo}
mkdir -p infrastructure/test-fixtures/schemas
mkdir -p infrastructure/test-data-loader

# Document the approach
cat > infrastructure/test-fixtures/README.md << 'FIXTURES_EOF'
# Test Data Fixtures

## Fixture Sets

- **minimal**: 5 users, 2 matches - Fast unit tests
- **standard**: 50 users, 20 matches - Integration tests  
- **load**: 1000 users, 500 matches - Performance tests
- **demo**: 10 curated personas - Stakeholder demos

## Usage

\`\`\`bash
# Load minimal fixture into test database
./test-data load minimal --env test

# Reset and reload
./test-data reset --env test
./test-data load standard --env test
\`\`\`

## Format

Fixtures are JSON files matching service data models:
- users.json - Keycloak users
- profiles.json - UserService profiles
- matches.json - MatchmakingService matches
- swipes.json - SwipeService swipe history
- photos.json - PhotoService metadata
FIXTURES_EOF

echo "✅ Test fixtures directory created"
```

### Action 3: Analyze Current Data Models (30 min)

```bash
# Find all data models across services
cd /home/m/development/DatingApp
grep -r "public class.*" UserService/Models/ --include="*.cs"
grep -r "public class.*" MatchmakingService/Models/ --include="*.cs"
grep -r "public class.*" SwipeService/Models/ --include="*.cs"
grep -r "public class.*" photo-service/Models/ --include="*.cs"
grep -r "public class.*" messaging-service/Models/ --include="*.cs"

# Document for fixture creation
cat > infrastructure/test-fixtures/schemas/data-models.md << 'MODELS_EOF'
# Service Data Models (for Fixture Creation)

## UserService
- UserProfile
- Wizard steps

## MatchmakingService  
- Match
- CompatibilityScore

## SwipeService
- Swipe
- SwipeHistory

## PhotoService
- Photo
- PrivacySettings

## MessagingService
- Message
- Conversation
MODELS_EOF
```

### Action 4: Create First Minimal Fixture (45 min)

Start with simplest fixture - 2 users who can match:

```bash
cd /home/m/development/DatingApp/infrastructure/test-fixtures/minimal

# Create fixture files (we'll add real AI-generated content after)
touch users.json profiles.json matches.json swipes.json photos.json
```

I'll help you generate these in the next step!

---

## 📝 Tasks to Add to tasks.md

When ready, integrate these into your MVP plan:

**Insert into Phase 0** (after T008):
```markdown
### Test Data Infrastructure
- [ ] T009.1 [P0] Design professional fixture strategy (infrastructure/test-fixtures/)
- [ ] T009.2 [P0] Create minimal test fixture set (5 users, 2 matches)
- [ ] T009.3 [P0] Build test-data loader CLI tool
- [ ] T009.4 [P1] Docker-compose test environment integration
- [ ] T009.5 [P2] Deprecate smart_demo_seeder_fixed.py
```

**Insert into Phase 8** (enhance existing tasks):
```markdown
### Enhanced E2E Testing (expands T077-T078)
- [ ] T077.0 [P1] Build vanilla Flutter test harness (integration debugging)
- [ ] T078.1 [P1] Headless API bot framework (Python, YAML scenarios)
- [ ] T078.2 [P2] Visual Flutter bot runner (demo videos)
```

---

## 🎯 Success Criteria

### End of Week 1
- ✅ Test fixtures load in <10s
- ✅ Can reset databases to known state
- ✅ Documentation explains fixture usage
- ✅ smart_demo_seeder_fixed.py deprecated

### End of Week 2
- ✅ 80%+ API endpoint coverage with tests
- ✅ CI runs API tests on every PR
- ✅ Vanilla harness validates integration

### End of Week 3
- ✅ Bots simulate 10+ user journeys
- ✅ Happy path runs successfully end-to-end
- ✅ Automated daily bot runs

### End of Week 4
- ✅ Production Flutter app passes all bot tests
- ✅ UI matches design system
- ✅ Ready for user acceptance testing

---

## ❓ Decision Needed From You

**QUESTION 1**: Do you want to start with Phase A (test infrastructure)?  
**QUESTION 2**: Should I generate the minimal fixture set now (2 users JSON)?  
**QUESTION 3**: Keep existing dejtingapp or build fresh on validated foundation?

Let me know and I'll help execute! 🚀

