# Test Fixtures Guide - DatingApp

## Overview

**Real Product Approach**: Professional test data management using API-based seeding with version-controlled JSON fixtures.

This system implements the industry-standard approach used by production applications:
- ✅ **API-based seeding** - Tests business logic, not just database constraints
- ✅ **Version controlled** - Fixtures tracked in Git alongside code
- ✅ **Idempotent** - Safe to re-run without side effects
- ✅ **Deterministic** - Tests use known data for predictable results
- ✅ **Dependency-aware** - Loads data in correct order (Keycloak → Profiles → Swipes → Matches → Messages)

## Quick Start

### One-Command Setup

```bash
# Load minimal test data (5 users, 2 matches, 2 messages)
./scripts/seed-test-data.sh minimal

# Validate fixtures without loading
./scripts/seed-test-data.sh --validate
```

### Available Fixture Sets

| Set | Users | Matches | Use Case |
|-----|-------|---------|----------|
| **minimal** | 5 | 2 | Fast contract testing, CI/CD |
| **standard** | 50 | ~25 | Integration testing, UI development |
| **load** | 500 | ~250 | Performance testing, stress tests |
| **demo** | 10 | 5 | Product demos, stakeholder reviews |

## Architecture

### Component Structure

```
infrastructure/test-fixtures/
├── minimal/                   # Fast test set (< 2s load time)
│   ├── keycloak_users.json   # 5 users (alice, bob, charlie, diana, erik)
│   ├── user_profiles.json    # Complete profiles with Swedish demo data
│   ├── swipes.json           # 7 swipe records
│   ├── matches.json          # 2 pre-configured matches
│   ├── messages.json         # 2 messages in bob↔charlie conversation
│   └── user_photos.json      # Photo metadata (4 photos each for alice/bob/charlie)
├── standard/                  # Standard test set (TODO)
├── load/                      # Load test set (TODO)
└── demo/                      # Demo set (TODO)

scripts/
├── fixture_loader.py          # Python CLI for loading fixtures
└── seed-test-data.sh         # Bash wrapper with health checks
```

### Data Flow

```
1. Keycloak Users Created
   └─> alice@test.se, bob@test.se, charlie@test.se (+ 2 more)
       └─> Keycloak assigns UUIDs

2. UserService Profiles Created
   └─> POST /api/user/profile (authenticated as each user)
       └─> UserService assigns ProfileIds
           └─> SwipeService creates UserProfileMappings (UUID → ProfileId)

3. Swipes Recorded
   └─> POST /api/swipes (authenticated, with idempotency keys)
       └─> SwipeService checks for mutual swipes
           └─> Auto-creates Matches when mutual

4. Messages Sent
   └─> POST /api/messages (requires existing match)
       └─> MessagingService validates match exists via UserProfileMappings
```

## Test Data Reference

### Minimal Fixture Set

#### Users (password: `Test123!`)

| Email | Age | Gender | Occupation | City | Keycloak UUID |
|-------|-----|--------|------------|------|---------------|
| alice@test.se | 28 | F | Photographer | Stockholm | a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d |
| bob@test.se | 32 | M | Musician | Göteborg | b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e |
| charlie@test.se | 30 | M | Fitness Coach | Malmö | c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f |
| diana@test.se | 27 | F | Graphic Designer | Linköping | d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a |
| erik@test.se | 35 | M | Civil Engineer | Uppsala | e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b |

#### Pre-configured Relationships

```
alice ↔ bob
  - Mutual match (both swiped right)
  - Match score: 85.5
  - No messages yet

bob ↔ charlie
  - Mutual match
  - Match score: 78.2
  - 2 messages:
    1. Bob: "Hey Charlie! Great profile! Love the fitness vibe 💪"
    2. Charlie: "Thanks Bob! Saw you're into music too. What concerts have you been to lately?"

alice → charlie
  - Alice swiped LEFT on Charlie
  - No match

charlie → diana
  - Charlie swiped right on Diana
  - Diana hasn't swiped yet (no match)
```

## Usage Guide

### For Integration Tests

**IMPORTANT**: Tests should use fixture users instead of creating random users.

```dart
// ❌ OLD APPROACH - Creates random users (unreliable)
final user1 = await TestUser.random();
final user2 = await TestUser.random();

// ✅ NEW APPROACH - Uses known fixture users
final alice = TestUser.fromFixture('alice@test.se', password: 'Test123!');
final bob = TestUser.fromFixture('bob@test.se', password: 'Test123!');

// Test with known data
expect(await alice.getMatches(), hasLength(1)); // alice ↔ bob
expect(await bob.getMessages('charlie'), hasLength(2)); // Pre-loaded messages
```

### For Manual Testing

```bash
# 1. Load fixtures
./scripts/seed-test-data.sh minimal

# 2. Get auth token
TOKEN=$(curl -s -X POST http://localhost:8080/realms/datingapp/protocol/openid-connect/token \
  -d 'grant_type=password' \
  -d 'username=alice@test.se' \
  -d 'password=Test123!' \
  -d 'client_id=datingapp-client' | jq -r '.access_token')

# 3. Test API
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/user/profile
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/swipes/matches/alice
curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/api/messages/conversations
```

### Expected Database State After Seeding

```sql
-- Keycloak (Postgres)
SELECT COUNT(*) FROM user_entity WHERE realm_id = 'datingapp';  -- 5 users

-- UserService (MySQL port 3308)
SELECT COUNT(*) FROM UserServiceDb.UserProfiles;  -- 5 profiles
SELECT Id, UserId, FirstName FROM UserServiceDb.UserProfiles ORDER BY Id;
-- | Id | UserId (UUID)                        | FirstName |
-- |  1 | a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d | Alice     |
-- |  2 | b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e | Bob       |
-- |  3 | c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f | Charlie   |
-- |  4 | d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a | Diana     |
-- |  5 | e5f6a7b8-c9d0-1e2f-3a4b-5c6d7e8f9a0b | Erik      |

-- SwipeService (MySQL port 3312)
SELECT COUNT(*) FROM SwipeDb.Swipes;  -- 7 swipes
SELECT COUNT(*) FROM SwipeDb.Matches;  -- 2 matches
SELECT COUNT(*) FROM SwipeDb.UserProfileMappings;  -- 5 mappings

-- MatchmakingService (MySQL port 3312)
SELECT COUNT(*) FROM MatchmakingDb.Matches;  -- 2 matches (synced from SwipeService)

-- MessagingService (MySQL port 3312)
SELECT COUNT(*) FROM MessagingDb.Messages;  -- 2 messages
```

## Advanced Usage

### Python CLI Direct Usage

```bash
# Validate fixture files
python3 scripts/fixture_loader.py validate --set minimal

# Load with verbose output
python3 scripts/fixture_loader.py load --set minimal --env demo

# Load to test environment (different ports)
python3 scripts/fixture_loader.py load --set minimal --env test

# Check available commands
python3 scripts/fixture_loader.py --help
```

### Environment Variables

Override default service URLs:

```bash
export KEYCLOAK_URL="http://keycloak.local:8080"
export USER_SERVICE_URL="http://userservice.local:8082"
export SWIPE_SERVICE_URL="http://swipeservice.local:8087"
export MATCHMAKING_SERVICE_URL="http://matchmaking.local:8083"
export MESSAGING_SERVICE_URL="http://messaging.local:8085"

./scripts/seed-test-data.sh minimal
```

## Extending Fixtures

### Adding New Users

Edit `infrastructure/test-fixtures/minimal/keycloak_users.json`:

```json
{
  "users": [
    {
      "id": "f6a7b8c9-d0e1-2f3a-4b5c-6d7e8f9a0b1c",
      "username": "frank",
      "email": "frank@test.se",
      "firstName": "Frank",
      "lastName": "Svensson",
      "enabled": true,
      "emailVerified": true,
      "credentials": [
        {
          "type": "password",
          "value": "Test123!",
          "temporary": false
        }
      ]
    }
  ]
}
```

Then add corresponding profile in `user_profiles.json`, swipes in `swipes.json`, etc.

### Creating New Fixture Sets

```bash
# Copy minimal as template
cp -r infrastructure/test-fixtures/minimal infrastructure/test-fixtures/my-test-set

# Edit JSON files with your data
nano infrastructure/test-fixtures/my-test-set/keycloak_users.json

# Load your custom set
./scripts/seed-test-data.sh my-test-set
```

## Troubleshooting

### "Services are not running"

```bash
# Start infrastructure
./infrastructure/start.sh

# Start services
./dev-start.sh

# Verify all services healthy
./scripts/seed-test-data.sh --validate
```

### "Profile creation failed"

Check UserService logs:

```bash
tail -f UserService/logs/*.log
```

Common causes:
- UserService not connected to database
- JWT token expired (fixture_loader caches tokens)
- API contract mismatch (check if profile JSON matches DTO)

### "Swipe creation failed: UserProfileMappings not found"

This means profiles weren't created in UserService. Verify:

```bash
# Check if profiles exist
mysql -h 127.0.0.1 -P 3308 -u root -proot_password \
  -e "SELECT COUNT(*) as profile_count FROM UserServiceDb.UserProfiles"

# Check if mappings exist
mysql -h 127.0.0.1 -P 3312 -u root -proot_password \
  -e "SELECT COUNT(*) as mapping_count FROM SwipeDb.UserProfileMappings"
```

If count is 0, run seeding again (it's idempotent).

### "Message sending failed: UNAUTHORIZED non-matched users"

This is CORRECT behavior! MessagingService validates that users have an active match before allowing messaging.

Check if match exists:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8087/api/swipes/match/{userId}/{targetUserId}"
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Integration Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start infrastructure
        run: ./infrastructure/start.sh
      
      - name: Start services
        run: ./dev-start.sh
      
      - name: Load test fixtures
        run: ./scripts/seed-test-data.sh minimal
      
      - name: Run integration tests
        run: |
          cd mobile-apps/flutter/dejtingapp
          flutter test integration_test/
```

## Best Practices

### ✅ DO

- Use fixture users in tests (deterministic)
- Re-run `seed-test-data.sh` when fixtures change
- Version control fixture JSON files
- Document expected relationships in fixture comments
- Use idempotency keys for swipes to enable re-runs

### ❌ DON'T

- Create random users in tests (flaky, unreliable)
- Manually INSERT data into databases (bypasses business logic)
- Hard-code UUIDs in tests (use fixture emails instead)
- Modify fixtures during test runs (fixtures should be read-only)
- Forget to load fixtures before running tests

## FAQ

**Q: How long does minimal fixture loading take?**  
A: ~5-10 seconds (Keycloak: 2s, Profiles: 2s, Swipes: 1s, Messages: 1s)

**Q: Can I run fixtures multiple times?**  
A: Yes! Idempotent design - existing users are updated, duplicates prevented.

**Q: What if I need more test users?**  
A: Use `standard` fixture set (50 users) or create custom fixture set.

**Q: Do fixtures work with Flutter integration tests?**  
A: Yes! Update tests to use `TestUser.fromFixture()` instead of `TestUser.random()`.

**Q: How do I reset to clean state?**  
A: Currently: restart services + reload fixtures. Future: `fixture_loader.py clean --set minimal`

**Q: Can I use fixtures in production?**  
A: NO! Fixtures are for **testing only**. Production uses real user registration.

## Next Steps

1. **[IMMEDIATE]** Update integration tests to use fixture users
2. **[WEEK 1]** Create standard/load/demo fixture sets
3. **[WEEK 2]** Implement photo upload fixtures (requires test image files)
4. **[WEEK 3]** Add fixture cleanup command (`clean --set minimal`)
5. **[FUTURE]** Auto-generate fixtures from production anonymized data

---

**Implemented**: 2026-02-01  
**Approach**: Real product standard (API-based, version-controlled, idempotent)  
**Maintainer**: See RUNBOOK.md for operational procedures
