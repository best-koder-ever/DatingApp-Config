#!/usr/bin/env bash
# Automated task implementation using Aider CLI
# Usage: ./implement_task.sh T024

set -euo pipefail

TASK_ID="${1:-}"

if [[ -z "$TASK_ID" ]]; then
  echo "Usage: $0 TASK_ID" >&2
  echo "Example: $0 T024" >&2
  exit 1
fi

if ! command -v aider >/dev/null 2>&1; then
  echo "Error: aider not installed" >&2
  echo "Install: pip install aider-chat" >&2
  echo "See: docs/CLI_AGENT_SETUP.md" >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh CLI required" >&2
  exit 1
fi

# Find issue number for task
echo "Looking up issue for $TASK_ID..."
ISSUE_NUM=$(gh issue list --repo best-koder-ever/DatingApp-Config \
  --search "$TASK_ID in:title" --state open --json number --jq '.[0].number // empty')

if [[ -z "$ISSUE_NUM" ]]; then
  echo "Error: No open issue found for $TASK_ID" >&2
  echo "Run: bash scripts/sync_mvp_project.sh" >&2
  exit 1
fi

# Get issue details
echo "Fetching issue #$ISSUE_NUM..."
ISSUE_JSON=$(gh issue view "$ISSUE_NUM" --repo best-koder-ever/DatingApp-Config --json title,body,labels)
TITLE=$(echo "$ISSUE_JSON" | jq -r .title)
BODY=$(echo "$ISSUE_JSON" | jq -r .body)

# Check agent recommendation
AGENT_MODE=$(echo "$BODY" | grep -A 1 "Recommended Agent Mode" | grep "^\*\*" | sed 's/\*//g' | xargs || echo "Unknown")

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Task: $TITLE"
echo "  Issue: #$ISSUE_NUM"
echo "  Recommended Agent: $AGENT_MODE"
echo "═══════════════════════════════════════════════════════════"
echo ""

if [[ "$AGENT_MODE" == *"Copilot"* ]]; then
  echo "⚠️  WARNING: This task recommends GitHub Copilot, not CLI agent"
  echo ""
  echo "To delegate to Copilot:"
  echo "  gh issue comment $ISSUE_NUM --repo best-koder-ever/DatingApp-Config --body '@copilot implement this'"
  echo ""
  read -p "Continue with Aider anyway? (y/N) " -n 1 -r
  echo
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
fi

# Extract affected files from issue body (look for file paths in markdown)
AFFECTED_FILES=$(echo "$BODY" | grep -E '\.(cs|dart|py|json|md|yml|yaml)' | \
  grep -v "^#" | \
  sed -E 's/.*`([^`]+\.(cs|dart|py|json|md|yml|yaml))`/\1/' | \
  grep -E '\.(cs|dart|py|json|md|yml|yaml)$' | \
  sort -u || echo "")

if [[ -n "$AFFECTED_FILES" ]]; then
  echo "Detected files from issue:"
  echo "$AFFECTED_FILES" | sed 's/^/  - /'
  echo ""
else
  echo "⚠️  No files auto-detected. You may need to specify them manually."
  echo ""
fi

# Save full issue body to temp file for reference
ISSUE_FILE="/tmp/aider-issue-$TASK_ID.md"
echo "$BODY" > "$ISSUE_FILE"
echo "Issue details saved to: $ISSUE_FILE"
echo ""

# Construct Aider prompt
AIDER_PROMPT="Implement $TASK_ID: $TITLE

Full task specification is in: $ISSUE_FILE

CRITICAL REQUIREMENTS:
- Read the FULL issue description from $ISSUE_FILE
- Follow ALL acceptance criteria listed
- Add structured logging with CorrelationId to all new/modified methods
  Format: _logger.LogInformation(\"{Operation} {Status} {Data}\", op, status, data)
- Write tests (unit + integration as specified)
- Update API contracts if schemas change
- Use clear commit messages

LOGGING TEMPLATE:
- Entry: _logger.LogInformation(\"Entering {Method}\", nameof(MethodName))
- Operation: _logger.LogInformation(\"{Operation} for {Entity} {Id}\", \"Create\", \"User\", userId)
- Success: _logger.LogInformation(\"{Operation} completed {Status}\", op, \"Success\")
- Error: _logger.LogError(ex, \"{Operation} failed {Context}\", op, context)

When done, commit with message: '$TASK_ID: $TITLE'
"

echo "Starting Aider..."
echo ""

# Check if files exist, if not, let Aider figure it out
if [[ -n "$AFFECTED_FILES" ]]; then
  # Convert to space-separated, check existence
  FILE_ARGS=""
  while IFS= read -r file; do
    if [[ -f "$file" ]]; then
      FILE_ARGS="$FILE_ARGS $file"
    else
      echo "⚠️  File not found (will be created): $file"
    fi
  done <<< "$AFFECTED_FILES"
  
  if [[ -n "$FILE_ARGS" ]]; then
    aider \
      --model anthropic/claude-3-5-sonnet-20241022 \
      --message "$AIDER_PROMPT" \
      $FILE_ARGS
  else
    echo "No existing files found. Running Aider without file arguments..."
    aider \
      --model anthropic/claude-3-5-sonnet-20241022 \
      --message "$AIDER_PROMPT"
  fi
else
  # Interactive mode - let user add files
  echo "No files auto-detected. Starting interactive Aider session..."
  echo "Use /add <file> to add files, then paste the implementation prompt."
  echo ""
  aider --model anthropic/claude-3-5-sonnet-20241022
fi

echo ""
echo "✅ Aider session complete"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Run tests: dotnet test (or flutter test, python3 -m pytest)"
echo "  3. Verify locally: ./dev-start.sh"
echo "  4. Create PR: gh pr create --fill"
echo "  5. Link to issue: gh pr comment --body 'Closes #$ISSUE_NUM'"
