# DatingApp Tester Guide

## Quick Start

### 1. Install the APK

Download `app-release.apk` and install on your Android device:

```bash
adb install -r mobile-apps/flutter/dejtingapp/build/app/outputs/flutter-apk/app-release.apk
```

Or copy to phone's Downloads folder:
```bash
scp /home/m/development/mobile-apps/flutter/dejtingapp/build/app/outputs/flutter-apk/app-release.apk phone:/sdcard/Download/
```

### 2. Login

Open the app. **Tap "Continue with Phone Number"** and enter your real mobile number (international format, e.g. +46701234567).

1. You'll receive an SMS code from Firebase.
2. Enter the code to verify your phone.
3. The app will log you in automatically — no password needed!

> The app connects to `https://fastdev.tail45c6a7.ts.net` (my laptop via Tailscale Funnel). As long as my laptop is running, you're connected.

### 3. What to Test

| # | What | How |
|---|------|-----|
| 1 | **Browse profiles** | Swipe through the candidate deck. Profiles have photos, bios, interests |
| 2 | **Swipe** | Swipe right to like, left to pass. You'll see a "It's a Match!" notification |
| 3 | **Match & chat** | Open your matches list (heart icon), tap a match, send a message |
| 4 | **Profile** | Tap your profile icon (bottom right). Edit bio, view photos |
| 5 | **Compatibility** | On match cards, you'll see a compatibility badge. Tap it for details |
| 6 | **Block** | Tap ⋮ on a match → Block to test safety |

### 4. Send Feedback

A purple mic FAB floats on screen. Tap it to record a voice memo (or type text). This goes directly to the dev team.

### 5. Reset State

If things get weird (matches stop working), ask me to run an admin reset. It wipes all matches, messages, and swipes so you start fresh.

## Known Issues

- **Chat "Connecting..."** — SignalR hub takes a few seconds to connect on first open. Try sending a message; it'll work via REST fallback.
- **No GPS on emulator** — Location timeout error is cosmetic. Works fine on real phones.
- **Bot messages** — Some bot profiles may send messages. They're automated test accounts, not real people.

## What NOT to Test

- ❌ Creating a new account (the wizard is built but not the focus right now)
- ❌ Premium features (not implemented yet)
- ❌ Account recovery / forgot password

## Need Help?

Send feedback via the mic FAB in the app, or message me directly.
