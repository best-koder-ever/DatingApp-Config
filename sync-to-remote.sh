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
echo -e "${YELLOW}🔨 Rebuilding and redeploying on remote...${NC}"
sshpass -p "$REMOTE_PASS" ssh $SSH_OPTS "$REMOTE_USER@$REMOTE_HOST" \
  "cd $REMOTE_DIR && docker compose build --no-cache 2>&1 && docker compose up -d --remove-orphans 2>&1"

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
