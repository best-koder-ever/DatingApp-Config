# DatingApp Runbook

Single source of truth for starting, stopping, seeding, and testing the app.

---

## Quick Start (3 commands)

```bash
./infrastructure/start.sh          # Start Keycloak + databases
./dev-start.sh                     # Start all 7 backend services + YARP gateway
./scripts/seed-test-data.sh minimal  # Seed 5 demo users with swipes/matches/messages
```

Then launch Flutter:
```bash
cd /home/m/development/mobile-apps/flutter/dejtingapp
flutter run -d chrome   # or: flutter run -d <device_id>
```

---

## Stop Everything

```bash
./dev-stop.sh              # Kill all dotnet service processes
./infrastructure/stop.sh   # Stop all Docker containers (Keycloak + all DBs)
```

---

## Service Ports

| Service             | Port  | URL                          |
|---------------------|-------|------------------------------|
| YARP Gateway        | 8080  | http://localhost:8080         |
| UserService         | 8082  | http://localhost:8082         |
| MatchmakingService  | 8083  | http://localhost:8083         |
| PhotoService        | 8085  | http://localhost:8085         |
| MessagingService    | 8086  | http://localhost:8086         |
| SwipeService        | 8087  | http://localhost:8087         |
| SafetyService       | 8088  | http://localhost:8088         |
| Keycloak            | 8090  | http://localhost:8090         |

### Database Containers

| Container              | Port  | Database             |
|------------------------|-------|----------------------|
| UserService-db         | 3308  | UserServiceDb        |
| MatchmakingService-db  | 3309  | MatchmakingServiceDb |
| swipe-service-db       | 3310  | SwipeServiceDb       |
| photo-service-db       | 3311  | PhotoServiceDb       |
| messaging-service-db   | 3312  | MessagingDb          |
| keycloak-db            | 5432  | keycloak (Postgres)  |

---

## Test Users

All seeded by `./scripts/seed-test-data.sh minimal`.

| Email            | Password  | Name    | Role/Notes              |
|------------------|-----------|---------|-------------------------|
| alice@test.se    | Test123!  | Alice   | 28F, Photographer       |
| bob@test.se      | Test123!  | Bob     | 32M, Musician           |
| charlie@test.se  | Test123!  | Charlie | 30M, Fitness Coach      |
| diana@test.se    | Test123!  | Diana   | 27F, Graphic Designer   |
| erik@test.se     | Test123!  | Erik    | 35M, Civil Engineer     |

Pre-existing Keycloak users (from realm export):
- `erik_astrom` / `Demo123!`
- `sara_blomqvist` / `Demo123!`

### Pre-configured Relationships (after seeding)

- alice ↔ bob — Matched (2 messages)
- bob ↔ charlie — Matched
- alice → charlie — Left swipe (no match)

---

## Data Management

### Seed demo data
```bash
./scripts/seed-test-data.sh minimal     # 5 users
./scripts/seed-test-data.sh standard    # 50 users (when implemented)
```

### Reset all databases (clean slate)
```bash
make quick-reset          # Truncate tables + re-seed (fast)
make reset                # Stop containers + prune volumes (nuclear)
```

### Validate fixtures
```bash
./scripts/seed-test-data.sh --validate
```

---

## Testing

```bash
# API smoke tests
python3 api_tests.py

# Flutter integration tests
cd /home/m/development/mobile-apps/flutter/dejtingapp
flutter test integration_test/

# Full clean test run (reset + seed + test)
make test-clean
```

---

## Health Check

```bash
# Quick check all services
for port in 8080 8082 8083 8085 8086 8087 8088; do
  echo -n "Port $port: "
  curl -sf http://localhost:$port/health && echo "OK" || echo "DOWN"
done
```

---

## Logs

All service logs in `logs/` directory:
```bash
tail -f logs/user-service.log
tail -f logs/matchmaking-service.log
tail -f logs/photo-service.log
tail -f logs/messaging-service.log
tail -f logs/swipe-service.log
tail -f logs/safety-service.log
tail -f logs/yarp-gateway.log
```

---

## Multi-Repo Git Workflow

This project has 8+ repos. Use the helper scripts:
```bash
./gita-workflow.sh          # Batch git operations across all repos
./ai-commit-helper.sh       # AI-assisted commit messages
./gh-multi-repo.sh          # GitHub operations across repos
```

---

## Makefile Targets

```bash
make help            # Show all available commands
make dev-start       # Start infrastructure + services
make dev-stop        # Stop everything
make reset           # Nuclear reset (prune volumes)
make quick-reset     # Truncate tables + re-seed
make seed-minimal    # Seed 5 test users
make test            # Run integration tests
make test-clean      # Reset + seed + test (CI-style)
make test-api        # API smoke tests
make health-check    # Check service health
```
