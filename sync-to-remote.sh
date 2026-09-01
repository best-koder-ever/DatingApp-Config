#!/usr/bin/env bash
# Sync DatingApp backend code to remote machine (100.86.173.9) and redeploy
set -euo pipefail

REMOTE_HOST="100.86.173.9"
REMOTE_USER="a"
REMOTE_PASS="a"
REMOTE_DIR="/home/a/datingapp"
SSH_OPTS="-o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PreferredAuthentications=password"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🔄 Syncing DatingApp backend to $REMOTE_HOST...${NC}"

SERVICES=(
  "UserService"
  "MatchmakingService"
  "swipe-service"
  "photo-service"
  "messaging-service"
  "safety-service"
  "bot-service"
  "dejting-yarp"
  "ai-tester-service"
  "forum-service"
  "reputation-service"
  "video-service"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Auto-discover NEW services (not yet in remote compose) and ensure they
#    are added to the remote compose + source rsynced, so the full rebuild
#    below picks them up. New service = dir with Dockerfile+Program.cs+csproj.
# ─────────────────────────────────────────────────────────────────────────
source "$SCRIPT_DIR/scripts/lib-discovery.sh" 2>/dev/null || true
for d in "$SCRIPT_DIR"/*/; do
  dir="${d%/}"
  is_service_dir "$dir" 2>/dev/null || continue
  discover_service "$dir" 2>/dev/null || continue
  if remote_compose_has "$SERVICE_KEBAB" 2>/dev/null; then
    continue
  fi
  echo -e "${YELLOW}  🆕 New service discovered: ${SERVICE_NAME} → ${SERVICE_KEBAB}${NC}"
  block_file="$(mktemp)"
  compose_block "$dir" > "$block_file"
  remote_append_compose "$SERVICE_KEBAB" "$block_file"
  rm -f "$block_file"
  echo -e "  📁 Syncing ${SERVICE_NAME} source..."
  sshpass -p "$REMOTE_PASS" rsync -az --delete     -e "ssh $SSH_OPTS"     --exclude='bin/' --exclude='obj/' --exclude='.git/'     --exclude='logs/' --exclude='TestResults/'     "$dir/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/$SERVICE_KEBAB/" 2>&1 | tail -1
done

for svc in "${SERVICES[@]}"; do
  SRC="$SCRIPT_DIR/$svc"
  if [ -d "$SRC" ]; then
    echo -e "  📁 Syncing $svc..."
    sshpass -p "$REMOTE_PASS" rsync -avz --delete \
      -e "ssh $SSH_OPTS" \
      --exclude='bin/' --exclude='obj/' --exclude='.git/' \
      --exclude='node_modules/' --exclude='logs/' --exclude='wwwroot/' \
      "$SRC/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/$svc/" 2>&1 | tail -1
  else
    echo -e "  ${YELLOW}⚠️  $svc not found locally — skipping${NC}"
  fi
done

# Also sync .env if needed
if [ -f "$SCRIPT_DIR/.env" ]; then
  echo -e "  📁 Syncing .env..."
  sshpass -p "$REMOTE_PASS" scp $SSH_OPTS "$SCRIPT_DIR/.env" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/.env"
fi

echo ""
echo -e "${YELLOW}🔨 Building images on remote (explicit docker build)...${NC}"
# The remote compose uses image:-only entries (no build: context), so we build
# each image explicitly from the synced source, then bring the stack up.
# Services whose Dockerfile expects the datingapp ROOT as build context.
ROOT_CONTEXT_SERVICES="${ROOT_CONTEXT_SERVICES:-MatchmakingService}"
declare -A CTX=(
  ["UserService"]="UserService"
  ["MatchmakingService"]="MatchmakingService"
  ["swipe-service"]="swipe-service"
  ["photo-service"]="photo-service"
  ["messaging-service"]="messaging-service"
  ["safety-service"]="safety-service/SafetyService"
  ["bot-service"]="bot-service/BotService"
  ["dejting-yarp"]="dejting-yarp"
  ["ai-tester-service"]="ai-tester-service"
  ["forum-service"]="forum-service"
  ["reputation-service"]="reputation-service"
  ["video-service"]="video-service"
)
# SKIP_IMAGE_BUILD="svc1 svc2" skips rebuilding those images (e.g. ones that
# hang on apt/network or were just built/transferred locally).
SKIP_IMAGE_BUILD="${SKIP_IMAGE_BUILD:-}"
for svc in "${SERVICES[@]}"; do
  ctx="${CTX[$svc]:-$svc}"
  keb="$(kebab "$svc" 2>/dev/null || echo "$svc" | sed -E 's/([a-z0-9])([A-Z])/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
  if echo "$SKIP_IMAGE_BUILD" | grep -qw "$keb"; then
    echo -e "  ⏭️  skipping datingapp-${keb} (in SKIP_IMAGE_BUILD)"
    continue
  fi
  echo -e "  🔨 datingapp-${keb} (from ${ctx})..."
  # Some Dockerfiles (e.g. MatchmakingService) expect the datingapp ROOT as the
  # build context (they COPY "<ServiceName>/..." paths). Build those with -f.
  # Each build is wrapped in a LOCAL timeout (600s) so a hanging remote build
  # (apt/network on this box) can't block the whole sync forever.
  if echo "$ROOT_CONTEXT_SERVICES" | grep -qw "$svc"; then
    timeout -k 30 600 sshpass -p "$REMOTE_PASS" ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" \
      "cd $REMOTE_DIR && docker build -f ${ctx}/Dockerfile -t datingapp-${keb}:latest . 2>&1 | tail -2" | sed 's/^/    /' || echo -e "    ⚠️  build failed/timed out for ${keb} (check manually)"
    continue
  fi
  timeout -k 30 600 sshpass -p "$REMOTE_PASS" ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" \
    "cd $REMOTE_DIR && docker build -t datingapp-${keb}:latest ${ctx} 2>&1 | tail -2" | sed 's/^/    /' || echo -e "    ⚠️  build failed/timed out for ${keb} (check manually)"
done

echo -e "${YELLOW}🚀 Starting stack on remote...${NC}"
sshpass -p "$REMOTE_PASS" ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" \
  "cd $REMOTE_DIR && docker compose up -d --remove-orphans 2>&1" | sed 's/^/    /' 

echo ""
echo -e "${YELLOW}🏥 Health checks...${NC}"
sleep 5
for port in 8080 8082 8083 8085 8086 8087 8088 8089 8091 8092 8093 8094; do
  code=$(sshpass -p "$REMOTE_PASS" ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" \
    "curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://localhost:$port/health 2>/dev/null || echo 'FAIL'")
  if [ "$code" = "200" ]; then
    echo -e "  :$port → ${GREEN}$code${NC}"
  else
    echo -e "  :$port → ${RED}$code${NC}"
  fi
done

echo ""
echo -e "${GREEN}✅ Sync complete! Backend running at http://$REMOTE_HOST:8080${NC}"
