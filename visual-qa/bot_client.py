"""
bot_client.py — HTTP client for the bot-service REST API (port 9091).

Used by run_visual_qa.py to seed test data before visual QA use-cases:
  - UC2 Discovery  : seed 5-10 synthetic profiles
  - UC3 Messaging  : seed a mutual match so the chat screen can be tested
  - UC4 Safety     : ensure at least one conversation exists (reuses UC3 match)
"""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_BOT_SERVICE_URL = "http://localhost:9091"
_DEFAULT_TIMEOUT = 60  # seconds — seeding can be slow in keycloak mode


class BotServiceError(RuntimeError):
    """Raised when the bot-service returns an unexpected response."""


class BotClient:
    """Thin HTTP wrapper around the bot-service REST API."""

    def __init__(
        self,
        base_url: str = DEFAULT_BOT_SERVICE_URL,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            resp = httpx.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise BotServiceError(
                f"GET {url} returned {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise BotServiceError(f"GET {url} failed: {exc}") from exc

    def _post(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            resp = httpx.post(url, json=payload or {}, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise BotServiceError(
                f"POST {url} returned {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise BotServiceError(f"POST {url} failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """Check that the bot-service is reachable and healthy."""
        return self._get("/api/health")

    def status(self) -> dict[str, Any]:
        """Return the current seeder state (running, created, failed, …)."""
        return self._get("/api/status")

    def seed_profiles(
        self,
        count: int = 10,
        mode: str = "local",
    ) -> dict[str, Any]:
        """
        Seed *count* synthetic bot profiles.

        Args:
            count: Number of profiles to create (5–50 recommended for QA).
            mode:  "local"    — build profiles in-memory only (fast, no services needed)
                   "keycloak" — also push profiles to Keycloak + UserService
        Returns:
            Dict with keys: seeded (int), mode (str), logs (list[str])
        """
        logger.info("Seeding %d profiles (mode=%s) …", count, mode)
        result = self._post("/api/seed", {"count": count, "mode": mode})
        logger.info("Seeded %d profiles", result.get("seeded", 0))
        for line in result.get("logs", []):
            logger.debug("  [bot-service] %s", line)
        return result

    def seed_match(self, mode: str = "keycloak") -> dict[str, Any]:
        """
        Seed a mutual match between two synthetic bot users.

        In keycloak mode this also submits right-swipes via SwipeService so
        the match is persisted and visible in the Messaging screen.

        Returns:
            Dict with keys: user_a, user_b, match_created (bool), mode, logs
        """
        logger.info("Seeding mutual match (mode=%s) …", mode)
        result = self._post("/api/seed-match", {"mode": mode})
        logger.info(
            "Match created=%s  user_a=%s  user_b=%s",
            result.get("match_created"),
            result.get("user_a", {}).get("username"),
            result.get("user_b", {}).get("username"),
        )
        for line in result.get("logs", []):
            logger.debug("  [bot-service] %s", line)
        return result

    # ------------------------------------------------------------------
    # Convenience: wait until the service is up
    # ------------------------------------------------------------------

    def wait_until_ready(self, max_wait: float = 30.0, poll_interval: float = 2.0) -> bool:
        """
        Poll /api/health until the bot-service responds or *max_wait* seconds elapse.

        Returns True if the service became ready, False on timeout.
        """
        deadline = time.monotonic() + max_wait
        while time.monotonic() < deadline:
            try:
                self.health()
                return True
            except BotServiceError:
                time.sleep(poll_interval)
        return False
