#!/usr/bin/env bash
# Add Phase 0 and Phase 1 options to GitHub Project #2

set -uo pipefail

PROJECT_NUMBER="2"
OWNER="best-koder-ever"

echo "🔍 Adding Phase 0 and Phase 1 to Project #$PROJECT_NUMBER..."
echo ""

# Check rate limit
remaining=$(gh api rate_limit | jq '.resources.graphql.remaining')
if [[ $remaining -lt 10 ]]; then
  reset_time=$(gh api rate_limit | jq -r '.resources.graphql.reset | strftime("%H:%M:%S")')
  echo "⚠️  GraphQL rate limit too low ($remaining/5000)"
  echo "   Resets at: $reset_time"
  echo ""
  echo "Manual option:"
  echo "1. Go to https://github.com/users/$OWNER/projects/$PROJECT_NUMBER/settings"
  echo "2. Find 'Phase' field"
  echo "3. Add options: 'Phase 0' and 'Phase 1'"
  exit 1
fi

# Get project ID
echo "📦 Fetching project ID..."
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
' -f owner="$OWNER" -F number=$PROJECT_NUMBER)

project_id=$(echo "$project_data" | jq -r '.data.user.projectV2.id')
phase_field=$(echo "$project_data" | jq -r '.data.user.projectV2.fields.nodes[] | select(.name == "Phase")')
field_id=$(echo "$phase_field" | jq -r '.id')

if [[ -z "$field_id" || "$field_id" == "null" ]]; then
  echo "❌ Phase field not found in project"
  exit 1
fi

echo "✓ Project ID: $project_id"
echo "✓ Phase Field ID: $field_id"
echo ""

# Check existing options
echo "📋 Current Phase options:"
echo "$phase_field" | jq -r '.options[] | "  - \(.name)"'
echo ""

# Add Phase 0
echo "➕ Adding 'Phase 0'..."
gh api graphql -f query='
  mutation($projectId: ID!, $fieldId: ID!, $name: String!) {
    addProjectV2SingleSelectFieldOption(input: {
      projectId: $projectId
      fieldId: $fieldId
      name: $name
    }) {
      option {
        id
        name
      }
    }
  }
' -f projectId="$project_id" -f fieldId="$field_id" -f name="Phase 0" > /dev/null && echo "✓ Added Phase 0"

# Add Phase 1
echo "➕ Adding 'Phase 1'..."
gh api graphql -f query='
  mutation($projectId: ID!, $fieldId: ID!, $name: String!) {
    addProjectV2SingleSelectFieldOption(input: {
      projectId: $projectId
      fieldId: $fieldId
      name: $name
    }) {
      option {
        id
        name
      }
    }
  }
' -f projectId="$project_id" -f fieldId="$field_id" -f name="Phase 1" > /dev/null && echo "✓ Added Phase 1"

echo ""
echo "✅ Phase options added successfully!"
echo ""
echo "Now run the sync script to tag all tasks:"
echo "  ./scripts/sync_mvp_project_fast.sh"
