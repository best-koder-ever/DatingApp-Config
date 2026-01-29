#!/usr/bin/env bash
# Bootstrap GitHub issues cache using REST API (bypasses GraphQL rate limits)

REPO="best-koder-ever/DatingApp-Config"
CACHE_FILE="/tmp/github_issues_cache.json"

echo "🔄 Bootstrapping GitHub issues cache for $REPO..."
echo "   (Using REST API - no GraphQL required)"
echo ""

# Fetch all issues with pagination (up to 300 issues)
ALL_ISSUES="[]"
for page in 1 2 3; do
  echo "   Fetching page $page..."
  PAGE_DATA=$(curl -s -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $(gh auth token)" \
    "https://api.github.com/repos/$REPO/issues?state=all&per_page=100&page=$page")
  
  # Check if we got an empty array (no more issues)
  if [[ "$(echo "$PAGE_DATA" | jq 'length')" == "0" ]]; then
    break
  fi
  
  ALL_ISSUES=$(echo "$ALL_ISSUES" "$PAGE_DATA" | jq -s 'add')
done

# Transform to match expected format
echo "$ALL_ISSUES" | jq '[.[] | {number: .number, title: .title, state: .state}]' > "$CACHE_FILE"

ISSUE_COUNT=$(jq 'length' "$CACHE_FILE")
TASK_COUNT=$(jq '[.[] | select(.title | test("^T[0-9]{3}"))] | length' "$CACHE_FILE")

echo ""
echo "✅ Cache created: $CACHE_FILE"
echo "   Total issues: $ISSUE_COUNT"
echo "   Task issues: $TASK_COUNT"
echo ""
echo "💡 Now run: bash scripts/sync_mvp_project_fast.sh"
