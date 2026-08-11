# Monetization Use Cases & Pricing Security

## Use Cases (for emulator verification)

### UC1: Free user sees 0 Sparks
1. Login as `demo-user` (free tier, no entitlement)
2. Go to Profile Hub → "Get More" tab
3. **Expected**: Sparks card shows "0", no daily allocation
4. Tap Sparks card → bottom sheet shows "Free: 0 Sparks. Upgrade for 2 Sparks/day"
5. Tap "Get more Sparks" → navigates to SparksStoreScreen

### UC2: Majestic user gets 2 Sparks/day auto-allocated
1. Grant premium: `POST /api/billing/purchase {"sku": "premium_month"}` (sandbox)
2. Go to Profile Hub → "Get More" tab
3. **Expected**: Sparks card shows "2" (or whatever remaining after daily allocation)
4. Tap Sparks card → bottom sheet shows "Majestic: 2 Sparks per day included."

### UC3: Spend a Spark (ping on a profile)
1. Be a Majestic user with Sparks available
2. On a profile in the discover deck, tap "Spark" / "Send Ping"
3. **Expected**: POST `/api/billing/sparks/spend {"action": "spark_ping"}` returns success
4. Sparks count decrements by 1

### UC4: Free user purchases Sparks bundle
1. Login as `demo-user` (free)
2. Go to SparksStoreScreen (from Profile Hub → Upgrade → See plans)
3. Tap "Buy" on a Sparks bundle (e.g. "Starter Pack" 100 Sparks for $0.99)
4. **Expected**: POST `/api/billing/purchase {"sku": "sparks_100"}` → 200 OK
5. Sparks balance updates to 100

### UC5: Spend Sparks from purchased balance when daily exhausted
1. Majestic user who already used 2 daily Sparks
2. On a 3rd profile, tap "Spark"
3. **Expected**: POST `/api/billing/sparks/spend` deducts from purchased balance
4. Response shows `dailyRemaining=0, newBalance=X-1`

### UC6: Blocked when out of Sparks
1. User with 0 Sparks (free, no purchases)
2. Try to Spark a profile
3. **Expected**: POST `/api/billing/sparks/spend` returns 402
4. Flutter shows PaywallSheet → "Upgrade to Premium" → "See plans" → SparksStoreScreen

### UC7: Swipe limit gate for free users
1. Login as `demo-user` (free)
2. Swipe right 25 times on profiles in discover
3. **Expected**: 26th swipe returns 402 → Flutter shows paywall
4. After upgrading to premium, swiping is unlimited

### UC8: Catalog is publicly readable
1. `GET /api/billing/catalog` with no auth header
2. **Expected**: 200 OK with plans + bundles list
3. Prices visible (this is intentional — like any app store)

---

## Pricing Security Plan

### Current state
```
GET  /api/billing/catalog    → [AllowAnonymous]  ← public, intentional
POST /api/billing/purchase   → [Authorize]       ← JWT required
POST /api/billing/sparks/spend → [Authorize]     ← JWT required
```

The catalog is public — this is the same model as app stores (Apple/Google show prices without login). No security issue.

### Risk assessment

| Risk | Current | Mitigation |
|------|---------|-----------|
| Price manipulation | Catalog hardcoded in controller | Low risk — code changes require deployment |
| Unauthorized purchases | JWT-protected, sandbox only | Acceptable for dev. Real IAP needs App Store/Play receipt validation |
| Price oracle (competitor scraping) | Public catalog | Acceptable — all dating apps have public pricing |
| Admin price changes | No admin endpoint exists | Need to build (see below) |

### Recommended production approach

**Phase 1 (now):** Hardcoded catalog is fine for dev/demo.
**Phase 2 (future):** Move catalog to configurable source:

```
appsettings.json → BillingConfig
{
  "Billing": {
    "Plans": [
      { "Sku": "premium_month", "Name": "Premium Month", "DurationDays": 30, "PriceUsdCents": 999 }
    ],
    "SparksBundles": [
      { "Sku": "sparks_100", "Sparks": 100, "PriceUsdCents": 99 }
    ]
  }
}
```

**Phase 3 (production):** Admin-only API for live price changes:

```
GET    /api/admin/billing/catalog          → public (read-only)
PUT    /api/admin/billing/catalog/plans     → [Authorize(Roles="admin")] + internal API key
PUT    /api/admin/billing/catalog/bundles   → [Authorize(Roles="admin")] + internal API key
PATCH  /api/admin/billing/catalog/plans/{sku}/price → admin only
```

Protected by:
- Keycloak admin role (`Role="datingapp-admin"`)
- Internal API key header for service-to-service calls
- Audit logging on every price change
- Price history table for rollback

**Receipt validation (future):**
- Apple App Store: `verifyReceipt` server-to-server
- Google Play: `purchases.products.acknowledge` API
- Stubbed in sandbox (current behavior)

### Decision for now

✅ Keep catalog `[AllowAnonymous]` — it's an app store, prices are public.
✅ Keep purchase `[Authorize]` — only logged-in users can buy.
✅ Prices hardcoded — fine for dev. Move to config when deploying to staging/production.
❌ Don't build admin API yet — not needed until real payment processing is implemented.
