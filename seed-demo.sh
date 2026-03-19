#!/bin/bash
# seed-demo.sh — Create permanent demo user + 10 bot profiles for manual testing
# Usage: ./seed-demo.sh
# After running: login on device with  demo / demo123
set -e

KC_URL="http://localhost:8090"
YARP_URL="http://localhost:8080"
REALM="DatingApp"
CLIENT_ID="dejtingapp-flutter"

command -v python3 >/dev/null || { echo "❌ python3 required"; exit 1; }
command -v curl >/dev/null || { echo "❌ curl required"; exit 1; }

python3 - << 'PYEOF'
import requests, json, sys

KC = "http://localhost:8090"
YARP = "http://localhost:8080"
REALM = "DatingApp"
CLIENT = "dejtingapp-flutter"

def get_admin_token():
    r = requests.post(f"{KC}/realms/master/protocol/openid-connect/token",
        data={"grant_type":"password","client_id":"admin-cli","username":"admin","password":"admin"})
    r.raise_for_status()
    return r.json()["access_token"]

def create_kc_user(admin_token, username, password, first, last, email):
    """Create Keycloak user + set password. Returns user UUID."""
    r = requests.post(f"{KC}/admin/realms/{REALM}/users",
        json={"username":username,"email":email,"firstName":first,"lastName":last,"enabled":True,"emailVerified":True},
        headers={"Authorization":f"Bearer {admin_token}","Content-Type":"application/json"})
    if r.status_code not in (201, 409):
        print(f"  ❌ Failed to create {username}: {r.status_code} {r.text[:100]}")
        return None
    # Get user ID
    r2 = requests.get(f"{KC}/admin/realms/{REALM}/users?username={username}&exact=true",
        headers={"Authorization":f"Bearer {admin_token}"})
    users = r2.json()
    if not users:
        print(f"  ❌ User {username} not found after creation")
        return None
    uid = users[0]["id"]
    # Set password
    requests.put(f"{KC}/admin/realms/{REALM}/users/{uid}/reset-password",
        json={"type":"password","value":password,"temporary":False},
        headers={"Authorization":f"Bearer {admin_token}","Content-Type":"application/json"})
    return uid

def get_user_token(username, password):
    r = requests.post(f"{KC}/realms/{REALM}/protocol/openid-connect/token",
        data={"grant_type":"password","client_id":CLIENT,"username":username,"password":password,"scope":"openid profile email"})
    r.raise_for_status()
    return r.json()["access_token"]

def onboard_wizard(token, first, gender, pref, bio, dob):
    """Run wizard steps 1-3 to create a Ready profile."""
    h = {"Authorization":f"Bearer {token}","Content-Type":"application/json"}
    r1 = requests.patch(f"{YARP}/api/wizard/step/1", json={"firstName":first,"lastName":"","dateOfBirth":dob,"gender":gender}, headers=h)
    r2 = requests.patch(f"{YARP}/api/wizard/step/2", json={"minAge":20,"maxAge":40,"maxDistance":100,"preferredGender":pref,"bio":bio}, headers=h)
    r3 = requests.patch(f"{YARP}/api/wizard/step/3", json={"photoUrls":[f"https://picsum.photos/seed/{first}/400/600"]}, headers=h)
    if r3.ok:
        data = r3.json().get("data",{})
        return data.get("id"), data.get("onboardingStatus")
    return None, None

USERS = [
    # (username, password, firstName, gender, preferredGender, bio, dob, isBot)
    ("demo", "demo123", "Demo", "Male", "Female", "Your permanent test account 🎯", "1995-03-15", False),
    ("bot_maja", "bot_pass_maja", "Maja", "Female", "Male", "Älskar fika och långpromenader ☕🌲", "1997-08-22", True),
    ("bot_elsa", "bot_pass_elsa", "Elsa", "Female", "Male", "Konstnär och hundmänniska 🎨🐕", "1996-04-10", True),
    ("bot_wilma", "bot_pass_wilma", "Wilma", "Female", "Male", "Yoganörd och matlagning 🧘‍♀️🍳", "1998-11-03", True),
    ("bot_linnea", "bot_pass_linnea", "Linnea", "Female", "Male", "Bokmal och vinprovning 📚🍷", "1995-07-19", True),
    ("bot_saga", "bot_pass_saga", "Saga", "Female", "Male", "Resenär och fotograf 📸✈️", "1999-02-14", True),
    ("bot_astrid", "bot_pass_astrid", "Astrid", "Female", "Male", "Sjukgymnast och löpare 🏃‍♀️", "1994-09-28", True),
    ("bot_oscar", "bot_pass_oscar", "Oscar", "Male", "Female", "Musikproducent och kattälskare 🎵🐈", "1996-01-12", True),
    ("bot_axel", "bot_pass_axel", "Axel", "Male", "Female", "Kodare och klättrare 💻🧗", "1997-05-30", True),
    ("bot_noah", "bot_pass_noah", "Noah", "Male", "Female", "Kock och surfingentusiast 🏄‍♂️🍕", "1998-12-08", True),
    ("bot_gustav", "bot_pass_gustav", "Gustav", "Male", "Female", "Arkitekt med kaffe-beroende ☕🏛️", "1995-06-25", True),
]

print("🔐 Getting Keycloak admin token...")
admin_token = get_admin_token()

print("\n═══════════════════════════════════════════════")
print("  Creating users + profiles")
print("═══════════════════════════════════════════════")

for username, password, first, gender, pref, bio, dob, is_bot in USERS:
    emoji = "🤖" if is_bot else "👤"
    print(f"  {emoji} {first:10s}", end="", flush=True)
    uid = create_kc_user(admin_token, username, password, first, "Botsson" if is_bot else "User", f"{username}@test.se")
    if not uid:
        continue
    token = get_user_token(username, password)
    pid, status = onboard_wizard(token, first, gender, pref, bio, dob)
    print(f" → profileId={pid} (status={status}) ✅")

print("\n═══════════════════════════════════════════════")
print("  📱 Login on device:")
print("     Username: demo")
print("     Password: demo123")
print("═══════════════════════════════════════════════")
PYEOF
