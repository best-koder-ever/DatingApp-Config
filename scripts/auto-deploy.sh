#!/usr/bin/env bash
# auto-deploy.sh — discover NEW DatingApp services on the laptop/workspace and
# deploy them to the little machine (100.86.173.9) automatically.
#
# For every service directory in the workspace that is NOT yet in the remote
# docker-compose.yml, this script will:
#   1. determine its port (appsettings.json "Urls", else auto-assigned 8096+)
#   2. generate a docker-compose service entry (+ MySQL db container if the
#      service reads a mysql-flavoured GetConnectionString)
#   3. append the entry to the remote /home/a/datingapp/docker-compose.yml
#   4. rsync the source to the remote
#   5. build the image on the remote and start it
#
# Usage:
#   bash scripts/auto-deploy.sh                 # deploy only NEW services
#   bash scripts/auto-deploy.sh --sync-all      # NEW services + full sync-to-remote
#   bash scripts/auto-deploy.sh --dry-run       # show what would happen (no changes)
#   bash scripts/auto-deploy.sh --only <name>   # deploy just one service
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib-discovery.sh"

DRY_RUN=0
SYNC_ALL=0
ONLY=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --sync-all) SYNC_ALL=1 ;;
    --only) ONLY="${2:-}"; shift ;;
  esac
  shift
done

deploy_new() {
  local dir="$1"
  discover_service "$dir"
  local name="$SERVICE_NAME" keb="$SERVICE_KEBAB" port="$SERVICE_PORT" dbtype="$SERVICE_DBTYPE"
  if remote_compose_has "$keb"; then
    echo "✓ ${name} (${keb}) — already deployed on remote"
    return 0
  fi
  echo ""
  echo "═══ NEW SERVICE: ${name} → ${keb} (port ${port:-AUTO}, db=${dbtype}) ═══"
  if [ -z "$port" ]; then
    port="$(auto_port "$name")"
    echo "   → assigned port ${port} (from .auto-ports registry)"
  fi

  local block_file
  block_file="$(mktemp)"
  compose_block "$dir" > "$block_file"

  remote_append_compose "$keb" "$block_file"
  rm -f "$block_file"

  if [ "$DRY_RUN" = "1" ]; then
    echo "   • ${keb}: WOULD rsync source + build + up"
    return 0
  fi

  echo "   • ${keb}: rsyncing source to remote..."
  sshpass -p "$REMOTE_PASS" rsync -az --delete \
    -e "ssh $SSH_OPTS" \
    --exclude='bin/' --exclude='obj/' --exclude='.git/' \
    --exclude='logs/' --exclude='TestResults/' --exclude='.pytest_cache/' \
    "$dir/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/$keb/" 2>&1 | tail -1

  echo "   • ${keb}: building image on remote (this can take a few minutes)..."
  $SSH "cd $REMOTE_DIR && docker compose build $keb 2>&1 | tail -3" 2>&1 | tail -3

  echo "   • ${keb}: starting container..."
  $SSH "cd $REMOTE_DIR && docker compose up -d $keb 2>&1" 2>&1 | tail -3

  echo "   • ${keb}: waiting for :${port} ..."
  sleep 6
  if $SSH "(echo > /dev/tcp/127.0.0.1/$port) 2>/dev/null && echo UP || echo DOWN" 2>&1 | grep -q UP; then
    echo "   ✅ ${keb} is UP on :${port}"
  else
    echo "   ⚠️  ${keb} on :${port} not answering yet — check: ssh a@$REMOTE_HOST 'docker logs ${keb}'"
  fi
}

# ── main ──
echo "🔎 Discovering DatingApp services in workspace..."
echo "============================================================"

NEW=0
for d in "$PROJECT_ROOT"/*/; do
  dir="${d%/}"
  is_service_dir "$dir" || continue
  discover_service "$dir"
  if [ -n "$ONLY" ] && [ "$SERVICE_NAME" != "$ONLY" ] && [ "$SERVICE_KEBAB" != "$ONLY" ]; then
    continue
  fi
  if remote_compose_has "$SERVICE_KEBAB"; then
    continue
  fi
  NEW=$((NEW+1))
  deploy_new "$dir"
done

if [ "$NEW" -eq 0 ]; then
  echo ""
  echo "✅ No new services to deploy — all discovered services are already on the little machine."
fi

if [ "$SYNC_ALL" = "1" ] && [ "$DRY_RUN" = "0" ]; then
  echo ""
  echo "🚀 --sync-all: running full sync-to-remote.sh (rsync + rebuild + restart all)..."
  bash "$SCRIPT_DIR/sync-to-remote.sh"
fi

echo ""
echo "✅ Done."
