#!/usr/bin/env bash
# lib-discovery.sh — shared helpers for DatingApp service auto-discovery & deploy.
# Sourced by discover-services.sh and auto-deploy.sh. Never executed directly.
#
# Discovery convention: a service is a directory under PROJECT_ROOT containing
#   - a Dockerfile
#   - a Program.cs at its root
#   - exactly one *.csproj (its own project, not a .Tests project)
# Port is taken from appsettings.json  "Urls": "http://0.0.0.0:PORT"  (newer
# services set this); otherwise it's marked AUTO and assigned by auto-deploy.sh.

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUTO_PORTS_FILE="${PROJECT_ROOT}/scripts/.auto-ports"

# Remote connection (same defaults as sync-to-remote.sh)
REMOTE_HOST="${REMOTE_HOST:-100.86.173.9}"
REMOTE_USER="a"
REMOTE_PASS="a"
REMOTE_DIR="/home/a/datingapp"
SSH_OPTS="-o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PreferredAuthentications=password"
SSH="sshpass -p ${REMOTE_PASS} ssh ${SSH_OPTS} ${REMOTE_USER}@${REMOTE_HOST}"
SCP="sshpass -p ${REMOTE_PASS} scp ${SSH_OPTS}"

# Directories that are NOT candidate services even if they match the shape.
NON_SERVICE_DIRS='Shared shared tools infrastructure infra config e2e-tests tests monitoring environments vs-code-ai-context-extension .old_scaffolds .specify .continue .claude'

# kebab <name> — UserService -> user-service, MatchmakingService -> matchmaking-service
kebab() {
  echo "$1" | sed -E 's/([a-z0-9])([A-Z])/\1-\2/g' | tr '[:upper:]' '[:lower:]'
}

# is_service_dir <dir> -> exit 0 if dir is a candidate service
is_service_dir() {
  local dir="$1"
  local base
  base="$(basename "$dir")"
  [[ "$base" == .* ]] && return 1
  for ns in $NON_SERVICE_DIRS; do
    [[ "$base" == "$ns" ]] && return 1
  done
  [ -f "$dir/Dockerfile" ] || return 1
  [ -f "$dir/Program.cs" ] || return 1
  local proj
  proj="$(ls "$dir"/*.csproj 2>/dev/null | head -1)"
  [ -n "$proj" ] || return 1
  echo "$proj" | grep -qE '\.Tests\.csproj$' && return 1
  return 0
}

# discover_service <dir> — sets SERVICE_NAME, SERVICE_PORT, SERVICE_DBKEY, SERVICE_DBTYPE
discover_service() {
  local dir="$1"
  SERVICE_NAME="$(basename "$dir")"
  SERVICE_KEBAB="$(kebab "$SERVICE_NAME")"
  SERVICE_PORT="$(grep -oE '"Urls"[[:space:]]*:[[:space:]]*"http://[^"]*:([0-9]+)' "$dir/appsettings.json" 2>/dev/null | grep -oE '[0-9]+$' | head -1 || true)"
  SERVICE_DBKEY=""
  SERVICE_DBTYPE="none"
  local prog="$dir/Program.cs"
  if [ -f "$prog" ]; then
    local key
    key="$(grep -oE 'GetConnectionString\("[^"]*"\)' "$prog" | head -1 | sed -n 's/GetConnectionString("\(.*\)")/\1/p' || true)"
    if [ -n "$key" ]; then
      SERVICE_DBKEY="$key"
      # DB type heuristic (strong signals first):
      #   "?? \"Server=..."  -> mysql
      #   "?? \"Data Source=..." -> sqlite
      #   UseSqlite gate present but no hardcoded fallback -> sqlite
      if grep -A3 "GetConnectionString(\"$key\")" "$prog" | grep -q '?? "Server='; then
        SERVICE_DBTYPE="mysql"
      elif grep -A3 "GetConnectionString(\"$key\")" "$prog" | grep -q '?? "Data Source='; then
        SERVICE_DBTYPE="sqlite"
      elif grep -q 'UseSqlite' "$prog"; then
        SERVICE_DBTYPE="sqlite"
      else
        SERVICE_DBTYPE="mysql"
      fi
    fi
  fi
}

# next_free_port <min> — smallest free port >= min not registered and not open locally
next_free_port() {
  local min="${1:-8096}"
  local p="$min"
  while true; do
    grep -qE "^[^=]+=${p}$" "$AUTO_PORTS_FILE" 2>/dev/null && { p=$((p+1)); continue; }
    if (echo > /dev/tcp/127.0.0.1/"$p") 2>/dev/null; then p=$((p+1)); continue; fi
    break
  done
  echo "$p"
}

# register_port <name> <port>
register_port() {
  touch "$AUTO_PORTS_FILE"
  if grep -qE "^$1=" "$AUTO_PORTS_FILE" 2>/dev/null; then
    sed -i "s|^$1=.*|$1=$2|" "$AUTO_PORTS_FILE"
  else
    echo "$1=$2" >> "$AUTO_PORTS_FILE"
  fi
}

# auto_port <name> — return registered port or assign+register next free (8096+)
auto_port() {
  local name="$1"
  local reg
  reg="$(grep -E "^$name=" "$AUTO_PORTS_FILE" 2>/dev/null | head -1 | cut -d= -f2 || true)"
  if [ -n "$reg" ]; then echo "$reg"; return; fi
  local p
  p="$(next_free_port 8096)"
  register_port "$name" "$p"
  echo "$p"
}

# remote_services — print compose service names on remote (one per line)
remote_services() {
  $SSH "cd $REMOTE_DIR && (docker compose config --services 2>/dev/null || grep -E '^  [a-zA-Z0-9_-]+:' docker-compose.yml | sed 's/^  //;s/:$//')" 2>/dev/null
}

# remote_next_db_hostport — next free host port in 3308-3400 for a new mysql db
remote_next_db_hostport() {
  local used
  used="$($SSH "docker ps --format '{{.Ports}}' 2>/dev/null | grep -oE '0.0.0.0:33[0-9][0-9]->3306' | grep -oE '33[0-9][0-9]' | sort -u" 2>/dev/null || true)"
  local p=3317
  while true; do
    echo "$used" | grep -q "^${p}$" && { p=$((p+1)); continue; }
    break
  done
  echo "$p"
}

# remote_compose_has <svc> — 0 if service (exact or kebab name) already in remote compose
remote_compose_has() {
  local svc="$1"
  local k
  k="$(kebab "$svc")"
  $SSH "grep -qE '^  (${svc}|${k}):' $REMOTE_DIR/docker-compose.yml" 2>/dev/null
}

# compose_block <dir> — prints YAML block to add for a (new) service, incl. db
compose_block() {
  local dir="$1"
  discover_service "$dir"
  local name="$SERVICE_NAME" keb="$SERVICE_KEBAB" port="$SERVICE_PORT" dbkey="$SERVICE_DBKEY" dbtype="$SERVICE_DBTYPE"
  if [ -z "$port" ]; then port="$(auto_port "$name")"; fi
  local dbhost
  dbhost="$(remote_next_db_hostport)"

  cat << BLOCK
  ${keb}:
    image: datingapp-${keb}:latest
    build:
      context: ./${keb}
      dockerfile: Dockerfile
    container_name: ${keb}
    ports:
    - "${port}:${port}"
    environment:
    - ASPNETCORE_ENVIRONMENT=Development
    - ASPNETCORE_URLS=http://*:${port}
BLOCK
  if [ "$dbtype" = "mysql" ] && [ -n "$dbkey" ]; then
    local dbname="$dbkey"
    if [ "$dbkey" = "DefaultConnection" ] || [ "$dbkey" = "default" ]; then
      dbname="$(echo "$keb" | sed -E 's/(^|-)([a-z])/\U\2/g')Db"
    fi
    cat << BLOCK
    - ConnectionStrings__${dbkey}=Server=${keb}-db;Port=3306;Database=${dbname};User=${keb}_user;Password=${keb}_user_password;
    depends_on:
    - ${keb}-db
    networks:
    - app-network
  ${keb}-db:
    image: mysql:8.0
    container_name: ${keb}-db
    environment:
    - MYSQL_ROOT_PASSWORD=root_password
    - MYSQL_DATABASE=${dbname}
    - MYSQL_USER=${keb}_user
    - MYSQL_PASSWORD=${keb}_user_password
    ports:
    - "${dbhost}:3306"
    volumes:
    - ${keb}-data:/var/lib/mysql
    networks:
    - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "${keb}-db"]
      interval: 10s
      timeout: 5s
      retries: 5
BLOCK
  else
    cat << BLOCK
    networks:
    - app-network
BLOCK
  fi
}

# remote_append_compose <keb> <block_file> — idempotently insert service into remote compose
remote_append_compose() {
  local keb="$1" block_file="$2"
  if remote_compose_has "$keb"; then
    echo "   • ${keb}: already in remote compose — skipping compose insert"
    return 0
  fi
  if [ "${DRY_RUN:-0}" = "1" ]; then
    echo "   • ${keb}: WOULD insert compose block:"
    sed 's/^/       /' "$block_file"
    return 0
  fi
  local b64
  b64="$(base64 -w0 "$block_file")"
  $SSH "cd $REMOTE_DIR && echo '$b64' | base64 -d > /tmp/newsvc-block.yml && python3 - << 'PY'
import re, pathlib
p = pathlib.Path('docker-compose.yml')
text = p.read_text()
block = pathlib.Path('/tmp/newsvc-block.yml').read_text()
first_line = block.strip().splitlines()[0].strip().rstrip(':')
if re.search(rf'^  {re.escape(first_line)}:', text, re.M):
    print('already present; no change'); raise SystemExit(0)
m = re.search(r'^volumes:\s*$', text, re.M)
if not m:
    print('ERROR: no top-level volumes: section found'); raise SystemExit(1)
text = text[:m.start()] + block + text[m.start():]
for vol in re.findall(r'^    - ([a-zA-Z0-9_-]+)-data:/var/lib/mysql', block, re.M):
    volname = vol + '-data'
    if re.search(rf'^  {re.escape(volname)}:', text, re.M):
        continue
    vm = re.search(r'^networks:\s*$', text, re.M)
    if vm:
        text = text[:vm.start()] + f'  {volname}:\n' + text[vm.start():]
    else:
        text += f'\nvolumes:\n  {volname}:\n'
p.write_text(text)
print('compose updated')
PY
" 2>&1 | tail -3
}
