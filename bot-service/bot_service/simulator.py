"""Behavior simulator — bots swipe, match, and message each other."""
import asyncio
import json
import random
from pathlib import Path
from typing import Callable

import httpx

from . import config
from .seeder import state as seeder_state

DATA_DIR = Path(__file__).parent / "data"


class SimulatorState:
    """Shared state for the simulator, observable by the dashboard."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.swipes = 0
        self.matches = 0
        self.messages_sent = 0
        self.active_bots = 0
        self.running = False
        self.cancelled = False
        self.speed = 1.0  # multiplier (0.1 = fast, 5.0 = slow)
        self.errors = 0


state = SimulatorState()

_conversations: list[list[str]] = []


def _load_conversations():
    """Load pre-generated conversation templates."""
    global _conversations
    if _conversations:
        return
    conv_file = DATA_DIR / "conversations.json"
    if conv_file.exists():
        with open(conv_file) as f:
            _conversations = json.load(f)
    else:
        # Fallback — simple messages
        _conversations = [
            ["Hej! Hur mår du? 😊", "Hej! Jag mår bra, tack! Själv? 🙂", "Bra tack! Vad gör du idag?"],
            ["Tjena! Gillade din profil 😄", "Tack, samma här! Vad har du för intressen?", "Jag älskar att vara ute i naturen!"],
            ["Hej hej! Fin bild 📸", "Tack så mycket! Den är från min senaste resa", "Var var du? 🌍"],
            ["Hallå! Såg att du också gillar matlagning 🍳", "Ja! Jag lagar mat nästan varje dag", "Vad är din specialrätt?"],
            ["Hej! Kul att vi matchade! 🎉", "Verkligen! Berätta lite om dig själv", "Jag är en spontan person som gillar äventyr"],
            ["Tja! Vad jobbar du med? 💼", "Jag är utvecklare, du då?", "Jag jobbar inom sjukvården"],
            ["Hej! Vilken fin hund du har! 🐕", "Tack! Han heter Max", "Åh så gulligt! Jag älskar hundar"],
            ["God kväll! Hur var din dag? 🌙", "Den var bra tack! Lite trött men nöjd", "Förstår! Ska du göra nåt kul i helgen?"],
            ["Hej! Jag ser att du gillar vandring 🥾", "Ja! Jag vandrade Kungsleden förra sommaren", "Imponerande! Det ska jag också göra"],
            ["Hey! Har du sett nån bra film på sistone? 🎬", "Jag såg precis den nya Marvel-filmen", "Åh, den vill jag också se!"],
        ]


async def _get_user_token(client: httpx.AsyncClient, username: str) -> str | None:
    """Get access token for a bot user."""
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


async def _get_candidates(
    client: httpx.AsyncClient, token: str
) -> list[dict]:
    """Fetch swipe candidates for a bot user."""
    try:
        resp = await client.get(
            f"{config.MATCHMAKING_URL}/api/candidates",
            headers={"Authorization": f"Bearer {token}"},
            params={"limit": 20},
        )
        if resp.status_code == 200:
            return resp.json() if isinstance(resp.json(), list) else resp.json().get("candidates", [])
        return []
    except Exception:
        return []


async def _swipe(
    client: httpx.AsyncClient, token: str, target_user_id: str, direction: str
) -> dict | None:
    """Perform a swipe action."""
    try:
        resp = await client.post(
            f"{config.SWIPE_SERVICE_URL}/api/swipes",
            headers={"Authorization": f"Bearer {token}"},
            json={"targetUserId": target_user_id, "direction": direction},
        )
        if resp.status_code in (200, 201):
            return resp.json()
        return None
    except Exception:
        return None


async def _send_message(
    client: httpx.AsyncClient, token: str, match_id: str, content: str
) -> bool:
    """Send a message via the messaging service."""
    try:
        resp = await client.post(
            f"{config.MESSAGING_URL}/api/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={"matchId": match_id, "content": content},
        )
        return resp.status_code in (200, 201)
    except Exception:
        return False


async def _simulate_bot(
    client: httpx.AsyncClient, bot: dict, log: Callable[[str], None]
):
    """Simulate one bot's behavior for one cycle."""
    username = bot.get("username")
    display = bot.get("display_name", username)

    token = await _get_user_token(client, username)
    if not token:
        state.errors += 1
        return

    # Get candidates
    candidates = await _get_candidates(client, token)
    if not candidates:
        return

    # Swipe on a few candidates
    swipe_count = random.randint(1, min(5, len(candidates)))
    for candidate in candidates[:swipe_count]:
        if state.cancelled:
            return

        target_id = candidate.get("userId") or candidate.get("id") or candidate.get("user_id", "")
        like = random.random() < config.SWIPE_RIGHT_PROBABILITY
        direction = "right" if like else "left"

        result = await _swipe(client, token, target_id, direction)
        state.swipes += 1

        if result and result.get("isMatch"):
            state.matches += 1
            match_id = result.get("matchId") or result.get("match_id", "")
            log(f"💕 {display} matched with someone!")

            # Send a conversation
            _load_conversations()
            if _conversations and match_id:
                convo = random.choice(_conversations)
                for msg in convo[:random.randint(1, len(convo))]:
                    if state.cancelled:
                        return
                    if await _send_message(client, token, match_id, msg):
                        state.messages_sent += 1
                    delay = config.DEFAULT_MESSAGE_DELAY_SEC * state.speed
                    await asyncio.sleep(delay * random.uniform(0.5, 1.5))

        delay = config.DEFAULT_SWIPE_DELAY_SEC * state.speed
        await asyncio.sleep(delay * random.uniform(0.5, 1.5))


async def run_simulation(
    log_callback: Callable[[str], None] | None = None,
    mode: str = "live",
    cycles: int = 0,  # 0 = infinite
):
    """
    Run the behavior simulation.

    Modes:
      - "live": Make real API calls to running services
      - "dry-run": Simulate without API calls (just log what would happen)

    Cycles:
      - 0: Run forever until stopped
      - N: Run N cycles then stop
    """

    def log(msg: str):
        if log_callback:
            log_callback(msg)

    bots = seeder_state.bot_users
    if not bots:
        log("⚠️  No bot users found — run the seeder first!")
        return

    state.running = True
    state.cancelled = False
    state.active_bots = len(bots)
    log(f"🚀 Starting simulation with {len(bots)} bots (mode: {mode})")

    cycle = 0
    async with httpx.AsyncClient(timeout=30) as client:
        while not state.cancelled:
            cycle += 1
            if cycles > 0 and cycle > cycles:
                break

            log(f"🔄 Cycle {cycle}" + (f"/{cycles}" if cycles > 0 else "") +
                f" — Swipes: {state.swipes} | Matches: {state.matches} | Msgs: {state.messages_sent}")

            if mode == "live":
                # Pick a random subset of bots to be active this cycle
                active = random.sample(bots, k=min(random.randint(3, 10), len(bots)))
                tasks = [_simulate_bot(client, bot, log) for bot in active]
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # Dry-run: just pretend
                for bot in random.sample(bots, k=min(5, len(bots))):
                    display = bot.get("display_name", bot.get("username", "?"))
                    state.swipes += random.randint(1, 5)
                    if random.random() < 0.2:
                        state.matches += 1
                        state.messages_sent += random.randint(1, 3)
                        log(f"💕 [dry-run] {display} matched!")
                    await asyncio.sleep(0.1)

            # Wait between cycles
            delay = config.DEFAULT_SWIPE_DELAY_SEC * state.speed * 3
            await asyncio.sleep(delay)

    state.running = False
    log(f"🏁 Simulation stopped — {state.swipes} swipes, {state.matches} matches, {state.messages_sent} messages")


def stop_simulation():
    """Signal the simulation to stop."""
    state.cancelled = True
