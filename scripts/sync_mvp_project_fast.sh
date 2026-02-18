#!/usr/bin/env bash
set -uo pipefail

REPO="best-koder-ever/DatingApp-Config"
PROJECT_NUMBER="2"
PROJECT_OWNER="best-koder-ever"
TASK_FILE="specs/001-mvp-foundation/tasks.md"
TMP_TASK_FILE="/tmp/mvp_tasks.csv"
CACHE_FILE="/tmp/github_issues_cache.json"
LAST_SYNC_FILE="/tmp/last_sync_state.txt"

# Check GraphQL rate limit (separate from REST)
echo "🔍 Checking API rate limits..."
RATE_LIMIT=$(gh api rate_limit 2>/dev/null || echo '{"resources":{"core":{"remaining":5000},"graphql":{"remaining":0}}}')
REST_REMAINING=$(echo "$RATE_LIMIT" | jq -r '.resources.core.remaining // 5000')
GRAPHQL_REMAINING=$(echo "$RATE_LIMIT" | jq -r '.resources.graphql.remaining // 0')
GRAPHQL_RESET=$(echo "$RATE_LIMIT" | jq -r '.resources.graphql.reset // 0')

echo "   REST API: $REST_REMAINING remaining"
echo "   GraphQL: $GRAPHQL_REMAINING remaining"

if [[ $GRAPHQL_REMAINING -lt 10 ]]; then
  RESET_DATE=$(date -d "@$GRAPHQL_RESET" 2>/dev/null || date -r "$GRAPHQL_RESET" 2>/dev/null || echo "unknown")
  echo ""
  echo "⚠️  GraphQL rate limit exhausted ($GRAPHQL_REMAINING remaining)"
  echo "   Resets at: $RESET_DATE"
  
  # Check if cache is available
  if [[ -f "$CACHE_FILE" ]]; then
    CACHE_AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0)))
    echo "   📦 Using cached data from $(date -d @"$(($(date +%s) - CACHE_AGE))" '+%H:%M:%S' 2>/dev/null || echo "${CACHE_AGE}s ago")"
  else
    echo ""
    echo "❌ Cannot proceed:"
    echo "   - GraphQL API exhausted (needed for 'gh issue list')"
    echo "   - No cached data available"
    echo "   - Wait ~1 hour or use REST API fallback"
    exit 1
  fi
fi

echo ""
echo "🚀 Fast Sync (rate-limit optimized)"

# Parse tasks
echo "📖 Parsing tasks from tasks.md..."
rm -f "$TMP_TASK_FILE"
current_phase=""

# First pass: collect all tasks (may have duplicate T-IDs across phases)
TMP_RAW="/tmp/mvp_tasks_raw.csv"
rm -f "$TMP_RAW"
while IFS= read -r line; do
  if [[ "$line" =~ ^##[[:space:]]+(Phase[[:space:]][0-9]+) ]]; then
    current_phase="${BASH_REMATCH[1]}"
  elif [[ "$line" =~ ^-[[:space:]]\[([[:space:]x])\][[:space:]]+(T[0-9]{3})[[:space:]]+(.+)$ ]]; then
    checkbox="${BASH_REMATCH[1]}"
    task_id="${BASH_REMATCH[2]}"
    task_title="${BASH_REMATCH[3]}"
    task_title=$(echo "$task_title" | tr -d '\n\r' | xargs 2>/dev/null || echo "$task_title" | tr -d '\n\r')
    
    [[ "$checkbox" == "x" ]] && task_status="complete" || task_status="incomplete"
    echo "$task_id|$task_title|$current_phase|$task_status" >> "$TMP_RAW"
  fi
done < "$TASK_FILE"

# Second pass: deduplicate T-IDs — if ANY instance is complete, mark complete
# (handles Phase 0 deferred tasks vs Phase 1/2 implemented tasks with same T-ID)
awk -F'|' '{
  if (!seen[$1] || $4 == "complete") {
    seen[$1] = 1
    data[$1] = $0
  }
} END {
  for (id in data) print data[id]
}' "$TMP_RAW" | sort -t'|' -k1,1 > "$TMP_TASK_FILE"

task_count=$(wc -l < "$TMP_TASK_FILE")
complete_count=$(grep -c "|complete$" "$TMP_TASK_FILE" || echo 0)
echo "✓ Parsed $task_count tasks ($complete_count complete)"

# Use cached issues if available or fetch if rate limit OK
if [[ -f "$CACHE_FILE" ]]; then
  CACHE_AGE=$(($(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0)))
  if [[ $CACHE_AGE -lt 300 ]]; then
    echo "📦 Using cached issues (${CACHE_AGE}s old)"
    cp "$CACHE_FILE" /tmp/existing_issues.json
  elif [[ $GRAPHQL_REMAINING -gt 10 ]]; then
    echo "📦 Refreshing cache (stale, ${CACHE_AGE}s old)..."
    gh issue list --repo "$REPO" --state all --limit 1000 --json number,title,state > /tmp/existing_issues.json 2>/dev/null || {
      echo "⚠️  Fetch failed, using stale cache"
      cp "$CACHE_FILE" /tmp/existing_issues.json
    }
    cp /tmp/existing_issues.json "$CACHE_FILE" 2>/dev/null || true
  else
    echo "📦 Using stale cache (${CACHE_AGE}s old, rate limit low)"
    cp "$CACHE_FILE" /tmp/existing_issues.json
  fi
elif [[ $GRAPHQL_REMAINING -gt 10 ]]; then
  echo "📦 Fetching issues (no cache)..."
  gh issue list --repo "$REPO" --state all --limit 1000 --json number,title,state > /tmp/existing_issues.json 2>/dev/null || {
    echo "❌ Failed to fetch issues and no cache available"
    exit 1
  }
  cp /tmp/existing_issues.json "$CACHE_FILE"
else
  echo "❌ No cache and rate limit exhausted"
  exit 1
fi

existing=$(jq '[.[] | select(.title | test("^T[0-9]{3}"))] | length' /tmp/existing_issues.json)
echo "✓ Found $existing task issues in cache/GitHub"

# Detect what changed since last sync
changes_needed=false
if [[ -f "$LAST_SYNC_FILE" ]]; then
  echo "🔍 Detecting changes since last sync..."
  LAST_COMPLETE=$(grep "^complete:" "$LAST_SYNC_FILE" 2>/dev/null | cut -d: -f2 || echo 0)
  CURR_COMPLETE=$complete_count
  
  if [[ $CURR_COMPLETE -ne $LAST_COMPLETE ]]; then
    DIFF=$((CURR_COMPLETE - LAST_COMPLETE))
    echo "✓ Detected $DIFF newly completed tasks"
    changes_needed=true
  else
    echo "✓ No status changes detected"
  fi
else
  echo "ℹ️  No previous sync state found (first run)"
  changes_needed=true
fi

# Only sync if there are changes
if $changes_needed; then
  echo "🔨 Checking for missing issues..."
  to_create=0
  
  while IFS='|' read -r tid ttitle _ _; do
    if [[ -z "$(jq -r --arg t "$tid" '.[] | select(.title | startswith($t)) | .number' /tmp/existing_issues.json)" ]]; then
      ((to_create++))
    fi
  done < "$TMP_TASK_FILE"
  
  if [[ $to_create -eq 0 ]]; then
    echo "✓ All issues exist"
  else
    echo "⚠️  $to_create issues missing (create manually or wait for rate limit)"
  fi
  
  # Sync states using REST API (only changed ones)
  echo "🔒 Syncing status changes..."
  closed=0
  reopened=0
  skipped=0
  
  while IFS='|' read -r tid _ _ tstatus; do
    num="$(jq -r --arg t "$tid" '.[] | select(.title | startswith($t)) | .number' /tmp/existing_issues.json)"
    state="$(jq -r --arg t "$tid" '.[] | select(.title | startswith($t)) | .state' /tmp/existing_issues.json)"
    
    [[ -z "$num" ]] && { ((skipped++)); continue; }
    
    if [[ "$tstatus" == "complete" && "$state" == "OPEN" ]]; then
      echo "  Closing #$num ($tid)..."
      # Use REST API directly instead of gh CLI to avoid GraphQL
      curl -s -X PATCH \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer $(gh auth token)" \
        "https://api.github.com/repos/$REPO/issues/$num" \
        -d '{"state":"closed","state_reason":"completed"}' > /dev/null && ((closed++)) || echo "    ⚠️  Failed"
    elif [[ "$tstatus" == "incomplete" && "$state" == "CLOSED" ]]; then
      echo "  Reopening #$num ($tid)..."
      curl -s -X PATCH \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer $(gh auth token)" \
        "https://api.github.com/repos/$REPO/issues/$num" \
        -d '{"state":"open"}' > /dev/null && ((reopened++)) || echo "    ⚠️  Failed"
    fi
  done < "$TMP_TASK_FILE"
  
  echo "✓ Closed $closed, reopened $reopened, skipped $skipped"
  
  # Save sync state
  echo "complete:$complete_count" > "$LAST_SYNC_FILE"
  echo "total:$task_count" >> "$LAST_SYNC_FILE"
  echo "timestamp:$(date +%s)" >> "$LAST_SYNC_FILE"
  
  # Invalidate cache if we made changes
  [[ $closed -gt 0 || $reopened -gt 0 ]] && rm -f "$CACHE_FILE" && echo "   (Cache invalidated - refresh on next run)"
else
  echo "⏭️  Skipping sync - no changes detected"
fi

echo ""
echo "✅ Sync complete!"
echo "   📊 Total: $task_count tasks ($complete_count complete)"
echo "   🔗 View: https://github.com/users/$PROJECT_OWNER/projects/$PROJECT_NUMBER"
echo ""
echo "💡 Tips:"
echo "   - Run frequently - only changed tasks sync (fast!)"
echo "   - Cache auto-refreshes every 5 minutes"
echo "   - Uses REST API to avoid GraphQL limits"
