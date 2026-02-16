# Phone OTP Authentication Architecture

**Passwordless phone verification using Firebase + Keycloak**

> 4-Layer Architecture Document — Context, Architecture, Implementation, Operations

---

## Layer 1: Context

### Why Passwordless?

Dating apps like Tinder, Bumble, and Hinge **never ask users to set a password**. Phone number verification provides:

- **Frictionless onboarding** — no password creation, no email verification delays
- **Real identity signal** — phone numbers are harder to fake than email addresses
- **Universal 2FA** — every phone receives SMS, no app-specific authenticator needed
- **Reduced account takeover** — no password reuse or phishing vectors

### Why Firebase Phone Auth?

| Feature | Firebase | Custom Keycloak SPI | Twilio Direct |
|---------|----------|-------------------|---------------|
| Free tier | 10K/month | N/A | Pay per SMS |
| Flutter SDK | First-class | None | HTTP only |
| Test phone numbers | Built-in | Manual | Manual |
| Abuse prevention | reCAPTCHA, rate limiting | Manual | Manual |
| SMS delivery | Google handles | You manage | You manage |
| Maintenance | Google maintains | Stale (KC 21.x) | You maintain |

**Decision: Firebase Phone Auth** — cheapest, easiest, best Flutter support, built-in abuse prevention.

### Design Principle

Firebase handles **phone verification only**. Keycloak remains the **identity provider** for all backend services. This means:
- Zero backend service changes
- All 6 services continue validating Keycloak JWTs
- Firebase is a verification layer, not an identity store

---

## Layer 2: Architecture

### Authentication Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Flutter App  │     │   Firebase   │     │   Keycloak   │
│              │     │  Phone Auth  │     │   (OIDC IDP) │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ 1. verifyPhone()   │                    │
       │───────────────────>│                    │
       │                    │ 2. Send SMS        │
       │                    │──────> User Phone  │
       │                    │                    │
       │ 3. Enter OTP code  │                    │
       │───────────────────>│                    │
       │                    │ 4. Verify OTP      │
       │  Firebase ID Token │                    │
       │<───────────────────│                    │
       │                    │                    │
       │ 5. Token Exchange (RFC 8693)            │
       │────────────────────────────────────────>│
       │            subject_token=firebase_jwt   │
       │            subject_issuer=firebase      │
       │                    │                    │
       │  Keycloak JWT      │  6. Validate       │
       │<────────────────────────────────────────│
       │  (access + refresh)│  Firebase token    │
       │                    │  → Issue KC JWT    │
       │                    │                    │
       │ 7. API calls with Keycloak JWT          │
       │────────────────────────────────────────>│ Backend Services
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| `FirebasePhoneAuthService` | Sends SMS, verifies OTP, returns Firebase ID token |
| `KeycloakTokenExchangeService` | Exchanges Firebase token → Keycloak JWT (RFC 8693) |
| `AuthSessionManager.loginWithPhone()` | Orchestrates exchange + stores session |
| `PhoneEntryScreen` | UI: phone input → triggers Firebase SMS |
| `SmsCodeScreen` | UI: OTP input → verifies → exchanges → session |
| `LoginScreen` | Phone-first entry point (no password fields) |
| `DevAutoLogin` | Admin API token issuance (no passwords in dev) |
| Keycloak Firebase IDP | Validates Firebase JWTs, creates/links users |
| Keycloak `test-runner` client | Service account for dev/test token issuance |

### Keycloak Identity Provider Configuration

Firebase is configured as an **OIDC Identity Provider** in Keycloak:

- **Alias**: `firebase`
- **Provider ID**: `oidc`
- **JWKS URL**: `https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com`
- **Issuer**: `https://securetoken.google.com/{FIREBASE_PROJECT_ID}`
- **Token Exchange**: Enabled on `dejtingapp-flutter` client

---

## Layer 3: Implementation

### Files Modified/Created

#### New Files
| File | Purpose |
|------|---------|
| `lib/services/firebase_phone_auth_service.dart` | Firebase phone verification lifecycle |
| `lib/services/keycloak_token_exchange_service.dart` | Firebase→Keycloak JWT exchange |
| `test/services/firebase_phone_auth_service_test.dart` | Unit tests |
| `test/services/keycloak_token_exchange_service_test.dart` | Unit tests |
| `config/keycloak/realms/datingapp-realm.json` | Updated with Firebase IDP + test-runner |

#### Modified Files
| File | Change |
|------|--------|
| `lib/screens/auth_screens.dart` | Phone-first login, removed password form |
| `lib/screens/wizard/phone_entry_screen.dart` | Wired to FirebasePhoneAuthService |
| `lib/screens/wizard/sms_code_screen.dart` | Firebase verify + token exchange |
| `lib/services/auth_session_manager.dart` | Added `loginWithPhone()` method |
| `lib/services/dev_auto_login.dart` | Admin API + token exchange (no passwords) |
| `pubspec.yaml` | Added firebase_core, firebase_auth |

### Token Exchange Request (RFC 8693)

```http
POST /realms/DatingApp/protocol/openid-connect/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:token-exchange
&client_id=dejtingapp-flutter
&subject_token={FIREBASE_ID_TOKEN}
&subject_token_type=urn:ietf:params:oauth:token-type:jwt
&subject_issuer=firebase
```

### Keycloak Realm Changes

1. **`dejtingapp-flutter` client**:
   - `directAccessGrantsEnabled: false` (ROPC disabled)
   - `token.exchange.standard.flow.enabled: true`
   - Added `phone-number-mapper` protocol mapper

2. **New `test-runner` client**:
   - Confidential, service account enabled
   - `client_credentials` + `password` grants
   - Used by DevAutoLogin and integration tests

3. **Firebase Identity Provider**:
   - OIDC provider with Google JWKS validation
   - Auto-creates Keycloak users on first login
   - Maps `phoneNumberVerified` attribute

---

## Layer 4: Operations

### Prerequisites

1. **Create Firebase Project**: https://console.firebase.google.com
2. **Enable Phone Auth**: Firebase Console → Authentication → Sign-in method → Phone
3. **Register Android app**: Package name from `build.gradle.kts`
4. **Download `google-services.json`** → `android/app/google-services.json`
5. **Register iOS app** (if needed): Download `GoogleService-Info.plist`
6. **Run FlutterFire CLI**: `flutterfire configure` → generates `firebase_options.dart`

### Firebase Test Phone Numbers (Dev)

In Firebase Console → Authentication → Sign-in method → Phone → Test phone numbers:

| Phone Number | Verification Code |
|-------------|-------------------|
| +46700000001 | 123456 |
| +46700000002 | 123456 |
| +46700000003 | 123456 |

These numbers **never send real SMS** — perfect for dev/CI.

### Keycloak Setup

After creating the Firebase project, update the realm JSON:

```bash
# Replace placeholder with your Firebase project ID
sed -i 's/FIREBASE_PROJECT_ID/your-actual-project-id/g' \
  config/keycloak/realms/datingapp-realm.json

# Restart Keycloak to apply
./infrastructure/stop.sh && ./infrastructure/start.sh
```

### Dev Workflow

```bash
# 1. Start infrastructure
./infrastructure/start.sh

# 2. Start services
./dev-start.sh

# 3. Run Flutter app
cd mobile-apps/flutter/dejtingapp
flutter run

# DevAutoLogin will auto-authenticate using Admin API (no passwords)
```

### Testing

```bash
# Unit tests
cd mobile-apps/flutter/dejtingapp
flutter test test/services/

# Integration tests (requires Keycloak running)
flutter test integration_test/

# API smoke tests
python3 api_tests.py
```

### Monitoring Auth Flow

```bash
# Watch Keycloak logs for token exchange
docker logs -f datingapp-keycloak 2>&1 | grep -i "token.exchange\|firebase"

# Check Firebase Auth users
# Firebase Console → Authentication → Users
```

### Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| "invalid_grant" on token exchange | Firebase IDP not configured | Update realm JSON with correct project ID |
| "No identity provider found" | Firebase alias mismatch | Check `subject_issuer=firebase` matches IDP alias |
| SMS not received | Firebase not initialized | Run `flutterfire configure`, add google-services.json |
| Token exchange 400 | Token exchange not enabled | Set `token.exchange.standard.flow.enabled: true` on client |
| DevAutoLogin fails | Keycloak not running | Run `./infrastructure/start.sh` first |
