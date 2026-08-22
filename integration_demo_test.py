#!/usr/bin/env python3
"""Integration test for Tester Demo Mode — bots as realistic fake users.

Verifies, end-to-end, that a real human tester:
  1. sees bot profiles in their discover feed,
  2. swipes right on a bot → the bot like-backs (reactive-only),
  3. a match is created,
  4. the bot sends an opener,
  5. the targeted bot-data purge endpoints work.

Requires the full stack up (infra + dev-start).
Run:  .venv/bin/python integration_demo_test.py
"""
from __future__ import annotations

import json
import sys
import time
import uuid
from datetime import datetime, timedelta

import httpx

KEYCLOAK = "http://localhost:8090"
REALM = "DatingApp"
ADMIN_USER, ADMIN_PASS = "admin", "admin"
CLIENT_ID = "dejtingapp-flutter"
SCOPES = "openid profile email"
DEMO_PASSWORD = "DemoTest!123"

USER_SVC = "http://localhost:8082"
SWIPE_SVC = "http://localhost:8087"
MATCH_SVC = "http://localhost:8083"
MSG_SVC = "http://localhost:8086"
GATEWAY = "http://localhost:8080"

PASS, FAIL = 0, 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def admin_token() -> str:
    r = httpx.post(
        f"{KEYCLOAK}/realms/master/protocol/openid-connect/token",
        data={"grant_type": "password", "client_id": "admin-cli",
              "username": ADMIN_USER, "password": ADMIN_PASS},
        timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]


def provision_human(token: str) -> dict:
    """Create a real human tester. Keycloak quirks handled:
    - username is normalized to the email,
    - VERIFY_EMAIL is force-added — must be cleared with a GET+full-PUT,
    - REST reset-password returns 204 but does nothing — password must be set
      via kcadm.sh inside the container.
    """
    import subprocess
    suffix = uuid.uuid4().hex[:8]
    username = f"demo_human_{suffix}".lower()
    email = f"{username}@demo.local"
    payload = {
        "username": username, "email": email, "firstName": "Testa",
        "lastName": "Human", "enabled": True, "emailVerified": True,
        "requiredActions": [], "realmRoles": ["user"],
    }
    h = {"Authorization": f"Bearer {token}"}
    r = httpx.post(f"{KEYCLOAK}/admin/realms/{REALM}/users", json=payload, headers=h, timeout=15)
    if r.status_code == 409:
        users = httpx.get(f"{KEYCLOAK}/admin/realms/{REALM}/users",
                          params={"username": username}, headers=h, timeout=15).json()
        kc_id = users[0]["id"]
    else:
        r.raise_for_status()
        kc_id = r.headers["Location"].rsplit("/", 1)[-1]
    # GET full user -> force emailVerified + clear requiredActions -> full PUT
    u = httpx.get(f"{KEYCLOAK}/admin/realms/{REALM}/users/{kc_id}", headers=h, timeout=15).json()
    u["emailVerified"] = True
    u["requiredActions"] = []
    httpx.put(f"{KEYCLOAK}/admin/realms/{REALM}/users/{kc_id}", json=u, headers=h, timeout=15)
    # set password via kcadm (email is the stored username; internal url is 8080)
    cmd = ["docker", "exec", "keycloak", "/opt/keycloak/bin/kcadm.sh", "set-password",
           "-r", REALM, "--username", email, "--new-password", DEMO_PASSWORD,
           "--server", "http://localhost:8080", "--realm", "master",
           "--user", "admin", "--password", "admin"]
    subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    return {"username": username, "email": email, "keycloakId": kc_id}


def human_token(username: str) -> str:
    """Log in using the email (Keycloak normalizes the username to the email)."""
    r = httpx.post(
        f"{KEYCLOAK}/realms/{REALM}/protocol/openid-connect/token",
        data={"grant_type": "password", "client_id": CLIENT_ID,
              "username": username, "password": DEMO_PASSWORD, "scope": SCOPES},
        timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]


def create_profile(tok: str, email: str) -> int:
    birth = (datetime.utcnow() - timedelta(days=26 * 365)).isoformat() + "Z"
    payload = {
        "name": "Testa Human", "email": email,
        "bio": "Integration test human.",
        "gender": "Female", "preferences": "Male", "dateOfBirth": birth,
        "city": "Stockholm", "state": "Stockholm County", "country": "Sweden",
        "latitude": 59.3293, "longitude": 18.0686, "occupation": "Tester",
        "education": "University", "interests": ["Hiking", "Music", "Food"],
        "languages": ["Swedish", "English"], "height": 168,
        "smokingStatus": "Never", "drinkingStatus": "Socially",
        "wantsChildren": True, "hasChildren": False, "relationshipType": "Long-term relationship",
    }
    r = httpx.post(f"{USER_SVC}/api/UserProfiles", json=payload,
                   headers={"Authorization": f"Bearer {tok}"}, timeout=15)
    if r.status_code >= 400:
        raise RuntimeError(f"Profile create failed: {r.status_code} {r.text}")
    # parse profile id from Location or body
    loc = r.headers.get("Location", "")
    try:
        return int(loc.rstrip("/").rsplit("/", 1)[-1])
    except ValueError:
        body = r.json()
        data = body.get("data") or body.get("value") or body
        return int(data.get("id", 0))


def candidates(pid: int, tok: str) -> list:
    r = httpx.get(f"{MATCH_SVC}/api/Matchmaking/profiles/{pid}",
                  headers={"Authorization": f"Bearer {tok}"}, timeout=15)
    if r.status_code >= 400:
        return []
    body = r.json()
    if isinstance(body, list):
        return body
    return body.get("data") or body.get("results") or []


def swipe(pid: int, target_pid: int, tok: str, direction: str = "like") -> dict:
    r = httpx.post(f"{SWIPE_SVC}/api/Swipes",
                   json={"targetUserId": str(target_pid), "direction": direction},
                   headers={"Authorization": f"Bearer {tok}"}, timeout=15)
    return {"status": r.status_code, "body": r.text}


def matches(pid: int, tok: str) -> list:
    r = httpx.get(f"{SWIPE_SVC}/api/Swipes/matches/{pid}",
                  headers={"Authorization": f"Bearer {tok}"}, timeout=15)
    body = r.json()
    if isinstance(body, list):
        return body
    return body.get("data") or []


def bot_token(persona: str) -> str:
    r = httpx.post(
        f"{KEYCLOAK}/realms/{REALM}/protocol/openid-connect/token",
        data={"grant_type": "password", "client_id": CLIENT_ID,
              "username": f"bot_{persona}@bot.local", "password": "BotPass123!",
              "scope": SCOPES}, timeout=15)
    if r.status_code >= 400:
        return ""
    return r.json().get("access_token", "")


def main() -> None:
    print("== Tester Demo Mode integration test ==")
    tok = admin_token()

    print("\n[1] Provision real human tester")
    human = provision_human(tok)
    check("Keycloak user created", bool(human["keycloakId"]), human["keycloakId"])
    ht = human_token(human["email"])
    check("Human token issued", bool(ht))
    human_pid = create_profile(ht, human["email"])
    check("Human profile created", human_pid > 0, f"profileId={human_pid}")

    print("\n[2] Discover feed shows bots")
    feed = candidates(human_pid, ht)
    check("Feed not empty", len(feed) > 0, f"count={len(feed)}")
    # Prefer an ACTIVE bot (skip demo-user profile 1 — the paused human test account).
    active_bot_pids = set()
    try:
        bstatus = httpx.get("http://localhost:8089/api/Bot/status", timeout=10).json()
        active_bot_pids = {b["profileId"] for b in bstatus["bots"]
                           if b.get("status") == "Active" and b.get("profileId")}
    except Exception as e:
        print(f"  (bot-service status unavailable: {e})")
    bot_candidate = None
    for c in feed:
        cid = int(c.get("id") or c.get("userId") or 0)
        if cid == 1:  # demo-user
            continue
        if c.get("isBot") is True or (active_bot_pids and cid in active_bot_pids):
            bot_candidate = c
            break
    check("Feed contains an active bot profile", bot_candidate is not None,
          f"feed_count={len(feed)} active_bots={len(active_bot_pids)}")

    if bot_candidate is None:
        print("\n⚠️  No active bot in feed — cannot test like-back. Dumping first 3 candidates:")
        for c in feed[:3]:
            print("   ", json.dumps(c)[:200])
        sys.exit(1 if FAIL else 0)

    bot_pid = int(bot_candidate.get("id") or bot_candidate.get("userId") or 0)
    check("Bot candidate has id", bot_pid > 0, f"botProfileId={bot_pid}")

    print("\n[3] Human swipes right on bot → bot like-backs (reactive-only)")
    sw = swipe(human_pid, bot_pid, ht, "like")
    check("Swipe accepted", sw["status"] < 400, f"status={sw['status']} {sw['body'][:120]}")
    mutual = "isMutualMatch" in sw["body"] and '"isMutualMatch":true' in sw["body"]
    # If the bot already liked the human (e.g., onboarding), this may be an instant match.
    # Otherwise the bot's like-back cycle creates the match within ~30s.
    print("   (waiting for bot like-back / match...)")
    matched = None
    for i in range(20):
        time.sleep(3)
        m = matches(human_pid, ht)
        if m:
            matched = m[0]
            break
    check("Match created via like-back", matched is not None,
          f"matches={len(matches(human_pid, ht))}")

    if matched is None:
        sys.exit(1 if FAIL else 0)

    print("\n[4] Bot sends an opener (turn-taking)")
    # bot sends the FIRST message after the match; poll the conversation
    # match keycloakId for the bot is resolved from match response
    other_kc = matched.get("keycloakUserId") or matched.get("matchedUserId")
    opener_seen = False
    conv = []
    for i in range(20):
        time.sleep(3)
        try:
            r = httpx.get(f"{MSG_SVC}/api/Messages/conversation/{other_kc}",
                          headers={"Authorization": f"Bearer {ht}"}, timeout=10)
            if r.status_code < 400:
                body = r.json()
                conv = body.get("data") if isinstance(body, dict) else body
                if isinstance(conv, list) and len(conv) > 0:
                    opener_seen = True
                    break
        except Exception:
            pass
    check("Bot sent an opener message", opener_seen, f"conv_msgs={len(conv) if isinstance(conv, list) else '?'}")
    if opener_seen and isinstance(conv, list) and conv:
        print(f"   opener: {str(conv[0].get('content'))[:80]}")

    print("\n[5] Targeted bot-data purge endpoints")
    for name, url, method in [
        ("swipe bot-swipe-data", f"{SWIPE_SVC}/api/admin/bot-swipe-data?olderThanHours=0", "DELETE"),
        ("messaging bot-messages", f"{MSG_SVC}/api/admin/bot-messages?olderThanHours=0", "DELETE"),
        ("matchmaking bot-match-data", f"{MATCH_SVC}/api/admin/bot-match-data?olderThanHours=0", "DELETE"),
        ("gateway composite", f"{GATEWAY}/api/admin/reset-bot-interactions", "POST"),
    ]:
        try:
            r = httpx.request(method, url, headers={"Authorization": f"Bearer {ht}"}, timeout=20)
            check(f"{name} -> {r.status_code}", r.status_code < 400, r.text[:140])
        except Exception as e:
            check(f"{name} -> exception", False, str(e))

    print("\n== Summary ==")
    print(f"  PASS: {PASS}   FAIL: {FAIL}")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()
