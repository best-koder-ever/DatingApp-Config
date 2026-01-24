# GitHub CLI Integration Guide

Complete guide for using GitHub CLI (`gh`) with the DatingApp multi-repo structure.

## Overview

GitHub CLI provides powerful automation for GitHub operations across all 8 microservice repositories. Combined with `gita`, you have complete local + remote workflow control.

## Authentication

```bash
# Check authentication status
gh auth status

# Login (if needed)
gh auth login

# Refresh token
gh auth refresh
```

Current auth: **best-koder-ever** with scopes: `repo`, `workflow`, `gist`, `read:org`

## Quick Reference

### Using gh-multi-repo.sh

```bash
# Show GitHub status for all repos (issues, PRs, last updated)
./gh-multi-repo.sh status

# List all open issues across repos
./gh-multi-repo.sh issues

# List all open pull requests
./gh-multi-repo.sh prs

# Create a PR from current branch
cd AuthService
git checkout -b feature/add-oauth
# make changes...
git commit -am "feat: add OAuth support"
git push
cd ..
./gh-multi-repo.sh create-pr

# Sync all repos with GitHub
./gh-multi-repo.sh sync

# Check GitHub Actions workflow status
./gh-multi-repo.sh workflows

# List latest releases
./gh-multi-repo.sh releases

# Get detailed repo information
./gh-multi-repo.sh repo-info

# Clone all service repos (new machine setup)
./gh-multi-repo.sh clone-all
```

### Integrated with gita-workflow.sh

```bash
# GitHub status from gita workflow
./gita-workflow.sh gh-status

# CI/CD pipeline status
./gita-workflow.sh workflows
```

## Common Workflows

### 1. Create Feature Branch & PR

```bash
# Start feature work
cd AuthService
git checkout -b feature/improve-jwt

# Make changes
# ...

# Validate before committing
../ai-commit-helper.sh validate

# Commit with conventional message
git add .
git commit -m "feat(auth): improve JWT token validation"

# Push and create PR
git push -u origin feature/improve-jwt
../gh-multi-repo.sh create-pr
```

### 2. Check CI/CD Status Across All Services

```bash
# Quick overview
./gita-workflow.sh workflows

# Detailed view
./gh-multi-repo.sh workflows
```

### 3. Monitor Issues and PRs

```bash
# Weekly check
./gh-multi-repo.sh status

# See what needs attention
./gh-multi-repo.sh issues
./gh-multi-repo.sh prs
```

### 4. Sync All Repos

```bash
# Full sync: fetch + pull all repos
./gh-multi-repo.sh sync

# Alternative: use gita workflow
./gita-workflow.sh sync
```

### 5. Release Management

```bash
# Check current releases
./gh-multi-repo.sh releases

# Create a release (in specific service)
cd AuthService
gh release create v1.2.0 --title "Auth Service v1.2.0" --notes "### Changes
- Improved JWT validation
- Fixed OAuth refresh token bug"
cd ..
```

## Advanced gh Commands

### Working with Issues

```bash
# Create issue in specific service
cd UserService
gh issue create --title "Add profile photo validation" \
  --body "Validate photo formats before upload"

# List issues with labels
gh issue list --label "bug"

# Close an issue
gh issue close 42

# View issue details
gh issue view 42
```

### Working with Pull Requests

```bash
# Create PR with custom base branch
gh pr create --base develop --head feature/new-api

# Review PR
gh pr view 17 --web

# Merge PR
gh pr merge 17 --squash

# Check PR status
gh pr status

# Approve a PR
gh pr review 17 --approve

# Request changes
gh pr review 17 --request-changes --body "Please add tests"
```

### GitHub Actions

```bash
# List workflow runs
gh run list --limit 10

# Watch a workflow run
gh run watch

# Re-run failed jobs
gh run rerun 12345

# View workflow logs
gh run view 12345 --log
```

### Repository Operations

```bash
# View repo in browser
gh repo view --web

# Clone a service repo
gh repo clone best-koder-ever/AuthService

# Fork a repo
gh repo fork

# Archive a repo
gh repo archive best-koder-ever/old-service
```

## AI Agent Usage

### For AI Agents Working in This Codebase

**Before pushing code:**
```bash
# 1. Validate changes
./ai-commit-helper.sh validate-all

# 2. Check GitHub status
./gh-multi-repo.sh status

# 3. Ensure CI passes
./gh-multi-repo.sh workflows
```

**Creating PRs:**
```bash
# Always use feature branches
git checkout -b feature/ai-suggested-fix

# After committing
./gh-multi-repo.sh create-pr
```

**Checking for existing issues:**
```bash
# Before creating new issue
./gh-multi-repo.sh issues | grep -i "keyword"
```

## Repository List

All managed repositories:

1. **AuthService** - Authentication & JWT
2. **UserService** - User profiles & photos
3. **MatchmakingService** - Matching algorithm
4. **dejting-yarp** - YARP API gateway
5. **messaging-service** - SignalR messaging
6. **swipe-service** - Swipe processing
7. **photo-service** - Photo storage & moderation
8. **TestDataGenerator** - Test data creation

Plus:
- **DatingApp** (root) - Config & orchestration
- **dejtingapp** (Flutter) - Mobile/web client

## Troubleshooting

### gh command not found
```bash
sudo apt install gh
```

### Authentication expired
```bash
gh auth refresh
gh auth status
```

### Can't create PR (no upstream)
```bash
cd <service>
git push -u origin <branch-name>
```

### Workflow permission denied
Check that your token has `workflow` scope:
```bash
gh auth status
# Should show: workflow
```

Re-authenticate if needed:
```bash
gh auth login --scopes repo,workflow,gist,read:org
```

## Best Practices

1. **Always check status before major operations**
   ```bash
   ./gh-multi-repo.sh status
   ```

2. **Use feature branches for all changes**
   ```bash
   git checkout -b feature/descriptive-name
   ```

3. **Verify CI before merging**
   ```bash
   ./gh-multi-repo.sh workflows
   ```

4. **Keep PRs small and focused**
   - One feature/fix per PR
   - Easy to review and test

5. **Use conventional commits**
   ```
   feat: add new feature
   fix: resolve bug
   docs: update documentation
   test: add tests
   chore: maintain dependencies
   ```

6. **Monitor releases across services**
   ```bash
   ./gh-multi-repo.sh releases
   ```

## Integration with CI/CD

All services use GitHub Actions. Workflow files are in `.github/workflows/` in each repo.

### Common Workflows

- `build-and-test.yml` - Build and test on push/PR
- `docker-build.yml` - Build Docker images
- `deploy.yml` - Deploy to environments

### Check workflow status
```bash
./gh-multi-repo.sh workflows
```

### View specific workflow
```bash
cd AuthService
gh run list --workflow build-and-test.yml
```

## Scripts Summary

| Script | Purpose | Example |
|--------|---------|---------|
| `gh-multi-repo.sh` | GitHub CLI operations | `./gh-multi-repo.sh status` |
| `gita-workflow.sh` | Git + GitHub workflows | `./gita-workflow.sh gh-status` |
| `ai-commit-helper.sh` | Pre-commit validation | `./ai-commit-helper.sh validate-all` |

## Next Steps

1. ✅ gh CLI installed and authenticated
2. ✅ Multi-repo scripts created
3. 🔄 Set up branch protection rules (optional)
4. 🔄 Configure PR templates (optional)
5. 🔄 Set up issue templates (optional)

---

**For complete git workflow:** See [AI_AGENT_GIT_GUIDE.md](AI_AGENT_GIT_GUIDE.md)
**For gita details:** See [GITA_WORKFLOW.md](GITA_WORKFLOW.md)
