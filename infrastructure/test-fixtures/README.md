# Test Fixtures Documentation

**Version**: 1.0.0  
**Last Updated**: 2026-01-28  
**Purpose**: Professional JSON-based test data for systematic backend validation

## Overview

Test fixtures replace the legacy `TestDataGenerator` with declarative, version-controlled JSON data. Fixtures are idempotent: loading the same fixture set twice produces identical database state.

## Fixture Sets

### 1. Minimal (`minimal/`)
**Purpose**: Fast contract testing, CI/CD  
**Size**: 5 users, 10 profiles, 20 photos, 3 matches  
**Load Time**: <30 seconds  
**Use Cases**:
- Unit test fixtures
- Contract test validation
- Quick local development
- GitHub Actions CI/CD

**Users**:
- `alice@test.se` - Complete profile, 4 photos
- `bob@test.se` - Complete profile, 3 photos
- `charlie@test.se` - Complete profile, 4 photos
- `diana@test.se` - Partial profile (wizard incomplete)
- `erik@test.se` - Just registered (no profile)

**Pre-configured Matches**:
- Alice ↔ Bob (mutual match, no messages)
- Bob ↔ Charlie (mutual match, 2 messages)
- Diana → Erik (one-way like, no match)

### 2. Standard (`standard/`)
**Purpose**: E2E journey testing, realistic scenarios  
**Size**: 50 users, Swedish demographic distribution, 150 photos, 25 matches  
**Load Time**: ~2 minutes  
**Use Cases**:
- E2E journey tests (signup → match → message)
- Matchmaking algorithm validation
- Photo moderation testing
- Distance/preference filtering

**Demographics**:
- Age: 22-45 (normal distribution, mean=32)
- Cities: Stockholm (30%), Göteborg (20%), Malmö (15%), others (35%)
- Gender: 50% men, 49% women, 1% non-binary
- Interests: Diverse tags (hiking, cooking, gaming, music, travel, etc.)

**Data Quality**:
- All profiles complete (ready for matching)
- Photos moderation: 80% approved, 15% pending, 5% rejected
- Match quality: Score distribution matches production algorithm

### 3. Load (`load/`)
**Purpose**: Performance testing, bot simulations  
**Size**: 500 users, 1500 photos, 200 matches  
**Load Time**: ~10 minutes  
**Use Cases**:
- Load testing with API bots
- Performance baseline (P95 < 350ms)
- Database query optimization
- Connection pool saturation testing

**Characteristics**:
- Realistic data distribution
- Pre-seeded swipe history (for matchmaking load)
- Message threads with varying lengths (1-50 messages)
- Simulates 3 months of organic usage

### 4. Demo (`demo/`)
**Purpose**: Visual bot demos, stakeholder presentations  
**Size**: 10 users (curated personas), 40 photos (high quality), 5 perfect matches  
**Load Time**: ~1 minute  
**Use Cases**:
- Visual Flutter integration_test recordings
- Stakeholder demo videos
- Marketing materials
- Feature showcase

**Personas**:
- **Alex** (28, Stockholm, hiking enthusiast) ↔ **Sara** (27, Stockholm, outdoor lover)
- **Viktor** (32, Göteborg, foodie) ↔ **Emma** (30, Göteborg, chef)
- **Oscar** (25, Malmö, gamer) ↔ **Lina** (24, Malmö, game designer)
- **Erik** (35, Uppsala, musician) ↔ **Sofia** (33, Uppsala, music teacher)
- **Johan** (29, Lund, traveler) ↔ **Anna** (28, Lund, photographer)

**Demo Features**:
- High-quality photos (professional headshots)
- Compelling bios (emotionally engaging)
- Instant matches (mutual likes pre-configured)
- Conversation starters pre-written

## Fixture Schema Validation

All fixtures follow JSON Schema definitions in `tests/shared/schemas/`:

```
tests/shared/schemas/
├── keycloak_user.schema.json       # Keycloak user provisioning
├── user_profile.schema.json        # UserService profile data
├── user_photo.schema.json          # PhotoService metadata
├── match.schema.json                # MatchmakingService match records
├── message.schema.json              # MessagingService message history
└── swipe.schema.json                # SwipeService swipe records
```

**Validation Rules**:
- Required fields enforced
- Type checking (string, number, boolean, date)
- Format validation (email, UUID, URL)
- Range constraints (age 18-100, photos 1-6, etc.)
- Referential integrity (swipe.userId must exist in users)

## Usage

### Load Fixtures
```bash
# Load minimal set for local testing
python scripts/fixture_loader.py load --set minimal --env demo

# Load standard set for E2E tests
python scripts/fixture_loader.py load --set standard --env demo

# Load with validation only (dry run)
python scripts/fixture_loader.py load --set minimal --validate-only
```

### Clean Fixtures
```bash
# Remove all test data (keeps Keycloak users)
python scripts/fixture_loader.py clean --set minimal

# Full cleanup (including Keycloak users)
python scripts/fixture_loader.py clean --set minimal --full
```

### Validate Fixtures
```bash
# Validate JSON schema compliance
python scripts/fixture_loader.py validate --set minimal

# Validate referential integrity
python scripts/fixture_loader.py validate --set minimal --check-refs
```

## Fixture Versioning

Fixtures use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking schema changes (e.g., remove required field)
- **MINOR**: Additive changes (e.g., new optional field, new user)
- **PATCH**: Data corrections (e.g., fix invalid email)

**Current Version**: 1.0.0

**Migration Strategy**:
- Loader checks fixture version vs schema version
- Migrations auto-applied when loading older fixtures
- Breaking changes require manual intervention

## File Structure

Each fixture set directory contains:

```
minimal/
├── metadata.json              # Fixture set metadata (version, description)
├── keycloak_users.json        # Keycloak user accounts
├── user_profiles.json         # UserService profile data
├── user_photos.json           # PhotoService photo metadata
├── matches.json               # MatchmakingService match records
├── messages.json              # MessagingService message history
└── swipes.json                # SwipeService swipe records
```

**Execution Order**:
1. Keycloak users (foundation)
2. User profiles (depends on Keycloak)
3. User photos (depends on profiles)
4. Swipes (depends on profiles)
5. Matches (depends on swipes)
6. Messages (depends on matches)

## Idempotency Guarantees

Fixture loader ensures idempotent loading:

1. **Keycloak users**: Create if not exists (check by email), update if exists
2. **Profiles**: Upsert by userId (last-write-wins)
3. **Photos**: Delete existing + insert (clean slate)
4. **Swipes**: Deduplicate by (fromUserId, toUserId, direction)
5. **Matches**: Deduplicate by (user1Id, user2Id) sorted pair
6. **Messages**: Deduplicate by messageId

**Rollback Strategy**:
- Loader wraps all operations in transaction
- On error: rollback DB changes + delete Keycloak users
- Partial state never left behind

## Integration with CI/CD

### GitHub Actions
```yaml
- name: Load test fixtures
  run: |
    python scripts/fixture_loader.py load --set minimal --env test
    
- name: Run contract tests
  run: |
    pytest tests/api/ -v --tb=short
```

### Docker Compose
```yaml
# docker-compose.test.yml
services:
  fixture-loader:
    image: python:3.12-slim
    volumes:
      - ./infrastructure/test-fixtures:/fixtures
      - ./scripts:/scripts
    command: python /scripts/fixture_loader.py load --set minimal
    depends_on:
      - keycloak-test
      - mysql-test
```

## Maintenance

### Adding New Users
1. Edit `<set>/keycloak_users.json` - add user account
2. Edit `<set>/user_profiles.json` - add profile data
3. Optionally add to `user_photos.json`, `matches.json`
4. Run validation: `python scripts/fixture_loader.py validate --set <set>`
5. Test load: `python scripts/fixture_loader.py load --set <set> --env demo`

### Updating Schema
1. Update JSON schema in `tests/shared/schemas/`
2. Increment fixture version in `metadata.json`
3. Add migration logic to `fixture_loader.py`
4. Update this README with changes
5. Test backward compatibility with all fixture sets

## Troubleshooting

### "Referential integrity violation"
- **Cause**: Swipe/match references non-existent user
- **Fix**: Ensure userId exists in `keycloak_users.json` and `user_profiles.json`

### "Keycloak user creation failed"
- **Cause**: Keycloak service not ready or network error
- **Fix**: Check `./infrastructure/start.sh` health, retry after 30s

### "Schema validation error"
- **Cause**: Fixture JSON doesn't match schema
- **Fix**: Run `validate --set <set>` for details, fix JSON

### "Load timeout"
- **Cause**: Large fixture set + slow network
- **Fix**: Increase timeout in `fixture_loader.py` config, use `load/{standard,load}` sparingly

## Future Enhancements

- [ ] Fixture diffing tool (compare two sets)
- [ ] Synthetic data generator (procedurally generate load fixtures)
- [ ] Fixture subsets ("standard-nomatch" = standard without matches)
- [ ] Photo file provisioning (currently only metadata)
- [ ] Multilingual fixtures (English, German, French)

---

**Related Documentation**:
- [Fixture Loader CLI](../../scripts/fixture_loader.py)
- [Testing Runbook](../../docs/TESTING_RUNBOOK.md)
- [Phase 13 Tasks](../../specs/001-mvp-foundation/tasks.md#phase-13)
