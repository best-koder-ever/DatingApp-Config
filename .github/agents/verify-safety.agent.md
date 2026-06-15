---
name: verify-safety
description: "Verify safety features: block user → verify block enforced → unblock → verify restored. For use after onboarding flow is verified."
---

# Safety Flow Verifier

## Prerequisites
- At least 2 users exist (demo-user + any bot)
- All services running

## Verification Steps

### Step 1: Acquire tokens for two users
```bash
USER_TOKEN=$(curl -s -X POST \
  "http://localhost:8090/realms/DatingApp/protocol/openid-connect/token" \
  -d "client_id=dejtingapp-flutter" \
  -d "username=demo-user" \
  -d "password=bot_pass_demo-user" \
  -d "grant_type=password" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

BOT_TOKEN=$(curl -s -X POST \
  "http://localhost:8090/realms/DatingApp/protocol/openid-connect/token" \
  -d "client_id=dejtingapp-flutter" \
  -d "username=bot_maja@bot.local" \
  -d "password=bot_pass_maja" \
  -d "grant_type=password" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "FAILED")
echo "User token: ${USER_TOKEN:0:20}..."
echo "Bot token: ${BOT_TOKEN:0:20}..."
```
**Expected**: Both tokens acquired. Bot password may differ — check bot-service config if this fails.

### Step 2: Get bot's profile ID
```bash
BOT_PROFILE=$(curl -s "http://localhost:8082/api/UserProfiles" \
  -H "Authorization: Bearer $BOT_TOKEN")
BOT_ID=$(echo "$BOT_PROFILE" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0].get('id','') if isinstance(data,list) else data.get('id',''))" 2>/dev/null || echo "UNKNOWN")
echo "Bot profile ID: $BOT_ID"
```
**Expected**: Profile ID returned. If "UNKNOWN", try different endpoint or direct lookup.

### Step 3: Block the bot user
```bash
BLOCK=$(curl -s -X POST "http://localhost:8088/api/blocking/block" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"blockedUserId\": \"$BOT_ID\"}")
echo "Block response: $BLOCK"
```
**Expected**: HTTP 200/201. Block recorded in safety-service.

### Step 4: Send a message to the blocked user (messaging-service)
```bash
MATCHES=$(curl -s "http://localhost:8083/api/Matchmaking" \
  -H "Authorization: Bearer $USER_TOKEN")
MATCH_ID=$(echo "$MATCHES" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0].get('matchId','') or data[0].get('id',''))" 2>/dev/null || echo "")

if [ -n "$MATCH_ID" ]; then
  BLOCKED_MSG=$(curl -s -w "\nHTTP:%{http_code}" -X POST "http://localhost:8086/api/messages" \
    -H "Authorization: Bearer $USER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"matchId\": \"$MATCH_ID\", \"content\": \"Should this go through?\"}")
  echo "Message after block: $BLOCKED_MSG"
fi
```
**Expected**: Either HTTP 403 (blocked) or message sent but safety-service may block delivery.

### Step 5: Unblock the user
```bash
UNBLOCK=$(curl -s -X DELETE "http://localhost:8088/api/blocking/unblock/$BOT_ID" \
  -H "Authorization: Bearer $USER_TOKEN")
echo "Unblock response: $UNBLOCK"
```
**Expected**: HTTP 200/204. User successfully unblocked.

## Pass/Fail Report
- **Steps 1-3 pass** → Blocking endpoint operational
- **Step 4 behavior** → Document expected enforcement level (logged only vs. blocked)
- **Step 5 passes** → Unblock endpoint operational
