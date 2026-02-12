"""Locust load test — simulates dating app user behavior at scale."""
import random
import json

from locust import HttpUser, task, between, events


KEYCLOAK_URL = "http://localhost:8090"
REALM = "DatingApp"
CLIENT_ID = "datingapp-backend"
BOT_PASSWORD = "BotPass123!"

# Pre-populate with bot usernames (or use a shared list)
BOT_USERNAMES = [f"bot_{i}" for i in range(50)]


class DatingAppUser(HttpUser):
    """Simulates a real dating app user's behavior."""

    wait_time = between(1, 5)
    host = "http://localhost:8080"

    def on_start(self):
        """Login and get token."""
        self.username = random.choice(BOT_USERNAMES)
        self.token = self._get_token()
        self.headers = {}
        if self.token:
            self.headers = {"Authorization": f"Bearer {self.token}"}

    def _get_token(self) -> str | None:
        """Authenticate via Keycloak."""
        try:
            resp = self.client.post(
                f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/token",
                data={
                    "grant_type": "password",
                    "client_id": CLIENT_ID,
                    "username": self.username,
                    "password": BOT_PASSWORD,
                },
                name="/keycloak/token",
            )
            if resp.status_code == 200:
                return resp.json()["access_token"]
        except Exception:
            pass
        return None

    @task(5)
    def browse_candidates(self):
        """Most common action — browse potential matches."""
        self.client.get(
            "/api/candidates",
            headers=self.headers,
            params={"limit": 20},
            name="/api/candidates",
        )

    @task(3)
    def swipe(self):
        """Swipe on a candidate."""
        # First get candidates
        resp = self.client.get(
            "/api/candidates",
            headers=self.headers,
            params={"limit": 5},
            name="/api/candidates [for swipe]",
        )
        if resp.status_code == 200:
            try:
                data = resp.json()
                items = data if isinstance(data, list) else data.get("candidates", [])
                if items:
                    target = random.choice(items)
                    target_id = target.get("userId") or target.get("id", "")
                    direction = "right" if random.random() < 0.3 else "left"
                    self.client.post(
                        "/api/swipes",
                        headers={**self.headers, "Content-Type": "application/json"},
                        data=json.dumps({"targetUserId": target_id, "direction": direction}),
                        name="/api/swipes",
                    )
            except Exception:
                pass

    @task(2)
    def view_profile(self):
        """View own profile."""
        self.client.get(
            "/api/profile/me",
            headers=self.headers,
            name="/api/profile/me",
        )

    @task(2)
    def check_messages(self):
        """Check messages."""
        self.client.get(
            "/api/messages",
            headers=self.headers,
            name="/api/messages",
        )

    @task(1)
    def view_matches(self):
        """View matches list."""
        self.client.get(
            "/api/matches",
            headers=self.headers,
            name="/api/matches",
        )
