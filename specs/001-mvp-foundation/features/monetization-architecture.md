# Monetization & Premium Features - Technical Specification

**Status**: 🟢 Planned for Phase 11 (Post-MMP)  
**Priority**: P2 (Revenue Generation)  
**Estimate**: 90-120 hours (3-4 weeks)  
**Last Updated**: 2026-01-28

---

## Executive Summary

Implement hybrid monetization model (subscription + virtual currency) to generate revenue while serving both committed and casual users. Based on competitive analysis, this approach generates **40% more revenue** than subscription-only models.

**Revenue Model:**
- **Premium Subscription**: $19.99/mo, $119/year (unlimited swipes, "See Who Liked You", advanced filters, read receipts, no ads)
- **Virtual Currency ("Sparks")**: $9.99 for 10 Sparks (consumable credits for Boost, Ping, Super Like, Undo Swipe)
- **À La Carte**: Individual purchases for casual users unwilling to commit to monthly subscription

**Security-First Architecture:**
- Platform-native IAP only (Google Play Billing, Apple In-App Purchase)
- Server-side receipt validation (zero client trust)
- PCI compliance via platform IAP (never handle credit cards)
- Fraud detection (device fingerprinting, velocity checks, refund abuse prevention)

---

## Layer 1: Feature Specification

### User Stories

**US-MON-1: Premium Subscription Discovery**
> As a free user, I want to see what Premium features are available so I can decide if upgrading is worth it.

**Acceptance Criteria:**
- [ ] "Upgrade to Premium" button visible in Settings
- [ ] Paywall modal shows feature comparison table (Free vs Premium)
- [ ] Annual pricing shows 40% savings vs monthly
- [ ] First-time users see 50% off first month (limited time offer)
- [ ] "Restore Purchases" button for users who reinstalled app

**US-MON-2: Frictionless Purchase Flow**
> As a user considering Premium, I want to purchase seamlessly using Apple/Google payment so I don't need to enter credit card info.

**Acceptance Criteria:**
- [ ] Tapping "Subscribe" opens platform-native payment sheet (face ID, fingerprint, or password)
- [ ] Purchase confirmation shows expiry date and features unlocked
- [ ] Subscription status appears in Settings (tier, renewal date, cancel option)
- [ ] Users can manage subscription via platform (App Store/Play Store)

**US-MON-3: Virtual Currency for Casual Spenders**
> As a user who doesn't want a monthly commitment, I want to buy individual features with Sparks so I can try premium benefits without subscribing.

**Acceptance Criteria:**
- [ ] "Sparks" balance visible in Settings and premium feature prompts
- [ ] Can purchase Spark packs: 5 Sparks ($4.99), 10 Sparks ($9.99), 25 Sparks ($19.99)
- [ ] Spend Sparks on: Boost (2 Sparks), Super Like (1 Spark), Undo Swipe (1 Spark), Ping (1 Spark)
- [ ] Transaction history shows all Spark purchases and spending

**US-MON-4: Premium Feature Access**
> As a Premium subscriber, I want instant access to unlimited swipes and "See Who Liked You" so I can match faster.

**Acceptance Criteria:**
- [ ] Free users: 100 swipes/day limit, Premium: unlimited
- [ ] "Likes" tab shows who swiped right (Premium only, blurred for free users with upgrade prompt)
- [ ] Advanced filters (dealbreakers, expanded age range) appear for Premium users
- [ ] Read receipts enabled automatically for Premium subscribers

**US-MON-5: Subscription Management**
> As a Premium subscriber, I want to cancel or change my subscription, understanding my access continues until the end of the billing period.

**Acceptance Criteria:**
- [ ] "Manage Subscription" button links to App Store/Play Store subscription settings
- [ ] Cancelled subscriptions show "Premium until [date]" with renewal disabled
- [ ] Backend continues granting Premium access until expiry date
- [ ] Email notification 3 days before expiry: "Your Premium access expires soon"

---

## Layer 2: Architecture & Implementation

### System Architecture

```mermaid
graph TB
    subgraph Flutter Client
        PurchaseUI[Purchase UI]
        IAPPlugin[in_app_purchase Plugin]
        FeatureGate[Feature Gate Checks]
    end
    
    subgraph YARP Gateway
        Routes[/billing/* routes]
    end
    
    subgraph BillingService
        ValidationAPI[Receipt Validation API]
        SubManager[Subscription Manager]
        CurrencyWallet[Currency Wallet]
        FraudDetection[Fraud Detection]
        Webhooks[Webhook Handlers]
    end
    
    subgraph App Stores
        GooglePlay[Google Play Billing]
        AppleIAP[Apple In-App Purchase]
    end
    
    subgraph Other Services
        UserService[UserService]
        MatchService[MatchmakingService]
        SwipeService[SwipeService]
    end
    
    PurchaseUI -->|Initiate Purchase| IAPPlugin
    IAPPlugin -->|Purchase Token| GooglePlay
    IAPPlugin -->|Receipt Data| AppleIAP
    
    GooglePlay -->|Purchase Event| IAPPlugin
    AppleIAP -->|Transaction| IAPPlugin
    
    IAPPlugin -->|Validate Receipt| Routes
    Routes -->|Forward| ValidationAPI
    
    ValidationAPI -->|Verify with Platform| GooglePlay
    ValidationAPI -->|Verify with Platform| AppleIAP
    
    ValidationAPI -->|Update Subscription| SubManager
    ValidationAPI -->|Grant Currency| CurrencyWallet
    
    GooglePlay -->|Refund/Cancel Event| Webhooks
    AppleIAP -->|Server Notification| Webhooks
    
    Webhooks -->|Revoke Access| SubManager
    Webhooks -->|Alert Admin| FraudDetection
    
    FeatureGate -->|Check Access| ValidationAPI
    MatchService -->|Is Premium?| ValidationAPI
    SwipeService -->|Check Limit| ValidationAPI
```

### Database Schema

```sql
-- Subscription tracking
CREATE TABLE Subscriptions (
    SubscriptionId VARCHAR(36) PRIMARY KEY,
    UserId VARCHAR(36) NOT NULL,
    Platform ENUM('iOS', 'Android', 'Web') NOT NULL,
    SubscriptionTier ENUM('Free', 'Premium', 'Premium+') NOT NULL DEFAULT 'Free',
    
    -- Platform identifiers
    PurchaseToken VARCHAR(500), -- Google Play token
    OriginalTransactionId VARCHAR(100), -- Apple transaction ID
    ProductId VARCHAR(100), -- e.g., 'premium_monthly'
    
    -- Lifecycle
    StartDate DATETIME NOT NULL,
    ExpiryDate DATETIME NOT NULL,
    AutoRenewing BOOLEAN DEFAULT TRUE,
    CancellationDate DATETIME NULL,
    
    -- Receipt storage (audit trail)
    LastReceiptData TEXT,
    LastValidatedAt DATETIME,
    
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_user_active (UserId, ExpiryDate),
    INDEX idx_platform_token (Platform, PurchaseToken(255)),
    INDEX idx_expiry (ExpiryDate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Virtual currency wallet
CREATE TABLE VirtualCurrency (
    UserId VARCHAR(36) PRIMARY KEY,
    Balance INT NOT NULL DEFAULT 3, -- 3 free Sparks on signup
    TotalPurchased INT NOT NULL DEFAULT 0,
    TotalSpent INT NOT NULL DEFAULT 0,
    LastUpdated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_balance (Balance)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Transaction log (immutable audit trail)
CREATE TABLE PurchaseTransactions (
    TransactionId VARCHAR(36) PRIMARY KEY,
    UserId VARCHAR(36) NOT NULL,
    ProductId VARCHAR(100) NOT NULL,
    PurchaseDate DATETIME NOT NULL,
    
    -- Financial data
    Amount DECIMAL(10,2),
    Currency CHAR(3) DEFAULT 'USD',
    
    -- Platform details
    Platform ENUM('iOS', 'Android', 'Web'),
    PlatformTransactionId VARCHAR(255),
    
    -- Status
    Status ENUM('Pending', 'Completed', 'Refunded', 'Failed', 'Cancelled') DEFAULT 'Pending',
    ReceiptValidated BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    ReceiptData TEXT,
    DeviceId VARCHAR(255),
    IpAddress VARCHAR(45),
    
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_date (UserId, PurchaseDate),
    INDEX idx_status (Status),
    INDEX idx_platform_tx (Platform, PlatformTransactionId(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Currency transaction log (for Sparks spend/grant)
CREATE TABLE CurrencyTransactions (
    Id VARCHAR(36) PRIMARY KEY,
    UserId VARCHAR(36) NOT NULL,
    Amount INT NOT NULL, -- Positive = grant, Negative = spend
    Type ENUM('Purchase', 'Spend', 'Refund', 'Grant', 'Promotion') NOT NULL,
    Reason VARCHAR(255), -- e.g., "Boost purchase", "Welcome bonus"
    RelatedTransactionId VARCHAR(36), -- Link to PurchaseTransactions if applicable
    
    CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_date (UserId, CreatedAt),
    INDEX idx_type (Type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Feature usage tracking (analytics)
CREATE TABLE FeatureUsage (
    Id VARCHAR(36) PRIMARY KEY,
    UserId VARCHAR(36) NOT NULL,
    FeatureName VARCHAR(100) NOT NULL, -- 'unlimited_swipes', 'see_likes', 'boost', etc.
    SubscriptionTier VARCHAR(50), -- Tier at time of use
    SparksSpent INT DEFAULT 0,
    Timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_feature (UserId, FeatureName),
    INDEX idx_timestamp (Timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Sequence Diagrams

#### Purchase Flow (Subscription)

```mermaid
sequenceDiagram
    actor User
    participant Flutter
    participant IAP as in_app_purchase
    participant Store as App Store/Play
    participant YARP
    participant BillingService
    participant DB
    
    User->>Flutter: Tap "Subscribe to Premium"
    Flutter->>IAP: queryProductDetails(['premium_monthly'])
    IAP->>Store: Fetch product info
    Store-->>IAP: { price: "$19.99", description: "..." }
    IAP-->>Flutter: ProductDetails
    Flutter->>User: Show price & features
    
    User->>Flutter: Confirm purchase
    Flutter->>IAP: buyNonConsumable(premium_monthly)
    IAP->>Store: Initiate purchase
    Store->>User: Face ID / Fingerprint prompt
    User->>Store: Authenticate
    
    Store-->>IAP: Purchase success + receipt
    IAP-->>Flutter: PurchaseDetails(status: purchased)
    
    Flutter->>YARP: POST /api/billing/validate {receipt, platform}
    YARP->>BillingService: Forward request
    BillingService->>Store: Verify receipt authenticity
    Store-->>BillingService: Valid, expires: 2026-02-28
    
    BillingService->>DB: INSERT Subscriptions (tier: Premium, expiry: 2026-02-28)
    BillingService-->>YARP: { valid: true, tier: "Premium", expiryDate: "..." }
    YARP-->>Flutter: Validation success
    
    Flutter->>IAP: completePurchase()
    Flutter->>User: "Premium activated! 🎉"
```

#### Virtual Currency Spend (Boost Feature)

```mermaid
sequenceDiagram
    actor User
    participant Flutter
    participant YARP
    participant BillingService
    participant MatchService
    participant DB
    
    User->>Flutter: Tap "Boost" (2 Sparks)
    Flutter->>YARP: GET /api/billing/currency/balance
    YARP->>BillingService: Forward
    BillingService->>DB: SELECT Balance FROM VirtualCurrency WHERE UserId=...
    DB-->>BillingService: Balance: 5
    BillingService-->>Flutter: { balance: 5 }
    
    Flutter->>User: Show "Boost for 2 Sparks? (You have 5)"
    User->>Flutter: Confirm
    
    Flutter->>YARP: POST /api/billing/currency/spend {amount: 2, reason: "Boost"}
    YARP->>BillingService: Forward
    
    BillingService->>DB: BEGIN TRANSACTION
    BillingService->>DB: UPDATE VirtualCurrency SET Balance=3 WHERE UserId=...
    BillingService->>DB: INSERT CurrencyTransactions (amount: -2, type: Spend)
    BillingService->>DB: COMMIT
    
    BillingService->>MatchService: POST /api/matchmaking/boost {userId, duration: 30min}
    MatchService->>DB: Set boost flag, priority score +1000
    
    BillingService-->>Flutter: { success: true, newBalance: 3 }
    Flutter->>User: "Boosted! You're visible to 10x more people for 30 min"
```

---

## Layer 3: API Contracts

### BillingService Endpoints

#### POST /api/billing/validate
**Description**: Validate iOS or Android receipt and grant subscription/currency  
**Authentication**: Required (JWT)  
**Rate Limit**: 10 requests/minute per user

**Request:**
```json
{
  "platform": "iOS" | "Android",
  "receiptData": "base64_encoded_receipt_or_purchase_token",
  "productId": "premium_monthly" | "sparks_10" | "boost_pack_5"
}
```

**Response (Subscription):**
```json
{
  "success": true,
  "subscriptionTier": "Premium",
  "expiryDate": "2026-02-28T23:59:59Z",
  "autoRenewing": true,
  "productId": "premium_monthly"
}
```

**Response (Virtual Currency):**
```json
{
  "success": true,
  "currencyGranted": 10,
  "newBalance": 13,
  "productId": "sparks_10"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid receipt format
- `403 Forbidden`: Receipt already used (replay attack)
- `422 Unprocessable Entity`: Receipt validation failed with platform

---

#### GET /api/billing/subscription/{userId}
**Description**: Get current subscription status  
**Authentication**: Required (JWT, must be userId or admin)

**Response:**
```json
{
  "userId": "a1b2c3d4...",
  "subscriptionTier": "Premium",
  "expiryDate": "2026-02-28T23:59:59Z",
  "autoRenewing": true,
  "platform": "iOS",
  "startDate": "2026-01-28T14:32:00Z",
  "cancelledAt": null,
  "features": [
    "unlimited_swipes",
    "see_who_liked_you",
    "advanced_filters",
    "read_receipts",
    "no_ads"
  ]
}
```

**Free User Response:**
```json
{
  "userId": "xyz...",
  "subscriptionTier": "Free",
  "expiryDate": null,
  "features": [],
  "upgradeUrl": "/api/billing/products"
}
```

---

#### GET /api/billing/currency/balance
**Description**: Get user's Spark balance  
**Authentication**: Required (JWT)

**Response:**
```json
{
  "userId": "abc...",
  "balance": 7,
  "totalPurchased": 20,
  "totalSpent": 13,
  "lastUpdated": "2026-01-28T15:45:00Z"
}
```

---

#### POST /api/billing/currency/spend
**Description**: Deduct Sparks for premium feature usage  
**Authentication**: Required (JWT)  
**Idempotency**: Supports `Idempotency-Key` header

**Request:**
```json
{
  "amount": 2,
  "reason": "Boost - 30 min priority",
  "featureId": "boost_30min" // Optional, for tracking
}
```

**Response (Success):**
```json
{
  "success": true,
  "amountSpent": 2,
  "newBalance": 5,
  "transactionId": "tx_abc123..."
}
```

**Response (Insufficient Funds):**
```json
{
  "success": false,
  "error": "Insufficient balance",
  "currentBalance": 1,
  "required": 2,
  "purchaseUrl": "/api/billing/products?filter=currency"
}
```

---

#### GET /api/billing/products
**Description**: Get available IAP products (for display in Flutter)  
**Authentication**: Optional (public)

**Response:**
```json
{
  "subscriptions": [
    {
      "productId": "premium_monthly",
      "title": "Premium - Monthly",
      "description": "Unlimited swipes, see who liked you, advanced filters",
      "price": "$19.99",
      "priceMicros": 19990000,
      "currency": "USD",
      "billingPeriod": "P1M",
      "freeTrialPeriod": "P7D",
      "features": ["unlimited_swipes", "see_likes", "advanced_filters", "read_receipts"]
    },
    {
      "productId": "premium_annual",
      "title": "Premium - Annual",
      "description": "Save 40%! All Premium features for a year",
      "price": "$119.00",
      "priceMicros": 119000000,
      "currency": "USD",
      "billingPeriod": "P1Y",
      "discount": "40%",
      "features": ["unlimited_swipes", "see_likes", "advanced_filters", "read_receipts"]
    }
  ],
  "consumables": [
    {
      "productId": "sparks_5",
      "title": "5 Sparks",
      "description": "Enough for 2 Boosts or 5 Super Likes",
      "price": "$4.99"
    },
    {
      "productId": "sparks_10",
      "title": "10 Sparks",
      "description": "Most popular! Best value for casual use",
      "price": "$9.99",
      "badge": "POPULAR"
    },
    {
      "productId": "sparks_25",
      "title": "25 Sparks",
      "description": "Power user pack with bonus Sparks",
      "price": "$19.99",
      "bonus": "+5 free"
    }
  ]
}
```

---

#### POST /api/billing/webhooks/appstore
**Description**: Apple App Store Server Notifications (subscription lifecycle events)  
**Authentication**: Signature verification with Apple's public key  
**Note**: This endpoint is called by Apple, not Flutter client

**Request (Example - Subscription Cancelled):**
```json
{
  "notification_type": "DID_CHANGE_RENEWAL_STATUS",
  "unified_receipt": {
    "latest_receipt_info": [{
      "original_transaction_id": "1000000123456789",
      "expires_date_ms": "1709164799000",
      "auto_renew_status": "0"
    }]
  }
}
```

**Action**: Update `Subscriptions.AutoRenewing = false`, send email to user

---

#### POST /api/billing/webhooks/googleplay
**Description**: Google Play Real-time Developer Notifications  
**Authentication**: Verify message signature with Google Cloud Pub/Sub

**Request (Example - Subscription Renewed):**
```json
{
  "message": {
    "data": "base64_encoded_notification",
    "messageId": "1234567890"
  }
}
```

**Decoded Notification:**
```json
{
  "version": "1.0",
  "packageName": "com.datingapp.mobile",
  "eventTimeMillis": "1706454000000",
  "subscriptionNotification": {
    "version": "1.0",
    "notificationType": 2, // SUBSCRIPTION_RENEWED
    "purchaseToken": "abc...xyz",
    "subscriptionId": "premium_monthly"
  }
}
```

**Action**: Extend `Subscriptions.ExpiryDate` by 1 month

---

### Feature Gate APIs (Middleware in other services)

#### GET /api/matchmaking/candidates (Updated)
**Authorization**: Enhanced with subscription tier check

**Before (Phase 4):**
```csharp
[HttpGet("candidates")]
[Authorize]
public async Task<IActionResult> GetCandidates()
{
    var userId = User.GetUserId();
    var candidates = await _matchmakingService.GetCandidates(userId);
    return Ok(candidates);
}
```

**After (Phase 11):**
```csharp
[HttpGet("candidates")]
[Authorize]
[RateLimit(free: 100/day, premium: unlimited)]
public async Task<IActionResult> GetCandidates()
{
    var userId = User.GetUserId();
    
    // Check if user has reached daily limit (free tier only)
    var canSwipe = await _billingClient.CanAccessFeature(userId, "unlimited_swipes");
    if (!canSwipe)
    {
        return StatusCode(402, new { 
            error = "Daily swipe limit reached (100/100)",
            upgradeUrl = "/api/billing/products",
            resetTime = DateTime.UtcNow.Date.AddDays(1)
        });
    }
    
    var candidates = await _matchmakingService.GetCandidates(userId);
    return Ok(candidates);
}
```

---

#### GET /api/swipes/incoming-likes (NEW - Premium Feature)
**Description**: Show users who swiped right on current user (Premium only)  
**Authentication**: Required + Premium subscription

**Request:**
```
GET /api/swipes/incoming-likes?limit=20&offset=0
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (Premium User):**
```json
{
  "likes": [
    {
      "userId": "user123",
      "displayName": "Alex, 28",
      "photos": ["https://...photo1.jpg"],
      "likedAt": "2026-01-28T10:30:00Z",
      "bio": "Coffee enthusiast, dog lover"
    }
  ],
  "total": 47,
  "limit": 20,
  "offset": 0
}
```

**Response (Free User - 402 Payment Required):**
```json
{
  "error": "Premium feature",
  "feature": "see_who_liked_you",
  "blurredCount": 47,
  "message": "47 people liked you! Upgrade to see who",
  "upgradeUrl": "/api/billing/products",
  "previewPhotos": [
    "https://...blurred1.jpg",
    "https://...blurred2.jpg",
    "https://...blurred3.jpg"
  ]
}
```

---

## Layer 4: Architecture Decision Records

### ADR-001: Platform-Native IAP Only (No Stripe, No Direct Billing)

**Status**: ✅ Accepted  
**Date**: 2026-01-28  
**Deciders**: Tech Lead, Founder

**Context:**
Need to monetize dating app. Options:
1. Platform IAP (Google Play, Apple App Store)
2. Stripe/PayPal (web-based payments)
3. Hybrid (IAP for mobile, Stripe for web)

**Decision:**
Use **platform-native IAP exclusively** for mobile app. No web payments in MVP.

**Rationale:**
- **App Store Compliance**: Apple requires IAP for digital goods (dating app subscriptions qualify). Violating this = app rejection.
- **Security**: Platform handles PCI compliance, fraud detection, chargebacks. Building custom billing = $50K+/year compliance cost.
- **User Trust**: Users trust Apple/Google payment systems. Entering credit cards in-app = conversion killer (70% drop-off).
- **Subscription Management**: Platform provides built-in subscription UI (upgrade, cancel, refund). Don't need to build admin portal.
- **Developer Velocity**: `in_app_purchase` plugin handles both platforms with single API. Stripe = separate mobile SDK + backend integration.

**Trade-offs:**
- ❌ **30% Commission**: Apple/Google take 30% (15% after 1 year or if Small Business Program eligible)
- ❌ **No Discount Codes**: Can't offer "SAVE20" promo codes (must use App Store subscription offers)
- ✅ **Faster Launch**: Skip payment form UI, PCI compliance, Stripe onboarding
- ✅ **Lower Risk**: App Store rejection avoided, fraud handled by platform

**Consequences:**
- Must create IAP products in App Store Connect + Google Play Console before testing
- Cannot mention prices outside app (no "Cheaper on web!" messaging)
- Refunds handled by Apple/Google (we must revoke access when notified)

---

### ADR-002: Server-Side Receipt Validation (Zero Client Trust)

**Status**: ✅ Accepted  
**Date**: 2026-01-28  
**Deciders**: Tech Lead, Security Reviewer

**Context:**
After Flutter client receives purchase confirmation from App Store/Play, how do we verify legitimacy before granting Premium access?

**Options:**
1. **Trust Client**: Flutter sends `isPremium: true` → Backend grants access (no verification)
2. **Client-Side Receipt Check**: Flutter validates receipt → Backend trusts result
3. **Server-Side Validation**: Backend calls Apple/Google APIs to verify receipt authenticity

**Decision:**
Implement **server-side receipt validation** for every purchase and subscription status check.

**Rationale:**
- **Jailbreak/Root Exploit**: Modified apps can fake purchase responses. Jailbroken iOS devices can bypass StoreKit validation. Server validation with Apple/Google's cryptographic signatures = unforgeable.
- **Production Precedent**: Tinder, Bumble, Netflix all validate server-side. Industry standard for subscription apps.
- **Fraud Prevention**: Prevents "Lucky Patcher" attacks (Android tool that cracks IAP). Without server validation, 15-20% of "Premium" users are fraudulent.
- **Business Logic**: Server needs subscription expiry date to enforce access. Receipt contains this (client could lie).

**Implementation:**
```csharp
// BillingService/Services/ReceiptValidationService.cs
public async Task<ValidationResult> ValidateAppleReceipt(string receiptData)
{
    var client = _httpClientFactory.CreateClient();
    var response = await client.PostAsJsonAsync(
        "https://buy.itunes.apple.com/verifyReceipt", // Production endpoint
        new { 
            "receipt-data" = receiptData,
            "password" = _config["AppStore:SharedSecret"], // From App Store Connect
            "exclude-old-transactions" = true
        }
    );
    
    var result = await response.Content.ReadFromJsonAsync<AppleReceiptResponse>();
    
    if (result.Status != 0) // 0 = valid
        throw new InvalidReceiptException($"Apple validation failed: {result.Status}");
    
    var latestReceipt = result.LatestReceiptInfo.OrderByDescending(r => r.ExpiresDateMs).First();
    
    // Check if expired
    var expiryDate = DateTimeOffset.FromUnixTimeMilliseconds(latestReceipt.ExpiresDateMs);
    if (expiryDate < DateTimeOffset.UtcNow)
        throw new SubscriptionExpiredException();
    
    return new ValidationResult {
        IsValid = true,
        ExpiryDate = expiryDate.DateTime,
        ProductId = latestReceipt.ProductId,
        OriginalTransactionId = latestReceipt.OriginalTransactionId
    };
}
```

**Security Checklist:**
- [ ] Store Apple Shared Secret in Azure Key Vault (not appsettings.json)
- [ ] Use production endpoint (`buy.itunes.apple.com`, not sandbox)
- [ ] Implement receipt deduplication (prevent replay attacks)
- [ ] Rate limit validation endpoint (10 requests/min per user)
- [ ] Log all validation attempts (audit trail for fraud investigation)

**Consequences:**
- Every premium feature check = 1 DB query to `Subscriptions` table (cache with Redis later)
- Apple/Google validation APIs can be slow (200-500ms) → validate async, don't block purchase flow
- Need webhook handling for subscription lifecycle events (renewal, cancellation, refund)

---

### ADR-003: Hybrid Monetization (Subscription + Virtual Currency)

**Status**: ✅ Accepted  
**Date**: 2026-01-28  
**Deciders**: Founder, Product Lead

**Context:**
Dating apps monetize via:
1. **Subscription-Only**: Monthly/annual plans (Match.com model)
2. **À La Carte**: Pay-per-feature (rare, confusing pricing)
3. **Hybrid**: Subscription + consumable currency (Tinder, Bumble model)

**Decision:**
Implement **hybrid model** with Premium subscription ($19.99/mo) + virtual currency ("Sparks") for à la carte purchases.

**Competitive Analysis:**
| App | Model | Revenue Split | ARPPU (Avg Revenue Per Paying User) |
|-----|-------|---------------|-------------------------------------|
| **Tinder** | Subscription + Boosts/Super Likes | 60% subs, 40% consumables | $58/month |
| **Bumble** | Subscription + Spotlight/Coins | 65% subs, 35% consumables | $52/month |
| **Hinge** | Subscription + Roses | 75% subs, 25% consumables | $45/month |
| **Match.com** | Subscription-only | 100% subs | $35/month |

**Why Hybrid Wins:**
1. **Captures Both Segments**:
   - **Committed users** → Subscribe ($19.99/mo steady revenue)
   - **Casual users** → Buy Sparks ($9.99 one-time, lower barrier)
   - Data: 70% of revenue from 20% of users (subscribers), 30% from 80% (casual spenders)

2. **Higher LTV (Lifetime Value)**:
   - Subscriber who also buys Boosts = $25-30/mo vs $20/mo subscription-only
   - "Whales" (top 5% spenders) buy $50-100/mo in virtual currency on top of subscription

3. **Psychological Pricing**:
   - "$9.99 for 10 Sparks" feels cheaper than "$19.99/month commitment"
   - Users buy Sparks impulsively (saw cute match, buy Boost immediately)
   - Leftover balances = sunk cost fallacy (bought 10, used 8, feel invested)

4. **Monetizes Free Users**:
   - Free user sees "47 people liked you" → buys 10 Sparks to see them (no subscription)
   - Conversion funnel: Free → Spark buyer (40%) → Subscriber (15%)

**Premium Features (Subscription):**
- Unlimited swipes (vs 100/day free)
- See who liked you (vs blurred for free)
- Read receipts
- Advanced filters (dealbreakers, expanded age range)
- No ads
- Priority in discovery queue

**Spark Purchases (Consumable):**
- **Boost** (2 Sparks): 30 min priority, 10x visibility
- **Super Like** (1 Spark): Signal strong interest, notification to recipient
- **Undo Swipe** (1 Spark): Reverse accidental left swipe
- **Ping** (1 Spark): Direct message before matching (Feeld model)

**Pricing Strategy:**
```
Subscriptions:
- Premium Monthly: $19.99 (best for trying)
- Premium Annual: $119.00 (40% savings, best value)
- First-time offer: 50% off first month ($9.99)

Sparks (consumable currency):
- 5 Sparks: $4.99 ($1.00 per Spark)
- 10 Sparks: $9.99 ($0.99 per Spark) ← POPULAR badge
- 25 Sparks: $19.99 ($0.80 per Spark) + 5 bonus Sparks
```

**User Journey Example:**
1. Free user (Day 1): Swipes 100 times, gets 3 matches
2. Day 3: Runs out of swipes, sees "47 likes" blurred → Buys 10 Sparks ($9.99) to reveal
3. Day 7: Likes new match, wants to stand out → Spends 1 Spark on Super Like
4. Day 14: Frustrated by 100/day limit → Subscribes to Premium ($19.99/mo)
5. Month 2: Still subscribed, occasionally buys Boosts (2 Sparks) for weekend visibility

**Total Revenue from This User:** $9.99 (Sparks) + $19.99 (Month 1 sub) + $19.99 (Month 2 sub) + $9.99 (Boost pack) = $59.96 in 60 days

**Consequences:**
- Need 2 separate purchase flows in Flutter (subscription vs consumable)
- Backend tracks both `Subscriptions` table and `VirtualCurrency` table
- Complexity: Feature gates check "Is Premium OR has 2+ Sparks?"
- Analytics: Track conversion funnel (Free → Spark buyer → Subscriber)

---

### ADR-004: Fraud Detection Strategy

**Status**: ✅ Accepted  
**Date**: 2026-01-28  
**Deciders**: Tech Lead, Finance

**Context:**
Dating apps are high-risk for payment fraud:
- **Refund Abuse**: User subscribes, screenshots profiles, requests refund within 48h
- **Account Sharing**: 1 Premium account shared across 5+ users
- **Geo-Arbitrage**: VPN to cheaper region (India $5/mo), use in US
- **Stolen Cards**: Fraudsters test cards with dating app subscriptions

**Decision:**
Implement multi-layer fraud detection with automated flagging and manual review.

**Detection Rules:**

**Rule 1: Velocity Checks**
```csharp
// Flag if user makes >3 purchases in 24 hours
public async Task<bool> IsVelocityAbuse(string userId)
{
    var recentPurchases = await _dbContext.PurchaseTransactions
        .Where(t => t.UserId == userId && 
                    t.PurchaseDate > DateTime.UtcNow.AddHours(-24))
        .CountAsync();
    
    return recentPurchases > 3; // Flag for review
}
```

**Rule 2: Device Fingerprint Sharing**
```csharp
// Flag if 5+ accounts use same device ID (rooted Android, jailbroken iOS)
public async Task<bool> IsDeviceSharing(string deviceId)
{
    var accountsOnDevice = await _dbContext.Subscriptions
        .Where(s => s.DeviceId == deviceId && s.ExpiryDate > DateTime.UtcNow)
        .Select(s => s.UserId)
        .Distinct()
        .CountAsync();
    
    return accountsOnDevice > 5;
}
```

**Rule 3: Refund Pattern Detection**
```csharp
// Flag if user has 2+ refunds in 90 days
public async Task<bool> IsRefundAbuser(string userId)
{
    var refundCount = await _dbContext.PurchaseTransactions
        .Where(t => t.UserId == userId && 
                    t.Status == TransactionStatus.Refunded &&
                    t.PurchaseDate > DateTime.UtcNow.AddDays(-90))
        .CountAsync();
    
    return refundCount >= 2;
}
```

**Rule 4: Geo-Arbitrage Detection**
```csharp
// Flag if billing country != detected country (via IP geolocation)
public bool IsGeoMismatch(PurchaseTransaction tx)
{
    var ipCountry = _geoService.GetCountryFromIP(tx.IpAddress); // e.g., "US"
    var billingCountry = tx.Currency == "INR" ? "IN" : "US"; // Simplified
    
    return ipCountry != billingCountry && tx.Amount < 10; // Cheap subscriptions from VPNs
}
```

**Automated Actions:**
- **Low Risk**: Auto-approve, grant access immediately
- **Medium Risk**: Auto-approve, flag for 48h review (revoke if chargeback)
- **High Risk**: Hold purchase, require email verification + ID upload

**Manual Review Triggers:**
- User flagged by 2+ rules
- Transaction amount >$100 in 24 hours
- Account created <24h ago + immediate Premium purchase
- Email domain is disposable (tempmail.com, guerrillamail.com)

**Example Fraud Case:**
```
User: fraud_user_123
- Created account 10 minutes ago
- Purchased Premium Annual ($119) via Indian VPN
- Device ID matches 3 other Premium accounts
- Email: randomstring@tempmail.com
- IP: Mumbai, India (currency: USD $119, not INR ₹1,999)

Fraud Score: 87/100 (HIGH RISK)
Action: Hold purchase, send email: "Verify your identity to activate Premium"
```

**Reporting to Platforms:**
- Apple: Report fraud via App Store Connect (suspend fraudulent Apple IDs)
- Google: Use Google Play Developer API to report abuse

**Consequences:**
- 3-5% of purchases flagged for review (false positives)
- Need support team to handle verification requests
- Fraud losses reduced from 8-10% to <2% (industry data)

---

## Implementation Checklist

### Phase 11.1: BillingService Foundation (30-40h)

#### Week 1: Service Scaffold & Database (12-15h)
- [ ] Create `BillingService/` directory with ASP.NET Core project
- [ ] Copy Program.cs pattern from UserService (MediatR, FluentValidation, JWT auth)
- [ ] Create `BillingService/Data/BillingDbContext.cs` with 5 tables
- [ ] Generate Entity Framework migrations for billing schema
- [ ] Add YARP routes: `/billing/*` → `http://localhost:8085`
- [ ] Configure MySQL connection string in appsettings.json
- [ ] Add to `dev-start.sh` script (port 8085)
- [ ] Create health check endpoint: `GET /health`

**Evidence:**
- `dotnet run --project BillingService` starts on port 8085
- `dotnet ef migrations list` shows initial migration
- YARP routes billing requests correctly

---

#### Week 1-2: Receipt Validation (iOS & Android) (15-18h)
- [ ] Install NuGet: `Google.Apis.AndroidPublisher.v3` for Google Play validation
- [ ] Create `Services/AppleReceiptValidator.cs` with `verifyReceipt` API call
- [ ] Create `Services/GooglePlayValidator.cs` with `purchases.subscriptions.get` API
- [ ] Add App Store Shared Secret to Azure Key Vault (or appsettings for dev)
- [ ] Add Google Play service account JSON to secure storage
- [ ] Implement receipt deduplication (check `PurchaseTransactions.PlatformTransactionId`)
- [ ] Create `POST /api/billing/validate` endpoint with validation logic
- [ ] Add error handling: Invalid receipt (400), Already used (403), Expired (422)
- [ ] Unit tests: Mock Apple/Google API responses

**Evidence:**
- Can validate real iOS subscription receipt (test with sandbox account)
- Can validate real Android subscription (test with Google Play test track)
- Duplicate receipt returns 403 Forbidden

---

#### Week 2: Subscription Management (8-10h)
- [ ] Create `Commands/GrantSubscriptionCommand.cs` (MediatR pattern)
- [ ] Create `GrantSubscriptionHandler.cs`: Insert/update `Subscriptions` table
- [ ] Create `Queries/GetSubscriptionStatusQuery.cs`
- [ ] Create `GetSubscriptionStatusHandler.cs`: Check expiry, return tier + features
- [ ] Implement `GET /api/billing/subscription/{userId}` endpoint
- [ ] Add subscription status caching (in-memory for MVP, Redis later)
- [ ] Create background job: `SubscriptionExpiryCheckService` (runs hourly)
  - Finds subscriptions expiring in <3 days
  - Sends email notification: "Your Premium expires soon"

**Evidence:**
- After validating receipt, subscription appears in DB with correct expiry date
- `GET /subscription/{userId}` returns Premium status
- Expired subscription returns Free tier

---

### Phase 11.2: Flutter IAP Integration (20-25h)

#### Week 2: Plugin Setup & Product Catalog (8-10h)
- [ ] Add `in_app_purchase: ^3.2.3` to `pubspec.yaml`
- [ ] Create App Store Connect products:
  - `premium_monthly` ($19.99, auto-renewing, 1 month)
  - `premium_annual` ($119.00, auto-renewing, 1 year)
  - `sparks_5` ($4.99, consumable)
  - `sparks_10` ($9.99, consumable)
  - `sparks_25` ($19.99, consumable)
- [ ] Create Google Play Console products (same IDs)
- [ ] Configure subscription groups in App Store Connect
- [ ] Set up sandbox test accounts (iOS + Android)
- [ ] Create `lib/services/billing_service.dart` with `in_app_purchase` wrapper
- [ ] Implement `queryProductDetails()` to fetch prices
- [ ] Add product display UI: `lib/screens/premium_modal.dart`

**Evidence:**
- Products load in Flutter app with correct prices
- Sandbox purchase flow works (no actual charge)

---

#### Week 3: Purchase Flow & Receipt Submission (10-12h)
- [ ] Implement purchase listener in `initState()` (handle `purchaseStream`)
- [ ] Create `buySubscription(productId)` method (calls `buyNonConsumable`)
- [ ] Create `buySparks(productId)` method (calls `buyConsumable`)
- [ ] On purchase success, send receipt to backend:
  - iOS: Extract `transactionReceipt` from `AppStorePurchaseDetails`
  - Android: Extract `purchaseToken` from `GooglePlayPurchaseDetails`
  - POST to `/api/billing/validate`
- [ ] Handle validation response: Update local state, show confirmation
- [ ] Call `completePurchase()` after backend validation (critical!)
- [ ] Implement "Restore Purchases" button (calls `restorePurchases()`)
- [ ] Add loading states, error handling (payment cancelled, network timeout)

**Evidence:**
- Real sandbox purchase works end-to-end (App Store → Flutter → Backend → DB)
- Subscription appears in Settings screen after purchase
- "Restore Purchases" retrieves past subscription

---

#### Week 3: Premium UI & Feature Gates (5-7h)
- [ ] Add "Upgrade to Premium" button in Settings
- [ ] Create paywall modal with feature comparison table
- [ ] Add Sparks balance widget in top bar (shows current balance)
- [ ] Create "Get Sparks" modal with pack options
- [ ] Implement feature gate checks before premium actions:
  - Unlimited swipes: Check `isPremium` before showing next candidate
  - See Likes: Check `isPremium` before showing `LikesScreen`
  - Boost: Check `sparksBalance >= 2` before allowing boost
- [ ] Add 402 Payment Required handling (show upgrade modal)
- [ ] Cache subscription status locally (auto-refresh every 24h)

**Evidence:**
- Free user sees "Upgrade" prompt when tapping "See Likes"
- Premium user has unlimited swipes (no daily limit message)
- Sparks balance updates immediately after purchase

---

### Phase 11.3: Virtual Currency & Premium Features (25-30h)

#### Week 3-4: Currency Wallet System (10-12h)
- [ ] Create `VirtualCurrency` table migration (Balance, TotalPurchased, TotalSpent)
- [ ] Grant 3 free Sparks on user registration (welcome bonus)
- [ ] Create `Commands/GrantCurrencyCommand.cs` (for purchases)
- [ ] Create `Commands/SpendCurrencyCommand.cs` (for feature usage)
- [ ] Implement transaction logging in `CurrencyTransactions` table
- [ ] Add idempotency key support (prevent double-spend if retry)
- [ ] Create `GET /api/billing/currency/balance` endpoint
- [ ] Create `POST /api/billing/currency/spend` endpoint
- [ ] Unit tests: Spend with sufficient balance, reject if insufficient

**Evidence:**
- New user has 3 Sparks in wallet
- After buying 10 Sparks, balance = 13
- Spending 2 Sparks updates balance to 11

---

#### Week 4: Premium Feature #1 - "See Who Liked You" (8-10h)
- [ ] Add `GET /api/swipes/incoming-likes` endpoint in SwipeService
- [ ] Filter by `WHERE swipe_direction='right' AND target_user_id=?`
- [ ] Add `[RequiresPremium]` attribute to endpoint
- [ ] Create middleware: Check subscription status via BillingService HTTP client
- [ ] Return 402 if free user, include `blurredCount` and upgrade URL
- [ ] Flutter: Create `LikesScreen` with grid of profile cards
- [ ] Free users see blurred photos + "47 likes" count + upgrade button
- [ ] Premium users see full profiles with "Like Back" / "Pass" buttons

**Evidence:**
- Premium user sees who liked them (unblurred)
- Free user sees count + blurred previews + paywall
- Tapping "Like Back" creates a match

---

#### Week 4: Premium Feature #2 - Unlimited Swipes (5-6h)
- [ ] Add daily swipe counter to `UserProfiles` table or Redis
- [ ] Increment counter on each swipe (POST `/api/swipes`)
- [ ] Check counter before returning candidates:
  - Free: Return 402 if count >= 100
  - Premium: Skip counter check
- [ ] Reset counter daily (background job at midnight UTC)
- [ ] Flutter: Show "X/100 swipes today" for free users
- [ ] When limit reached, show upgrade modal

**Evidence:**
- Free user hits limit after 100 swipes
- Premium user can swipe >1000 times (no limit)
- Counter resets at midnight

---

#### Week 4: Premium Feature #3 - Boost (5-7h)
- [ ] Add `BoostExpiresAt` field to `UserProfiles` table
- [ ] Create `POST /api/matchmaking/boost` endpoint (costs 2 Sparks)
- [ ] Check Spark balance, deduct 2 if sufficient
- [ ] Set `BoostExpiresAt = Now + 30 minutes`
- [ ] Update matchmaking candidate query: Boosted users get +1000 priority score
- [ ] Create background job: Clear expired boosts (runs every 5 min)
- [ ] Flutter: Add "Boost" button in discovery screen
- [ ] Show countdown timer: "Boost active for 27:35"

**Evidence:**
- Spending 2 Sparks activates Boost for 30 minutes
- User appears first in other users' candidate queues
- Timer shows remaining boost time

---

### Phase 11.4: Webhooks & Subscription Lifecycle (15-20h)

#### Week 4-5: Apple App Store Server Notifications (8-10h)
- [ ] Create `POST /api/billing/webhooks/appstore` endpoint
- [ ] Implement signature verification (decode JWT, verify with Apple's public key)
- [ ] Handle notification types:
  - `INITIAL_BUY`: New subscription (already handled by `/validate`)
  - `DID_RENEW`: Extend expiry date by billing period
  - `DID_CHANGE_RENEWAL_STATUS`: User cancelled (set `AutoRenewing=false`)
  - `REFUND`: Revoke access immediately, set status to Refunded
  - `EXPIRED`: Mark subscription as expired
- [ ] Log all webhook events to `WebhookLogs` table (audit trail)
- [ ] Send email notifications for cancellations: "We're sorry to see you go"
- [ ] Test with App Store Sandbox notifications

**Evidence:**
- When user cancels in App Store, webhook updates DB within 5 minutes
- Refunded subscription immediately revokes Premium access
- Webhook logs show all events with timestamps

---

#### Week 5: Google Play Real-time Developer Notifications (7-10h)
- [ ] Set up Google Cloud Pub/Sub topic + subscription
- [ ] Configure Play Console to send notifications to Pub/Sub
- [ ] Create `POST /api/billing/webhooks/googleplay` endpoint
- [ ] Verify message signature (Google Cloud authentication)
- [ ] Decode base64 notification data
- [ ] Handle notification types (similar to Apple):
  - Type 2 `SUBSCRIPTION_RENEWED`: Extend expiry
  - Type 3 `SUBSCRIPTION_CANCELED`: Set non-renewing
  - Type 12 `SUBSCRIPTION_REFUNDED`: Revoke access
- [ ] Implement deduplication (check `messageId` to avoid double-processing)
- [ ] Test with Google Play test tracks

**Evidence:**
- When user cancels in Play Store, DB updates within 5 minutes
- Refund events revoke access immediately
- No duplicate processing of same webhook

---

### Phase 11.5: Security, Analytics & Polish (10-15h)

#### Week 5: Fraud Detection (6-8h)
- [ ] Implement velocity check: Flag >3 purchases in 24h
- [ ] Detect device sharing: Flag if >5 accounts on same device
- [ ] Track refund patterns: Flag users with 2+ refunds in 90 days
- [ ] Add geo-mismatch detection (IP country vs billing currency)
- [ ] Create `FraudScores` table with automated flagging
- [ ] Build admin dashboard: `/admin/fraud` (Razor Pages or React)
- [ ] Email alerts for high-risk transactions (>80 fraud score)
- [ ] Manual review workflow: Approve/Reject flagged purchases

**Evidence:**
- User making 5 purchases in 1 hour gets flagged
- Device with 8 Premium accounts triggers alert
- Admin dashboard shows flagged transactions

---

#### Week 5: Analytics & Metrics (4-5h)
- [ ] Add OpenTelemetry metrics:
  - `billing_purchases_total` (counter by product_id)
  - `billing_revenue_usd` (gauge, daily rolling sum)
  - `billing_subscription_churn_rate` (gauge, % cancellations)
  - `billing_fraud_detections_total` (counter)
- [ ] Create Grafana dashboard: Revenue, conversions, churn
- [ ] Track feature usage: Log when premium features are accessed
- [ ] A/B test tracking: Tag purchases with experiment ID (for future price testing)
- [ ] Create `/metrics` endpoint (Prometheus scraping)

**Evidence:**
- Grafana shows daily revenue chart
- Metrics show conversion funnel: Free → Spark buyer → Subscriber

---

#### Week 5: Documentation & Polish (2-4h)
- [ ] Update API documentation (Swagger/OpenAPI specs)
- [ ] Create runbook: "How to handle refund requests"
- [ ] Create runbook: "How to investigate fraud alerts"
- [ ] Add Terms of Service acceptance checkbox (required for subscriptions)
- [ ] Update Privacy Policy: Mention payment data handling
- [ ] Create FAQ: "How do I cancel?", "What happens if I cancel?", "Refund policy"
- [ ] Add customer support email: billing@datingapp.com
- [ ] Load testing: Simulate 1000 concurrent purchases

**Evidence:**
- API docs show all billing endpoints with examples
- Runbooks guide support team through common issues
- Load test confirms system handles Black Friday traffic

---

## Security Checklist

### Pre-Launch Requirements
- [ ] **Never trust client**: All feature gates check server-side subscription status
- [ ] **Receipt validation**: 100% of purchases validated with Apple/Google APIs
- [ ] **Secrets management**: Shared secrets, API keys stored in Azure Key Vault (not git)
- [ ] **HTTPS only**: All billing endpoints use TLS 1.2+ (no HTTP fallback)
- [ ] **Rate limiting**: 10 requests/minute per user on validation endpoints
- [ ] **Audit logging**: All purchases, validations, frauds logged to immutable table
- [ ] **Webhook security**: Verify signatures for Apple/Google webhooks (prevent spoofing)
- [ ] **Idempotency**: Duplicate receipts rejected (prevent double-granting)
- [ ] **PCI compliance**: Confirmed we never see/store credit card numbers
- [ ] **Refund handling**: Automated revocation when webhook receives refund event
- [ ] **Grace period**: 7-day grace period for failed renewals (App Store requirement)
- [ ] **Fraud detection**: Automated flagging for suspicious patterns (velocity, geo, refunds)

---

## Testing Strategy

### Unit Tests (40+ tests)
- Receipt validation logic (mock Apple/Google responses)
- Subscription status calculation (expired, active, cancelled)
- Currency wallet transactions (spend, grant, insufficient balance)
- Fraud detection rules (velocity, device sharing, geo-mismatch)
- Feature gate authorization (premium vs free user access)

### Integration Tests (20+ tests)
- End-to-end purchase flow (sandbox → Flutter → backend → DB)
- Webhook processing (refund, cancel, renewal events)
- Subscription expiry (check access revoked after expiry date)
- Cross-service feature gates (billing check in MatchmakingService)

### Manual Testing Checklist
- [ ] iOS sandbox purchase (monthly subscription)
- [ ] iOS sandbox purchase (annual subscription with 7-day trial)
- [ ] Android test track purchase (Google Play)
- [ ] Restore purchases after reinstalling app
- [ ] Cancel subscription in App Store → verify webhook fires
- [ ] Request refund in Play Store → verify access revoked
- [ ] Spark purchase (buy 10, verify balance = 13 with welcome bonus)
- [ ] Spend Sparks on Boost → verify countdown timer
- [ ] Free user hits swipe limit → verify paywall appears
- [ ] Premium user unlimited swipes → verify no limit
- [ ] Free user taps "See Likes" → verify blurred paywall
- [ ] Premium user sees likes → verify unblurred profiles
- [ ] Subscription expires → verify reverts to free tier
- [ ] Fraud scenario: 5 purchases in 10 minutes → verify flagged

---

## Compliance & Legal

### App Store Review Requirements
- [ ] **In-App Purchase Metadata**: All products configured in App Store Connect with descriptions, screenshots
- [ ] **Subscription Disclosure**: Terms clearly state auto-renewal, price, cancellation policy
- [ ] **Restore Purchases Button**: Visible in Settings (App Store requirement)
- [ ] **No External Payment Links**: Cannot mention "Cheaper on web" or link to Stripe
- [ ] **Privacy Nutrition Label**: Updated to include "Purchase History" data collection
- [ ] **Guideline 3.1.1 Compliance**: All digital goods use IAP (no cryptocurrency, no tips for profiles)

### Google Play Requirements
- [ ] **Subscription Details Page**: Clear description of billing, cancellation, refund policy
- [ ] **Free Trial Disclosure**: "Free for 7 days, then $19.99/month" (if offering trial)
- [ ] **Subscription Management**: Link to Google Play subscription settings
- [ ] **Content Rating**: Dating apps = "Mature 17+" (include in listing)

### Financial Regulations
- [ ] **Sales Tax**: Apple/Google collect tax (we receive net revenue)
- [ ] **Revenue Recognition**: Subscription revenue recognized monthly (not upfront)
- [ ] **Refund Reserve**: Set aside 2-3% of revenue for chargebacks (industry standard)

---

## Rollout Strategy

### Phase 1: Soft Launch (Week 1-2 post-implementation)
- Enable billing for 10% of users (A/B test)
- Monitor: Conversion rate, refund rate, fraud flags
- Gather feedback: "Was Premium worth it?" survey
- Pricing test: Half see $19.99, half see $24.99 (measure conversion)

### Phase 2: Full Launch (Week 3-4)
- Enable for 100% of users
- Press release: "DatingApp now offers Premium subscriptions"
- Email existing users: "Upgrade to Premium for 50% off (limited time)"
- Track metrics: Daily revenue, subscriber churn, Spark purchases

### Phase 3: Optimization (Month 2+)
- A/B test pricing: $14.99 vs $19.99 vs $24.99
- Test subscription tiers: Single Premium vs Bronze/Silver/Gold
- Optimize paywall copy: "Join 50,000 Premium members" vs "Unlimited swipes"
- Add scarcity: "24-hour sale - 40% off Premium!"

---

## Success Metrics

### Business Metrics
- **Target ARPPU**: $25-30/month (avg revenue per paying user)
- **Target Conversion**: 3-5% of free users → paying users (industry benchmark)
- **Target Churn**: <5% monthly churn (subscribers cancelling)
- **Target Refund Rate**: <2% (industry standard)

### Technical Metrics
- **Receipt Validation Latency**: <500ms p95
- **Webhook Processing Time**: <2 seconds (revoke access quickly)
- **Fraud Detection Accuracy**: <3% false positive rate
- **Payment Uptime**: 99.9% (Apple/Google reliability)

---

## Dependencies & Risks

### External Dependencies
- **Apple App Store Connect**: Product setup, shared secret generation
- **Google Play Console**: Product catalog, webhook configuration
- **Azure Key Vault**: Secret storage (or AWS Secrets Manager)
- **Email Service**: Subscription notifications (can reuse existing SMTP)

### Risks & Mitigations
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| App Store rejection (IAP implementation issue) | Medium | High | Follow guidelines strictly, test in sandbox, submit for review early |
| Fraud spike (stolen cards) | Low | Medium | Implement fraud detection before launch, monitor daily |
| Webhook downtime (Apple/Google outage) | Low | Low | Queue webhook processing with retry, manual reconciliation script |
| Conversion <1% (users unwilling to pay) | Medium | High | A/B test pricing, offer free trial, improve premium features |
| Chargeback abuse (users gaming refunds) | Low | Medium | Track refund patterns, ban repeat abusers |

---

## Next Steps After Phase 11

### Phase 12: Advanced Monetization (Future)
- SuperBoost (8 Sparks): Priority for 24 hours
- Profile Verification Badge ($29.99 one-time)
- See Who Viewed Your Profile (Premium+)
- Priority Likes (spend 1 Spark to move your like to front of their queue)
- Gifts (send virtual roses, 3 Sparks each)

### Phase 13: Referral Program
- Invite friend → Both get 5 free Sparks
- Refer paying user → Get 1 month free Premium

### Phase 14: Enterprise Features
- Group dating packages (split cost among friends)
- Event tickets (speed dating nights, 10 Sparks entry)
- Premium+ tier ($39.99/mo): Background checks, concierge service

---

**End of Monetization Architecture Document**
