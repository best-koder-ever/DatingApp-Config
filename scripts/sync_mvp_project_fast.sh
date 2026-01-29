#!/usr/bin/env bash
set -uo pipefail

REPO="best-koder-ever/DatingApp-Config"
PROJECT_NUMBER="2"
TASK_FILE="specs/001-mvp-foundation/tasks.md"
TMP_TASK_FILE="/tmp/mvp_tasks.csv"
TMP_EXISTING="/tmp/existing_issues.json"

# Map phase numbers to descriptive names (matches GitHub Project field options)
declare -A PHASE_MAP=(
  ["Phase 0"]="P0 - Planning & Visibility"
  ["Phase 1"]="P1 - Infrastructure"
  ["Phase 2"]="P2 - Foundation"
  ["Phase 3"]="P3 - Onboarding"
  ["Phase 4"]="P4 - Discovery"
  ["Phase 5"]="P5 - Messaging"
  ["Phase 6"]="P6 - Safety"
  ["Phase 7"]="P7 - Polish"
  ["Phase 8"]="P8 - Testing"
)

echo "🚀 Fast Sync (with Project linking)"

# Parse tasks
echo "📖 Parsing tasks..."
rm -f "$TMP_TASK_FILE"
current_phase=""

while IFS= read -r line; do
  if [[ "$line" =~ ^##[[:space:]]+(Phase[[:space:]][0-9]) ]]; then
    raw_phase="${BASH_REMATCH[1]}"
    # Map to descriptive name
    current_phase="${PHASE_MAP[$raw_phase]:-$raw_phase}"
  elif [[ "$line" =~ ^-[[:space:]]\[([[:space:]x])\][[:space:]]+(T[0-9]{3})[[:space:]]+(.+)$ ]]; then
    checkbox="${BASH_REMATCH[1]}"
    task_id="${BASH_REMATCH[2]}"
    task_title="${BASH_REMATCH[3]}"
    task_title=$(echo "$task_title" | tr -d '\n\r' | xargs 2>/dev/null || echo "$task_title" | tr -d '\n\r')
    
    [[ "$checkbox" == "x" ]] && task_status="complete" || task_status="incomplete"
    echo "$task_id|$task_title|$current_phase|$task_status" >> "$TMP_TASK_FILE"
  fi
done < "$TASK_FILE"

task_count=$(wc -l < "$TMP_TASK_FILE")
complete_count=$(grep -c "|complete$" "$TMP_TASK_FILE" || echo 0)
echo "✓ Parsed $task_count tasks ($complete_count complete)"

# Cache existing issues
echo "📦 Caching issues..."
gh issue list --repo "$REPO" --state all --limit 500 --json number,title,state > "$TMP_EXISTING"
existing=$(jq '[.[] | select(.title | test("^T[0-9]{3}"))] | length' "$TMP_EXISTING")
echo "✓ Found $existing task issues"

# Create missing
echo "🔨 Creating missing issues..."
created=0
total=0

while IFS='|' read -r tid _ _ _; do
  [[ -z "$(jq -r --arg t "$tid" '.[] | select(.title | startswith($t)) | .number' "$TMP_EXISTING")" ]] && ((total++)) || true
done < "$TMP_TASK_FILE"

if [[ $total -eq 0 ]]; then
  echo "✓ All issues exist"
else
  echo "Creating $total issues..."
  while IFS='|' read -r tid ttitle _ tstatus; do
    if [[ -z "$(jq -r --arg t "$tid" '.[] | select(.title | startswith($t)) | .number' "$TMP_EXISTING")" ]]; then
      ((created++))
      gh issue create --repo "$REPO" \
        --title "$tid – $ttitle" \
        --body "**Spec:** $tid | **Status:** $tstatus | See tasks.md" \
        > /dev/null 2>&1 || echo "  ⚠ Failed: $tid"
      
      (( created % 10 == 0 )) && echo "  [$created/$total]" || true
    fi
  done < "$TMP_TASK_FILE"
  echo "✓ Created $created issues"
fi

# Refresh cache
gh issue list --repo "$REPO" --state all --limit 500 --json number,title,state > "$TMP_EXISTING"

# Sync states
echo "🔒 Syncing states..."
closed=0
reopened=0

while IFS='|' read -r tid _ _ tstatus; do
  num="$(jq -r --arg t "$tid" '.[] | select(.title | startswith($t)) | .number' "$TMP_EXISTING")"
  state="$(jq -r --arg t "$tid" '.[] | select(.title | startswith($t)) | .state' "$TMP_EXISTING")"
  
  [[ -z "$num" ]] && continue
  
  if [[ "$tstatus" == "complete" && "$state" == "OPEN" ]]; then
    gh issue close "$num" --repo "$REPO" > /dev/null 2>&1 && ((closed++)) || true
  elif [[ "$tstatus" == "incomplete" && "$state" == "CLOSED" ]]; then
    gh issue reopen "$num" --repo "$REPO" > /dev/null 2>&1 && ((reopened++)) || true
  fi
done < "$TMP_TASK_FILE"

[[ $closed -gt 0 || $reopened -gt 0 ]] && echo "✓ Closed $closed, reopened $reopened" || echo "✓ States correct"

# Add to project
echo "🔗 Adding to project #$PROJECT_NUMBER..."
added=0

while IFS='|' read -r tid _ _ _; do
  num="$(jq -r --arg t "$tid" '.[] | select(.title | startswith($t)) | .number' "$TMP_EXISTING")"
  [[ -z "$num" ]] && continue
  
  # Check if already in project
  in_project=$(gh project item-list "$PROJECT_NUMBER" --owner best-koder-ever --format json --limit 1000 2>/dev/null | jq -r --arg n "$num" '.items[] | select(.content.number == ($n | tonumber)) | .id' || echo "")
  
  if [[ -z "$in_project" ]]; then
    issue_url="https://github.com/$REPO/issues/$num"
    gh project item-add "$PROJECT_NUMBER" --owner best-koder-ever --url "$issue_url" > /dev/null 2>&1 && ((added++)) || true
    
    (( added % 20 == 0 )) && echo "  [$added added]" || true
  fi
done < "$TMP_TASK_FILE"

[[ $added -gt 0 ]] && echo "✓ Added $added items to project" || echo "✓ All already in project"

echo ""
echo "✅ Sync complete!"
echo "   📊 Total: $task_count tasks ($complete_count complete)"
echo "   🔗 View: https://github.com/users/best-koder-ever/projects/2"
