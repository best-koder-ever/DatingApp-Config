# Keycloak Configuration for User Registration & Email Verification

**Task**: T022 [US1]  
**Status**: ✅ Complete  
**Date**: 2026-01-25

---

## Overview

Configured Keycloak realm (`DatingApp`) to support:
- ✅ User self-registration  
- ✅ Email verification (required action)
- ✅ SMTP integration via MailHog (dev)
- ✅ Flutter client (PKCE-enabled public client)
- ✅ All microservice clients (matchmaking, photo, swipe, messaging, yarp)

---

## Changes Made

### 1. Realm Configuration (`config/keycloak/realms/datingapp-realm.json`)

```json
{
  "registrationAllowed": true,           // ✅ Enabled self-registration
  "verifyEmail": true,                   // ✅ Require email verification
  "registrationEmailAsUsername": true,   // ✅ Use email as username
  "loginWithEmailAllowed": true,
  "requiredActions": [
    {
      "alias": "VERIFY_EMAIL",
      "name": "Verify Email",
      "providerId": "VERIFY_EMAIL",
      "enabled": true,
      "defaultAction": true            // ✅ Auto-required for new users
    }
  ],
  "smtpServer": {
    "host": "localhost",
    "port": "1025",                     // ✅ MailHog SMTP
    "from": "noreply@datingapp.local",
    "fromDisplayName": "DatingApp"
  }
}
```

### 2. Infrastructure Updates

**docker-compose.yml**:
```yaml
mailhog:
  image: mailhog/mailhog:latest
  ports:
    - "1025:1025"  # SMTP server
    - "8025:8025"  # Web UI
  networks:
    - app-network
```

**infrastructure/start.sh**:
```bash
REQUIRED_SERVICES=(keycloak-db keycloak mailhog MatchmakingService-db)
```

---

## Testing the Configuration

### 1. Start Infrastructure

```bash
./infrastructure/start.sh
```

This will start:
- Keycloak on `http://localhost:8090`
- MailHog SMTP on `localhost:1025` 
- MailHog Web UI on `http://localhost:8025`

### 2. Test User Registration

**Via Keycloak UI**:
1. Navigate to `http://localhost:8090/realms/DatingApp/account`
2. Click "Register"
3. Fill in email + password
4. Check MailHog UI (`http://localhost:8025`) for verification email
5. Click verification link

**Via API** (for automated tests):
```python
# See api_tests.py _provision_user() method
response = requests.post(
    f"{keycloak_base}/admin/realms/DatingApp/users",
    json={
        "username": "user@example.com",
        "email": "user@example.com",
        "emailVerified": False,  # Force verification flow
        "enabled": True,
        "requiredActions": ["VERIFY_EMAIL"]
    },
    headers={"Authorization": f"Bearer {admin_token}"}
)
```

---

## Client Configuration

### Flutter Client (`dejtingapp-flutter`)

```json
{
  "clientId": "dejtingapp-flutter",
  "publicClient": true,  // No client secret
  "redirectUris": [
    "dejtingapp://callback",
    "com.dejtingapp://oauth2redirect"
  ],
  "attributes": {
    "pkce.code.challenge.method": "S256"  // PKCE for mobile security
  }
}
```

### Microservice Clients

All configured with:
- `serviceAccountsEnabled: true` (for service-to-service auth)
- `directAccessGrantsEnabled: true` (for password grant)  
- Audience mappers for proper token validation

---

## Email Templates

Keycloak uses default templates. To customize:

1. Navigate to Keycloak Admin Console
2. Realm Settings → Themes → Email Theme
3. Or mount custom templates via Docker volume

---

## Production Considerations

⚠️ **Before Production:**

1. **Replace MailHog with real SMTP**:
   ```json
   "smtpServer": {
     "host": "smtp.sendgrid.net",
     "port": "587",
     "from": "noreply@datingapp.com",
     "auth": "true",
     "starttls": "true",
     "user": "apikey",
     "password": "<SENDGRID_API_KEY>"
   }
   ```

2. **Enable HTTPS**:
   - Set `KC_HTTPS_CERTIFICATE_FILE` and `KC_HTTPS_CERTIFICATE_KEY_FILE`
   - Update redirectUris to use `https://`

3. **Secure client secrets**:
   - Rotate all `CHANGE_ME_*` secrets to strong random values
   - Store in environment variables, not realm export

4. **Configure email verification expiration**:
   - Realm Settings → Tokens → Email Verification (default 12 hours)

---

## Troubleshooting

**Issue**: Verification emails not arriving  
**Fix**: Check MailHog UI (`http://localhost:8025`) or container logs:
```bash
docker logs mailhog
```

**Issue**: "Invalid redirect_uri" error from Keycloak  
**Fix**: Verify Flutter client `redirectUris` match app config:
```dart
// lib/config/environment.dart
keycloakRedirectUri: 'dejtingapp://callback'
```

**Issue**: Users can't login after registration  
**Fix**: Ensure `emailVerified: true` after verification:
```bash
# Check via Keycloak Admin Console:
# Users → [user] → Email Verified = ON
```

---

## Next Steps

- [ ] **T023**: Update UserService wizard endpoints to sync with Keycloak events  
- [ ] **T028**: Implement Keycloak webhook listener for profile auto-creation  
- [ ] **T029**: Migrate TestDataGenerator to Keycloak-first flow  

---

**References**:
- [Keycloak Documentation](https://www.keycloak.org/docs/latest/)
- [MailHog GitHub](https://github.com/mailhog/MailHog)
- [PKCE for Mobile Apps](https://oauth.net/2/pkce/)
