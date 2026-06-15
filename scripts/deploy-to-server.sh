#!/usr/bin/env bash
# Deploy DatingApp images to the dev server at 192.168.1.103
# Builds locally (fast tether), transfers, and restarts the stack.
set -euo pipefail

SERVER="a@192.168.1.103"
SERVER_DIR="/home/a/datingapp"
SSH_OPTS="-o PubkeyAuthentication=no -o StrictHostKeyChecking=no"
SSH="sshpass -p 'a' ssh $SSH_OPTS"
SCP="sshpass -p 'a' scp $SSH_OPTS"

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🔨 Building DatingApp images on laptop (tether)..."
echo ""

# Build each service
declare -A SERVICES=(
  ["yarp"]="dejting-yarp"
  ["user-service"]="UserService"
  ["matchmaking-service"]="MatchmakingService"
  ["swipe-service"]="swipe-service"
  ["photo-service"]="photo-service"
  ["messaging-service"]="messaging-service"
  ["safety-service"]="safety-service/SafetyService"
)

for svc in "${!SERVICES[@]}"; do
  ctx="${SERVICES[$svc]}"
  echo "  Building datingapp-$svc..."
  
  if [ "$svc" = "matchmaking-service" ]; then
    docker build -f "$ctx/Dockerfile" -t "datingapp-$svc:latest" . 2>&1 | tail -1
  elif [ "$svc" = "messaging-service" ]; then
    # Use local publish approach (shared lib dependency)
    dotnet publish "$ctx/MessagingService.csproj" -c Release -o /tmp/msg-publish 2>&1 | tail -1
    cat > /tmp/msg-dockerfile << 'DOCKERFILE'
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
COPY . .
ENTRYPOINT ["dotnet", "MessagingService.dll"]
DOCKERFILE
    docker build -t "datingapp-$svc:latest" -f /tmp/msg-dockerfile /tmp/msg-publish 2>&1 | tail -1
  else
    docker build -t "datingapp-$svc:latest" "$ctx" 2>&1 | tail -1
  fi
done

echo ""
echo "📦 Saving images..."
docker save \
  datingapp-yarp:latest \
  datingapp-user-service:latest \
  datingapp-matchmaking-service:latest \
  datingapp-swipe-service:latest \
  datingapp-photo-service:latest \
  datingapp-safety-service:latest \
  datingapp-messaging-service:latest \
  -o /tmp/datingapp-deploy.tar

echo "📤 Transferring to $SERVER..."
$SCP /tmp/datingapp-deploy.tar "$SERVER:/tmp/"

echo "📥 Loading on server..."
$SSH "$SERVER" "
  sudo docker load -i /tmp/datingapp-deploy.tar
  cd $SERVER_DIR
  sudo docker compose up -d --remove-orphans
  echo ''
  echo '⏳ Waiting 10s for services...'
  sleep 10
  echo ''
  echo '=== Health Check ==='
  for port in 8080 8082 8083 8085 8086 8087; do
    code=\$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 http://localhost:\$port/health 2>/dev/null || echo 'NO')
    echo \"  :\$port → \$code\"
  done
"

echo ""
echo "✅ Deploy complete!"
rm -f /tmp/datingapp-deploy.tar
