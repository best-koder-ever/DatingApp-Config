# DatingApp Operations Runbook

**A runbook** = The "how to actually run this thing" guide. Commands you run, in the order you run them, with no ambiguity.

## 🚨 CRITICAL: This is a Multi-Repo Project

This workspace contains **8+ independent Git repositories**. Never manually loop through repos with `cd`. Use the tools below.

---

## Multi-Repo Operations

### Check Status of All Repos

```bash
# Option 1: Using gita (recommended)
gita ll                                    # List all repos with status
gita super status                          # Detailed git status for all

# Option 2: Using our helper script
./gita-workflow.sh status
```

### Commit Changes Across Repos

```bash
# Option 1: Interactive (checks each repo, asks for message)
./ai-commit-helper.sh commit

# Option 2: Same message for all repos with changes
./gita-workflow.sh commit "feat: your commit message"

# Option 3: Validate before committing
./ai-commit-helper.sh validate-all         # Check what would be committed
```

### Push All Repos

```bash
# Push all repos that have commits to push
gita super push

# Or using our script
./gita-workflow.sh push
```

### Pull Latest from All Repos

```bash
gita super pull
# Or
./gita-workflow.sh pull
```

### Initial Setup (First Time Only)

If gita repos aren't registered yet:

```bash
# Register all repos with gita
gita add -a /home/m/development/DatingApp/*
gita add /home/m/development/mobile-apps/flutter/dejtingapp

# Verify registration
gita ll
```

---

## Development Environment

### Start the System

```bash
# 1. Start infrastructure (Keycloak, databases)
./infrastructure/start.sh

# 2. Start all microservices
./dev-start.sh

# Wait ~30 seconds for services to come up
```

### Stop the System

```bash
# Stop services
./dev-stop.sh

# Stop infrastructure
./infrastructure/stop.sh
```

### Verify System Health

```bash
# Run API smoke tests
python3 api_tests.py

# Check service logs
docker-compose -f infrastructure/docker-compose.yml logs -f keycloak
docker-compose -f infrastructure/docker-compose.yml logs -f postgres
```

---

## Build & Test

### Build All .NET Services

```bash
# Build each service
cd UserService && dotnet build && cd ..
cd swipe-service && dotnet build SwipeService.csproj && cd ..
cd messaging-service && dotnet build && cd ..
cd photo-service && dotnet build PhotoService.csproj && cd ..
cd MatchmakingService && dotnet build && cd ..
cd AuthService && dotnet build && cd ..

# Or build YARP gateway
cd dejting-yarp/src/dejting-yarp && dotnet build && cd ../../..
```

### Run Flutter Tests

```bash
cd mobile-apps/flutter/dejtingapp
flutter test integration_test/visual_photo_upload_test.dart
```

### Code Quality

```bash
# Python linting
ruff check .

# .NET analyzers run automatically during build
```

---

## GitHub Operations

### Create PRs Across Repos

```bash
# Create PR for all repos with changes
./gh-multi-repo.sh create-prs "PR title" "PR description"
```

### Check CI Status

```bash
# View CI status for all repos
./gh-multi-repo.sh check-ci
```

### List Open Issues

```bash
./gh-multi-repo.sh list-issues
```

---

## Repository Structure

```
DatingApp/                              # Main config repo
├── .github/copilot-instructions.md     # AI agent guidelines
├── RUNBOOK.md                          # This file
├── gita-workflow.sh                    # Multi-repo git helper
├── ai-commit-helper.sh                 # AI-friendly commit tool
├── gh-multi-repo.sh                    # GitHub CLI multi-repo tool
├── infrastructure/                     # Docker compose for Keycloak, DBs
├── dev-start.sh                        # Start all services
└── dev-stop.sh                         # Stop all services

AuthService/                            # Separate git repo
UserService/                            # Separate git repo
MatchmakingService/                     # Separate git repo
swipe-service/                          # Separate git repo
messaging-service/                      # Separate git repo
photo-service/                          # Separate git repo
dejting-yarp/                           # Separate git repo
mobile-apps/flutter/dejtingapp/         # Separate git repo
```

---

## Common Workflows

### Adding a New Feature

```bash
# 1. Pull latest from all repos
gita super pull

# 2. Create feature branches
gita super checkout -b feature/new-feature

# 3. Make your changes...

# 4. Commit across all changed repos
./gita-workflow.sh commit "feat: implement new feature"

# 5. Push all
gita super push

# 6. Create PRs
./gh-multi-repo.sh create-prs "New Feature" "Description of changes"
```

### Fixing a Bug Across Services

```bash
# 1. Create fix branches
gita super checkout -b fix/bug-description

# 2. Make fixes...

# 3. Validate builds
# (Build each service - see "Build All .NET Services" above)

# 4. Run smoke tests
python3 api_tests.py

# 5. Commit
./gita-workflow.sh commit "fix: resolve bug-description"

# 6. Push and create PRs
gita super push
./gh-multi-repo.sh create-prs "Fix: Bug Description" "Root cause and solution"
```

### Emergency Rollback

```bash
# Revert to previous commit across all repos
gita super reset --hard HEAD~1

# Or revert to specific commit
gita super reset --hard <commit-sha>

# Force push (⚠️ DANGEROUS - coordinate with team first)
gita super push --force
```

---

## Troubleshooting

### "gita command not found"

```bash
sudo apt install gita
# Or
pip install gita
```

### "gh command not found"

```bash
# Install GitHub CLI
sudo apt install gh
# Then authenticate
gh auth login
```

### Services Won't Start

```bash
# Check if ports are in use
sudo netstat -tulpn | grep -E ':(5000|5001|5002|5003|5004|5005|8080)'

# Kill conflicting processes
./cleanup_flutter_processes.sh

# Restart infrastructure
./infrastructure/stop.sh
./infrastructure/start.sh
```

### Merge Conflicts Across Repos

```bash
# See which repos have conflicts
gita super status | grep -i conflict

# Handle each manually
cd <repo-with-conflict>
git status
# Resolve conflicts, then:
git add .
git commit
cd ..
```

### Database Issues

```bash
# Reset databases (⚠️ DESTROYS DATA)
docker-compose -f infrastructure/docker-compose.yml down -v
docker-compose -f infrastructure/docker-compose.yml up -d

# Or just restart
docker-compose -f infrastructure/docker-compose.yml restart postgres mysql
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Check all repo status | `gita ll` |
| Commit all changes | `./gita-workflow.sh commit "message"` |
| Push all repos | `gita super push` |
| Pull all repos | `gita super pull` |
| Start system | `./infrastructure/start.sh && ./dev-start.sh` |
| Stop system | `./dev-stop.sh && ./infrastructure/stop.sh` |
| Run tests | `python3 api_tests.py` |
| Create PRs | `./gh-multi-repo.sh create-prs "title" "desc"` |
| View CI status | `./gh-multi-repo.sh check-ci` |

---

## For AI Agents

**⚠️ BEFORE doing git operations:**

1. Check if `gita-workflow.sh`, `ai-commit-helper.sh`, or `gh-multi-repo.sh` exist
2. Use those scripts instead of manual `cd repo && git commit` loops
3. This saves time and reduces errors

**⚠️ BEFORE starting services:**

1. Check if `dev-start.sh` exists
2. Use that instead of manually running each service

**⚠️ ALWAYS prefer automation over manual repetition**

---

Last updated: 2026-01-24
