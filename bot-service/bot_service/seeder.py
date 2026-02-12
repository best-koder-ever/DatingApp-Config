"""Profile seeder — creates bot users via randomuser.me + Keycloak + UserService APIs."""
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import Callable

import httpx
from faker import Faker

from . import config

fake = Faker("sv_SE")


class SeederState:
    """Shared state for the seeder, observable by the dashboard."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.total = 0
        self.created = 0
        self.failed = 0
        self.running = False
        self.cancelled = False
        self.bot_users: list[dict] = []

    @property
    def progress(self) -> float:
        return self.created / max(self.total, 1)


state = SeederState()


async def _get_keycloak_admin_token(client: httpx.AsyncClient) -> str | None:
    """Get Keycloak admin access token."""
    try:
        resp = await client.post(
            f"{config.KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "admin-cli",
                "username": config.KEYCLOAK_ADMIN_USER,
                "password": config.KEYCLOAK_ADMIN_PASS,
            },
        )
        if resp.status_code == 200:
            return resp.json()["access_token"]
        # Try password grant as fallback
        resp = await client.post(
            f"{config.KEYCLOAK_URL}/realms/master/protocol/openid-connect/token",
            data={
                "grant_type": "password",
                "client_id": "admin-cli",
                "username": config.KEYCLOAK_ADMIN_USER,
                "password": config.KEYCLOAK_ADMIN_PASS,
            },
        )
        if resp.status_code == 200:
            return resp.json()["access_token"]
        return None
    except Exception:
        return None


async def _create_keycloak_user(
    client: httpx.AsyncClient, token: str, user_data: dict
) -> str | None:
    """Create a user in Keycloak and return their ID."""
    try:
        resp = await client.post(
            f"{config.KEYCLOAK_URL}/admin/realms/{config.KEYCLOAK_REALM}/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": user_data["username"],
                "email": user_data["email"],
                "firstName": user_data["first_name"],
                "lastName": user_data["last_name"],
                "enabled": True,
                "emailVerified": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": config.DEFAULT_BOT_PASSWORD,
                        "temporary": False,
                    }
                ],
                "attributes": {"bot": ["true"]},
            },
        )
        if resp.status_code == 201:
            location = resp.headers.get("location", "")
            return location.split("/")[-1]  # Extract user ID from location header
        return None
    except Exception:
        return None


async def _get_user_token(client: httpx.AsyncClient, username: str) -> str | None:
    """Get an access token for a bot user."""
    try:
        resp = await client.post(
            f"{config.KEYCLOAK_URL}/realms/{config.KEYCLOAK_REALM}/protocol/openid-connect/token",
            data={
                "grant_type": "password",
                "client_id": "datingapp-backend",
                "username": username,
                "password": config.DEFAULT_BOT_PASSWORD,
            },
        )
        if resp.status_code == 200:
            return resp.json()["access_token"]
        return None
    except Exception:
        return None


async def _create_user_profile(
    client: httpx.AsyncClient, token: str, profile: dict
) -> bool:
    """Create/update a user profile in UserService."""
    try:
        resp = await client.put(
            f"{config.USER_SERVICE_URL}/api/profile/me",
            headers={"Authorization": f"Bearer {token}"},
            json=profile,
        )
        return resp.status_code in (200, 201, 204)
    except Exception:
        return False


def _build_profile(raw_user: dict) -> dict:
    """Build a full DatingApp profile from randomuser.me data + faker enrichment."""
    gender = raw_user.get("gender", random.choice(["male", "female"]))
    dob = raw_user.get("dob", {})
    age = dob.get("age", random.randint(22, 45))
    location = raw_user.get("location", {})
    city = location.get("city", random.choice(config.SWEDISH_CITIES))
    name_data = raw_user.get("name", {})
    first_name = name_data.get("first", fake.first_name())
    last_name = name_data.get("last", fake.last_name())
    pic = raw_user.get("picture", {})
    photo_url = pic.get("large", f"https://i.pravatar.cc/400?u={uuid.uuid4()}")
    login_data = raw_user.get("login", {})
    username = login_data.get("username", fake.user_name())
    email = raw_user.get("email", fake.email())

    interests = random.sample(config.INTERESTS_POOL, k=random.randint(3, 7))
    occupation = random.choice(config.OCCUPATIONS_POOL)

    bio_template = random.choice(config.BIO_TEMPLATES)
    bio = bio_template.format(
        interest1=interests[0],
        interest2=interests[1],
        interest3=interests[2] if len(interests) > 2 else interests[0],
        occupation=occupation,
        city=city,
    )

    # Build prompt answers
    prompts = []
    selected_questions = random.sample(config.PROMPT_QUESTIONS, k=random.randint(2, 4))
    for q in selected_questions:
        prompts.append(
            {"question": q, "answer": random.choice(config.PROMPT_ANSWERS_POOL)}
        )

    height_cm = random.randint(155, 195) if gender == "male" else random.randint(150, 180)

    return {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "display_name": first_name,
        "gender": gender,
        "age": age,
        "date_of_birth": (datetime.now() - timedelta(days=age * 365)).isoformat()[:10],
        "city": city,
        "latitude": location.get("coordinates", {}).get("latitude", str(fake.latitude())),
        "longitude": location.get("coordinates", {}).get("longitude", str(fake.longitude())),
        "bio": bio,
        "occupation": occupation,
        "interests": interests,
        "height_cm": height_cm,
        "photo_url": photo_url,
        "photo_thumbnail": pic.get("thumbnail", photo_url),
        "photos": [
            {"url": photo_url, "is_primary": True, "order_index": 0},
        ],
        "prompts": prompts,
        "relationship_goal": random.choice(config.RELATIONSHIP_GOALS),
        "is_bot": True,
        "is_verified": random.random() > 0.3,  # 70% verified
        "is_online": random.random() > 0.5,
        "preference": {
            "distance_km": random.choice([10, 25, 50, 100]),
            "age_range": {
                "min": max(18, age - random.randint(3, 8)),
                "max": age + random.randint(3, 8),
            },
            "relationship_goals": random.choice(config.RELATIONSHIP_GOALS),
        },
    }


async def _fetch_random_users(client: httpx.AsyncClient, count: int) -> list[dict]:
    """Fetch random users from randomuser.me API."""
    try:
        batch_size = min(count, 100)  # API max is 5000 but be nice
        users = []
        while len(users) < count:
            fetch = min(batch_size, count - len(users))
            resp = await client.get(
                config.RANDOMUSER_API,
                params={
                    "results": fetch,
                    "nat": config.RANDOMUSER_NATIONALITIES,
                    "inc": "name,email,login,dob,gender,location,picture",
                },
                timeout=30,
            )
            if resp.status_code == 200:
                users.extend(resp.json().get("results", []))
            else:
                # Fallback: generate locally with faker
                for _ in range(fetch):
                    users.append({})  # Empty dict triggers faker fallback in _build_profile
            await asyncio.sleep(0.5)  # Be nice to the API
        return users[:count]
    except Exception:
        return [{} for _ in range(count)]  # All faker fallback


async def seed_bots(
    count: int = 50,
    log_callback: Callable[[str], None] | None = None,
    mode: str = "keycloak",
) -> list[dict]:
    """
    Seed bot profiles.

    Modes:
      - "keycloak": Create real Keycloak users + UserService profiles (requires services running)
      - "local": Generate profiles as JSON only (no API calls, works offline)
    """

    def log(msg: str):
        if log_callback:
            log_callback(msg)

    state.reset()
    state.total = count
    state.running = True

    log(f"🚀 Starting seeder — creating {count} bot profiles (mode: {mode})")

    async with httpx.AsyncClient(timeout=30) as client:
        # Step 1: Fetch random user data
        log(f"📡 Fetching {count} random users from randomuser.me...")
        raw_users = await _fetch_random_users(client, count)
        log(f"✅ Got {len(raw_users)} user templates")

        # Step 2: Build profiles
        profiles = [_build_profile(u) for u in raw_users]
        log(f"🔨 Built {len(profiles)} enriched profiles")

        if mode == "local":
            # Just store locally, no API calls
            state.bot_users = profiles
            state.created = len(profiles)
            state.running = False
            log(f"✅ Generated {len(profiles)} profiles (local mode — no API calls)")
            return profiles

        # Step 3: Keycloak mode — create real users
        admin_token = await _get_keycloak_admin_token(client)
        if not admin_token:
            log("⚠️  Could not get Keycloak admin token — falling back to local mode")
            state.bot_users = profiles
            state.created = len(profiles)
            state.running = False
            return profiles

        log("🔑 Got Keycloak admin token")

        for i, profile in enumerate(profiles):
            if state.cancelled:
                log(f"⛔ Cancelled after {state.created} bots")
                break

            username = profile["username"]
            try:
                # Create Keycloak user
                kc_id = await _create_keycloak_user(client, admin_token, profile)
                if kc_id:
                    profile["keycloak_id"] = kc_id

                    # Get user token and create profile
                    user_token = await _get_user_token(client, username)
                    if user_token:
                        await _create_user_profile(client, user_token, profile)

                    state.created += 1
                    state.bot_users.append(profile)
                    if (i + 1) % 10 == 0 or i == 0:
                        log(f"👤 [{state.created}/{count}] Created: {profile['display_name']}, {profile['age']}, {profile['city']}")
                else:
                    state.failed += 1
                    log(f"❌ Failed to create Keycloak user: {username}")
            except Exception as e:
                state.failed += 1
                log(f"❌ Error creating {username}: {e}")

            # Small delay to not overwhelm services
            await asyncio.sleep(0.1)

    state.running = False
    log(f"🏁 Seeding complete: {state.created} created, {state.failed} failed")
    return state.bot_users


async def reset_bots(log_callback: Callable[[str], None] | None = None):
    """Delete all bot users from Keycloak."""

    def log(msg: str):
        if log_callback:
            log_callback(msg)

    log("🗑️  Resetting all bot users...")
    async with httpx.AsyncClient(timeout=30) as client:
        admin_token = await _get_keycloak_admin_token(client)
        if not admin_token:
            log("⚠️  Could not get Keycloak admin token — clearing local state only")
            state.reset()
            return

        # Find bot users
        try:
            resp = await client.get(
                f"{config.KEYCLOAK_URL}/admin/realms/{config.KEYCLOAK_REALM}/users",
                headers={"Authorization": f"Bearer {admin_token}"},
                params={"max": 5000, "q": "bot:true"},
            )
            if resp.status_code != 200:
                log("⚠️  Could not fetch users — clearing local state only")
                state.reset()
                return

            users = resp.json()
            bot_users = [u for u in users if u.get("attributes", {}).get("bot", [None])[0] == "true"]
            log(f"Found {len(bot_users)} bot users to delete")

            deleted = 0
            for user in bot_users:
                try:
                    await client.delete(
                        f"{config.KEYCLOAK_URL}/admin/realms/{config.KEYCLOAK_REALM}/users/{user['id']}",
                        headers={"Authorization": f"Bearer {admin_token}"},
                    )
                    deleted += 1
                except Exception:
                    pass

            log(f"✅ Deleted {deleted} bot users from Keycloak")
        except Exception as e:
            log(f"❌ Error during reset: {e}")

    state.reset()
    log("🧹 Local state cleared")
