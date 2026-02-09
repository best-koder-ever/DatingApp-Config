# DatingApp Onboarding & Auth Roadmap

> Generated from user feedback sessions with Tinder reference screenshots.
> Last updated: 2026-02-09

---

## 📱 Current Onboarding Flow (11 screens)

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
2. **🍎 Apple Sign-In (REQUIRED for iOS)** — App Store Guideline 4.8 mandates it if ANY social login is offered.
3. **🔵 Google Sign-In (RECOMMENDED)** — Near-universal on Android, one-tap UX.
4. **👤 Facebook Login (OPTIONAL)** — Declining relevance, deprioritized.

### Implementation Plan

#### Phase 1: Firebase SMS Verification ← DECIDED
**Provider: Firebase Authentication** (chosen over Twilio, self-hosted rejected)
- [ ] Create Firebase project, enable Phone Auth
- [ ] Add `firebase_auth` + `firebase_core` to Flutter
- [ ] Configure **test phone numbers** in Firebase Console for development (free, no real SMS)
- [ ] Wire `sms_code_screen.dart` to `PhoneAuthProvider.verifyPhoneNumber()`
- [ ] On Android: Firebase auto-uses **SMS Retriever API** (zero-permission auto-fill!)
- [ ] On iOS: OTP auto-fill is built into the OS (set `textContentType: .oneTimeCode`)
- [ ] Set Firebase **budget alerts** — $10/month spending cap to prevent bot abuse
- [ ] Add rate limiting: 5 SMS/hr per phone, 150/hr per IP
- [ ] Block VoIP numbers via Firebase's built-in fraud detection
- [ ] 6-digit code, 10min expiry, exponential lockout after failures
- [ ] **Cost at scale:** $0.01-0.06/verification. 10K users ≈ $100-600/month

**Budget protection against bots:**
- [ ] Firebase Console → Budget & Alerts → set $10/month cap
- [ ] Enable reCAPTCHA verification (automatic on web, built into Android)
- [ ] Rate limit at YARP gateway level too (defense in depth)
- [ ] Monitor Firebase usage dashboard weekly
- [ ] Consider App Check (device attestation) to block emulators/bots

#### Android SMS Auto-Read Task
- [ ] Firebase Auth handles this automatically on Android via SMS Retriever API
- [ ] Verify it works: SMS Retriever requires the SMS to contain app hash (Firebase formats this)
- [ ] Fallback: If not using Firebase, use `smart_auth` package (193 likes, actively maintained)
  - `smartAuth.getSmsWithRetrieverApi()` — zero permissions, auto-extracts code
  - `smartAuth.requestPhoneNumberHint()` — shows SIM phone numbers
- [ ] Test on real Android device to confirm auto-fill works end-to-end

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
- [ ] A/B test whether button improves conversion (likely won't)

---

## ✅ Verification Badge System — SELF-HOSTED, OPEN-SOURCE

> **Decision:** Build our own using open-source ML instead of paying Azure/AWS.
> Self-hosted = full data control (GDPR), no per-call costs, and we learn the tech.

### Architecture Overview
```
┌─────────────────────────────────────────────────────┐
│                  FLUTTER CLIENT                      │
│  1. Open camera with face guide oval                 │
│  2. google_mlkit_face_detection for landmarks        │
│  3. Challenge-response liveness check:               │
│     - "Turn left" → verify headEulerAngleY           │
│     - "Blink" → verify eyeOpenProbability            │
│     - "Smile" → verify smilingProbability            │
│  4. Capture best frame during challenges             │
│  5. Send selfie + liveness attestation to server     │
└───────────────────┬─────────────────────────────────┘
                    │ HTTPS (base64 image + metadata)
┌───────────────────▼─────────────────────────────────┐
│              PHOTO-SERVICE (.NET 8)                  │
│  1. Validate image (size, format, has face)          │
│  2. Forward to DeepFace service for:                 │
│     a. Server-side anti-spoofing (Silent-Face)       │
│     b. Face embedding extraction (Facenet512)        │
│     c. Compare against profile photo embeddings      │
│  3. Decision: verified / rejected / pending          │
│  4. Update verification status in UserService        │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│          DEEPFACE SERVICE (Python, Docker)            │
│  - DeepFace library (22K+ GitHub stars, MIT)         │
│  - Built-in REST API on port 5005                    │
│  - Facenet512 model: 98.4% accuracy (LFW)           │
│  - Built-in anti-spoofing (Silent-Face)              │
│  - Runs on CPU, no GPU needed for MVP                │
│  - ~200-500ms per verification on 4-core CPU         │
└─────────────────────────────────────────────────────┘
```

### Why DeepFace over alternatives?
| Library | Stars | Accuracy (LFW) | Anti-Spoofing | Docker API | License |
|---------|-------|-----------------|---------------|------------|---------|
| **DeepFace** ⭐ | 22.2K | 98.4% (Facenet512) | ✅ Built-in | ✅ Built-in | MIT |
| InsightFace | 27.8K | 99.77% (ArcFace) | ❌ Separate | ❌ DIY | ⚠️ Non-commercial models |
| face_recognition | 56.1K | 99.38% (dlib) | ❌ None | ❌ DIY | MIT but unmaintained |
| OpenCV SFace | Built-in | 99.5% | ❌ None | ❌ DIY | Apache 2.0 |

**DeepFace wins** because: one-line verify API, built-in anti-spoofing, ships with Docker, MIT license, actively maintained.

### Phase 1: On-Device Liveness Detection (Flutter) — 1 week
> Goal: Prevent photo-of-a-photo and video replay attacks on the client side.

- [ ] Add `google_mlkit_face_detection` to Flutter (306 likes, Android+iOS)
- [ ] Build camera screen with oval face guide overlay
- [ ] Implement challenge-response system:
  - Server sends random sequence of 3 challenges (from pool of 5):
    - "Look left slowly" → track `headEulerAngleY > 20°`
    - "Look right slowly" → track `headEulerAngleY < -20°`
    - "Blink twice" → track `eyeOpenProbability` drops twice
    - "Smile" → track `smilingProbability > 0.7`
    - "Nod" → track `headEulerAngleX` change
  - Each challenge must complete within 5 seconds
  - Record multiple frames during challenges
- [ ] Extract best quality frame (sharpest, most frontal)
- [ ] Send selfie + challenge metadata to server

### Phase 2: DeepFace Server Setup — 1 week
> Goal: Deploy face comparison + anti-spoofing as a Docker microservice.

- [ ] Add DeepFace Docker container to `docker-compose.yml`
  ```yaml
  deepface:
    image: serengil/deepface
    ports: ["5005:5005"]
    environment:
      - DEEPFACE_HOME=/root/.deepface
    volumes:
      - deepface-models:/root/.deepface
  ```
- [ ] Pre-download Facenet512 model on first start (~90MB)
- [ ] Test API endpoint: `POST /verify` with `anti_spoofing: true`
- [ ] Add health check endpoint monitoring
- [ ] Configure YARP to NOT expose DeepFace externally (internal service only)

### Phase 3: photo-service Integration — 1 week
> Goal: Wire everything together through the .NET photo-service.

- [ ] New endpoint: `POST /api/verification/submit`
  - Accept: selfie image (base64), challenge metadata
  - Validate image: size, format, resolution, blur check (OpenCvSharp)
  - Call DeepFace `/verify` for each profile photo
  - Apply decision logic (see thresholds below)
- [ ] Store verification results in database:
  ```
  VerificationAttempts: Id, UserId, AttemptedAt, SelfieUrl,
    LivenessScore, SimilarityScore, ProfilePhotoId,
    Result (Verified/Rejected/Pending), RejectionReason
  Users: + IsVerified, VerifiedAt, VerificationAttemptCount
  ```
- [ ] Rate limit: max 3 attempts per 24 hours
- [ ] Notify UserService to update badge status

### Phase 4: Flutter UI + Badge Display — 1 week
> Goal: Complete the user-facing verification flow.

- [ ] "Get Verified" button in profile settings
- [ ] Verification flow screens: explanation → camera → processing → result
- [ ] Blue checkmark badge (✓) on profile cards in discovery feed
- [ ] Badge on user's own profile page
- [ ] "Verified" label in match/chat list

### Phase 5: Hardening & Edge Cases — 1-2 weeks
- [ ] Manual review queue for borderline cases (similarity 0.3-0.5)
- [ ] Admin panel: review pending verifications
- [ ] Re-verification: require every 6-12 months or after profile photo change
- [ ] Store face embeddings in PostgreSQL for faster re-verification
- [ ] Multiple profile photo comparison (verify against ALL photos, best match wins)
- [ ] Logging & analytics: track verification rates, rejection reasons

### Decision Thresholds (Facenet512)
| Cosine Similarity | Decision | Action |
|-------------------|----------|--------|
| > 0.40 | ✅ Verified | Auto-approve, blue badge |
| 0.30 — 0.40 | ⏳ Pending | Queue for manual admin review |
| < 0.30 | ❌ Rejected | Show "Face didn't match" + retry option |

### Future Phase: ONNX Migration (eliminate Python dependency)
> Only if needed — when DeepFace container feels like overhead.
- [ ] Download ArcFace ONNX model (248MB fp32 or 63MB int8)
- [ ] Use `Microsoft.ML.OnnxRuntime` NuGet in photo-service
- [ ] Implement face preprocessing in C# (detection, alignment, normalization)
- [ ] Port anti-spoofing model to ONNX too
- [ ] Remove DeepFace Docker container

### Hardware Requirements (self-hosted, no GPU needed)
| Scale | RAM | CPU | Cost/Month | Perf |
|-------|-----|-----|------------|------|
| MVP (<1K users) | 4GB | 2 vCPU | ~$20-40 | ~1-2s per verify |
| Growth (1-10K) | 8GB | 4 vCPU | ~$40-80 | ~500ms per verify |
| Scale (10K+) | 16GB | 8 vCPU | ~$80-160 | handles concurrency |

---

## 📊 Profile Completeness System

### The Big Picture
Profile completeness is NOT just about filling out onboarding fields. It's a **living score** that grows as users enrich their profile over time — better bio, more photos, more details, even fun things like a Spotify anthem.

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
| **Encouraged** (nudge) | Bio text (50+ chars), 5+ Interests, Relationship goals, Height | 35% |
| **Optional** (nice to have) | Job title, Company, Education, Smoking, Exercise, Pets, Religion, Politics, Children prefs, Languages, Zodiac (auto from birthday), Communication style, Love language, 4+ photos, Verification badge | 25% |

### Living Profile — Things That Grow Over Time
The score should reward users who keep enriching their profile:
- **More photos** → score increases (2=minimum, 4+=bonus, 6=max)
- **Longer bio** → score increases (empty=0, 50chars=partial, 150+=full credit)
- **More interests** → already captured (max 10)
- **Lifestyle details** → smoking, exercise, pets (from onboarding or later in settings)
- **About me** → communication style, love language, education (from onboarding or later)
- **Prompted answers** → Tinder-style prompts like "My ideal Sunday" (future feature)

### Backend Implementation
- [ ] Add `profileCompleteness` float field to UserService profile
- [ ] Recalculate on every profile update (photo add/remove, bio edit, field change)
- [ ] Expose via GET `/api/users/{id}/profile` response
- [ ] MatchmakingService: Factor completeness into candidate scoring
- [ ] Track per-field completion for targeted nudges ("Add a bio to get 15% more matches!")

### UX Behavior
- Show completion % on profile page with circular progress ring
- Nudge notifications: "Complete your profile to get 3x more matches!"
- Matchmaking boost: Higher completeness → better visibility in discovery
- Per-field nudges → "Add more photos" / "Write a bio" / "Tell us about yourself"

### 💡 Future Ideas (saved, not now)

#### Spotify Song Anthem 🎵
> "It would be cool to share a Spotify song anthem like on Tinder — let people listen to what music you want to present yourself with."

- **Default:** OFF (opt-in only — respect users who don't want music)
- **How it works:** Spotify oEmbed API (free, no auth needed) or Spotify Web API with OAuth
- **Display:** 30-second preview snippet on profile card with album art
- **Contributes to:** Profile completeness optional tier (small bonus)
- **Tech:** `spotify_sdk` Flutter package or just embed the Spotify preview URL
- **Considerations:** Licensing? Spotify's terms allow embedding previews. No download/full play.
- **Priority:** After core MVP is stable — fun polish feature, not critical path

#### Profile Prompts (Hinge-style)
> "My ideal Sunday..." / "I'm looking for..." / "Best travel story..."
- 3 text prompts, user picks from curated list
- 150-char answers displayed on profile
- Contributes to encouraged tier

#### Relationship Goals / Dating Intentions
> "Looking for: Long-term / Short-term / Friends / Not sure yet"
- Single-select chip in onboarding or profile settings
- Displayed prominently on profile
- Contributes to encouraged tier

---

## 📅 Age Verification Rules
- Birthday is **locked permanently** after setting
- Minimum age: **18**, maximum dropdown: **90 years ago**
- Three dropdowns: Month → Day (adjusts for month/leap year) → Year (descending)
- Show "You are X years old" confirmation, note: "You won't be able to change this later."

---

## 📱 SMS Auto-Fill — Platform Details

### Android (requires implementation)
- **With Firebase Auth:** Auto-handled! Firebase uses SMS Retriever API automatically.
  - No SMS permission needed, zero user action
  - SMS must contain app hash (Firebase formats this correctly)
- **Without Firebase (own backend):** Use `smart_auth` Flutter package
  - `smartAuth.getSmsWithRetrieverApi()` — zero permissions
  - `smartAuth.requestPhoneNumberHint()` — show SIM phone numbers
  - Requires SMS format: `<#> Your code is: 123456\nFA+9qCX9VSu`
- [ ] **Task:** Test auto-fill on real Android device end-to-end
- [ ] **Task:** Verify Firebase formats SMS correctly for Retriever API

### iOS (built into the OS)
- iOS auto-suggests OTP from Messages when `textContentType: .oneTimeCode` is set
- No package needed, no extra code beyond setting the content type
- Works automatically with any SMS provider (Firebase, Twilio, etc.)

---

## 🔮 What about iOS/iPhone?

Flutter supports iOS natively — same codebase.
1. **Apple Developer Account** ($99/year) for TestFlight + App Store
2. **Apple Sign-In** — MANDATORY if any social login offered
3. **Push notifications** — APNs via Firebase Cloud Messaging
4. **SMS auto-fill** — Built into OS, just works
5. **Build/test** — Need macOS machine with Xcode
6. **Timeline** — After Android MVP is stable

---

## 🚀 Sprint Priorities

### Sprint 1 — DONE ✅
- [x] 11-screen onboarding flow complete
- [x] Birthday dropdown validation (18-90)
- [x] Orientation descriptions
- [x] Gender search bar removed
- [x] SMS code entry screen (UI only)
- [x] Lifestyle/interests/about-me screens

### Sprint 2 (Next)
- [ ] Firebase Auth setup (project + test phone numbers + budget cap $10/mo)
- [ ] Wire `sms_code_screen.dart` to Firebase `PhoneAuthProvider`
- [ ] Test Android SMS auto-fill (Retriever API via Firebase)
- [ ] Persist onboarding data to UserService
- [ ] Photo upload integration with photo-service
- [ ] Profile completeness calculation backend

### Sprint 3
- [ ] Apple Sign-In (Keycloak + Flutter)
- [ ] Google Sign-In (Keycloak + Flutter)
- [ ] Profile completeness display on profile page
- [ ] Bio/relationship goals screens

### Sprint 4 — Verification Badge Phase 1+2
- [ ] Deploy DeepFace Docker container
- [ ] Flutter: liveness detection (google_mlkit_face_detection + challenge-response)
- [ ] photo-service: `/api/verification/submit` endpoint
- [ ] Face comparison pipeline (Facenet512, anti-spoofing)
- [ ] Blue badge display on profile cards

### Sprint 5 — Verification Hardening
- [ ] Manual review queue + admin panel
- [ ] Re-verification triggers (photo change, 6-month expiry)
- [ ] Face embedding storage in PostgreSQL
- [ ] iOS TestFlight build

### Sprint 6+
- [ ] Profile completeness nudge notifications
- [ ] Prompted answers / relationship goals
- [ ] Facebook Login (if A/B test shows value)
- [ ] Spotify anthem integration (fun feature, OFF by default)
- [ ] ONNX migration (eliminate Python/DeepFace if needed)
