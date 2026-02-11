# CLI Agent Setup for DatingApp Development

## Recommended Tool: Aider

**Why Aider?** 
- ✅ Fully automated (no manual copy/paste)
- ✅ Works with Claude, GPT-4, Gemini, local models
- ✅ Git-aware (auto-commits changes)
- ✅ Context-efficient (only reads relevant files)
- ✅ Supports complex refactors across multiple files

**Alternative**: Cursor CLI (if you use Cursor editor)

---

## Installation

### Aider (Recommended)

```bash
# Install via pip
cd /home/m/development/DatingApp
source .venv/bin/activate
pip install aider-chat

# Verify installation
aider --version
```

### Configuration

Create `~/.aider.conf.yml`:

```yaml
# Model selection (pick one)
model: anthropic/claude-3-5-sonnet-20241022  # Best for complex tasks
# model: openai/gpt-4-turbo-preview           # Alternative
# model: google/gemini-2.0-flash-exp          # Fast, good for simple tasks

# Repository settings
auto-commits: true
dirty-commits: true
git: true

# Context management
show-diffs: true
map-tokens: 2048  # Repo context for large projects

# Logging for debugging
verbose: false
```

### API Keys

```bash
# Add to ~/.bashrc or ~/.zshrc

# For Claude (recommended)
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenAI
export OPENAI_API_KEY="sk-..."

# For Gemini
export GOOGLE_API_KEY="..."

# Reload shell
source ~/.bashrc
```

---

## Usage Patterns

### Pattern 1: Implement Single Task

```bash
# Navigate to repo
cd /home/m/development/DatingApp

# Start Aider for specific task (T024 example)
aider \
  --model anthropic/claude-3-5-sonnet-20241022 \
  --message "Implement T024: Enhance PhotoService moderation + blur pipeline. 

Read the full task description from GitHub issue #7: https://github.com/best-koder-ever/DatingApp-Config/issues/7

Follow ALL acceptance criteria:
- Add ML.NET moderation to PhotoService
- Generate blurred versions for MatchOnly privacy
- Add PrivacyLevel enum to PhotoMetadata
- Implement privacy enforcement logic
- Add structured logging with CorrelationId
- Write unit tests in photo-service.Tests/
- Add integration test to api_tests.py

Affected files:
- photo-service/Services/ModerationService.cs
- photo-service/Services/ImageProcessingService.cs  
- photo-service/Data/PhotoMetadata.cs
- specs/001-mvp-foundation/contracts/api-spec.md" \
  photo-service/Services/ModerationService.cs \
  photo-service/Services/ImageProcessingService.cs \
  photo-service/Data/PhotoMetadata.cs
```

**Aider will**:
1. Read the files
2. Implement changes
3. Run tests (if you configure it)
4. Auto-commit to git with descriptive message

### Pattern 2: Interactive Mode

```bash
# Start interactive session
aider photo-service/Services/ModerationService.cs

# Then chat with Aider
> Read task T024 from issue #7 and implement the ML.NET moderation pipeline

> Add unit tests for the moderation service

> Add structured logging with CorrelationId to all methods

> /commit  # Commit when satisfied
> /exit
```

### Pattern 3: Batch Processing (Multiple Tasks)

```bash
#!/bin/bash
# scripts/aider_batch.sh

TASKS=(
  "T015:monitoring/dashboards/mvp-overview.json,specs/001-mvp-foundation/plan.md"
  "T016:specs/001-mvp-foundation/plan.md,specs/001-mvp-foundation/contracts/api-spec.md"
)

for task_spec in "${TASKS[@]}"; do
  task_id="${task_spec%%:*}"
  files="${task_spec#*:}"
  
  echo "Processing $task_id..."
  aider \
    --yes \
    --model anthropic/claude-3-5-sonnet-20241022 \
    --message "Implement $task_id following GitHub issue acceptance criteria" \
    ${files//,/ }
    
  sleep 5  # Rate limit protection
done
```

---

## Integration with GitHub Issues

### Fetch Issue Details in Aider Prompt

```bash
# Get rich issue description
ISSUE_BODY=$(gh issue view 7 --json body --jq .body)

# Pass to Aider
aider --message "Implement this task:

$ISSUE_BODY

Focus on acceptance criteria and follow observability guidelines." \
  photo-service/Services/ModerationService.cs
```

### Automated Workflow Script

Create `scripts/implement_task.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

TASK_ID="$1"  # e.g., T024

# Find issue number for task
ISSUE_NUM=$(gh issue list --repo best-koder-ever/DatingApp-Config \
  --search "$TASK_ID in:title" --json number --jq '.[0].number')

if [[ -z "$ISSUE_NUM" ]]; then
  echo "Issue not found for $TASK_ID" >&2
  exit 1
fi

# Get issue details
ISSUE_JSON=$(gh issue view "$ISSUE_NUM" --json title,body,labels)
TITLE=$(echo "$ISSUE_JSON" | jq -r .title)
BODY=$(echo "$ISSUE_JSON" | jq -r .body)
AGENT_MODE=$(echo "$BODY" | grep "Recommended Agent Mode" -A 3 | grep -o "CLI\|GitHub Copilot" | head -1)

if [[ "$AGENT_MODE" != "CLI"* ]]; then
  echo "Warning: Issue #$ISSUE_NUM recommends GitHub Copilot, not CLI agent"
  echo "Consider assigning to @copilot instead"
  read -p "Continue anyway? (y/N) " -n 1 -r
  echo
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
fi

# Extract affected files from issue body
AFFECTED_FILES=$(echo "$BODY" | sed -n '/## 📂 Affected Components/,/##/p' | grep -E '\.cs$|\.dart$|\.py$|\.json$|\.md$' | sed 's/^[- ]*//' | tr '\n' ' ')

echo "Implementing: $TITLE"
echo "Files: $AFFECTED_FILES"
echo ""
echo "Starting Aider..."

aider \
  --model anthropic/claude-3-5-sonnet-20241022 \
  --message "Implement $TASK_ID: $TITLE

FULL TASK DESCRIPTION:
$BODY

CRITICAL:
- Follow ALL acceptance criteria
- Add structured logging with CorrelationId  
- Write tests (unit + integration)
- Update contracts if needed
- Commit with message: '$TASK_ID: $TITLE'" \
  $AFFECTED_FILES
```

Usage:
```bash
chmod +x scripts/implement_task.sh
./scripts/implement_task.sh T024
```

---

## Aider Best Practices

### 1. Always Provide Context

❌ Bad:
```bash
aider --message "fix the bug" file.cs
```

✅ Good:
```bash
aider --message "Fix T024: Photo moderation not applying privacy rules.

Expected: Non-matches should see blurred photos when privacy=MatchOnly
Actual: All users see original photos

Root cause: ModerationService doesn't check privacy level before serving photos

Fix by:
1. Add privacy check to GetPhoto endpoint
2. Return blurred URL when viewer is not matched
3. Add test coverage" \
  photo-service/Controllers/PhotosController.cs \
  photo-service/Services/PhotoService.cs
```

### 2. Specify Expected Changes

```bash
aider --message "Add structured logging to all methods in UserProfilesController.

For each method:
- Log entry: LogInformation(\"Entering {Method}\", nameof(Method))
- Log operation: LogInformation(\"{Operation} for UserId {UserId}\", op, userId)
- Log errors: LogError(ex, \"Failed {Operation}\", op)

Include CorrelationId in all logs." \
  UserService/Controllers/UserProfilesController.cs
```

### 3. Use Git Integration

```bash
# Aider auto-commits by default
aider --auto-commits true --dirty-commits true --message "..." files...

# Review changes before committing
aider --no-auto-commits --message "..." files...
# Then manually: git diff, git add, git commit
```

### 4. Iterative Refinement

```bash
# Start interactive mode
aider UserService/Controllers/UserProfilesController.cs

> Add structured logging with CorrelationId

> Now add unit tests for the logging

> Refactor to reduce duplication

> /run dotnet test  # Run tests within Aider

> /commit with message "T023: Add structured logging + tests"

> /exit
```

---

## Comparison: CLI vs GitHub Copilot

| Factor | Aider (CLI) | GitHub Copilot Workspace |
|--------|-------------|--------------------------|
| **Setup** | `pip install aider-chat` | No setup (cloud) |
| **Local Testing** | ✅ Run tests immediately | ❌ Must pull PR to test |
| **Iteration Speed** | ✅ Fast (local) | ⚠️ Slower (wait for PR updates) |
| **Context Size** | ⚠️ Limited by model | ✅ Can access full repo |
| **Multi-file Refactors** | ✅ Excellent | ✅ Excellent |
| **Cost** | API costs (~$0.01-0.05/task) | Free (GitHub quota) |
| **Audit Trail** | Git commits | Issue → PR → Review |
| **Best For** | Complex tasks, rapid iteration | Async delegation, team workflow |

---

## Recommended Workflow

**For DatingApp MVP**:

1. **Foundational tasks (T015-T017)**: Aider CLI (need iteration)
2. **Well-defined features (T021, T022, T029)**: Aider CLI (need local testing)
3. **Simple implementations (T023, T026)**: GitHub Copilot (delegate async)
4. **Complex algorithms (T024, T032)**: Aider CLI (iterative tuning)
5. **Documentation (T060, T072)**: GitHub Copilot (straightforward)

**Daily Routine**:
```bash
# Morning: Check which tasks are ready
gh issue list --repo best-koder-ever/DatingApp-Config \
  --label "ai-ready" --state open

# Pick a CLI-recommended task
./scripts/implement_task.sh T024

# Delegate Copilot-recommended tasks
gh issue comment 5 --body "@copilot implement this"

# Afternoon: Review Copilot PRs, use Aider for fixes
```

---

## Troubleshooting

### Aider Can't Find Files

```bash
# Make sure you're in repo root
cd /home/m/development/DatingApp
aider <files>
```

### API Rate Limits

```bash
# Use faster/cheaper model for simple tasks
aider --model google/gemini-2.0-flash-exp --message "..." files...

# Add delays between batch tasks
sleep 5
```

### Aider Makes Wrong Changes

```bash
# Don't auto-commit, review first
aider --no-auto-commits --message "..." files...

# Check diff
git diff

# If wrong, reset and provide more context
git restore .
aider --message "More specific instructions..." files...
```

---

## Next Steps

1. **Install Aider**: `pip install aider-chat`
2. **Set API key**: `export ANTHROPIC_API_KEY=sk-ant-...`
3. **Test on T015** (documentation): `./scripts/implement_task.sh T015`
4. **Compare to Copilot** on T016: Assign to @copilot and see which you prefer

After rate limit resets, the sync script will create all issues with rich descriptions including agent recommendations!
