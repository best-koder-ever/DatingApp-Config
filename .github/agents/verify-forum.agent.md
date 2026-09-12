---
name: verify-forum
description: "Verify the anonymous Community forum end-to-end: unit tests → contract drift → live smoke through the gateway → Flutter client tests. Run after any forum change, before opening a forum PR."
---

# Forum Verifier

Run these in order and report a pass/fail table. Stop at the first hard failure and report it
rather than continuing — later steps depend on earlier ones.

**Scope**: `forum-service` (:8092), the YARP route, and the Flutter Community tab.
**Repos touched**: `forum-service`, `dejting-yarp`, `dejtingapp`, `DatingApp` (root).

## Step 1 — Backend unit tests

```bash
cd forum-service
dotnet test ForumService.Tests/ForumService.Tests.csproj --nologo
```
**Expected**: all pass (67 as of 2026-09-12). Report the exact count — a falling count means
tests were deleted, not that the change is smaller.

## Step 2 — Contract drift (no services needed)

```bash
cd ..
bash scripts/check-forum-contract.sh
```
**Expected**: `Contract is consistent.` across the topic fields, answer fields and the text
limit.

If it fails, the Dart client and the API have diverged. **Do not "fix" this by editing the
checker** — that check exists because the contract drifted twice, once in each direction.
Report which field or limit drifted and which side changed.

## Step 3 — Services up

```bash
./dev-start.sh          # or confirm :8092 and :8080 are already answering
curl -s localhost:8092/health
curl -s -o /dev/null -w '%{http_code}\n' localhost:8080/health
```
**Expected**: `{"status":"healthy",...,"database":"up"}` and `200`.

A 502 on `/api/forum/**` almost always means forum-service was not started — `dev-start.sh`
launches it.

## Step 4 — Live contract smoke through the gateway

```bash
bash scripts/forum-smoke.sh
```
**Expected**: `failed 0` and exit 0. `skipped` lines are fine and mean the per-day topic cap
was already reached; the script prints the exact reset command.

Read the skip count. Silently skipping the whole lifecycle on every run would hide a real
regression, so if everything is skipped, reset the quota and run once more.

## Step 5 — Python API scenario

```bash
python3 api_tests.py --forum
```
**Expected**: `Forum scenario succeeded`.

## Step 6 — Flutter client

```bash
cd mobile-apps/flutter/dejtingapp    # note: a sibling workspace root, not under DatingApp
flutter analyze lib test
flutter test test/services/forum_service_test.dart test/screens/forum_feed_screen_test.dart
```
**Expected**: 0 errors from analyze (warnings and infos are pre-existing and unrelated), and
30 tests passing.

## Step 7 — Anonymity assertion (the one that must never regress)

```bash
TOKEN=$(curl -s -X POST localhost:8090/realms/DatingApp/protocol/openid-connect/token \
  -d grant_type=password -d client_id=dejtingapp-flutter \
  -d username=bot_demo-user@bot.local -d password=bot_pass_demo-user \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

for path in /api/forum/topics "/api/forum/topics/1" "/api/forum/topics/1/answers"; do
  echo "== $path"
  curl -s -H "Authorization: Bearer $TOKEN" "localhost:8080$path" \
    | grep -oiE 'keycloakId|authorId|"sub"' || echo "clean"
done
```
**Expected**: `clean` for every path. Any hit is a critical failure — the forum must expose
only `colorHex` + `pseudonym` + `isOwn`.

## Step 8 — AI abuse probes (optional, needs the stack up)

```bash
curl -s -X POST localhost:8093/api/tester/security/run  | head -50
curl -s -X POST localhost:8093/api/tester/abuse/run     | head -50
```
**Expected**: no `Critical` finding mentioning `/api/forum`. A 429 from the forum is expected
here, not a finding — these agents run repeatedly and legitimately hit the daily cap.

## Report

| Step | Result | Evidence |
|---|---|---|
| 1 unit tests | | pass count |
| 2 contract | | checker output |
| 3 services | | health bodies |
| 4 smoke | | passed/failed/skipped |
| 5 api_tests | | scenario result |
| 6 flutter | | analyze + test counts |
| 7 anonymity | | clean / leak |
| 8 AI probes | | finding count |

State clearly whether anything was **skipped**, and why. A green report that skipped the
lifecycle is not a green report.
