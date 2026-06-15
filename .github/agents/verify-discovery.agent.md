---
name: verify-discovery
description: "Verify the discovery and matching flow: login → fetch candidates → swipe → match detection → match notification. Run after verify-onboarding."
---

# Discovery & Match Verifier

## Prerequisites
- All services running
- At least 2 bot users provisioned (run `./dev-start.sh` which seeds bots)
- Admin reset endpoint available

## Verification Steps

### Step 1: Acquire demo-user token
```bash
DEMO_TOKEN=$(curl -s -X POST \
  "http://localhost:8090/realms/DatingApp/protocol/openid-connect/token" \
  -d "client_id=dejtingapp-flutter" \
  -d "username=demo-user" \
  -d "password=bot_pass_demo-user" \
  -d "grant_type=password" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Demo token: ${DEMO_TOKEN:0:20}..."
```
**Expected**: Token acquired. If fails → check Keycloak realm and user credentials.

### Step 2: Reset interactions to clean state
```bash
RESET=$(curl -s -X POST "http://localhost:8080/api/admin/reset-interactions" \
  -H "Authorization: Bearer $DEMO_TOKEN")
echo "Reset: $RESET"
```
**Expected**: HTTP 200 or 207 (multi-status). Resets matches+messages+swipes.

### Step 3: Fetch candidates
```bash
CANDIDATES=$(curl -s "http://localhost:8083/api/matchmaking/candidates?limit=20" \
  -H "Authorization: Bearer $DEMO_TOKEN")
CANDIDATE_COUNT=$(echo "$CANDIDATES" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "parse_error")
echo "Candidates returned: $CANDIDATE_COUNT"
```
**Expected**: Count >= 1. Should see bot profiles in the candidate list.

### Step 4: Swipe right on the first candidate
```bash
FIRST_ID=$(echo "$CANDIDATES" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0]['userId'] if isinstance(data,list) and data else data.get('userId','NONE'))" 2>/dev/null || echo "NONE")
echo "First candidate ID: $FIRST_ID"

if [ "$FIRST_ID" != "NONE" ]; then
  SWIPE=$(curl -s -X POST "http://localhost:8087/api/Swipes" \
    -H "Authorization: Bearer $DEMO_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"targetUserId\": \"$FIRST_ID\", \"direction\": \"like\", \"idempotencyKey\": \"verify_$(date +%s)\"}")
  echo "Swipe response: $SWIPE"
fi
```
**Expected**: HTTP 200 OK. Swipe recorded.

### Step 5: Check for matches
```bash
MATCHES=$(curl -s "http://localhost:8083/api/Matchmaking" \
  -H "Authorization: Bearer $DEMO_TOKEN")
MATCH_COUNT=$(echo "$MATCHES" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
echo "Matches found: $MATCH_COUNT"
```
**Expected**: Match count >= 1 if a bot also swiped right on demo-user (bots are configured to swipe right on all profiles).

### Step 6: Verify match insight endpoint (Spec 005 feature)
```bash
if [ "$MATCH_COUNT" -ge 1 ]; then
  FIRST_MATCH_ID=$(echo "$MATCHES" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0].get('matchId','') or data[0].get('id',''))" 2>/dev/null)
  INSIGHT=$(curl -s "http://localhost:8083/api/matchmaking/matches/$FIRST_MATCH_ID/insight" \
    -H "Authorization: Bearer $DEMO_TOKEN")
  echo "Match insight: ${INSIGHT:0:200}..."
fi
```
**Expected**: Insight object with reasons, optionally frictions and growth fields.

## Pass/Fail Report
- **Steps 1-3 pass** → Discovery engine operational
- **Steps 4-5 pass** → Swipe pipeline and match detection operational
- **Step 6 passes** → Match Insight feature operational
