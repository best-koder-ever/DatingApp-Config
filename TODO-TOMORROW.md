# TODO — Current State

**Updated**: 2026-06-12
**Active track**: 5-icon bottom navigation + Sparks Store

---

## 🟢 What's Done Today (2026-06-12)

### ✅ 5-Icon Bottom Navigation — SHIPPED
- Top Picks tab with spark mechanic screen
- Messages tab extracted from old matches screen
- Simplified Matches screen (no inner tabs)
- MainApp restructured from 3→5 tabs

### ✅ Sparks Store — SHIPPED (with fixes)
- Screen renders catalog with hardcoded fallback data (never blank)
- Premium Plans + Sparks Bundles visible
- Purchase buttons functional (sandbox)
- **Fix**: `ElevatedButton` → `OutlinedButton` (ElevatedButton caused black screen on emulator)
- **Fix**: `Navigator.pop(context)` → root navigator (stale context fix)
- **Fix**: `dev_auto_login` preserves existing session (was clearing and breaking auth)

### ✅ Dashboard — SHIPPED
- ⚡ Start/Stop Lightweight buttons in Stack tab
- Starts: infra + YARP + UserService + Matchmaking + Messaging + Swipe
- Saves ~40% RAM vs full stack

---

## 📋 Sparks Store / Billing — Remaining Work

### 🔴 NEEDS FIX — Spark deduction from discover screen
- [ ] **Top Picks "Connect with ⚡"** — button only shows snackbar, doesn't hit `BillingService.spendSpark()` or navigate to chat/profile. Wire to backend spark deduction endpoint.
- [ ] **Discover screen spark button** — when user has 0 sparks, shows PaywallSheet → "Upgrade" → SparksStoreScreen (navigates but sparks/entitlement doesn't refresh after purchase). Need `setState` or callback to reload spark balance when returning from store.
- [ ] **Get Sparks button in Top Picks** — `_showNoSparksDialog()` has "Get Sparks" button that just closes the dialog. Needs to navigate to SparksStoreScreen.

### 🟡 COSMETIC / POLISH
- [ ] **Plans have prices** — premium plans show `priceSparks: 0` in catalog (sandbox). For production, add real prices to `PremiumPlanSku`.
- [ ] **Bundle prices not visible in backend** — prices are in `priceUsdCents` but dashboard pricing table shows "—" for all plans (they have `price: "—"` hardcoded). Update dashboard to fetch from catalog API.
- [ ] **Purchase spinner** — loading spinner shows during purchase but doesn't auto-refresh the screen or navigate back after purchase completes.
- [ ] **Top Picks backend** — Flutter `_fetchTopPicksFromBackend()` throws `UnimplementedError`. Wire to `GET api/matchmaking/top-picks` once deployed.

### 🟢 WORKS OK
- ✅ Sparks Store shows all 6 items (3 plans + 3 bundles) with buttons and prices
- ✅ Purchase buttons call `BillingService.purchase(sku)` successfully (sandbox)
- ✅ Spark balance displays in Top Picks AppBar (from `EntitlementStatus`)
- ✅ Dashboard "Grant Free Sparks" works via Billing tab
- ✅ Dashboard billing stats show from `GET api/billing/admin/stats`
- ✅ Dashboard pricing catalog table shows hardcoded SKUs

---

## Pre-Existing Follow-ups (not blocking)
- [ ] Audio retention policy — nightly job in bot-service
- [ ] Crash/error capture — attach log lines to voice feedback
- [ ] Persist Keycloak overrides in dev compose
- [ ] Hinge-style "Likes You" flow (separate feature)
