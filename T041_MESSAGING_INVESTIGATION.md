# T041 Messaging Tests Investigation

**Date**: 2026-01-30  
**Status**: IN PROGRESS - 1/8 tests passing  
**Priority**: CRITICAL BLOCKER for 26/26 test completion

## Problem Statement

T041 messaging integration tests timeout after 30 seconds when attempting to send messages after match creation. Only the error-handling test passes (1/8).

## Timeline of Investigation

### Issue #1: MySQL Container Missing ✅ RESOLVED
- **Problem**: MessagingService crashed on startup with `MySqlConnector.MySqlException`
- **Root Cause**: MySQL container for MessagingService was never created
- **Evidence**: `docker ps -a | grep mysql` showed no messaging-related MySQL
- **Expected**: MySQL on port 3313 per appsettings.Development.json
- **Actual**: Port 3312 in docker-compose.yml, container not in `infrastructure/start.sh`
- **Solution**: 
  - Started `messaging-service-db` container: `docker compose up -d messaging-service-db`
  - Fixed port mismatch: 3313 → 3312 in appsettings.Development.json
- **Result**: MySQL container running and healthy

### Issue #2: Keycloak Authentication Misconfiguration ✅ RESOLVED
- **Problem**: MessagingService returned 401 Unauthorized for all authenticated requests
- **Root Cause**: appsettings.Development.json had `Jwt` section, but `KeycloakAuthenticationExtensions.cs` expects `Authentication:Keycloak`
- **Evidence**: 
  ```csharp
  // Extension code expects:
  var keycloakSection = configuration.GetSection("Authentication:Keycloak");
  
  // But appsettings had:
  "Jwt": {
    "Issuer": "http://localhost:8090/realms/DatingApp",
    "Audience": "datingapp-backend"
  }
  ```
- **Solution**: Restructured appsettings.Development.json to use correct format:
  ```json
  "Authentication": {
    "Keycloak": {
      "Authority": "http://localhost:8090/realms/DatingApp",
      "Audience": "datingapp-backend",
      "RequireHttpsMetadata": false
    }
  }
  ```
- **Verification**: 
  - Restarted MessagingService: PID 118780
  - Health check: ✅ Healthy
  - Direct endpoint test: Returns 401 without auth (expected), accepts Bearer tokens

### Issue #3: Test Timeouts After Match Creation ❌ ACTIVE BLOCKER

#### Symptoms
- All 7 tests that create matches timeout at exactly 30 seconds (apiTimeout)
- Only test without match creation passes immediately (0s)
- Timeout occurs after `createMatch()` completes successfully
- Pattern: ✅ Register users → ✅ Complete onboarding → ✅ Create match → ❌ Send message (30s timeout)

#### Evidence
```
📋 Step 3 complete - testuser_1769774854382 profileId: 87
📋 Step 3 complete - testuser_1769774854394 profileId: 88
🔄 createMatch: testuser_1769774854382 (ID=87) <-> testuser_1769774854394 (ID=88)
[30 second wait]
TimeoutException after 0:00:30.000000: Test timed out after 30 seconds
```

#### Infrastructure Status
- ✅ **MessagingService**: Healthy on port 8086 (verified during test run)
- ✅ **YARP Gateway**: Healthy on port 8080
- ✅ **UserService**: Responding on port 8082 (200 OK)
- ✅ **SwipeService**: Responding on port 8087 (200 OK)
- ✅ **Keycloak**: Running, tokens generated successfully
- ✅ **MySQL (3312)**: Healthy, MessagingService connected

#### YARP Routing Configuration
```json
{
  "messagingRoute": {
    "ClusterId": "messagingCluster",
    "Match": { "Path": "/api/messages/{**catch-all}" },
    "Metadata": { "RateLimitPolicy": "MessagesPerMinute" }
  },
  "messagingCluster": {
    "Destinations": {
      "messagingService": { "Address": "http://localhost:8086/" }
    }
  }
}
```
- ✅ YARP routes `/api/messages` → `http://localhost:8086`
- ✅ Manual curl test: `curl -X POST http://localhost:8080/api/messages` → 401 (correct, no auth)
- ✅ Rate limit policy `MessagesPerMinute` defined but not configured (null in appsettings)

#### Diagnostic Tests Attempted

1. **Direct MessagingService Test**:
   ```bash
   curl -X POST http://localhost:8086/api/messages \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"recipientUserId":"fake-id","text":"Test"}'
   ```
   - Result: 401 Unauthorized (token validation issue initially, fixed)

2. **YARP Routing Test**:
   ```bash
   curl -X POST http://localhost:8080/api/messages \
     -H "Content-Type: application/json" \
     -d '{"recipientUserId":"test","text":"test"}'
   ```
   - Result: 401 Unauthorized (expected without Bearer token)
   - Confirms YARP routing works

3. **Test Without Match Creation**:
   ```dart
   test('Error: Cannot message non-matched user', () async {
     await registerUser(user1);
     await registerUser(user2);
     await completeOnboarding(user1);
     await completeOnboarding(user2);
     // NO match created
     expect(() async => await sendMessage(...), throwsException);
   });
   ```
   - Result: ✅ PASSES immediately (0 seconds)
   - Confirms test framework works, auth works, MessagingService is reachable

4. **Live Health Check During Test**:
   - Started test in background
   - Checked MessagingService health after 25s: ✅ Healthy
   - Checked direct POST endpoint availability: ✅ Responds
   - **Critical Finding**: No requests appear in MessagingService logs during test execution

5. **Service Logs Analysis**:
   - MessagingService logs: No POST /api/messages requests logged during test runs
   - YARP logs: Not checked yet
   - Implication: Requests may not be leaving the test framework or are stuck in YARP

#### Current Hypothesis

**Primary Suspect**: Request never reaches MessagingService despite YARP routing being correct.

**Potential Causes**:
1. **Flutter HTTP client issue**: Test framework might be waiting for something before sending request
2. **YARP rate limiting**: Even though policy is null, middleware might be hanging
3. **CORS preflight**: Flutter might send OPTIONS request that YARP doesn't handle
4. **Test framework bug**: Stream channel error seen: "Cannot close sink while adding stream"
5. **Network layer deadlock**: Request sent but response never received

**Evidence Against Each**:
1. ❌ Other tests pass (UserService, SwipeService work fine)
2. ❌ No rate limit policy configured (`RateLimitingPolicies.MessagesPerMinute: null`)
3. ❓ Need to check YARP CORS configuration
4. ✅ Test crash seen: "Bad state: Cannot close sink while adding stream" after timeout
5. ❓ Need to capture network traffic or add detailed logging

## Code Changes Made

### 1. MessagingService POST Endpoint
**Files Modified**:
- `messaging-service/Commands/SendMessageCommand.cs` (created)
- `messaging-service/Commands/SendMessageHandler.cs` (created)
- `messaging-service/DTOs/SendMessageRequestRest.cs` (created)
- `messaging-service/Controllers/MessagesController.cs` (updated)

**Endpoint Implementation**:
```csharp
[HttpPost]
public async Task<IActionResult> SendMessage([FromBody] SendMessageRequestRest request)
{
    var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
    if (string.IsNullOrEmpty(userId)) return Unauthorized();

    var command = new SendMessageCommand
    {
        SenderId = userId,
        ReceiverId = request.RecipientUserId,
        Content = request.Text,
        Type = request.Type ?? Models.MessageType.Text
    };

    var result = await _mediator.Send(command);
    if (result.IsFailure)
        return StatusCode(500, ApiResponse<object>.FailureResult(result.Error!));

    return Created($"/api/messages/{result.Value!.Id}", 
                   ApiResponse<object>.SuccessResult(result.Value));
}
```

### 2. Dart Test Helpers
**Files Modified**:
- `integration_test/helpers/message_helpers.dart`
- `integration_test/t041_messaging_test.dart`

**Key Changes**:
- Changed `recipientUserId` from `int` (profileId) to `String` (Keycloak GUID)
- Updated all test calls to use `user.userId!` instead of `user.profileId!`
- Fixed `markMessageRead()` to use POST instead of PUT

### 3. Configuration Files
**messaging-service/appsettings.Development.json**:
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3312;Database=MessagingServiceDb;User=messagingservice_user;Password=messagingservice_user_password;"
  },
  "Authentication": {
    "Keycloak": {
      "Authority": "http://localhost:8090/realms/DatingApp",
      "Audience": "datingapp-backend",
      "RequireHttpsMetadata": false
    }
  },
  "Gateway": {
    "BaseUrl": "http://localhost:8080"
  }
}
```

## Next Steps

### Immediate Actions (Next 30 minutes)
1. **Check YARP logs** for incoming requests during test run
2. **Add request logging** to MessagingService controller (log before auth check)
3. **Test with verbose HTTP logging** in Flutter test
4. **Verify CORS configuration** in YARP for POST /api/messages
5. **Check if rate limiting middleware** is blocking requests silently

### If Still Blocked
1. **Bypass YARP temporarily**: Change test to call `http://localhost:8086` directly
2. **Add tcpdump/wireshark**: Capture actual network packets
3. **Simplify test**: Create minimal reproduction case without full test framework
4. **Check SwipeService implementation**: How do similar POST requests work there?

### Alternative Approaches
1. **Use SignalR instead of REST**: Tests might work better with WebSocket
2. **Check if match validation is required**: MessageServiceSpec might enforce match checking
3. **Verify test execution order**: Maybe match creation state isn't persisting

## Test Results Summary

| Test | Status | Time | Error |
|------|--------|------|-------|
| Contract: Users can send messages after match | ❌ FAIL | 30s | TimeoutException |
| Contract: Recipients can retrieve sent messages | ❌ FAIL | 30s | TimeoutException |
| Contract: Can exchange multiple messages | ❌ FAIL | 30s | TimeoutException |
| Contract: Conversations list shows active chats | ❌ FAIL | 30s | TimeoutException |
| Contract: Mark message as read | ❌ FAIL | 30s | TimeoutException |
| Contract: Pagination works for long conversations | ❌ FAIL | 30s | TimeoutException |
| Error: Cannot message non-matched user | ✅ PASS | 0s | - |
| Flow: Complete messaging journey | ❌ FAIL | 30s | TimeoutException |

**Current Score**: 1/8 (12.5%)  
**Target**: 8/8 (100%)

## References

- **T021 Success**: 9/9 tests passing (profile onboarding works perfectly)
- **Test Configuration**: `integration_test/helpers/test_config.dart`
- **API Timeout**: 30 seconds (hardcoded in TestConfig.apiTimeout)
- **Infrastructure Script**: `infrastructure/start.sh` (does not include messaging-service-db)

## BREAKTHROUGH: Root Cause Identified

**Timestamp**: 2026-01-30 13:30  
**Status**: ✅ FOUND THE ISSUE

### The Smoking Gun

YARP logs show requests ARE reaching MessagingService:
```
2026-01-30 13:22:49.474 [INF] Proxying to http://localhost:8086/api/messages HTTP/2
2026-01-30 13:22:49.571 [INF] Received HTTP/1.1 response 401.
```

**Key Finding**: MessagingService returns 401 Unauthorized in only 97ms. But tests still timeout for 30 seconds!

### The Real Problem

**Tests receive 401 but Flutter HTTP client hangs instead of throwing exception.**

The timeline:
1. ✅ Test creates users and match successfully  
2. ✅ Test calls `sendMessage()` with valid Bearer token  
3. ✅ Request reaches YARP at 13:22:49.474  
4. ✅ YARP proxies to MessagingService  
5. ✅ MessagingService returns 401 at 13:22:49.571  
6. ❌ **Flutter HTTP client never processes the 401 response**
7. ❌ Test waits for full 30s timeout  
8. ❌ Test framework error: "Cannot close sink while adding stream"

### Why 401 Despite Keycloak Config Fix?

The Keycloak authentication config was fixed in appsettings.Development.json, but **tokens might still be invalid**. Possible causes:

1. **Token audience mismatch**: Tests use `dejtingapp-flutter` client, MessagingService expects `datingapp-backend`
2. **Token claims missing**: MessagingService extracts `ClaimTypes.NameIdentifier` which might not exist in test tokens
3. **Token not being sent**: Despite auth headers, requests might be missing Bearer token
4. **YARP stripping headers**: YARP might remove Authorization header during proxying

### Next Action

Add detailed logging to see ACTUAL token being sent and received.

