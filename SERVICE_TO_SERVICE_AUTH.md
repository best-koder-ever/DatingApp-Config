# Service-to-Service Authentication

## Overview

Internal API key authentication implemented to secure cross-service communication. Each service has a unique API key for outgoing requests and validates a list of authorized API keys for incoming internal requests.

## Architecture

### Components

**InternalApiKeyAuthHandler** (`Common/InternalApiKeyAuthHandler.cs`)
- DelegatingHandler that adds `X-Internal-API-Key` header to outgoing HTTP requests
- Automatically attached to all service-to-service HttpClients
- Reads API key from `InternalAuth:ApiKey` configuration

**InternalApiKeyAuthFilter** (`Common/InternalApiKeyAuthFilter.cs`)
- Authorization filter that validates incoming internal API requests
- Checks `X-Internal-API-Key` header against `InternalAuth:ValidApiKeys` list
- Returns 401 Unauthorized if key missing or invalid

**[RequireInternalApiKey]** Attribute
- Apply to controllers/actions that should only accept internal service calls
- Example: `[RequireInternalApiKey]` on match verification endpoints

### Configuration

Each service requires `InternalAuth` section in `appsettings.Development.json`:

```json
{
  "InternalAuth": {
    "ApiKey": "service-name-internal-key-dev-only",
    "ValidApiKeys": "other-service-1-key,other-service-2-key,..."
  }
}
```

**Current DEV Keys** (change in production):
- PhotoService: `photo-service-internal-key-dev-only`
- MatchmakingService: `matchmaking-service-internal-key-dev-only`
- MessagingService: `messaging-service-internal-key-dev-only`
- SwipeService: `swipe-service-internal-key-dev-only`
- UserService: `user-service-internal-key-dev-only`
- SafetyService: `safety-service-internal-key-dev-only` (when implemented)

### Service Matrix

| Service | Calls (Outgoing) | Receives From (Incoming) |
|---------|------------------|--------------------------|
| PhotoService | MatchmakingService, SafetyService | MessagingService, UserService (for photo requests) |
| MatchmakingService | UserService, SafetyService | PhotoService, MessagingService, SwipeService |
| MessagingService | SafetyService, MatchmakingService | PhotoService (for match checks) |
| SwipeService | MatchmakingService | None currently |
| UserService | None currently | MatchmakingService |

## Implementation Status

✅ **Implemented:**
- PhotoService (main repo commit a5a71ec)
- MessagingService (main repo commit a5a71ec)
- MatchmakingService (submodule commit 03601ac)
- SwipeService (submodule commit fa9bb9f)

⏳ **Configuration Only:**
- UserService (appsettings updated, no outgoing calls yet)

❌ **Not Implemented:**
- SafetyService (doesn't exist yet - placeholder)

## Usage

### Protecting Endpoints

Add `[RequireInternalApiKey]` to controllers/actions that should only accept internal calls:

```csharp
[ApiController]
[Route("api/[controller]")]
public class InternalMatchesController : ControllerBase
{
    [HttpGet("check/{userId1}/{userId2}")]
    [RequireInternalApiKey]  // 👈 Requires valid internal API key
    public async Task<ActionResult<bool>> CheckMatch(string userId1, string userId2)
    {
        // Only other services with valid API keys can call this
    }
}
```

### Testing Internal Endpoints

Use `X-Internal-API-Key` header with correct key:

```bash
curl -H "X-Internal-API-Key: matchmaking-service-internal-key-dev-only" \
  http://localhost:8085/api/photos/internal/check-access/123
```

Without valid key:
```bash
curl http://localhost:8085/api/photos/internal/check-access/123
# Returns: 401 Unauthorized {"error":"Missing internal API key"}
```

## Security Model

### Development Mode
- Keys configured in appsettings.Development.json (NOT in git)
- If `ValidApiKeys` is empty, requests are allowed (gradual rollout)
- Logs warnings for missing/invalid keys

### Production Mode (TODO)
- Keys stored in environment variables or secret manager
- Strict validation (no fallback to allow mode)
- Rotate keys regularly
- Use longer, cryptographically secure keys

### Best Practices
1. **Never commit appsettings.Development.json** - already gitignored
2. **Rotate keys regularly** in production
3. **Use environment-specific keys** - different for dev/staging/prod
4. **Apply [RequireInternalApiKey]** only to internal endpoints
5. **Keep user-facing endpoints public** - protected by JWT auth instead

## Migration Path

All services now have internal auth infrastructure. To start enforcing:

1. Add `[RequireInternalApiKey]` to internal-only endpoints
2. Monitor logs for auth failures during development
3. Fix any missing configurations
4. Enable strict mode (remove empty ValidApiKeys fallback)

## Future Enhancements

1. **mTLS** - Mutual TLS for stronger authentication
2. **Service identity tokens** - Short-lived JWT tokens instead of static keys
3. **Request signing** - Sign requests with service private keys
4. **Rate limiting** - Per-service rate limits on internal endpoints
5. **Audit logging** - Track all internal API calls

## Troubleshooting

**"Missing internal API key" errors:**
- Check `InternalAuth:ApiKey` is configured in calling service
- Verify HttpClient has `.AddHttpMessageHandler<InternalApiKeyAuthHandler>()`

**"Invalid internal API key" errors:**
- Check receiving service's `InternalAuth:ValidApiKeys` includes calling service's key
- Verify keys match exactly (case-sensitive)

**Requests still work without keys:**
- DEV mode allows requests if `ValidApiKeys` is empty
- Add keys to ValidApiKeys list to start enforcing

---

**Created:** 2026-01-26  
**Part of:** Backend Solidification Plan - Week 1  
**Related:** T007 (Database Consolidation), T008 (Remove AuthService), T052 (Privacy Enforcement)
