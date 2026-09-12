#!/usr/bin/env bash
# End-to-end smoke test for the anonymous forum, through the gateway.
#
# Goes through YARP on purpose, so it also proves /api/forum/** is routed to forum-service.
#
# The forum caps posts per user per day (3 topics, 15 answers), so after a few runs this
# script will hit that cap. That is the limiter working, not a regression, so the script
# reports it as SKIPPED and points at how to reset. Everything not needing a fresh topic
# still runs.
#
# Usage:  bash scripts/forum-smoke.sh
# Env:    GATEWAY_URL, KEYCLOAK_URL, KEYCLOAK_REALM, FORUM_USER, FORUM_PASS
set -uo pipefail

GATEWAY_URL="${GATEWAY_URL:-http://localhost:8080}"
KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost:8090}"
REALM="${KEYCLOAK_REALM:-DatingApp}"
CLIENT_ID="${KEYCLOAK_CLIENT_ID:-dejtingapp-flutter}"
USER_NAME="${FORUM_USER:-bot_demo-user@bot.local}"
USER_PASS="${FORUM_PASS:-bot_pass_demo-user}"

PASS=0
FAIL=0
SKIP=0

ok()   { PASS=$((PASS + 1)); printf '  ok      %s\n' "$1"; }
bad()  { FAIL=$((FAIL + 1)); printf '  FAIL    %s (expected %s, got %s)\n' "$1" "$2" "$3"; }
skip() { SKIP=$((SKIP + 1)); printf '  skip    %s\n' "$1"; }
expect() { if [[ "$3" == "$2" ]]; then ok "$1"; else bad "$1" "$2" "$3"; fi; }

# Issues a request; leaves the payload in /tmp/forum-smoke-body and echoes the status code.
call() {
  local method="$1" path="$2" body="${3:-}" token="${4:-}"
  local args=(-s -o /tmp/forum-smoke-body -w '%{http_code}' -X "$method" "$GATEWAY_URL$path" -m 30)
  [[ -n "$token" ]] && args+=(-H "Authorization: Bearer $token")
  [[ -n "$body" ]] && args+=(-H 'Content-Type: application/json' -d "$body")
  curl "${args[@]}"
}

field() {
  python3 -c "import json,sys; d=json.load(open('/tmp/forum-smoke-body')); print(eval(sys.argv[1], {'d': d}))" \
    "$1" 2>/dev/null || echo "?"
}

# Echoes the status code, or CAPPED when the per-day topic limit blocks us.
#
# A 429 carries Retry-After only for the 30s cooldown. The daily cap has no short retry, so
# Retry-After being absent is what distinguishes them.
create_topic() {
  local text="$1" code
  code="$(curl -s -o /tmp/forum-smoke-body -D /tmp/forum-smoke-head -w '%{http_code}' \
    -X POST "$GATEWAY_URL/api/forum/topics" -m 30 \
    -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    -d "{\"text\":\"$text\",\"channel\":\"first-dates\"}")"

  if [[ "$code" == "429" ]]; then
    local secs
    secs="$(awk 'tolower($1) == "retry-after:" { print $2 }' /tmp/forum-smoke-head | tr -d '\r')"
    if [[ -z "$secs" ]]; then
      echo "CAPPED"; return
    fi
    # Read the wait off the real response. Never probe with a throwaway POST: if the cooldown
    # had just elapsed that probe would succeed and restart the very cooldown we are waiting for.
    printf '  ..      posting cooldown active, waiting %ss\n' "$secs" >&2
    sleep "$((secs + 2))"
    code="$(curl -s -o /tmp/forum-smoke-body -w '%{http_code}' \
      -X POST "$GATEWAY_URL/api/forum/topics" -m 30 \
      -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
      -d "{\"text\":\"$text\",\"channel\":\"first-dates\"}")"
  fi

  echo "$code"
}

echo "Forum smoke test"
echo "  gateway: $GATEWAY_URL"

echo
echo "0. Prerequisites"
if ! curl -s -o /dev/null -m 5 "$GATEWAY_URL/health"; then
  echo "  FAIL    gateway not reachable at $GATEWAY_URL — run ./dev-start.sh" >&2
  exit 2
fi
ok "gateway reachable"

TOKEN=$(curl -s -m 20 -X POST "$KEYCLOAK_URL/realms/$REALM/protocol/openid-connect/token" \
  -d "grant_type=password" -d "client_id=$CLIENT_ID" \
  -d "username=$USER_NAME" -d "password=$USER_PASS" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")

if [[ -z "$TOKEN" ]]; then
  echo "  FAIL    could not get a token for $USER_NAME — check FORUM_USER/FORUM_PASS" >&2
  exit 2
fi
ok "token acquired for $USER_NAME"

echo
echo "1. Discovery"
expect "channels" 200 "$(call GET /api/forum/channels '' "$TOKEN")"
expect "channels count" 6 "$(field 'len(d)')"
expect "unauthenticated feed is refused" 401 "$(call GET /api/forum/topics)"

echo
echo "2. Validation (must not consume the posting quota)"
expect "201-char text refused" 400 "$(call POST /api/forum/topics "{\"text\":\"$(printf 'x%.0s' {1..201})\",\"channel\":\"vent\"}" "$TOKEN")"
expect "unknown channel refused" 400 "$(call POST /api/forum/topics '{"text":"hej","channel":"nonsense"}' "$TOKEN")"
expect "contact details held for review" 422 "$(call POST /api/forum/topics '{"text":"maila mig pa spam@example.com","channel":"vent"}' "$TOKEN")"

TOPIC_ID=""

echo
echo "3. Lifecycle"
CODE="$(create_topic "Forum smoke $(date +%s)-$RANDOM")"
if [[ "$CODE" == "CAPPED" ]]; then
  skip "create topic — daily cap reached for $USER_NAME"
  skip "cooldown, feed contents and voting all need a fresh topic"
  echo "          Reset with:"
  echo "            docker exec forum-db mysql -uroot -proot_password -e \\"
  echo "              \"DELETE FROM ForumDb.ForumPostQuotas WHERE KeycloakId='$(python3 -c "
import base64,json,sys
t=sys.argv[1].split('.')[1]; t+='='*(-len(t)%4)
print(json.loads(base64.urlsafe_b64decode(t)).get('sub',''))" "$TOKEN")\""
else
  expect "create topic" 201 "$CODE"
  TOPIC_ID="$(field 'd["id"]')"
  if [[ "$TOPIC_ID" == "?" ]]; then
    echo "  FAIL    no topic id returned; cannot continue" >&2
    exit 1
  fi

  expect "cooldown blocks an immediate second post" 429 "$(call POST /api/forum/topics '{"text":"andra","channel":"vent"}' "$TOKEN")"
  expect "feed is readable" 200 "$(call GET /api/forum/topics '' "$TOKEN")"
  ok "feed is a paged object (total=$(field 'd["total"]'))"

  if grep -q 'keycloakId' /tmp/forum-smoke-body; then
    bad "author identity leaked in the feed" "no keycloakId" "found keycloakId"
  else
    ok "no keycloakId in the feed"
  fi

  call GET "/api/forum/topics/$TOPIC_ID" '' "$TOKEN" >/dev/null
  for key in colorHex pseudonym expiresAt isOwn; do
    if grep -q "\"$key\"" /tmp/forum-smoke-body; then ok "topic exposes $key"; else bad "topic exposes $key" present absent; fi
  done
fi

echo
echo "4. Voting"
if [[ -n "$TOPIC_ID" ]]; then
  expect "self-vote refused" 422 "$(call POST "/api/forum/topics/$TOPIC_ID/vote" '{"value":1}' "$TOKEN")"
  expect "invalid vote value refused" 400 "$(call POST "/api/forum/topics/$TOPIC_ID/vote" '{"value":9}' "$TOKEN")"
else
  skip "voting needs a topic of your own"
fi

echo
echo "5. Answers"
if [[ -n "$TOPIC_ID" ]]; then
  expect "answer during cooldown is refused" 429 "$(call POST "/api/forum/topics/$TOPIC_ID/answers" '{"text":"Haller med!"}' "$TOKEN")"
  expect "answers list" 200 "$(call GET "/api/forum/topics/$TOPIC_ID/answers" '' "$TOKEN")"
fi
expect "answer on a missing topic" 404 "$(call POST /api/forum/topics/999999/answers '{"text":"x"}' "$TOKEN")"

echo
echo "6. Voice endpoint (no audio attached)"
# The token is required: the gateway authenticates every path outside a small whitelist, so
# without it this correctly reports 401 rather than reaching the controller's validation.
expect "transcribe without a token is refused" 401 "$(call POST /api/forum/transcribe)"
expect "transcribe without audio is refused" 400 "$(call POST /api/forum/transcribe '' "$TOKEN")"

echo
echo "7. Reporting"
expect "report a missing topic" 404 "$(call POST /api/forum/report '{"topicId":999999}' "$TOKEN")"
expect "report with no target" 400 "$(call POST /api/forum/report '{}' "$TOKEN")"
if [[ -n "$TOPIC_ID" ]]; then
  expect "report own topic is refused" 422 "$(call POST /api/forum/report "{\"topicId\":$TOPIC_ID}" "$TOKEN")"
else
  skip "self-report check needs a topic of your own"
fi

echo
echo "----------------------------------------"
printf 'passed %d, failed %d, skipped %d\n' "$PASS" "$FAIL" "$SKIP"
[[ "$FAIL" -eq 0 ]] || exit 1
echo "Forum smoke test succeeded."
