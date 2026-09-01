#!/usr/bin/env bash
# discover-services.sh — list DatingApp services on the laptop/workspace and
# report which ones are NOT yet deployed on the little machine.
#
# Usage:
#   bash scripts/discover-services.sh            # list all + mark NEW
#   bash scripts/discover-services.sh --json     # machine-readable TSV
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-discovery.sh"

MODE="${1:-table}"

discover_all() {
  for d in "$PROJECT_ROOT"/*/; do
    dir="${d%/}"
    is_service_dir "$dir" || continue
    discover_service "$dir"
    # remote presence
    if remote_compose_has "$SERVICE_NAME"; then
      PRESENT="yes"
    else
      PRESENT="NO"
    fi
    echo -e "${SERVICE_NAME}\t${SERVICE_PORT:-AUTO}\t${SERVICE_DBKEY:--}\t${SERVICE_DBTYPE}\t${PRESENT}"
  done
}

if [ "$MODE" = "--json" ]; then
  discover_all | sort
else
  printf "%-28s %-8s %-18s %-8s %-6s\n" "SERVICE" "PORT" "DBKEY" "DBTYPE" "ON_REMOTE"
  printf "%-28s %-8s %-18s %-8s %-6s\n" "-------" "----" "-----" "------" "---------"
  discover_all | sort | while IFS=$'\t' read -r name port dbkey dbtype present; do
    printf "%-28s %-8s %-18s %-8s %-6s\n" "$name" "$port" "$dbkey" "$dbtype" "$present"
  done
fi
