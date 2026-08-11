#!/usr/bin/env python3
"""Reset interactions and seed mutual matches for the demo-user.

Usage:
    python3 scripts/reset-and-seed.py          # uses localhost defaults
    python3 scripts/reset-and-seed.py --host 192.168.1.103  # custom host

What it does:
1. Authenticates the demo-user via Keycloak ROPC
2. Calls admin reset endpoints on matchmaking, messaging, swipe services
3. Seeds mutual likes between demo-user and active bot profiles
4. Reports results
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

# ── Config ──────────────────────────────────────────────────────────────────
KEYCLOAK_REALM = "DatingApp"
KEYCLOAK_CLIENT = "dejtingapp-flutter"
DEMO_USERNAME = "bot_demo-user@bot.local"
DEMO_PASSWORD = "bot_pass_demo-user"

# Bot profiles that should like the demo-user (by profile ID from bot state)
BOT_PROFILES = [
    {"id": 2, "name": "maja"},
    {"id": 3, "name": "elsa"},
    {"id": 4, "name": "linnea"},
]
DEMO_PROFILE_ID = 1

# ── Helpers ─────────────────────────────────────────────────────────────────

def e(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def http(url, method="GET", data=None, token=None, timeout=15):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as ex:
        raw = ex.read().decode()
        try:
            return ex.code, json.loads(raw)
        except json.JSONDecodeError:
            return ex.code, raw
    except Exception as ex:
        return 0, str(ex)


def get_token(keycloak_url):
    """Get an access token for the demo-user via ROPC."""
    token_url = f"{keycloak_url}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = urllib.parse.urlencode({
        "grant_type": "password",
        "client_id": KEYCLOAK_CLIENT,
        "username": DEMO_USERNAME,
        "password": DEMO_PASSWORD,
        "scope": "openid profile email",
    }).encode()
    req = urllib.request.Request(
        token_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode())
            token = body.get("access_token")
            if not token:
                e(f"ROPC response missing access_token: {body}")
            print(f"  ✅ Got access token (expires in {body.get('expires_in', '?')}s)")
            return token
    except urllib.error.HTTPError as ex:
        raw = ex.read().decode()
        e(f"ROPC failed ({ex.code}): {raw}")
    except Exception as ex:
        e(f"ROPC error: {ex}")


def call_admin_reset(host, token):
    """Call admin reset endpoints on each service."""
    targets = [
        ("matchmaking", f"http://{host}:8083/api/admin/matches"),
        ("messaging", f"http://{host}:8086/api/admin/messages"),
        ("swipe", f"http://{host}:8087/api/admin/swipes"),
    ]
    all_ok = True
    for name, url in targets:
        status, body = http(url, method="DELETE", token=token)
        ok = status in (200, 204)
        icon = "✅" if ok else "⚠️"
        print(f"  {icon} {name} ({status}): {body if isinstance(body, str) else json.dumps(body, indent=2)[:200]}")
        if not ok:
            all_ok = False
    return all_ok


def seed_mutual_likes(host, token):
    """Seed mutual likes between demo-user and bot profiles via batch swipe endpoint."""
    print(f"\n  📋 Seeding mutual likes: demo-user({DEMO_PROFILE_ID}) ↔ bots...")

    # Demo-user likes all bots (uses JWT auth on single-swipe endpoint)
    for bot in BOT_PROFILES:
        swipe_data = {
            "targetUserId": str(bot["id"]),
            "direction": "like",
        }
        status, body = http(
            f"http://{host}:8087/api/swipes",
            method="POST",
            data=swipe_data,
            token=token,
        )
        ok = status in (200, 201)
        icon = "✅" if ok else "⚠️"
        detail = body.get("data", {}).get("message", str(body)) if isinstance(body, dict) else str(body)
        print(f"    {icon} demo-user → {bot['name']}({bot['id']}): [{status}] {detail[:120]}")

    # Now bots like demo-user — we need tokens for each bot
    print(f"\n  📋 Bots liking demo-user...")
    for bot in BOT_PROFILES:
        bot_username = f"bot_{bot['name']}@bot.local"
        bot_password = f"bot_pass_{bot['name']}"
        bot_token = get_token_for_bot(host, bot_username, bot_password)
        if not bot_token:
            print(f"    ⚠️  Could not get token for {bot['name']}, skipping...")
            continue

        swipe_data = {
            "targetUserId": str(DEMO_PROFILE_ID),
            "direction": "like",
        }
        status, body = http(
            f"http://{host}:8087/api/swipes",
            method="POST",
            data=swipe_data,
            token=bot_token,
        )
        ok = status in (200, 201)
        icon = "✅" if ok else "⚠️"
        detail = body.get("data", {}).get("message", str(body)) if isinstance(body, dict) else str(body)
        print(f"    {icon} {bot['name']}({bot['id']}) → demo-user: [{status}] {detail[:120]}")

    print()
    return True


def get_token_for_bot(host, username, password):
    """Get token for a bot user via ROPC."""
    token_url = f"http://{host}:8090/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = urllib.parse.urlencode({
        "grant_type": "password",
        "client_id": KEYCLOAK_CLIENT,
        "username": username,
        "password": password,
        "scope": "openid profile email",
    }).encode()
    req = urllib.request.Request(
        token_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
            return body.get("access_token")
    except Exception:
        return None


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Reset and seed demo data")
    parser.add_argument("--host", default="localhost",
                        help="Backend host (default: localhost)")
    parser.add_argument("--keycloak-port", default=8090, type=int,
                        help="Keycloak port (default: 8090)")
    args = parser.parse_args()

    host = args.host
    kc_url = f"http://{args.host}:{args.keycloak_port}"
    gateway_url = f"http://{host}:8080"

    print(f"\n🔧 Reset & Seed Demo Environment")
    print(f"   Host:     {host}")
    print(f"   Keycloak: {kc_url}")
    print(f"   Gateway:  {gateway_url}")
    print()

    # 1. Get token
    print("🔑 Getting auth token...")
    token = get_token(kc_url)

    # 2. Reset interactions
    print("\n🗑️  Resetting interactions...")
    call_admin_reset(host, token)

    # Small pause for DB consistency
    time.sleep(1)

    # 3. Seed mutual likes
    print("❤️  Seeding mutual likes...")
    seed_mutual_likes(host, token)

    print("✅ Done! Demo-user should now have matches to swipe on.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
