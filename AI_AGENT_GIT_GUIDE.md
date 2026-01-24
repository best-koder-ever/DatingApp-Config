# AI Agent Instructions for DatingApp Multi-Repo Workspace

## Repository Structure

This workspace uses **gita** to manage multiple independent git repositories. Each service is a separate GitHub repo:

```
DatingApp/               # Root repo (orchestration, docs, scripts)
├── AuthService/         # https://github.com/best-koder-ever/AuthService
├── UserService/         # https://github.com/best-koder-ever/UserService
├── MatchmakingService/  # https://github.com/best-koder-ever/MatchmakingService
├── dejting-yarp/        # https://github.com/best-koder-ever/dejting-yarp
├── messaging-service/   # https://github.com/best-koder-ever/messaging-service
├── swipe-service/       # https://github.com/best-koder-ever/swipe-service
├── photo-service/       # https://github.com/best-koder-ever/photo-service
├── TestDataGenerator/   # https://github.com/best-koder-ever/TestDataGenerator
└── mobile-apps/flutter/dejtingapp/  # https://github.com/best-koder-ever/mobile_dejtingapp
```

## Quick Reference for AI Agents

```bash
# Status check (ALWAYS do this first!)
gita ll                            # Overview of all repos
./gita-workflow.sh status          # Local git status
./gita-workflow.sh gh-status       # GitHub issues/PRs

# Before committing - validate!
./ai-commit-helper.sh validate         # Check current repo
./ai-commit-helper.sh validate-all     # Check all repos

# Making changes
cd ServiceName
# ... edit files ...
./ai-commit-helper.sh safe-commit "feat(service): description"
git push

# Or interactive across all changed repos
./gita-workflow.sh commit
./gita-workflow.sh push

# GitHub operations
./gh-multi-repo.sh create-pr       # Create PR from current branch
./gh-multi-repo.sh workflows       # Check CI/CD status
./gh-multi-repo.sh issues          # List all issues
```

## Critical Rules for AI Agents

### ❌ NEVER COMMIT:
- `bin/`, `obj/`, `out/` directories
- `*.dll`, `*.exe`, `*.pdb`, `*.cache` files
- `*.db`, `*.db-shm`, `*.db-wal` database files
- `*.key`, `*.pem`, `secrets.json`, `.env` files
- Any build outputs or temporary files

### ✅ ALWAYS:
1. Run `gita ll` before starting work
2. Validate before commit: `./ai-commit-helper.sh validate`
3. Use meaningful commit messages (conventional commits format)
4. Commit to the correct service repo (not root)
5. Check `git status` to verify what you're committing

## Commit Message Format

Use conventional commits:
```
<type>(<scope>): <description>

Types: feat, fix, refactor, docs, test, chore
Scope: Service name (auth, user, matchmaking, etc.)
```

**Examples:**
- ✅ `feat(auth): add JWT refresh token endpoint`
- ✅ `fix(user): correct profile validation logic`
- ✅ `refactor(matchmaking): optimize candidate scoring`
- ❌ `update files` (too generic)
- ❌ `changes` (no context)

##AI Workflow Patterns

### Pattern 1: Single Service Change
```bash
gita ll                        # Check status
cd ServiceName
# ... make changes ...
./ai-commit-helper.sh validate # Validate
git add .
git commit -m "feat(service): specific change"
git push
cd ..
gita ll                        # Verify
```

### Pattern 2: Multi-Service Feature
```bash
gita ll  # Check all repos clean

# Update each service
cd AuthService
# ... changes ...
git add . && git commit -m "feat(auth): add RefreshToken contract"
git push
cd ..

cd UserService
# ... changes ...
git add . && git commit -m "feat(user): integrate refresh token"
git push
cd ..

gita ll  # Verify all updated
```

### Pattern 3: Quick Save All
```bash
./gita-workflow.sh commit-auto  # Auto-generate messages
./gita-workflow.sh push         # Push everything
```

## Available Helper Commands

### Gita Commands
```bash
gita ll                    # List all repos with status
gita super pull            # Pull all repos
gita super fetch           # Fetch all without merge
gita super status          # Detailed status across all
```

### Workflow Scripts
```bash
./gita-workflow.sh status        # Formatted status view
./gita-workflow.sh commit        # Interactive commit per repo
./gita-workflow.sh commit-auto   # Auto-generated commit messages
./gita-workflow.sh push          # Push all repos
./gita-workflow.sh sync          # Pull + commit + push all
./gita-workflow.sh clean         # Clean build artifacts
```

### AI Helper Scripts
```bash
./ai-commit-helper.sh validate         # Validate current repo
./ai-commit-helper.sh validate-all     # Validate all repos
./ai-commit-helper.sh safe-commit "msg"  # Validate & commit
./ai-commit-helper.sh clean-artifacts  # Remove build artifacts
./ai-commit-helper.sh suggest-message  # Get commit message ideas
```

### GitHub CLI Scripts
```bash
./gh-multi-repo.sh status              # GitHub repo status (issues, PRs)
./gh-multi-repo.sh issues              # List all open issues
./gh-multi-repo.sh prs                 # List all pull requests
./gh-multi-repo.sh create-pr           # Create PR from current branch
./gh-multi-repo.sh workflows           # GitHub Actions status
./gh-multi-repo.sh releases            # List latest releases
```

## Pre-Commit Validation

The AI helper automatically checks for:
- ✓ Build artifacts (bin/, obj/, *.dll, *.pdb)
- ✓ Database files (*.db, *.sqlite)
- ✓ Secret files (*.key, *.pem, .env)
- ✓ .gitignore presence

**Always validate before committing:**
```bash
./ai-commit-helper.sh validate
```

## Common Mistakes to Avoid

1. **Committing build artifacts** - Run `./ai-commit-helper.sh clean-artifacts` first
2. **Generic commit messages** - Use `./ai-commit-helper.sh suggest-message` for ideas
3. **Committing to wrong repo** - Verify with `pwd` and `git remote -v`
4. **Not checking status first** - Always `gita ll` before starting
5. **Batch unrelated changes** - Commit logically related changes together
6. **Not checking CI/CD status** - Run `./gh-multi-repo.sh workflows` after pushing
7. **Creating PR without validation** - Always validate before creating PR

## Integration with Project Guidelines

This file focuses on **git workflow**. For tech stack and coding standards, see:
- [/.github/copilot-instructions.md](copilot-instructions.md) - Project tech stack, API contracts
- [GITA_WORKFLOW.md](GITA_WORKFLOW.md) - Detailed gita usage
- [MULTI_REPO_STRATEGY.md](MULTI_REPO_STRATEGY.md) - Multi-repo architecture

## Debugging

**Repo appears modified but shouldn't be:**
```bash
cd ServiceName
./ai-commit-helper.sh clean-artifacts
git status  
```

**Lost track of changes:**
```bash
gita super status --porcelain
```

**Need to undo uncommitted changes:**
```bash
cd ServiceName
git checkout -- path/to/file
```

---

**Summary**: Think of each service as independent. Use gita for overview, commit individually with care. When in doubt, use `./ai-commit-helper.sh validate` before committing.
