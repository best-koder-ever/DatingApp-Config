# Multi-Repo Workflow with Gita

You can keep all your services in separate GitHub repos AND manage them efficiently with **gita**.

## ✅ Setup Complete

All 10 repositories are now registered with gita:
- 8 microservices (AuthService, UserService, etc.)  
- 1 root repo (DatingApp)
- 1 tool repo (spec-kit)

## Quick Commands

### View Status
```bash
gita ll                    # List all repos with branch & status
gita super status          # Detailed git status for all repos
./gita-workflow.sh status  # Pretty formatted status
```

### Commit & Push

**Option 1: Per-repo (recommended for meaningful commits)**
```bash
cd AuthService
git add .
git commit -m "feat: add JWT refresh token support"
git push

cd ../UserService  
git add .
git commit -m "fix: correct profile photo validation"
git push
```

**Option 2: Interactive batch**
```bash
./gita-workflow.sh commit  # Asks for message per changed repo
./gita-workflow.sh push    # Push all repos
```

**Option 3: Auto-commit (for quick saves)**
```bash
./gita-workflow.sh commit-auto  # Generates commit messages
./gita-workflow.sh push
```

**Option 4: Full sync**
```bash
./gita-workflow.sh sync   # pull → commit → push everything
```

### Pull Latest Changes
```bash
gita super pull           # Pull all repos
./gita-workflow.sh pull   # Same with pretty output
```

### Fetch Without Merging
```bash
gita super fetch          # Fetch from all remotes
```

## Common Workflows

### Daily Work on One Service
```bash
# Work normally in individual repos
cd AuthService
git checkout -b feature/new-auth
# ... make changes ...
git add .
git commit -m "feat: implement OAuth2"
git push origin feature/new-auth

# Check if other repos need updates
gita ll
```

### Update Everything
```bash
# See what changed across all repos
gita ll

# Pull latest from all
gita super pull

# Or full sync (pull + commit + push)
./gita-workflow.sh sync
```

### Before Starting Work
```bash
./gita-workflow.sh pull    # Get latest from all repos
./gita-workflow.sh status  # See current state
```

### End of Day
```bash
./gita-workflow.sh status        # Review changes
./gita-workflow.sh commit        # Commit with meaningful messages
./gita-workflow.sh push          # Push everything
```

## Advanced Gita Features

### Work with Specific Repos
```bash
# See all registered repos
gita ls

# Run command on specific repos
gita shell AuthService UserService -c 'git status'

# Run command on all
gita super git fetch --prune
```

### Groups
```bash
# List groups
gita group ll

# Create custom group
gita group add backend AuthService UserService MatchmakingService

# Run commands on group
gita group ls backend
gita shell backend -c 'git pull'
```

### Information Commands
```bash
gita info AuthService      # Show repo details
gita diff                  # Show uncommitted changes
gita ll -C                 # Colorful list view
```

## .gitignore Strategy

Each service repo should ignore build artifacts:
```gitignore
bin/
obj/
*.dll
*.pdb
*.cache
```

Root repo should ignore nested repos (already configured):
```gitignore
# Services are tracked separately
AuthService/
UserService/
# ... etc
```

## Migration from Old Scripts

| Old Script | New Command |
|------------|-------------|
| `./commit_and_push_all.sh` | `./gita-workflow.sh sync` |
| `./check_all_and_push_all.sh` | `./gita-workflow.sh commit && ./gita-workflow.sh push` |
| Manual check each repo | `gita ll` |

## Best Practices

### ✅ DO
- Write meaningful commit messages for each service
- Commit services independently when possible
- Use `gita ll` to overview all repos before committing
- Pull regularly: `gita super pull`
- Use branches for features: `cd Service && git checkout -b feature/x`

### ❌ DON'T  
- Auto-commit everything with generic messages (unless quick work-in-progress)
- Commit build artifacts (bin/, obj/, *.dll)
- Force push: gita doesn't support it (and you shouldn't need it)

## Why This is Better Than Your Old Scripts

1. **Proper Git Practice**: Each repo maintains its own meaningful history
2. **Selective Operations**: Work on one service without affecting others  
3. **Branch Support**: Create feature branches per service
4. **GitHub CI/CD**: Each repo can have its own Actions workflows
5. **Cleaner History**: No more "Update all services" commits
6. **Team Ready**: Easy for future collaborators to work on specific services
7. **Standard Tool**: Gita is open source and widely used

## Troubleshooting

### Gita not finding repos
```bash
gita add -a /home/m/development/DatingApp
```

### Remove a repo from gita (doesn't delete files)
```bash
gita rm TestDataGenerator
```

### Reset gita config
```bash
gita clear  # Remove all repos
gita add -a /home/m/development/DatingApp  # Re-add
```

### See gita config
```bash
cat ~/.config/gita/repos.csv
```

## Helper Script Options

```bash
./gita-workflow.sh --help   # Show all commands

# Available commands:
status      # Overview of all repos
commit      # Interactive commit (asks for messages)
commit-auto # Auto-generated commit messages  
push        # Push all repos
pull        # Pull all repos
fetch       # Fetch from all remotes
sync        # Full pull→commit→push workflow
clean       # Clean .NET build artifacts
```

## Example Daily Workflow

```bash
# Morning: Get latest
./gita-workflow.sh pull

# Work on specific feature in AuthService
cd AuthService
git checkout -b feature/improve-auth
# ... code changes ...
git add .
git commit -m "feat(auth): add rate limiting to token endpoint"
git push origin feature/improve-auth

# Check other repos
cd ..
gita ll

# Update related services if needed
cd UserService
# ... changes ...
git add .
git commit -m "feat(user): integrate with new auth rate limiting"
git push

# End of day: clean up any uncommitted stuff
./gita-workflow.sh status
./gita-workflow.sh commit  # If there are other changes
./gita-workflow.sh push
```

## You Still Have Separate GitHub Repos! 🎉

Each service remains in its own GitHub repository:
- ✅ https://github.com/best-koder-ever/AuthService
- ✅ https://github.com/best-koder-ever/UserService  
- ✅ https://github.com/best-koder-ever/MatchmakingService
- ... etc

Gita just makes managing them locally much easier!
