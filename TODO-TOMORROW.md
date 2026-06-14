# TODO — Current State

**Updated**: 2026-06-14
**Active track**: Sparks Send/Receive + 3-Tab Matches Menu

---

## ✅ COMPLETED (Sessions 2026-06-12 to 2026-06-14)

### ✅ 5-Icon Bottom Navigation — SHIPPED
- Top Picks tab with spark mechanic screen
- Messages tab extracted from old matches screen
- Simplified Matches screen (no inner tabs)
- MainApp restructured from 3→5 tabs

### ✅ Sparks Store — SHIPPED
- Catalog renders plans + bundles with fallback data
- Sandbox purchase works (premium & spark bundles)
- `ElevatedButton`→`OutlinedButton` fix (black screen on emulator)
- Root navigator pattern for navigation
- Auto-navigate back after purchase (800ms delay)

### ✅ Debug Logging — SHIPPED
- Silent catch blocks in home_screen, top_picks_screen, profile_hub now log errors

### ✅ Backend Spark System — SHIPPED
- `SparkRecord` entity + EF migration
- `POST /api/billing/sparks/send` — deducts spark, creates record, optional message
- `GET /api/billing/sparks/received` — received sparks with sender info
- `GET /api/billing/sparks/sent` — sent spark history
- `POST /api/billing/sparks/{id}/read` — mark received spark as read
- CQRS handlers: SendSparkHandler, GetReceivedSparksHandler, GetSentSparksHandler

### ✅ Spark Sending with Optional Message — SHIPPED
- `_SparkMessageSheet` bottom sheet with 200-char optional message
- `sendSpark(recipientUserId, message)` → new backend endpoint
- Separates Cancel (null) vs Send without message (empty string)

### ✅ 3-Tab Matches Menu — SHIPPED
- Tab 1 **Matches** (favorite): mutual matches with avatar carousel
- Tab 2 **Sparks** (bolt): received sparks with sender info, message, unread dot
- Tab 3 **History** (history): sent likes via `GET /api/swipes/user/{userId}?isLike=true`
- Pull-to-refresh on all tabs, empty states, relative timestamps
- `SwipeService.getLikesHistory(profileId)` for history tab

### ✅ Type Safety — SHIPPED
- Fixed `json['tier'] as String?` crash in both `purchase()` and `EntitlementStatus.fromJson()`
- Handles int (enum 0/1) and string tier values

### ✅ Tests — SHIPPED
- **Flutter** (12 tests): EntitlementStatus.fromJson with int/string/missing tier, SparkReceived.fromJson, realistic API response parsing
- **Backend** (32 tests, 13 new): SendSparkHandler, GetReceivedSparksHandler, GetSentSparksHandler, controller response format (tier as int)

---

## 🔴 Security Audit Findings (2026-06-14)

### CRITICAL — Double-Spend Race Condition
- **File**: `EntitlementCommands.cs` `DebitSparksHandler`
- Two concurrent requests can both read balance +100 and each deduct 50 → BalanceAfter 50 (should be 0 or error)
- **No transaction isolation or optimistic locking**
- Affects ALL spark spending (send, spend, boost, rewind)
- **Fix**: Wrap debit in `BeginTransactionAsync()` or use `IsolationLevel.Serializable`

### HIGH — No Recipient Existence Validation
- **File**: `BillingController.cs` `SendSpark()` endpoint
- Can send sparks to non-existent user IDs
- Creates orphaned SparkRecord in database
- **Fix**: Check `UserProfiles.FindAsync(recipientUserId)` before deducting

### HIGH — No Rate Limiting on SendSpark
- **File**: `BillingController.cs`
- No per-second/per-minute rate limiting
- User with purchased sparks can spam indefinitely
- **Fix**: Add `[RateLimit("sparks-send:10/60")]` or integrate with YARP rate limiting

### MEDIUM — No MarkSparkRead Test
- **File**: `BillingTests.cs`
- Missing unit test for the mark-read endpoint

### MEDIUM — Sequential SparkRecord IDs
- Predictable auto-increment IDs (no actual security impact since records are filtered by userId)

---

## 📋 Remaining Work

### 🔴 CRITICAL — DebitSparksHandler Race Condition
- [ ] Wrap debit logic in database transaction
- [ ] Add integration test for concurrent spend

### 🟡 HIGH — Spark Send Missing Features
- [ ] Validate recipient existence before deducting spark
- [ ] Add rate limiting on SendSpark endpoint
- [ ] SignalR notification for received sparks (optional — for v2)
- [ ] Push notification for received sparks (optional — for v2)

### 🟡 COSMETIC / POLISH
- [ ] Top Picks backend endpoint (`_fetchTopPicksFromBackend` throws `UnimplementedError`)
- [ ] Real prices in catalog (priceSparks: 0 → real USD)
- [ ] Dashboard pricing table with real catalog data
- [ ] MarkSparkRead unit test

### 🟢 WORKS OK
- ✅ Full send/receive spark flow: Buy → Send → Recipient sees in Sparks tab
- ✅ Optional message with spark (200 char)  
- ✅ Cancel vs Send without message correctly distinguished
- ✅ 3-tab matches menu with pull-to-refresh
- ✅ Spark balance refresh chain (paywall, store return)
- ✅ Backend tests (32 passing) + Flutter tests (12 passing)

---

## Pre-Existing Follow-ups (not blocking)
- [ ] Audio retention policy — nightly job in bot-service
- [ ] Crash/error capture — attach log lines to voice feedback
- [ ] Persist Keycloak overrides in dev compose
- [ ] Hinge-style "Likes You" flow (separate feature)
