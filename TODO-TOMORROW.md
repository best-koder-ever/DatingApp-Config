# TODO — Current State

**Updated**: 2026-06-15
**Active track**: Profile Settings Overhaul — COMPLETE ✅

---

## ✅ COMPLETED (2026-06-15 session)

### Phase 1: Fix Broken Settings Persistence
- [x] Discovery prefs (age range, distance) now save to `PUT /api/userprofiles/{userId}/preferences`
- [x] "Show in discovery" toggle persists via `showMeInDiscovery`
- [x] Privacy display toggles (show age, show distance) persist via `PUT /api/userprofiles/{profileId}/privacy`
- [x] Notification preferences: new backend model + `GET/PUT /api/profiles/me/notifications` endpoints + Flutter wiring
- [x] Loading/error/optimistic states on settings screen

### Phase 2: Competitive Parity
- [x] Political views field (backend + Flutter dropdown in edit profile)
- [x] Pets field (backend + Flutter dropdown in edit profile)
- [x] Zodiac sign (auto-computed from DOB via `ZodiacHelper`, displays on profile detail)
- [x] Incognito mode toggle in privacy settings (wired to `isPrivate` field)
- [x] Message filter dropdown (Off/Disrespectful/AllOffensive) in privacy settings
- [x] Help/FAQ screen with 6 expandable questions
- [x] Dating tips dialog replaces "Coming Soon" placeholder

### Phase 3: Settings UX Polish
- [x] Settings reorganized into card-based sections (Discovery, Profile Display, Privacy & Safety, Notifications, Account, Support)
- [x] Profile Strength card at top — real % from backend, color-coded, with suggestions
- [x] Account pause quick-action — bottom sheet with duration options (24h/72h/1 week/Indefinite), wired to `POST /api/account/pause` + resume

### Profile Detail Display
- [x] New fields (political views, pets, zodiac) shown in lifestyle section

### Tests
- [x] Flutter: 3 widget tests for settings screen (scaffold, loading, accessibility)
- [x] Backend: 6 new unit tests (notification prefs CRUD + new profile fields)
- [x] All 277 backend tests pass, all Flutter tests pass
- [x] Full `flutter analyze` — 0 errors in changed files

---

## 📋 Remaining Polish (Minor/Deferred)

- [ ] Top Picks backend endpoint (`_fetchTopPicksFromBackend` throws `UnimplementedError`)
- [ ] Real prices in catalog (sandbox: `priceSparks: 0`)
- [ ] Dashboard pricing table from catalog API
- [ ] Push notifications for received sparks (needs FCM)
- [ ] Spotlight scheduling (date/time picker)
- [ ] Read receipts toggle
- [ ] Video clips

---

## Stability (2026-06-15)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Backend tests | ✅ 277/277 passing | All handlers + controllers + new tests |
| Flutter tests | ✅ 3/3 passing | Settings screen rendering |
| Flutter analyze | ✅ 0 errors | Changed files all clean |
| Settings persistence | ✅ Fixed | 6 formerly-broken toggles now wired |
| Missing fields | ✅ Added | political views, pets, zodiac |
| Missing features | ✅ Added | incognito, message filter, FAQ, dating tips |
| Settings UX | ✅ Improved | Card sections, profile strength, pause |
