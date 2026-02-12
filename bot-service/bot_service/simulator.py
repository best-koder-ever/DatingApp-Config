"""Behavior simulator — bots swipe, match, and message each other."""
import asyncio
import json
import os
import random
import subprocess
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
        self.startup_phase = ""  # shown in UI during service bring-up
        self.services_up = 0
        self.services_total = len(config.SERVICES)


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


# ─── Health Check & Auto-Start ──────────────────────────────────────────────

# Human-readable labels for each service
_SERVICE_LABELS = {
    "Keycloak":           "Keycloak (auth, :8090)",
    "YARP Gateway":       "YARP Gateway (:8080)",
    "UserService":        "UserService (:8082)",
    "MatchmakingService": "MatchmakingService (:8083)",
    "PhotoService":       "PhotoService (:8085)",
    "MessagingService":   "MessagingService (:8086)",
    "SwipeService":       "SwipeService (:8087)",
}

# Which services are "infrastructure" (docker containers) vs ".NET services"
_INFRA_SERVICES = {"Keycloak"}
_DOTNET_SERVICES = {"YARP Gateway", "UserService", "MatchmakingService",
                    "PhotoService", "MessagingService", "SwipeService"}


async def _check_service(client: httpx.AsyncClient, name: str, url: str) -> bool:
    """Ping a single service health endpoint."""
    try:
        resp = await client.get(url, timeout=3)
        return resp.status_code < 500
    except Exception:
        return False


async def _check_all_services(client: httpx.AsyncClient) -> dict[str, bool]:
    """Check all services concurrently. Returns {name: is_healthy}."""
    async def _check(name: str, url: str) -> tuple[str, bool]:
        ok = await _check_service(client, name, url)
        return name, ok

    tasks = [_check(n, info["health"]) for n, info in config.SERVICES.items()]
    pairs = await asyncio.gather(*tasks)
    return dict(pairs)


def _log_status_table(
    status: dict[str, bool],
    log: Callable[[str], None],
) -> tuple[list[str], list[str]]:
    """Log a status line per service, return (up_list, down_list)."""
    up, down = [], []
    for name in config.SERVICES:
        label = _SERVICE_LABELS.get(name, name)
        if status.get(name):
            log(f"   ✅ {label}")
            up.append(name)
        else:
            log(f"   ❌ {label}")
            down.append(name)
    state.services_up = len(up)
    return up, down


def _run_script(
    script: str,
    label: str,
    log: Callable[[str], None],
    timeout: int = 180,
) -> bool:
    """Run a shell script, stream last few lines of output on failure."""
    if not os.path.isfile(script):
        log(f"❌ Script not found: {script}")
        return False
    log(f"⚙️  Running {label}...")
    try:
        result = subprocess.run(
            ["bash", script],
            cwd=config.DATINGAPP_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            log(f"✅ {label} completed")
            return True
        else:
            for line in (result.stderr or result.stdout or "").strip().splitlines()[-8:]:
                log(f"   {line}")
            log(f"❌ {label} failed (exit code {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        log(f"❌ {label} timed out ({timeout}s)")
        return False
    except Exception as e:
        log(f"❌ {label} error: {e}")
        return False


async def _wait_for_services(
    names: set[str],
    log: Callable[[str], None],
    max_seconds: int = 60,
    poll_interval: int = 3,
) -> bool:
    """
    Poll until all services in `names` are healthy.
    Logs progress like "3/6 services ready...".
    Returns True when all healthy, False on timeout or cancel.
    """
    total = len(names)
    attempts = max_seconds // poll_interval

    async with httpx.AsyncClient() as client:
        for attempt in range(attempts):
            if state.cancelled:
                return False

            status = await _check_all_services(client)
            ready = [n for n in names if status.get(n)]
            not_ready = [n for n in names if not status.get(n)]
            state.services_up = sum(1 for v in status.values() if v)

            if not not_ready:
                log(f"   ✅ {total}/{total} services ready!")
                return True

            # Show which ones are still missing
            ready_names = ", ".join(_SERVICE_LABELS.get(n, n) for n in ready) if ready else "none yet"
            waiting_names = ", ".join(_SERVICE_LABELS.get(n, n) for n in not_ready)
            elapsed = attempt * poll_interval
            log(f"   ⏳ {len(ready)}/{total} ready ({elapsed}s) — waiting for: {waiting_names}")
            state.startup_phase = f"{len(ready)}/{total} services ready..."

            await asyncio.sleep(poll_interval)

    # Final report on what didn't come up
    log(f"❌ Timeout after {max_seconds}s — these services never became healthy:")
    for n in not_ready:
        log(f"   ❌ {_SERVICE_LABELS.get(n, n)}")
    return False


async def _ensure_services_running(
    log: Callable[[str], None],
) -> bool:
    """
    Check all services, auto-start what's missing. Returns True when ready.

    Flow:
      1. Health-check all 7 services
      2. If Keycloak is down → run infrastructure/start.sh (docker compose)
      3. If any .NET services are down → run dev-start.sh (dotnet run)
      4. Wait with progress counter until everything is healthy
    """
    total = len(config.SERVICES)
    state.startup_phase = f"Checking {total} services..."
    log(f"🔍 Checking {total} services...")

    async with httpx.AsyncClient() as client:
        status = await _check_all_services(client)

    up, down = _log_status_table(status, log)

    if not down:
        log(f"✅ All {total} services healthy — ready to simulate!")
        state.startup_phase = ""
        return True

    log(f"")
    log(f"📊 {len(up)}/{total} services up, {len(down)} need starting")

    # ── Step 1: Infrastructure (Keycloak + databases via docker compose) ──
    infra_down = [n for n in down if n in _INFRA_SERVICES]
    dotnet_down = [n for n in down if n in _DOTNET_SERVICES]

    if infra_down:
        state.startup_phase = "Starting Keycloak + databases..."
        log("")
        log("🐳 Step 1/2: Starting infrastructure (Keycloak + databases)...")
        ok = await asyncio.get_event_loop().run_in_executor(
            None,
            _run_script,
            config.INFRASTRUCTURE_SCRIPT,
            "infrastructure/start.sh",
            log,
            180,
        )
        if not ok:
            state.startup_phase = "❌ Infrastructure failed"
            return False

        # Wait specifically for Keycloak
        log("⏳ Waiting for Keycloak to become ready (can take 30-60s)...")
        state.startup_phase = "Waiting for Keycloak..."
        keycloak_ok = await _wait_for_services(
            {"Keycloak"}, log, max_seconds=90, poll_interval=3
        )
        if not keycloak_ok:
            state.startup_phase = "❌ Keycloak didn't start"
            log("❌ Keycloak failed to become ready")
            return False

        log("✅ Keycloak is ready")
    else:
        log("")
        log("✅ Step 1/2: Infrastructure already running (Keycloak ✅)")

    # ── Step 2: .NET services via dev-start.sh ──
    if dotnet_down:
        state.startup_phase = f"Starting {len(dotnet_down)} .NET services..."
        log("")
        svc_names = ", ".join(_SERVICE_LABELS.get(n, n) for n in dotnet_down)
        log(f"🚀 Step 2/2: Starting .NET services ({svc_names})...")
        log(f"   Running dev-start.sh — this starts all services with 'dotnet run'")
        ok = await asyncio.get_event_loop().run_in_executor(
            None,
            _run_script,
            config.DEV_START_SCRIPT,
            "dev-start.sh",
            log,
            180,
        )
        if not ok:
            state.startup_phase = "❌ dev-start.sh failed"
            return False

        # Wait for all .NET services
        log(f"⏳ Waiting for {len(dotnet_down)} .NET services to become healthy...")
        state.startup_phase = f"Waiting for .NET services..."
        all_ok = await _wait_for_services(
            set(dotnet_down), log, max_seconds=60, poll_interval=3
        )
        if not all_ok:
            state.startup_phase = "❌ Some services didn't start"
            return False
    else:
        log("")
        log("✅ Step 2/2: All .NET services already running")

    # ── Final check ──
    log("")
    async with httpx.AsyncClient() as client:
        final_status = await _check_all_services(client)
    final_up = sum(1 for v in final_status.values() if v)
    state.services_up = final_up

    if final_up == total:
        state.startup_phase = ""
        log(f"🎉 All {total}/{total} services healthy — starting simulation!")
        return True
    else:
        still_down = [n for n, ok in final_status.items() if not ok]
        labels = ", ".join(_SERVICE_LABELS.get(n, n) for n in still_down)
        state.startup_phase = f"❌ {len(still_down)} services still down"
        log(f"❌ {final_up}/{total} up — still down: {labels}")
        return False


# ─── API Helpers ─────────────────────────────────────────────────────────────


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


async def _get_candidates(client: httpx.AsyncClient, token: str) -> list[dict]:
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


async def _swipe(client: httpx.AsyncClient, token: str, target_user_id: str, direction: str) -> dict | None:
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


async def _send_message(client: httpx.AsyncClient, token: str, match_id: str, content: str) -> bool:
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


# ─── Bot Simulation Loop ────────────────────────────────────────────────────


async def _simulate_bot(client: httpx.AsyncClient, bot: dict, log: Callable[[str], None]):
    """Simulate one bot's behavior for one cycle."""
    username = bot.get("username")
    display = bot.get("display_name", username)

    token = await _get_user_token(client, username)
    if not token:
        state.errors += 1
        return

    candidates = await _get_candidates(client, token)
    if not candidates:
        return

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

            _load_conversations()
            if _conversations and match_id:
                convo = random.choice(_conversations)
                for msg in convo[:random.randint(1, len(convo))]:
                    if state.cancelled:
                        return
                    if await _send_message(client, token, match_id, msg):
                        state.messages_sent += 1
                    delay = config.MESSAGE_DELAY_SEC * state.speed
                    await asyncio.sleep(delay * random.uniform(0.5, 1.5))

        delay = config.SWIPE_DELAY_SEC * state.speed
        await asyncio.sleep(delay * random.uniform(0.5, 1.5))


async def run_simulation(
    log_callback: Callable[[str], None] | None = None,
    mode: str = "live",
    cycles: int = 0,
):
    """
    Run the behavior simulation.

    Modes:
      - "live": Real API calls — auto-starts services if needed
      - "dry-run": Simulated activity without calling any APIs

    Cycles:
      - 0: Run forever until stopped
      - N: Run N cycles then stop
    """

    def log(msg: str):
        if log_callback:
            log_callback(msg)

    bots = seeder_state.bot_users
    if not bots:
        log("⚠️  No bot users found — go to 🌱 Seed tab and seed some bots first!")
        return

    state.running = True
    state.cancelled = False
    state.active_bots = len(bots)

    # ── Live mode: check + auto-start services ──
    if mode == "live":
        total = len(config.SERVICES)
        log(f"🔎 Live mode — checking {total} services before starting...")
        log("")
        ok = await _ensure_services_running(log)
        if not ok:
            log("")
            log("❌ Cannot start simulation — fix the services above and try again")
            state.running = False
            return
        if state.cancelled:
            log("⛔ Cancelled during startup")
            state.running = False
            return
        log("")

    log(f"🚀 Simulation started — {len(bots)} bots, mode: {mode}")

    cycle = 0
    async with httpx.AsyncClient(timeout=30) as client:
        while not state.cancelled:
            cycle += 1
            if cycles > 0 and cycle > cycles:
                break

            log(f"🔄 Cycle {cycle}" + (f"/{cycles}" if cycles > 0 else "") +
                f" — Swipes: {state.swipes} | Matches: {state.matches} | Msgs: {state.messages_sent}")

            if mode == "live":
                active = random.sample(bots, k=min(random.randint(3, 10), len(bots)))
                tasks = [_simulate_bot(client, bot, log) for bot in active]
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                for bot in random.sample(bots, k=min(5, len(bots))):
                    display = bot.get("display_name", bot.get("username", "?"))
                    state.swipes += random.randint(1, 5)
                    if random.random() < 0.2:
                        state.matches += 1
                        state.messages_sent += random.randint(1, 3)
                        log(f"💕 [dry-run] {display} matched!")
                    await asyncio.sleep(0.1)

            delay = config.SWIPE_DELAY_SEC * state.speed * 3
            await asyncio.sleep(delay)

    state.running = False
    state.startup_phase = ""
    log(f"🏁 Simulation done — {state.swipes} swipes, {state.matches} matches, {state.messages_sent} messages")


def stop_simulation():
    """Signal the simulation to stop."""
    state.cancelled = True
