---
name: verify-messaging
description: "Verify the messaging flow: match exists → send message via REST → verify persistence → check conversation list. Run after verify-discovery has created at least one match."
---

# Messaging Flow Verifier

## Prerequisites
- verify-discovery agent completed successfully (at least 1 match exists)
- All services running

## Verification Steps

### Step 1: Acquire demo-user token and find existing match
```bash
DEMO_TOKEN=$(curl -s -X POST \
  "http://localhost:8090/realms/DatingApp/protocol/openid-connect/token" \
  -d "client_id=dejtingapp-flutter" \
  -d "username=demo-user" \
  -d "password=bot_pass_demo-user" \
  -d "grant_type=password" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

MATCHES=$(curl -s "http://localhost:8083/api/Matchmaking" \
  -H "Authorization: Bearer $DEMO_TOKEN")
MATCH_COUNT=$(echo "$MATCHES" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
echo "Matches available: $MATCH_COUNT"
```
**Expected**: Match count >= 1. If 0 → run verify-discovery first.

### Step 2: Get first match and send a message
```bash
MATCH_ID=$(echo "$MATCHES" | python3 -c "import sys,json; data=json.load(sys.stdin); print(data[0].get('matchId','') or data[0].get('id',''))" 2>/dev/null)
echo "Match ID: $MATCH_ID"

SEND_MSG=$(curl -s -X POST "http://localhost:8086/api/messages" \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"matchId\": \"$MATCH_ID\", \"content\": \"Hej! Verification message from messaging agent at $(date)\"}")
echo "Send message response: $SEND_MSG"
```
**Expected**: HTTP 200 OK. Message accepted by messaging-service.

### Step 3: Verify conversation list shows the message
```bash
CONVERSATIONS=$(curl -s "http://localhost:8086/api/messages/conversations" \
  -H "Authorization: Bearer $DEMO_TOKEN")
echo "Conversations: ${CONVERSATIONS:0:300}..."
```
**Expected**: Conversation list contains at least one entry with the match. Last message content matches what we sent.

### Step 4: Verify message retrieval
```bash
MESSAGES=$(curl -s "http://localhost:8086/api/messages/conversations/$MATCH_ID" \
  -H "Authorization: Bearer $DEMO_TOKEN")
MSG_COUNT=$(echo "$MESSAGES" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
echo "Messages in conversation: $MSG_COUNT"
```
**Expected**: Message count >= 1. Message content and sender are correct.

### Step 5: SignalR hub connection test (basic)
```bash
# Test that the SignalR negotiate endpoint responds
NEGOTIATE=$(curl -s -X POST "http://localhost:8086/api/messaging/negotiate" \
  -H "Authorization: Bearer $DEMO_TOKEN" -w "\nHTTP_CODE:%{http_code}")
echo "Negotiate: $NEGOTIATE"
```
**Expected**: HTTP 200 with negotiate response (connectionId, availableTransports). If 404, SignalR uses default `/messaginghub` route.

## Pass/Fail Report
- **Steps 1-2 pass** → Message sending operational (REST)
- **Steps 3-4 pass** → Message persistence and retrieval operational
- **Step 5 passes** → SignalR negotiation endpoint available
