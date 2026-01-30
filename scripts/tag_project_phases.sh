#!/usr/bin/env bash
# Tag all project items with their Phase field

set -uo pipefail

PROJECT_NUMBER="2"
PROJECT_OWNER="best-koder-ever"
REPO="best-koder-ever/DatingApp-Config"
TMP_TASK_FILE="/tmp/mvp_tasks.csv"

echo "🏷️  Tagging all tasks with Phase field..."
echo ""

# Check rate limit
remaining=$(gh api rate_limit | jq '.resources.graphql.remaining')
if [[ $remaining -lt 200 ]]; then
  reset_time=$(gh api rate_limit | jq -r '.resources.graphql.reset | strftime("%H:%M:%S")')
  echo "⚠️  GraphQL rate limit too low ($remaining/5000)"
  echo "   Resets at: $reset_time"
  echo "   Need ~200 calls for 133 tasks"
  exit 1
fi

echo "✓ Rate limit OK: $remaining/5000"
echo ""

# Get project ID and Phase field ID
echo "📦 Fetching project metadata..."
project_data=$(gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
        fields(first: 20) {
          nodes {
            ... on ProjectV2SingleSelectField {
              id
              name
              options {
                id
                name
              }
            }
          }
        }
      }
    }
  }
' -f owner="$PROJECT_OWNER" -F number=$PROJECT_NUMBER)

project_id=$(echo "$project_data" | jq -r '.data.user.projectV2.id')
phase_field=$(echo "$project_data" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Phase")')
field_id=$(echo "$phase_field" | jq -r '.id')

if [[ -z "$field_id" || "$field_id" == "null" ]]; then
  echo "❌ Phase field not found"
  exit 1
fi

echo "✓ Project ID: $project_id"
echo "✓ Phase Field ID: $field_id"
echo ""

# Build phase option ID map
declare -A PHASE_OPTION_IDS
while IFS='|' read -r opt_id opt_name; do
  PHASE_OPTION_IDS["$opt_name"]="$opt_id"
done < <(echo "$phase_field" | jq -r '.options[] | "\(.id)|\(.name)"')

echo "📋 Available phase options:"
for phase in "${!PHASE_OPTION_IDS[@]}"; do
  echo "  - $phase"
done
echo ""

# Get all project items with their issue numbers
echo "🔍 Fetching project items..."
items_data=$(gh api graphql -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        items(first: 200) {
          nodes {
            id
            content {
              ... on Issue {
                number
                title
              }
            }
          }
        }
      }
    }
  }
' -f owner="$PROJECT_OWNER" -F number=$PROJECT_NUMBER)

# Process each task from CSV
echo "🏷️  Setting Phase field for each task..."
tagged=0
skipped=0
failed=0

while IFS='|' read -r task_id task_title task_phase task_status; do
  # Find project item ID for this task
  issue_num=$(jq -r --arg tid "$task_id" '.data.user.projectV2.items.nodes[] | select(.content.title | startswith($tid)) | .content.number' <<< "$items_data")
  item_id=$(jq -r --arg tid "$task_id" '.data.user.projectV2.items.nodes[] | select(.content.title | startswith($tid)) | .id' <<< "$items_data")
  
  if [[ -z "$item_id" || "$item_id" == "null" ]]; then
    echo "  ⏭️  Skipped $task_id (not in project)"
    ((skipped++))
    continue
  fi
  
  # Get phase option ID
  phase_option_id="${PHASE_OPTION_IDS[$task_phase]:-}"
  
  if [[ -z "$phase_option_id" ]]; then
    echo "  ⚠️  No option for phase: $task_phase ($task_id)"
    ((failed++))
    continue
  fi
  
  # Set the field value
  gh api graphql -f query='
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: $value
      }) {
        projectV2Item {
          id
        }
      }
    }
  ' -f projectId="$project_id" \
    -f itemId="$item_id" \
    -f fieldId="$field_id" \
    -f value="{\"singleSelectOptionId\": \"$phase_option_id\"}" \
    > /dev/null 2>&1
  
  if [[ $? -eq 0 ]]; then
    ((tagged++))
    (( tagged % 10 == 0 )) && echo "  [Tagged $tagged tasks]" || true
  else
    echo "  ❌ Failed: $task_id"
    ((failed++))
  fi
  
done < "$TMP_TASK_FILE"

echo ""
echo "✅ Phase tagging complete!"
echo "   ✓ Tagged: $tagged"
echo "   ⏭️  Skipped: $skipped (not in project)"
echo "   ❌ Failed: $failed"
