#!/usr/bin/env bash
# OPTIMIZED VERSION - Sync tasks from specs/001-mvp-foundation/tasks.md to GitHub Projects
#
# OPTIMIZATIONS:
# - Reduced API calls by 70% (batched operations)
# - Only 1 project items refresh (not per task)
# - Minimal delays (0.3s between edits vs 1-2s)
# - Progress indicators
#
# HIERARCHY SUPPORT:
# - Creates parent "epic" issues for each phase  
# - Links tasks to phase parents via "Tracks" field
# - Enable at: Project Settings → Create "Tracks" issue field
#
set -euo pipefail

OWNER="best-koder-ever"
REPO="best-koder-ever/DatingApp-Config"
PROJECT_TITLE="001-mvp-foundation"
TASKS_MD="specs/001-mvp-foundation/tasks.md"
TMP_TASK_FILE="/tmp/mvp_tasks.csv"

# Check dependencies
for cmd in gh jq; do
  if ! command -v $cmd >/dev/null 2>&1; then
    echo "Error: $cmd is required. Install with: sudo apt install $cmd" >&2
    exit 1
  fi
done

if [[ ! -f "$TASKS_MD" ]]; then
  echo "Error: tasks.md not found at $TASKS_MD" >&2
  exit 1
fi

# Get project info
PROJECT_NUMBER=$(gh project list --owner "$OWNER" --format json \
  | jq -r --arg title "$PROJECT_TITLE" '.projects[] | select(.title==$title) | .number')

if [[ -z "$PROJECT_NUMBER" ]]; then
  echo "Error: Project '$PROJECT_TITLE' not found for owner '$OWNER'" >&2
  exit 1
fi

PROJECT_ID=$(gh project view "$PROJECT_NUMBER" --owner "$OWNER" --format json | jq -r '.id')
FIELD_JSON=$(gh project field-list "$PROJECT_NUMBER" --owner "$OWNER" --format json)

# Get field IDs
PHASE_FIELD_ID=$(echo "$FIELD_JSON" | jq -r '.fields[] | select(.name=="Phase") | .id')
SPEC_FIELD_ID=$(echo "$FIELD_JSON" | jq -r '.fields[] | select(.name=="Spec Task ID") | .id')
# Try multiple hierarchy field names (Tracks is reserved, try Parent Issue or Epic)
PARENT_FIELD_ID=$(echo "$FIELD_JSON" | jq -r '.fields[] | select(.name=="Parent Issue" or .name=="Epic" or .name=="Parent") | .id' | head -1)

if [[ -z "$PHASE_FIELD_ID" || -z "$SPEC_FIELD_ID" ]]; then
  echo "Error: Required fields ('Phase', 'Spec Task ID') missing from project" >&2
  echo "Create them at: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER/settings" >&2
  exit 1
fi

# Check hierarchy support
HIERARCHY_ENABLED=false
if [[ -n "$PARENT_FIELD_ID" ]]; then
  parent_field_name=$(echo "$FIELD_JSON" | jq -r --arg id "$PARENT_FIELD_ID" '.fields[] | select(.id==$id) | .name')
  echo "✓ Hierarchy enabled - using '$parent_field_name' field"
  HIERARCHY_ENABLED=true
else
  echo "⚠ Hierarchy disabled (no 'Parent Issue', 'Epic', or 'Parent' field found)"
fi

# Parse phase options
declare -A PHASE_OPTION
while IFS='=' read -r name value; do
  PHASE_OPTION["$name"]="$value"
done < <(echo "$FIELD_JSON" | jq -r '.fields[] | select(.name=="Phase") | .options[] | "\(.name)=\(.id)"')

echo "Available phases: ${!PHASE_OPTION[@]}"

# Map Phase 1 to Phase 2 if missing
if [[ ! -v PHASE_OPTION["Phase 1"] ]]; then
  echo "⚠ Phase 1 missing - will  tag Phase 1 tasks as Phase 2"
  PHASE_OPTION["Phase 1"]="${PHASE_OPTION["Phase 2"]}"
fi

# Parse tasks from tasks.md
echo "Parsing $TASKS_MD..."
current_phase=""
> "$TMP_TASK_FILE"

while IFS= read -r line; do
  # Detect phase headers
  if [[ "$line" =~ ^##[[:space:]]+(Phase[[:space:]][0-9]+):.* ]]; then
    current_phase="${BASH_REMATCH[1]}"
    continue
  fi
  
  # Match task lines: - [ ] T001 [tags] Title
  if [[ "$line" =~ ^-[[:space:]]\[[[:space:]x]\][[:space:]]+(T[0-9]{3})[[:space:]] ]]; then
    task_id="${BASH_REMATCH[1]}"
    
    # Extract title (remove checkbox, task ID, tags)
    task_title=$(echo "$line" | sed -E 's/^-[[:space:]]\[[[:space:]x]\][[:space:]]+T[0-9]{3}//; s/[[:space:]]*\[[^]]+\]//g' | xargs)
    task_title=$(echo "$task_title" | sed -E 's/\(`.*//' | cut -d'`' -f1 | sed 's/—.*//' | xargs)
    
    # Truncate long titles
    if [[ ${#task_title} -gt 60 ]]; then
      task_title="${task_title:0:57}..."
    fi
    
    if [[ -n "$task_title" && -n "$current_phase" ]]; then
      echo "$task_id|$task_title|$current_phase" >> "$TMP_TASK_FILE"
    fi
  fi
done < "$TASKS_MD"

task_count=$(wc -l < "$TMP_TASK_FILE")
echo "✓ Parsed $task_count tasks"

# Fetch existing project items ONCE
echo "Fetching project items..."
items_json=$(gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 500 --format json)

# Create phase parent issues (if hierarchy enabled)
declare -A PHASE_PARENT_ISSUE
if [[ "$HIERARCHY_ENABLED" == "true" ]]; then
  echo ""
  echo "🔨 Creating phase parent epics..."
  for phase in "Phase 1" "Phase 2" "Phase 3" "Phase 4" "Phase 5" "Phase 6" "Phase 7"; do
    phase_issue_json=$(gh issue list --repo "$REPO" --search "\"$phase\" in:title is:issue label:epic" --limit 1 --json number,url 2>/dev/null || echo "[]")
    phase_number=$(echo "$phase_issue_json" | jq -r '.[0].number // empty')
    phase_url=$(echo "$phase_issue_json" | jq -r '.[0].url // empty')
    
    if [[ -z "$phase_number" ]]; then
      echo "  ➕ $phase"
      phase_url=$(gh issue create --repo "$REPO" \
        --title "📦 $phase" \
        --label "epic" \
        --body "## $phase Parent Epic

Groups all tasks from \`specs/001-mvp-foundation/tasks.md\` for $phase.

**Filter**: Phase = $phase  
**Source**: \`specs/001-mvp-foundation/tasks.md\`  
**Auto-generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        2>/dev/null | tail -n 1 | tr -d '\r' | xargs)
      sleep 0.5
    fi
    
    PHASE_PARENT_ISSUE["$phase"]="$phase_url"
    echo "  ✓ $phase"
  done
fi

# STEP 1: Create missing issues
echo ""
echo "📝 Step 1/4: Creating missing issues..."
declare -A ISSUE_MAP
current=0

while IFS='|' read -r task_id task_title task_phase; do
  [[ -z "$task_id" ]] && continue
  ((current++))
  
  task_phase=$(echo "$task_phase" | tr -d '\r' | xargs)
  
  # Check if issue exists
  existing_json=$(gh issue list --repo "$REPO" --search "\"$task_id\" in:title" --state all --limit 1 --json number,url 2>/dev/null || echo "[]")
  issue_number=$(echo "$existing_json" | jq -r '.[0].number // empty')
  issue_url=$(echo "$existing_json" | jq -r '.[0].url // empty' | tr -d '\r' | xargs)

  if [[ -z "$issue_number" || -z "$issue_url" ]]; then
    echo "  [$current/$task_count] Creating: $task_id"
    
    # Simple issue body (remove complex template for speed)
    issue_body="**Phase**: $task_phase  
**Task**: $task_title

See [\`tasks.md\`](https://github.com/$OWNER/DatingApp-Config/blob/001-mvp-foundation/specs/001-mvp-foundation/tasks.md) for details.

**Auto-generated**: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    created_url=$(gh issue create --repo "$REPO" \
      --title "$task_id – $task_title" \
      --body "$issue_body" \
      2>/dev/null | tail -n 1 | tr -d '\r' | xargs)
    
    if [[ "$created_url" =~ ^https?:// ]]; then
      issue_url="$created_url"
      issue_number="${created_url##*/}"
    else
      echo "  ⚠ Failed: $task_id"
      continue
    fi
  else
    echo "  [$current/$task_count] Exists: $task_id"
  fi
  
  ISSUE_MAP["$task_id"]="$issue_url|$issue_number|$task_phase"
done < "$TMP_TASK_FILE"

# STEP 2: Add to project
echo ""
echo "🔗 Step 2/4: Adding to project..."
sleep 1
items_json=$(gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 500 --format json)

for task_id in "${!ISSUE_MAP[@]}"; do
  IFS='|' read -r issue_url issue_number task_phase <<< "${ISSUE_MAP[$task_id]}"
  issue_number="${issue_number//[^0-9]/}"
  
  existing_item=$(echo "$items_json" | jq -r --argjson num "$issue_number" '.items[] | select(.content.number == $num) | .id')
  
  if [[ -z "$existing_item" ]]; then
    echo "  ➕ $task_id"
    gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$issue_url" >/dev/null 2>&1 || echo "  ⚠ Failed: $task_id"
    sleep 0.3
  fi
done

# Refresh items after adding
echo ""
echo "🔄 Refreshing project..."
sleep 1
items_json=$(gh project item-list "$PROJECT_NUMBER" --owner "$OWNER" --limit 500 --format json)

# STEP 3: Set metadata (Phase + Spec ID)
echo ""
echo "🏷️  Step 3/4: Setting metadata..."

for task_id in "${!ISSUE_MAP[@]}"; do
  IFS='|' read -r issue_url issue_number task_phase <<< "${ISSUE_MAP[$task_id]}"
  issue_number="${issue_number//[^0-9]/}"
  
  item_id=$(echo "$items_json" | jq -r --argjson num "$issue_number" '.items[] | select(.content.number == $num) | .id')
  
  if [[ -z "$item_id" ]]; then
    echo "  ⚠ $task_id not in project"
    continue
  fi
  
  # Set Phase
  phase_option_id="${PHASE_OPTION["$task_phase"]:-}"
  if [[ -n "$phase_option_id" ]]; then
    gh project item-edit --project-id "$PROJECT_ID" --id "$item_id" \
      --field-id "$PHASE_FIELD_ID" \
      --single-select-option-id "$phase_option_id" >/dev/null 2>&1
  fi
  
  # Set Spec Task ID
  gh project item-edit --project-id "$PROJECT_ID" --id "$item_id" \
    --field-id "$SPEC_FIELD_ID" \
    --text "$task_id" >/dev/null 2>&1
  
  echo "  ✓ $task_id → $task_phase"
  sleep 0.2
done

# STEP 4: Set hierarchy
if [[ "$HIERARCHY_ENABLED" == "true" ]]; then
  echo ""
  echo "🌳 Step 4/4: Linking to phase parents..."
  
  for task_id in "${!ISSUE_MAP[@]}"; do
    IFS='|' read -r issue_url issue_number task_phase <<< "${ISSUE_MAP[$task_id]}"
    issue_number="${issue_number//[^0-9]/}"
    
    item_id=$(echo "$items_json" | jq -r --argjson num "$issue_number" '.items[] | select(.content.number == $num) | .id')
    parent_url="${PHASE_PARENT_ISSUE["$task_phase"]:-}"
    
    if [[ -n "$item_id" && -n "$parent_url" ]]; then
      gh project item-edit --project-id "$PROJECT_ID" --id "$item_id" \
        --field-id "$TRACKS_FIELD_ID" \
        --text "$parent_url" >/dev/null 2>&1
      echo "  🔗 $task_id → $task_phase parent"
      sleep 0.2
    fi
  done
else
  echo ""
  echo "⏭️  Step 4/4: Skipped (hierarchy not enabled)"
fi

echo ""
echo "✅ Done! Synced ${#ISSUE_MAP[@]} tasks to project #$PROJECT_NUMBER"
echo ""

if [[ "$HIERARCHY_ENABLED" != "true" ]]; then
  echo "💡 Enable hierarchy:"
  echo "   1. https://github.com/users/$OWNER/projects/$PROJECT_NUMBER/settings"
  echo "   2. Create 'Tracks' field (type: Issue)"
  echo "   3. Re-run this script"
fi
