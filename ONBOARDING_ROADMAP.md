# DatingApp Onboarding & Auth Roadmap

> Generated from user feedback session with Tinder reference screenshots.
> Last updated: 2025-07-14

---

## 📱 Current Onboarding Flow (11 screens, commit d4c23ab)

```
Welcome → Phone → Verify Code → Community Guidelines → First Name →
Birthday → Gender → Orientation → Photos → Lifestyle → Interests →
About Me → Home
```

### Screen Status
| # | Screen | Status | Style |
|---|--------|--------|-------|
| 1 | Welcome | ✅ Done | Light theme, coral accent |
| 2 | Phone Entry | ✅ Done | Country code picker + validation |
| 3 | **Verify Code** | ✅ NEW | 6-digit OTP, 60s resend, 5 retries |
| 4 | Community Guidelines | ✅ Done | Agree to proceed |
| 5 | First Name | ✅ Done | Single text field |
| 6 | **Birthday** | ✅ REWRITTEN | All dropdowns, 18-90 range, leap year |
| 7 | **Gender** | ✅ REWRITTEN | Search bar removed from More... sheet |
| 8 | **Orientation** | ✅ REWRITTEN | Dark theme cards with descriptions |
| 9 | Photos | ✅ Done | 6-slot grid, 2 min required |
| 10 | **Lifestyle** | ✅ NEW | Smoking/exercise/pets (optional) |
| 11 | **Interests** | ✅ NEW | 7 categories, max 10 picks (optional) |
| 12 | **About Me** | ✅ NEW | Communication/love lang/education (optional) |

---

## 🔐 Authentication Strategy

### Current: Keycloak ROPC (dev only)
Phone number + Keycloak `DatingApp` realm with `dejtingapp-flutter` client.

### Target Architecture: Phone-First + Social Login

**Priority order:**
1. **📱 Phone (PRIMARY)** — Universal, works everywhere. Required for account creation.
2. **🍎 Apple Sign-In (REQUIRED for iOS)** — App Store Guideline 4.8 mandates it if ANY social login is offered. "Hide My Email" is a pro for dating privacy.
3. **🔵 Google Sign-In (RECOMMENDED)** — Near-universal on Android, one-tap UX. Good Keycloak integration.
4. **👤 Facebook Login (OPTIONAL)** — Declining relevance, Gen Z abandoned it. Privacy anxiety is #1 killer. Offer but don't prioritize.

**Tinder's approach:** Phone is always required first → then optionally connect Apple/Google/Facebook for convenience login later.

### Implementation Plan

#### Phase 1: SMS Verification (next sprint)
- [ ] Choose provider: **Firebase Auth** (recommended) or Twilio
  - Firebase: $0.01-0.06/verification, auto-verify on Android, reCAPTCHA, test phone numbers
  - Twilio: ~$0.013-0.015/SMS + A2P fees. 10K users ≈ $130-150/month
- [ ] Wire up `sms_code_screen.dart` to actual verification backend
- [ ] Add rate limiting: 5 SMS/hr per phone, 150/hr per IP
- [ ] Block VoIP numbers (Twilio Lookup API or equivalent)
- [ ] 6-digit code, 10min expiry, exponential lockout after failures
- [ ] **Self-hosted SMS (Gammu/phone-as-gateway):** ❌ REJECTED
  - Carrier blocking within days, 1 SMS/sec throughput, no redundancy, regulatory risk

#### Phase 2: Apple Sign-In (before App Store submission)
- [ ] Register Apple Developer account, configure Sign In with Apple
- [ ] Keycloak: Add Apple identity provider (OIDC)
- [ ] Flutter: `sign_in_with_apple` package
- [ ] Show Apple button ONLY on iOS/macOS
- [ ] Handle "Hide My Email" relay addresses

#### Phase 3: Google Sign-In
- [ ] Google Cloud Console: OAuth 2.0 credentials (iOS + Android + web)
- [ ] Keycloak: Add Google identity provider
- [ ] Flutter: `google_sign_in` package
- [ ] Show on all platforms

#### Phase 4: Facebook Login (deprioritized)
- [ ] Meta Developer Console: App registration
- [ ] Keycloak: Add Facebook identity provider
- [ ] Flutter: `flutter_facebook_auth` package
- [ ] A/B test whether button improves conversion (likely won't)

### Welcome Screen Button Layout
```
┌─────────────────────────────────┐
│     [Continue with phone]       │  ← Primary, always shown
│     [Continue with Apple]       │  ← iOS/macOS only
│     [Continue with Google]      │  ← All platforms
│     [Continue with Facebook]    │  ← Optional, low priority
│                                 │
│  By tapping Continue, you agree │
│  to our Terms and Privacy Policy│
└─────────────────────────────────┘
```

---

## ✅ Verification Badge System

### How Tinder does it:
Real-time selfie → match a specific pose → AI compares face to profile photos → optional human review → blue checkmark badge.

### Our phased approach:

#### Phase 1: MVP Selfie Verification (~$1/1K verifications)
- [ ] "Get verified" button in profile settings
- [ ] Capture single front-facing selfie
- [ ] Send to **Azure Face API** for face comparison against profile photos
- [ ] Confidence threshold ≥ 0.7 → auto-approve
- [ ] 0.5-0.7 → queue for manual admin review
- [ ] < 0.5 → reject, suggest better photo
- [ ] Store verification status in UserService: `verificationStatus` enum (none, pending, verified, rejected)
- [ ] Display blue checkmark on profile card

#### Phase 2: Liveness Detection
- [ ] Add pose matching (turn head left, smile, look up)
- [ ] Prevents photo-of-a-photo attacks
- [ ] Consider on-device ML (Google ML Kit Face Detection)

#### Phase 3: Advanced
- [ ] ID verification (passport/driver's license OCR)
- [ ] ML.NET on-premise face embeddings (reduce API costs)
- [ ] Age estimation from face to cross-check birthday

---

## 📊 Profile Completeness System

### Formula
```
Score = (required_filled / total_required) × 40%
      + (encouraged_filled / total_encouraged) × 35%
      + (optional_filled / total_optional) × 25%
```

### Field Tiers

| Tier | Fields | Weight |
|------|--------|--------|
| **Required** (must have) | Name, Birthday, Gender, 2+ Photos | 40% |
| **Encouraged** (nudge) | Bio, Interests, Relationship Goals, Height | 35% |
| **Optional** (nice to have) | Job, Education, Drinking, Smoking, Exercise, Pets, Religion, Politics, Children preferences, Languages, Zodiac (auto from birthday), Communication style, Love language | 25% |

### UX Behavior
- Show completion % on profile page with circular progress ring
- Nudge notifications: "Complete your profile to get 3x more matches!"
- Matchmaking boost: Higher completeness → better visibility in discovery
- Optional screens (lifestyle, interests, about-me) skippable but contribute to %

### Backend Implementation
- [ ] Add `profileCompleteness` float field to UserService profile
- [ ] Recalculate on every profile update
- [ ] Expose via GET `/api/users/{id}/profile` response
- [ ] MatchmakingService: Factor completeness into candidate scoring

---

## 📅 Age Verification Rules
- Birthday is **locked permanently** after setting (Tinder/Bumble/Hinge all do this)
- Minimum age: **18** (worldwide legal consensus for dating apps)
- Maximum dropdown year: **90 years ago** (practical limit)
- Three dropdowns: Month (full names) → Day (adjusts for month/leap year) → Year (descending)
- Show "You are X years old" confirmation before proceeding
- Ask birthday **BEFORE** collecting personal data (COPPA/GDPR compliance)
- Note displayed: "You won't be able to change this later."

---

## 🔮 What about iOS/iPhone?

Flutter supports iOS natively. Current considerations:
1. **Apple Developer Account** ($99/year) — required for TestFlight + App Store
2. **Apple Sign-In** — MANDATORY (Guideline 4.8) if any social login offered
3. **Push notifications** — APNs setup (Firebase Cloud Messaging handles abstraction)
4. **SMS auto-fill** — iOS handles OTP auto-fill from Messages automatically (no extra code needed vs Android's SmsRetriever)
5. **Build/test** — Need macOS machine with Xcode for iOS builds
6. **Timeline** — After Android MVP is stable, build iOS simultaneously (Flutter = same codebase)

---

## 🚀 Sprint Priorities

### Sprint 1 (Current — DONE ✅)
- [x] 11-screen onboarding flow complete
- [x] Birthday dropdown validation (18-90)
- [x] Orientation descriptions
- [x] Gender search bar removed
- [x] SMS code entry screen (UI only)
- [x] Lifestyle/interests/about-me screens

### Sprint 2 (Next)
- [ ] Wire SMS verification to Firebase Auth
- [ ] Profile completeness calculation backend
- [ ] Persist onboarding data to UserService
- [ ] Photo upload integration with photo-service
- [ ] Welcome screen: Add Apple + Google login buttons (UI, not wired)

### Sprint 3
- [ ] Apple Sign-In (Keycloak + Flutter)
- [ ] Google Sign-In (Keycloak + Flutter)
- [ ] Profile completeness display on profile page
- [ ] Bio/relationship goals screens (add to wizard)

### Sprint 4
- [ ] Selfie verification MVP (Azure Face API)
- [ ] Verification badge display on cards
- [ ] Profile completeness nudge notifications
- [ ] iOS TestFlight build

### Sprint 5+
- [ ] Liveness detection (pose matching)
- [ ] Facebook Login (if A/B test shows value)
- [ ] ID verification
- [ ] Profile completeness → matchmaking score integration
