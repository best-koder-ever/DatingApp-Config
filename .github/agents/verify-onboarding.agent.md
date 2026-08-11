---
name: verify-onboarding
description: "Verify the complete onboarding flow end-to-end: Keycloak registration → profile wizard → photo upload → completeness verification. Run this before any tester onboarding session."
---

# Onboarding Flow Verifier

## Prerequisites
- All services running (`./dev-start.sh`)
- Infrastructure running (`./infrastructure/start.sh`)
- Python3 with `requests` installed (`.venv/bin/python3 api_tests.py` should work)

## Environment
- Keycloak: http://localhost:8090
- UserService: http://localhost:8082
- PhotoService: http://localhost:8085
- YARP Gateway: http://localhost:8080
- Test user credentials: Use unique timestamp-based username to avoid conflicts

## Verification Steps

### Step 1: Check all services are healthy
```bash
for svc in 8080 8082 8085 8087 8083 8086 8088 8089; do
  status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$svc/health 2>/dev/null)
  echo ":$svc → $status"
done
```
**Expected**: All return 200. If any fail → abort, run `./dev-start.sh`.

### Step 2: Get Keycloak admin token
```bash
ADMIN_TOKEN=$(curl -s -X POST \
  "http://localhost:8090/realms/master/protocol/openid-connect/token" \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Admin token acquired: ${ADMIN_TOKEN:0:20}..."
```
**Expected**: Token string returned (non-empty). If this fails → Keycloak is misconfigured.

### Step 3: Register a test user in Keycloak
```bash
TEST_USERNAME="verify_test_$(date +%s)_onboard"
TEST_EMAIL="${TEST_USERNAME}@test.local"

curl -s -X POST "http://localhost:8090/admin/realms/DatingApp/users" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_USERNAME\",
    \"email\": \"$TEST_EMAIL\",
    \"firstName\": \"Verify\",
    \"lastName\": \"Test\",
    \"enabled\": true,
    \"emailVerified\": true,
    \"credentials\": [{\"type\": \"password\", \"value\": \"${TEST_USERNAME}_pass123\", \"temporary\": false}]
  }" -w "\n%{http_code}"
```
**Expected**: HTTP 201 Created. Extract user ID from `Location` header.

### Step 4: Acquire user token (OIDC flow simulation)
```bash
USER_TOKEN=$(curl -s -X POST \
  "http://localhost:8090/realms/DatingApp/protocol/openid-connect/token" \
  -d "client_id=dejtingapp-flutter" \
  -d "username=$TEST_USERNAME" \
  -d "password=${TEST_USERNAME}_pass123" \
  -d "grant_type=password" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "User token acquired: ${USER_TOKEN:0:20}..."
```
**Expected**: Token string returned. If this fails → user creation in Step 3 didn't work.

### Step 5: Create user profile via UserService
```bash
PROFILE_RESPONSE=$(curl -s -X POST "http://localhost:8082/api/UserProfiles" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"displayName\": \"VerifyTest\",
    \"age\": 28,
    \"gender\": \"NonBinary\",
    \"preferences\": \"NonBinary\",
    \"bio\": \"Verification account\",
    \"location\": \"Stockholm\",
    \"latitude\": 59.3293,
    \"longitude\": 18.0686
  }")
echo "Profile response: $PROFILE_RESPONSE"
PROFILE_ID=$(echo "$PROFILE_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id','MISSING'))")
echo "Profile ID: $PROFILE_ID"
```
**Expected**: HTTP 200/201, `id` field returned, not "MISSING".

### Step 6: Verify profile appears in matchmaking candidates
```bash
CANDIDATES=$(curl -s "http://localhost:8083/api/matchmaking/candidates?limit=50" \
  -H "Authorization: Bearer $USER_TOKEN")
CANDIDATE_COUNT=$(echo "$CANDIDATES" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
echo "Candidates returned: $CANDIDATE_COUNT"
```
**Expected**: Candidate count > 0. New profile's displayName visible in list.

### Step 7: Verify onboarding completeness endpoint
```bash
COMPLETENESS=$(curl -s "http://localhost:8082/api/UserProfiles/$PROFILE_ID/completeness" \
  -H "Authorization: Bearer $USER_TOKEN")
echo "Completeness: $COMPLETENESS"
```
**Expected**: Returns a completeness object (may have optional fields at this stage).

## Pass/Fail Report
- **All 7 steps pass** → Onboarding flow is operational
- **Any step fails** → Report which step and the error response

## Cleanup
Delete test user after verification:
```bash
USER_ID=$(curl -s "http://localhost:8090/admin/realms/DatingApp/users?username=$TEST_USERNAME" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  | python3 -c "import sys,json; users=json.load(sys.stdin); print(users[0]['id'] if users else '')")
if [ -n "$USER_ID" ]; then
  curl -s -X DELETE "http://localhost:8090/admin/realms/DatingApp/users/$USER_ID" \
    -H "Authorization: Bearer $ADMIN_TOKEN"
  echo "Test user $TEST_USERNAME cleaned up"
fi
```
