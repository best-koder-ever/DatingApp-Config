# Git & GitHub Workflow Integration - Complete Setup

## Overview

Complete multi-repo management system combining **gita** (local git operations), **GitHub CLI** (remote operations), and custom validation tools.

## ✅ What's Installed

1. **gita** - Multi-repository manager
2. **GitHub CLI (gh)** - GitHub automation tool
3. **Custom scripts** - DatingApp-specific workflow automation

## 🛠️ Available Tools

### 1. gita-workflow.sh
**Primary workflow orchestrator** - Handles common git + GitHub operations

```bash
./gita-workflow.sh status        # Local git status
./gita-workflow.sh gh-status     # GitHub status (issues, PRs)
./gita-workflow.sh commit        # Interactive commit
./gita-workflow.sh commit-auto   # Auto-commit with messages
./gita-workflow.sh push          # Push all repos
./gita-workflow.sh pull          # Pull all repos
./gita-workflow.sh sync          # Full sync (pull + commit + push)
./gita-workflow.sh clean         # Remove build artifacts
./gita-workflow.sh workflows     # Check CI/CD status
```

### 2. gh-multi-repo.sh
**GitHub CLI wrapper** - Specialized GitHub operations

```bash
./gh-multi-repo.sh status        # Detailed GitHub status
./gh-multi-repo.sh issues        # List all issues
./gh-multi-repo.sh prs           # List all pull requests
./gh-multi-repo.sh create-pr     # Create PR from current branch
./gh-multi-repo.sh sync          # Sync with GitHub (fetch + pull)
./gh-multi-repo.sh workflows     # GitHub Actions status
./gh-multi-repo.sh releases      # List latest releases
./gh-multi-repo.sh clone-all     # Clone all service repos
./gh-multi-repo.sh repo-info     # Detailed repo information
```

### 3. ai-commit-helper.sh
**AI agent validation** - Pre-commit safety checks

``bash
./ai-commit-helper.sh validate            # Check current repo
./ai-commit-helper.sh validate-all        # Check all repos
./ai-commit-helper.sh safe-commit         # Validate + commit
./ai-commit-helper.sh clean-artifacts     # Remove build files
./ai-commit-helper.sh suggest-message     # Generate commit message
```

## 📋 Common Workflows

### Daily Development

```bash
# Morning: sync everything
./gita-workflow.sh pull

# Check status
./gita-workflow.sh status
./gita-workflow.sh gh-status

# Make changes...

# Validate and commit
./ai-commit-helper.sh validate-all
./gita-workflow.sh commit

# Push everything
./gita-workflow.sh push

# Check CI/CD
./gita-workflow.sh workflows
```

### Create Feature with PR

```bash
# Navigate to service
cd UserService

# Create feature branch
git checkout -b feature/add-avatar-crop

# Make changes...

# Validate
../ai-commit-helper.sh validate

# Commit
git add .
git commit -m "feat(user): add avatar cropping feature"

# Push and create PR
git push -u origin feature/add-avatar-crop
cd ..
./gh-multi-repo.sh create-pr

# Monitor CI
./gh-multi-repo.sh workflows
```

### Quick Status Check

```bash
# One-liner: local + GitHub status
./gita-workflow.sh status && echo && ./gita-workflow.sh gh-status
```

### Emergency Hotfix

```bash
# Sync first
./gita-workflow.sh pull

# Navigate to service
cd photo-service

# Create hotfix branch
git checkout -b hotfix/fix-memory-leak

# Fix code...

# Fast validate
../ai-commit-helper.sh validate

# Commit
git add .
git commit -m "fix(photo): resolve memory leak in image processing"

# Push and PR
git push -u origin hotfix/fix-memory-leak
cd ..
./gh-multi-repo.sh create-pr

# Watch CI
./gh-multi-repo.sh workflows
```

## 🎯 Tool Decision Matrix

| Task | Use This Tool |
|------|---------------|
| Check what changed locally | `./gita-workflow.sh status` |
| Check GitHub issues/PRs | `./gita-workflow.sh gh-status` |
| Validate before commit | `./ai-commit-helper.sh validate-all` |
| Commit one repo | `cd <repo> && git commit -m "..."` |
| Commit all changed repos | `./gita-workflow.sh commit` |
| Push everything | `./gita-workflow.sh push` |
| Create pull request | `./gh-multi-repo.sh create-pr` |
| Check CI/CD pipelines | `./gita-workflow.sh workflows` |
| List all open issues | `./gh-multi-repo.sh issues` |
| Sync everything | `./gita-workflow.sh sync` |
| Remove build artifacts | `./gita-workflow.sh clean` |

## 🔑 Key Files Reference

| File | Purpose | Location |
|------|---------|----------|
| `gita-workflow.sh` | Main workflow orchestrator | `/home/m/development/DatingApp/` |
| `gh-multi-repo.sh` | GitHub CLI wrapper | `/home/m/development/DatingApp/` |
| `ai-commit-helper.sh` | Validation tool | `/home/m/development/DatingApp/` |
| `AI_AGENT_GIT_GUIDE.md` | AI agent instructions | `/home/m/development/DatingApp/` |
| `GH_CLI_INTEGRATION.md` | GitHub CLI complete guide | `/home/m/development/DatingApp/` |
| `GITA_WORKFLOW.md` | Gita detailed docs | `/home/m/development/DatingApp/` |
| `.gitignore` | Build artifact exclusions | In each service repo |

## 📚 Documentation

- **[AI_AGENT_GIT_GUIDE.md](AI_AGENT_GIT_GUIDE.md)** - Quick reference for AI agents
- **[GH_CLI_INTEGRATION.md](GH_CLI_INTEGRATION.md)** - Complete GitHub CLI usage guide
- **[GITA_WORKFLOW.md](GITA_WORKFLOW.md)** - Gita theory and advanced usage
- **[MULTI_REPO_STRATEGY.md](MULTI_REPO_STRATEGY.md)** - Multi-repo architecture explanation

## 🚀 Managed Repositories

1. **AuthService** - `best-koder-ever/auth-service`
2. **UserService** - `best-koder-ever/UserService`
3. **MatchmakingService** - `best-koder-ever/MatchmakingService`
4. `**dejting-yarp** - `best-koder-ever/dejting-yarp`
5. **messaging-service** - `best-koder-ever/messaging-service`
6. **swipe-service** - `best-koder-ever/swipe-service`
7. **photo-service** - `best-koder-ever/photo-service`
8. **TestDataGenerator** - `best-koder-ever/TestDataGenerator`
9. **DatingApp** (root) - `best-koder-ever/DatingApp-Config`
10. **dejtingapp** (Flutter) - `best-koder-ever/dejtingapp`

## ⚙️ Configuration

### GitHub CLI Auth
```bash
gh auth status
# Authenticated as: best-koder-ever
# Scopes: repo, workflow, gist, read:org
```

### Gita Repos
```bash
gita ll
# Shows all 10 registered repositories
```

### Validation Rules
Build artifacts checked by `ai-commit-helper.sh`:
- `bin/`, `obj/` directories
- `*.dll`, `*.pdb`, `*.exe`
- `*.db`, `*.sqlite`
- `.env`, `*.key`, `*.pfx` (secrets)
- `node_modules/`, `__pycache__/`

## 🛡️ Best Practices

1. **Always validate before committing**
   ```bash
   ./ai-commit-helper.sh validate-all
   ```

2. **Use conventional commits**
   ```
   feat: add feature
   fix: fix bug
   docs: update docs
   test: add tests
   chore: maintenance
   ```

3. **Check CI before merging**
   ```bash
   ./gh-multi-repo.sh workflows
   ```

4. **Use feature branches**
   ```bash
   git checkout -b feature/descriptive-name
   ```

5. **Keep PRs small and focused**
   - One feature or fix per PR
   - Easy to review and test

## 🔧 Troubleshooting

### gita command not found
```bash
sudo apt install gita
gita add -a /home/m/development/DatingApp
```

### gh command not found
```bash
sudo apt install gh
gh auth login
```

### Permission denied on scripts
```bash
chmod +x gita-workflow.sh gh-multi-repo.sh ai-commit-helper.sh
```

### Build artifacts in git
```bash
./ai-commit-helper.sh clean-artifacts <repo-name>
cd <repo>
git rm -r --cached bin/ obj/
git commit -m "chore: remove build artifacts from git"
```

## 🎓 Learning Path

1. **Day 1:** Learn basic commands
   - `./gita-workflow.sh status`
   - `./gita-workflow.sh commit`
   - `./gita-workflow.sh push`

2. **Day 2:** Understand GitHub integration
   - `./gh-multi-repo.sh status`
   - `./gh-multi-repo.sh create-pr`
   - `./gh-multi-repo.sh workflows`

3. **Day 3:** Master validation
   - `./ai-commit-helper.sh validate-all`
   - `./ai-commit-helper.sh safe-commit`

4. **Week 2:** Advanced workflows
   - Read [GH_CLI_INTEGRATION.md](GH_CLI_INTEGRATION.md)
   - Customize commit messages
   - Set up branch protection

## 📞 Quick Help

```bash
./gita-workflow.sh --help
./gh-multi-repo.sh --help
./ai-commit-helper.sh --help
```

---

**Status:** ✅ Fully integrated and tested  
**Last Updated:** 2025-01-26  
**Maintainer:** AI Assistant + User
