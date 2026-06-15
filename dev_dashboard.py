#!/usr/bin/env python3
"""Local NiceGUI control dashboard for the DatingApp development stack.

Run with:
    ./.venv/bin/python dev_dashboard.py

The dashboard is intentionally local/dev focused. It wraps existing services,
scripts, APIs, Android tooling, and smoke checks without changing backend APIs.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import shlex
import signal
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable


ROOT = Path(os.getenv("DATINGAPP_ROOT", Path(__file__).resolve().parent)).resolve()
FLUTTER_ROOT = Path(
    os.getenv("FLUTTER_ROOT", "/home/m/development/mobile-apps/flutter/dejtingapp")
).resolve()
LOG_DIR = ROOT / "logs"
DEFAULT_PORT = int(os.getenv("DASHBOARD_PORT", "9100"))

APP_PACKAGE = "com.dejting.app"
APP_ACTIVITY = ".MainActivity"
DEMO_USERNAME = "bot_demo-user@bot.local"
DEMO_PASSWORD = "bot_pass_demo-user"
DEMO_PROFILE_ID = 1
FALLBACK_BOT_PROFILE_IDS = [2, 3, 4]

httpx = None
ui = None
app = None


def _load_runtime_dependencies(require_ui: bool) -> None:
    """Import optional runtime dependencies with a useful local-dev hint."""
    global httpx, ui, app
    try:
        import httpx as imported_httpx

        httpx = imported_httpx
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: httpx. Run this dashboard with "
            "`./.venv/bin/python dev_dashboard.py` from the DatingApp root."
        ) from exc

    if require_ui:
        try:
            from nicegui import app as imported_app
            from nicegui import ui as imported_ui

            ui = imported_ui
            app = imported_app
        except ImportError as exc:
            raise SystemExit(
                "Missing dependency: nicegui. Run this dashboard with "
                "`./.venv/bin/python dev_dashboard.py` from the DatingApp root."
            ) from exc


def mask_secrets(value: Any) -> str:
    """Mask bearer tokens, access tokens, and passwords before logging."""
    text = str(value)
    text = re.sub(r"Bearer\s+[A-Za-z0-9._\-]+", "Bearer <masked>", text)
    text = re.sub(
        r'("?(?:access_token|refresh_token|id_token)"?\s*[:=]\s*"?)[^",\s}]+',
        r"\1<masked>",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'("?(?:password|client_secret)"?\s*[:=]\s*"?)[^",\s}]+',
        r"\1<masked>",
        text,
        flags=re.IGNORECASE,
    )
    text = text.replace(DEMO_PASSWORD, "<masked>")
    return text


def now_label() -> str:
    return datetime.now().strftime("%H:%M:%S")


def shell_join(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def port_open(port: int, host: str = "127.0.0.1", timeout: float = 0.3) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def load_env_files() -> dict[str, str]:
    """Load simple KEY=VALUE pairs from .env.local and .env without shell eval."""
    env: dict[str, str] = {}
    for file_name in (".env.local", ".env"):
        path = ROOT / file_name
        if not path.exists():
            continue
        for raw in path.read_text(errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                env[key] = value
    return env


def service_env(port: int) -> dict[str, str]:
    env = os.environ.copy()
    env.update(load_env_files())
    env.update(
        {
            "ASPNETCORE_ENVIRONMENT": "Development",
            "ASPNETCORE_URLS": f"http://+:{port}",
        }
    )
    return env


@dataclass(frozen=True)
class ServiceSpec:
    key: str
    name: str
    port: int
    cwd: Path
    command: list[str]
    log_file: Path
    health_url: str
    stop_patterns: list[str] = field(default_factory=list)


SERVICES: list[ServiceSpec] = [
    ServiceSpec(
        "user",
        "UserService",
        8082,
        ROOT / "UserService",
        ["dotnet", "run"],
        LOG_DIR / "user-service.log",
        "http://localhost:8082/health",
        ["UserService"],
    ),
    ServiceSpec(
        "matchmaking",
        "MatchmakingService",
        8083,
        ROOT / "MatchmakingService",
        ["dotnet", "run"],
        LOG_DIR / "matchmaking-service.log",
        "http://localhost:8083/health",
        ["MatchmakingService"],
    ),
    ServiceSpec(
        "photo",
        "PhotoService",
        8085,
        ROOT / "photo-service",
        ["dotnet", "run"],
        LOG_DIR / "photo-service.log",
        "http://localhost:8085/health",
        ["photo-service", "PhotoService"],
    ),
    ServiceSpec(
        "messaging",
        "MessagingService",
        8086,
        ROOT / "messaging-service",
        ["dotnet", "run"],
        LOG_DIR / "messaging-service.log",
        "http://localhost:8086/health",
        ["MessagingService", "messaging-service"],
    ),
    ServiceSpec(
        "swipe",
        "SwipeService",
        8087,
        ROOT / "swipe-service",
        ["dotnet", "run", "--project", "SwipeService.csproj"],
        LOG_DIR / "swipe-service.log",
        "http://localhost:8087/health",
        ["SwipeService", "swipe-service"],
    ),
    ServiceSpec(
        "safety",
        "SafetyService",
        8088,
        ROOT / "safety-service" / "SafetyService",
        ["dotnet", "run"],
        LOG_DIR / "safety-service.log",
        "http://localhost:8088/health",
        ["SafetyService"],
    ),
    ServiceSpec(
        "yarp",
        "YARP Gateway",
        8080,
        ROOT / "dejting-yarp" / "src" / "dejting-yarp",
        ["dotnet", "run"],
        LOG_DIR / "yarp-gateway.log",
        "http://localhost:8080/health",
        ["dejting-yarp"],
    ),
    ServiceSpec(
        "bot",
        "BotService",
        8089,
        ROOT / "bot-service" / "BotService",
        ["dotnet", "run"],
        LOG_DIR / "bot-service.log",
        "http://localhost:8089/health",
        ["BotService"],
    ),
]

SERVICE_BY_KEY = {service.key: service for service in SERVICES}

INFRA_SERVICES = [
    "keycloak-db",
    "keycloak",
    "mailhog",
    "UserService-db",
    "MatchmakingService-db",
    "swipe-service-db",
    "photo-service-db",
    "messaging-service-db",
]

ANDROID_PERMISSIONS = [
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.CAMERA",
    "android.permission.RECORD_AUDIO",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.READ_MEDIA_IMAGES",
    "android.permission.POST_NOTIFICATIONS",
]


class DevDashboard:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run
        self.processes: dict[str, asyncio.subprocess.Process] = {}
        self.busy = False
        self.active_job = "Idle"
        self.last_refresh = "Never"
        self.selected_device: str | None = None
        self.action_buttons: list[Any] = []

        self.event_log = None
        self.status_label = None
        self.device_label = None
        self.job_label = None
        self.refresh_label = None
        self.unstick_btn = None

        self.service_table = None
        self.infra_table = None
        self.health_table = None
        self.db_table = None
        self.bot_table = None
        self.findings_table = None
        self.android_table = None
        self.android_log = None
        self.android_status = None
        self.conn_table = None
        self.conn_action_plan = None
        self.smoke_log = None
        self.log_tail = None
        self.log_select = None
        self.vikunja_status_label = None
        self.billing_premium_label = None
        self.billing_purchases_label = None
        self.billing_credited_label = None
        self.billing_spent_label = None
        self.billing_updated_label = None
        self.billing_pricing_table = None
        self.billing_purchases_table = None
        self.billing_subs_table = None
        self.billing_sparks_table = None
        self.stack_event_log = None

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def log(self, message: Any) -> None:
        line = f"[{now_label()}] {mask_secrets(message)}"
        print(line, flush=True)
        if self.event_log is not None:
            self.event_log.push(line)
        if self.stack_event_log is not None:
            self.stack_event_log.push(line)

    def set_busy(self, value: bool, label: str = "Idle") -> None:
        self.busy = value
        self.active_job = label if value else "Idle"
        if self.job_label is not None:
            self.job_label.text = f"Job: {self.active_job}"
        if hasattr(self, "unstick_btn") and self.unstick_btn is not None:
            self.unstick_btn.visible = value
        for button in self.action_buttons:
            if value:
                button.disable()
            else:
                button.enable()

    def add_button(
        self,
        label: str,
        on_click: Callable[[], Awaitable[None] | None],
        *,
        icon: str | None = None,
        color: str = "primary",
        tooltip: str = "",
    ) -> Any:
        button = ui.button(label, on_click=on_click, icon=icon, color=color).props("dense")
        if tooltip:
            button.tooltip(tooltip)
        self.action_buttons.append(button)
        return button

    async def guarded(self, label: str, action: Callable[[], Awaitable[None]]) -> None:
        if self.busy:
            ui.notify("Another command is running", type="warning")
            return
        self.set_busy(True, label)
        # Auto-reset after 120s to prevent UI getting stuck
        timeout_task = asyncio.create_task(asyncio.sleep(120))
        try:
            await action()
        except asyncio.CancelledError:
            self.log(f"{label}: cancelled by user")
        except Exception as exc:
            self.log(f"{label} failed: {exc}")
            ui.notify(f"{label} failed", type="negative")
        finally:
            if not timeout_task.done():
                timeout_task.cancel()
            self.set_busy(False)
            await self.refresh_all()
            # If the timeout fired, notify
            if timeout_task.done() and not timeout_task.cancelled():
                self.log(f"{label}: auto-released guard after 120s timeout")
                ui.notify("Previous command timed out — guard released", type="info")

    def force_unbusy(self) -> None:
        """Unstick the busy state if a command hung. Safe to call anytime."""
        if self.busy:
            self.log(f"Force-releasing stuck guard (was: {self.active_job})")
            self.set_busy(False)

    def confirm(
        self,
        title: str,
        message: str,
        action: Callable[[], Awaitable[None]],
    ) -> None:
        with ui.dialog() as dialog, ui.card().classes("w-[28rem]"):
            ui.label(title).classes("text-lg font-semibold")
            ui.label(message).classes("text-sm text-gray-700")
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Cancel", on_click=dialog.close).props("flat")

                async def run_confirmed() -> None:
                    dialog.close()
                    await action()

                ui.button("Confirm", on_click=run_confirmed, color="negative")
        dialog.open()

    # ------------------------------------------------------------------
    # Command helpers
    # ------------------------------------------------------------------
    async def capture(
        self,
        cmd: list[str],
        *,
        cwd: Path = ROOT,
        env: dict[str, str] | None = None,
        timeout: float = 20,
    ) -> tuple[int, str]:
        if self.dry_run:
            return 0, f"DRY RUN: {shell_join(cmd)}"
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(cwd),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return proc.returncode or 0, stdout.decode(errors="replace")
        except asyncio.TimeoutError:
            return 124, f"Timed out after {timeout}s: {shell_join(cmd)}"
        except FileNotFoundError as exc:
            return 127, str(exc)

    async def run_command(
        self,
        cmd: list[str],
        *,
        cwd: Path = ROOT,
        env: dict[str, str] | None = None,
        label: str | None = None,
    ) -> int:
        title = label or shell_join(cmd)
        self.log(f"Running {title}: {shell_join(cmd)}")
        if self.dry_run:
            self.log("Dry run: command not executed")
            return 0
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(cwd),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except FileNotFoundError as exc:
            self.log(f"Command not found: {exc}")
            return 127

        assert proc.stdout is not None
        while True:
            raw = await proc.stdout.readline()
            if not raw:
                break
            self.log(raw.decode(errors="replace").rstrip())
        return_code = await proc.wait()
        self.log(f"{title} finished with exit code {return_code}")
        return return_code

    async def run_command_streaming(
        self,
        cmd: list[str],
        *,
        cwd: Path = ROOT,
        env: dict[str, str] | None = None,
        label: str = "Background task",
    ) -> int:
        """Run a command in a background task, streaming output to the Android log.

        Returns immediately after spawning the background task. The command runs
        independently — the dashboard stays responsive. Output appears in the
        Android tab's build log area.
        """
        title = label or shell_join(cmd)
        self.log(f"[BG] Starting: {title}")

        if self.android_status is not None:
            self.android_status.text = f"⏳ {title}..."
            self.android_status.classes("text-orange-600 font-semibold text-sm")

        async def _runner() -> int:
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=str(cwd),
                    env=env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                )
            except FileNotFoundError as exc:
                msg = f"Command not found: {exc}"
                self.log(f"[BG] {msg}")
                if self.android_log is not None:
                    self.android_log.push(f"[ERROR] {msg}")
                if self.android_status is not None:
                    self.android_status.text = f"❌ {title} failed: not found"
                    self.android_status.classes("text-red-600 font-semibold text-sm")
                return 127

            assert proc.stdout is not None
            line_count = 0
            while True:
                raw = await proc.stdout.readline()
                if not raw:
                    break
                line = raw.decode(errors="replace").rstrip()
                self.log(f"[BG:{title}] {line}")
                if self.android_log is not None:
                    # Batch updates every 5 lines to reduce UI churn
                    line_count += 1
                    if line_count % 5 == 1 or 'error' in line.lower() or 'fail' in line.lower():
                        self.android_log.push(line)
            return_code = await proc.wait()
            status_icon = "✅" if return_code == 0 else "❌"
            msg = f"{status_icon} {title} finished (exit {return_code})"
            self.log(f"[BG] {msg}")
            if self.android_log is not None:
                self.android_log.push(msg)
            if self.android_status is not None:
                if return_code == 0:
                    self.android_status.text = f"✅ {title} done"
                    self.android_status.classes("text-green-600 font-semibold text-sm")
                else:
                    self.android_status.text = f"❌ {title} failed (exit {return_code})"
                    self.android_status.classes("text-red-600 font-semibold text-sm")
            return return_code

        asyncio.create_task(_runner())
        return 0  # Return immediately — task runs in background

    async def start_service(self, key: str) -> None:
        service = SERVICE_BY_KEY[key]
        if port_open(service.port):
            self.log(f"{service.name} appears to already be listening on :{service.port}")
            return
        if not service.cwd.exists():
            self.log(f"Cannot start {service.name}: missing directory {service.cwd}")
            return

        LOG_DIR.mkdir(exist_ok=True)
        self.log(f"Starting {service.name} on :{service.port}")
        self.log(f"Log: {service.log_file.relative_to(ROOT)}")
        if self.dry_run:
            self.log(f"Dry run: {shell_join(service.command)} in {service.cwd}")
            return

        service.log_file.parent.mkdir(parents=True, exist_ok=True)
        log_handle = service.log_file.open("ab", buffering=0)
        try:
            process = await asyncio.create_subprocess_exec(
                *service.command,
                cwd=str(service.cwd),
                env=service_env(service.port),
                stdout=log_handle,
                stderr=asyncio.subprocess.STDOUT,
                start_new_session=True,
            )
        finally:
            log_handle.close()
        self.processes[key] = process
        self.log(f"{service.name} started with PID {process.pid}")

    async def stop_service(self, key: str) -> None:
        service = SERVICE_BY_KEY[key]
        process = self.processes.get(key)
        if process and process.returncode is None:
            self.log(f"Stopping {service.name} PID {process.pid}")
            try:
                os.killpg(process.pid, signal.SIGTERM)
                await asyncio.wait_for(process.wait(), timeout=8)
            except (ProcessLookupError, asyncio.TimeoutError):
                self.log(f"Force-stopping {service.name} PID {process.pid}")
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            return

        for pattern in service.stop_patterns:
            await self.run_command(["pkill", "-f", pattern], label=f"stop {service.name} fallback")

        if port_open(service.port):
            rc, out = await self.capture(["lsof", "-ti", f":{service.port}"], timeout=5)
            pids = [line.strip() for line in out.splitlines() if line.strip()]
            for pid in pids:
                self.log(f"Killing process {pid} on :{service.port}")
                await self.capture(["kill", "-TERM", pid], timeout=5)

    async def start_all_services(self) -> None:
        for key in ["user", "matchmaking", "photo", "messaging", "swipe", "safety", "yarp", "bot"]:
            await self.start_service(key)
            await asyncio.sleep(1.0)

    async def stop_all_services(self) -> None:
        for key in ["bot", "yarp", "safety", "swipe", "messaging", "photo", "matchmaking", "user"]:
            await self.stop_service(key)

    @staticmethod
    def _svc_project_flag(svc: ServiceSpec) -> list[str]:
        """Extract --project flag from a service's command, if present."""
        cmd = svc.command
        try:
            idx = cmd.index("--project")
            return ["--project", cmd[idx + 1]]
        except (ValueError, IndexError):
            return []

    async def rebuild_all_services(self) -> None:
        """Run dotnet restore && dotnet build in every service directory."""
        for key in ["user", "matchmaking", "photo", "messaging", "swipe", "safety", "yarp", "bot"]:
            svc = SERVICE_BY_KEY[key]
            proj_flag = self._svc_project_flag(svc)
            self.log(f"--- Rebuilding {svc.name} ({svc.cwd}) ---")
            rc_r, _ = await self.capture(
                ["dotnet", "restore", *proj_flag],
                cwd=svc.cwd,
                timeout=120,
            )
            if rc_r != 0:
                self.log(f"⚠️  dotnet restore failed for {svc.name} (exit {rc_r})")
                continue
            rc_b, _ = await self.capture(
                ["dotnet", "build", "--no-restore", *proj_flag],
                cwd=svc.cwd,
                timeout=180,
            )
            if rc_b != 0:
                self.log(f"⚠️  dotnet build failed for {svc.name} (exit {rc_b})")
            else:
                self.log(f"✅ {svc.name} rebuilt successfully")

    # ------------------------------------------------------------------
    # Infra, status, and health
    # ------------------------------------------------------------------
    async def start_infra(self) -> None:
        await self.run_command(["bash", "infrastructure/start.sh"], label="infrastructure/start.sh")

    async def stop_infra(self) -> None:
        await self.run_command(["bash", "infrastructure/stop.sh"], label="infrastructure/stop.sh")

    async def full_stack_start(self) -> None:
        await self.start_infra()
        await self.start_all_services()

    async def full_stack_stop(self) -> None:
        await self.stop_all_services()
        await self.stop_infra()

    async def lightweight_stack_start(self) -> None:
        """Start essentials: infra + YARP + UserService + Matchmaking + Messaging + Swipe.
        Leaves out: photo-service, safety-service, bot-service.
        Saves ~40% RAM vs full stack while keeping matches, messages, and swipes working."""
        await self.start_infra()
        await asyncio.sleep(2.0)  # Let DBs + Keycloak come up
        for key in ["yarp", "user", "matchmaking", "messaging", "swipe"]:
            await self.start_service(key)
            await asyncio.sleep(1.0)

    async def lightweight_stack_stop(self) -> None:
        """Stop lightweight stack: user, matchmaking, messaging, swipe, yarp + infra."""
        for key in ["user", "matchmaking", "messaging", "swipe", "yarp"]:
            await self.stop_service(key)
        await self.stop_infra()

    # ------------------------------------------------------------------
    # Vikunja (Kanban board) helpers
    # ------------------------------------------------------------------
    async def start_vikunja(self) -> None:
        """Start a local Vikunja container named 'datingapp-vikunja' on port 3456."""
        if port_open(3456):
            self.log("Vikunja already appears to be listening on :3456")
            return
        # Ensure data dir exists
        data_dir = ROOT / "vikunja-data"
        data_dir.mkdir(parents=True, exist_ok=True)
        # If container exists, start it; otherwise run a new container
        rc, out = await self.capture(["docker", "ps", "-a", "--filter", "name=datingapp-vikunja", "--format", "{{.Names}}"], timeout=6)
        if rc == 0 and "datingapp-vikunja" in out.splitlines():
            await self.run_command(["docker", "start", "datingapp-vikunja"], label="start vikunja")
        else:
            # Ensure subdirectories for DB and file storage exist
            db_dir = data_dir / "db"
            files_dir = data_dir / "files"
            db_dir.mkdir(parents=True, exist_ok=True)
            files_dir.mkdir(parents=True, exist_ok=True)

            # Fix ownership on host mount points so the Vikunja process (uid 1000) can write files.
            # Use an ephemeral alpine container (runs as root) to chown the mounted paths.
            await self.run_command([
                "docker",
                "run",
                "--rm",
                "-v",
                f"{str(db_dir)}:/target",
                "alpine",
                "sh",
                "-c",
                "chown -R 1000:0 /target || true",
            ], label="fix vikunja db ownership")
            await self.run_command([
                "docker",
                "run",
                "--rm",
                "-v",
                f"{str(files_dir)}:/target",
                "alpine",
                "sh",
                "-c",
                "chown -R 1000:0 /target || true",
            ], label="fix vikunja files ownership")

            # Run container with explicit mounts and env vars so Vikunja can use SQLite and file storage.
            # Provide several env-var name variants to satisfy different config loaders (SERVICE_PUBLICURL, SERVICE__PUBLICURL, etc.).
            await self.run_command([
                "docker",
                "run",
                "-d",
                "--name",
                "datingapp-vikunja",
                "-p",
                "3456:3456",
                "-v",
                f"{str(data_dir)}:/data",
                "-v",
                f"{str(db_dir)}:/db",
                "-v",
                f"{str(files_dir)}:/app/vikunja/files",
                "-e",
                "SERVICE_PUBLICURL=http://localhost:3456",
                "-e",
                "SERVICE__PUBLICURL=http://localhost:3456",
                "-e",
                "VIKUNJA_SERVICE_PUBLICURL=http://localhost:3456",
                "-e",
                "VIKUNJA__SERVICE__PUBLICURL=http://localhost:3456",
                "-e",
                "CORS_ENABLE=false",
                "-e",
                "CORS__ENABLE=false",
                "-e",
                "SERVICE__CORS__ENABLE=false",
                "-e",
                "VIKUNJA_CORS_ENABLE=false",
                "-e",
                "VIKUNJA_DATABASE_ADAPTER=sqlite",
                "vikunja/vikunja:latest",
            ], label="run vikunja")

            # Give Vikunja a few seconds to initialize and update status
            await asyncio.sleep(2.0)

    async def stop_vikunja(self) -> None:
        """Stop and remove the local Vikunja container if present."""
        await self.run_command(["docker", "stop", "datingapp-vikunja"], label="stop vikunja")
        await self.run_command(["docker", "rm", "datingapp-vikunja"], label="rm vikunja")

    async def refresh_vikunja(self) -> None:
        """Update Vikunja status label reflecting container/port state."""
        is_listening = port_open(3456)
        rc, out = await self.capture(["docker", "ps", "--filter", "name=datingapp-vikunja", "--format", "{{.Status}}"], timeout=4)
        status = out.strip() if rc == 0 and out.strip() else ("listening" if is_listening else "stopped")
        label_text = f"Vikunja: {'Up' if is_listening else 'Down'} ({status})"
        if self.vikunja_status_label is not None:
            self.vikunja_status_label.text = label_text

    async def service_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        client = httpx.AsyncClient(timeout=3)
        async with client:
            for service in SERVICES:
                port_state = port_open(service.port)
                health_code = "000"
                health_state = "Down"
                try:
                    response = await client.get(service.health_url)
                    health_code = str(response.status_code)
                    health_state = "Healthy" if response.status_code == 200 else "Warn"
                except Exception:
                    health_state = "Down"
                process = self.processes.get(service.key)
                pid = process.pid if process and process.returncode is None else ""
                rows.append(
                    {
                        "key": service.key,
                        "service": service.name,
                        "port": service.port,
                        "port_state": "Open" if port_state else "Closed",
                        "health": health_state,
                        "code": health_code,
                        "pid": pid,
                        "log": str(service.log_file.relative_to(ROOT)),
                    }
                )
        return rows

    async def infra_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        rc, out = await self.capture(["docker", "compose", "ps", "--format", "json"], timeout=20)
        by_name: dict[str, dict[str, Any]] = {}
        if rc == 0:
            for line in out.splitlines():
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                name = data.get("Service") or data.get("Name")
                if name:
                    by_name[name] = data
        for name in INFRA_SERVICES:
            data = by_name.get(name, {})
            rows.append(
                {
                    "service": name,
                    "state": data.get("State", "unknown"),
                    "status": data.get("Status", ""),
                    "publishers": data.get("Publishers", ""),
                }
            )
        return rows

    async def health_rows(self) -> list[dict[str, Any]]:
        probes = [
            ("Gateway", "http://localhost:8080/health"),
            ("Gateway diagnostics", "http://localhost:8080/api/Diagnostics"),
            ("Keycloak realm", "http://localhost:8090/realms/DatingApp"),
            ("UserService", "http://localhost:8082/health"),
            ("Matchmaking", "http://localhost:8083/health"),
            ("Matchmaking metrics", "http://localhost:8083/api/matchmaking/health"),
            ("PhotoService", "http://localhost:8085/health"),
            ("Photo detailed", "http://localhost:8085/api/health/detailed"),
            ("Messaging", "http://localhost:8086/health"),
            ("Swipe", "http://localhost:8087/health"),
            ("Safety", "http://localhost:8088/health"),
            ("BotService", "http://localhost:8089/health"),
            ("Bot status", "http://localhost:8089/api/Bot/status"),
        ]
        rows: list[dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=5) as client:
            for name, url in probes:
                started = time.monotonic()
                try:
                    response = await client.get(url)
                    latency = int((time.monotonic() - started) * 1000)
                    ok = response.status_code < 400
                    rows.append(
                        {
                            "probe": name,
                            "status": "OK" if ok else "Warn",
                            "code": response.status_code,
                            "latency": f"{latency} ms",
                            "url": url,
                        }
                    )
                except Exception as exc:
                    rows.append(
                        {
                            "probe": name,
                            "status": "Down",
                            "code": "000",
                            "latency": "-",
                            "url": url,
                            "error": str(exc),
                        }
                    )
        return rows

    async def db_rows(self) -> list[dict[str, Any]]:
        checks = [
            ("UserServiceDb", "UserService-db", "UserServiceDb", "UserProfiles"),
            ("Matchmaking matches", "MatchmakingService-db", "MatchmakingServiceDb", "Matches"),
            ("Matchmaking interactions", "MatchmakingService-db", "MatchmakingServiceDb", "UserInteractions"),
            ("Swipe swipes", "swipe-service-db", "SwipeServiceDb", "Swipes"),
            ("Swipe matches", "swipe-service-db", "SwipeServiceDb", "Matches"),
            ("Swipe mappings", "swipe-service-db", "SwipeServiceDb", "UserProfileMappings"),
            ("Photo metadata", "photo-service-db", "PhotoServiceDb", "Photos"),
        ]
        rows: list[dict[str, Any]] = []
        for label, container, database, table in checks:
            query = f"SELECT COUNT(*) FROM {database}.{table};"
            rc, out = await self.capture(
                ["docker", "exec", container, "mysql", "-uroot", "-proot_password", "-N", "-e", query],
                timeout=8,
            )
            count = out.strip().splitlines()[-1] if rc == 0 and out.strip() else "?"
            rows.append(
                {
                    "name": label,
                    "container": container,
                    "table": f"{database}.{table}",
                    "status": "OK" if rc == 0 else "Unknown",
                    "count": count,
                }
            )

        script = (
            "mysql -uroot -proot_password -N -e "
            "'SELECT COUNT(*) FROM MessagingServiceDb.Messages;' "
            "|| mysql -uroot -proot_password -N -e "
            "'SELECT COUNT(*) FROM MessagingDb.Messages;'"
        )
        rc, out = await self.capture(["docker", "exec", "messaging-service-db", "sh", "-lc", script], timeout=8)
        rows.append(
            {
                "name": "Messaging messages",
                "container": "messaging-service-db",
                "table": "Messages",
                "status": "OK" if rc == 0 else "Unknown",
                "count": out.strip().splitlines()[-1] if rc == 0 and out.strip() else "?",
            }
        )

        bot_db = ROOT / "bot-service" / "BotService" / "bot-service.db"
        if bot_db.exists():
            rc, out = await self.capture(
                ["sqlite3", str(bot_db), "SELECT COUNT(*) FROM BotStates;"],
                timeout=5,
            )
            rows.append(
                {
                    "name": "BotService bot states",
                    "container": "sqlite",
                    "table": "BotStates",
                    "status": "OK" if rc == 0 else "Unknown",
                    "count": out.strip() if rc == 0 else "?",
                }
            )
        return rows

    async def refresh_all(self) -> None:
        await self.refresh_status()
        await self.refresh_infra()
        await self.refresh_health()
        await self.refresh_bots()
        await self.refresh_android()
        await self.refresh_vikunja()

    async def refresh_status(self) -> None:
        rows = await self.service_rows()
        if self.service_table is not None:
            self.service_table.rows = rows
            self.service_table.update()
        healthy = sum(1 for row in rows if row["health"] == "Healthy")
        if self.status_label is not None:
            self.status_label.text = f"Stack: {healthy}/{len(rows)} healthy"
        self.last_refresh = now_label()
        if self.refresh_label is not None:
            self.refresh_label.text = f"Last refresh: {self.last_refresh}"

    async def refresh_infra(self) -> None:
        if self.infra_table is not None:
            self.infra_table.rows = await self.infra_rows()
            self.infra_table.update()

    async def refresh_health(self) -> None:
        if self.health_table is not None:
            self.health_table.rows = await self.health_rows()
            self.health_table.update()
        if self.db_table is not None:
            self.db_table.rows = await self.db_rows()
            self.db_table.update()

    # ------------------------------------------------------------------
    # Bot and fresh-start operations
    # ------------------------------------------------------------------
    async def bot_json(self, path: str, method: str = "GET", json_body: dict[str, Any] | None = None) -> Any:
        url = f"http://localhost:8089{path}"
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.request(method, url, json=json_body)
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}

    async def refresh_bots(self) -> None:
        bot_rows: list[dict[str, Any]] = []
        finding_rows: list[dict[str, Any]] = []
        try:
            status = await self.bot_json("/api/Bot/status")
            bots = status.get("bots", [])
            for bot in bots:
                bot_rows.append(
                    {
                        "persona": bot.get("personaId") or bot.get("PersonaId"),
                        "status": bot.get("status"),
                        "profile": bot.get("profileId"),
                        "swipes": bot.get("swipesToday"),
                        "messages": bot.get("messagesSentToday"),
                        "matches": bot.get("matchCount"),
                        "last": bot.get("lastAction") or "",
                    }
                )
        except Exception as exc:
            bot_rows.append({"persona": "BotService unavailable", "status": str(exc)})

        try:
            summary = await self.bot_json("/api/Findings/summary")
            for key in ("bySeverity", "byType", "byService"):
                data = summary.get(key) or {}
                if isinstance(data, dict):
                    for name, count in data.items():
                        finding_rows.append({"group": key, "name": name, "count": count})
            llm = await self.bot_json("/api/Findings/llm-stats")
            finding_rows.append(
                {
                    "group": "llm",
                    "name": f"{llm.get('primaryProvider', 'provider')} budget",
                    "count": f"{llm.get('tokensUsedToday', 0)}/{llm.get('dailyBudget', 0)}",
                }
            )
        except Exception as exc:
            finding_rows.append({"group": "Findings unavailable", "name": str(exc), "count": ""})

        if self.bot_table is not None:
            self.bot_table.rows = bot_rows
            self.bot_table.update()
        if self.findings_table is not None:
            self.findings_table.rows = finding_rows
            self.findings_table.update()

    async def get_demo_token(self) -> str:
        token_url = "http://localhost:8090/realms/DatingApp/protocol/openid-connect/token"
        payload = {
            "grant_type": "password",
            "client_id": "dejtingapp-flutter",
            "username": DEMO_USERNAME,
            "password": DEMO_PASSWORD,
            "scope": "openid profile email",
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(token_url, data=payload)
            response.raise_for_status()
            token = response.json().get("access_token")
            if not token:
                raise RuntimeError("ROPC response did not include access_token")
            return str(token)

    async def active_bot_profile_ids(self) -> list[int]:
        try:
            status = await self.bot_json("/api/Bot/status")
            result: list[int] = []
            for bot in status.get("bots", []):
                persona = (bot.get("personaId") or "").lower()
                state = (bot.get("status") or "").lower()
                profile_id = bot.get("profileId")
                if persona == "demo-user":
                    continue
                if state in {"active", "idle"} and isinstance(profile_id, int):
                    result.append(profile_id)
            return result or FALLBACK_BOT_PROFILE_IDS
        except Exception:
            return FALLBACK_BOT_PROFILE_IDS

    async def fresh_start(self, *, clear_app_data: bool, launch_app: bool) -> None:
        self.log("Fresh start: pausing demo-user bot")
        try:
            await self.bot_json("/api/Bot/pause/demo-user", method="POST")
        except Exception as exc:
            self.log(f"Could not pause demo-user bot: {exc}")

        self.log("Fresh start: acquiring demo token")
        token = await self.get_demo_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        self.log("Fresh start: reset interactions through YARP")
        async with httpx.AsyncClient(timeout=30) as client:
            reset = await client.post("http://localhost:8080/api/admin/reset-interactions", headers=headers)
            self.log(f"Admin reset status: {reset.status_code} {reset.text[:500]}")

        self.log("Fresh start: reset bot counters")
        try:
            await self.bot_json("/api/Bot/reset-counters", method="POST")
        except Exception as exc:
            self.log(f"Bot counter reset failed: {exc}")

        bot_profile_ids = await self.active_bot_profile_ids()
        self.log(f"Fresh start: seeding mutual likes for bot profiles {bot_profile_ids}")
        async with httpx.AsyncClient(timeout=15) as client:
            for bot_id in bot_profile_ids:
                response = await client.post(
                    "http://localhost:8080/api/swipes",
                    headers=headers,
                    json={"targetUserId": str(bot_id), "direction": "like"},
                )
                self.log(f"demo-user -> {bot_id}: {response.status_code}")

            for bot_id in bot_profile_ids:
                response = await client.post(
                    "http://localhost:8080/api/swipes/batch",
                    headers={"Content-Type": "application/json"},
                    json={
                        "userId": bot_id,
                        "swipes": [{"targetUserId": str(DEMO_PROFILE_ID), "isLike": True}],
                    },
                )
                self.log(f"{bot_id} -> demo-user: {response.status_code}")

        if clear_app_data:
            await self.clear_app_data()
        if launch_app:
            await self.launch_android_app()

    # ------------------------------------------------------------------
    # Android operations
    # ------------------------------------------------------------------
    async def adb_devices(self) -> list[dict[str, str]]:
        rc, out = await self.capture(["adb", "devices", "-l"], timeout=8)
        devices: list[dict[str, str]] = []
        if rc != 0:
            return devices
        for line in out.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            serial = parts[0]
            state = parts[1] if len(parts) > 1 else "unknown"
            detail = " ".join(parts[2:])
            devices.append({"serial": serial, "state": state, "detail": detail})
        return devices

    async def refresh_android(self) -> None:
        devices = await self.adb_devices()
        if devices and (not self.selected_device or self.selected_device not in {d["serial"] for d in devices}):
            self.selected_device = devices[0]["serial"]
        if self.android_table is not None:
            self.android_table.rows = devices
            self.android_table.update()
        if self.device_label is not None:
            self.device_label.text = f"Device: {self.selected_device or 'none'}"

    async def adb(self, args: list[str], *, label: str | None = None) -> int:
        if not self.selected_device:
            self.log("No Android device selected")
            ui.notify("No Android device selected", type="warning")
            return 1
        return await self.run_command(["adb", "-s", self.selected_device, *args], label=label)

    async def start_emulator(self, avd: str, memory: int) -> None:
        await self.run_command(["bash", "scripts/start-emulator.sh", avd, str(memory)], label="start emulator")

    async def stop_emulator(self) -> None:
        await self.adb(["emu", "kill"], label="stop emulator")

    async def build_apk(self, mode: str) -> None:
        if not FLUTTER_ROOT.exists():
            self.log(f"Flutter root missing: {FLUTTER_ROOT}")
            if self.android_status is not None:
                self.android_status.text = "❌ Flutter root missing"
            return
        # Clear previous build log
        if self.android_log is not None:
            self.android_log.clear()
            self.android_log.push(f"Starting flutter build apk --{mode}...")
        # Run in background — dashboard stays responsive
        await self.run_command_streaming(
            ["flutter", "build", "apk", f"--{mode}"],
            cwd=FLUTTER_ROOT,
            label=f"Build APK ({mode})",
        )

    def apk_path(self, mode: str) -> Path:
        file_name = "app-release.apk" if mode == "release" else "app-debug.apk"
        return FLUTTER_ROOT / "build" / "app" / "outputs" / "flutter-apk" / file_name

    async def install_apk(self, mode: str) -> None:
        apk = self.apk_path(mode)
        if not apk.exists():
            self.log(f"APK missing: {apk}. Build it first.")
            if self.android_status is not None:
                self.android_status.text = "❌ APK missing — build first"
            ui.notify("APK missing; build first", type="warning")
            return
        if not self.selected_device:
            self.log("No Android device selected")
            ui.notify("No Android device selected", type="warning")
            return
        # Clear previous log
        if self.android_log is not None:
            self.android_log.clear()
            self.android_log.push(f"Installing {apk.name}...")
        await self.run_command_streaming(
            ["adb", "-s", self.selected_device, "install", "-r", "-g", str(apk)],
            label=f"Install APK ({mode})",
        )

    async def launch_android_app(self) -> None:
        await self.adb(["shell", "am", "start", "-n", f"{APP_PACKAGE}/{APP_ACTIVITY}"], label="launch app")


    async def flutter_run(self) -> None:
        """Launch `flutter run -d linux` — desktop app at phone-like dimensions.

        No emulator needed. The Linux desktop target renders the exact same Flutter
        UI as Android but runs natively with zero emulation overhead. Resize the
        window to phone proportions (~412x915) for a device-accurate preview.
        """
        if not FLUTTER_ROOT.exists():
            self.log(f"Flutter root missing: {FLUTTER_ROOT}")
            if self.android_status is not None:
                self.android_status.text = "❌ Flutter root missing"
            ui.notify("Flutter root missing", type="negative")
            return

        # Clear previous log
        if self.android_log is not None:
            self.android_log.clear()
            self.android_log.push(
                "Launching Flutter desktop (linux) — no emulator needed. "
                "Resize window to ~412x915 for phone-like dimensions."
            )
        await self.run_command_streaming(
            ["flutter", "run", "-d", "linux", "--debug"],
            cwd=FLUTTER_ROOT,
            label="Flutter Run (desktop — phone-size window)",
        )

    async def force_stop_app(self) -> None:
        await self.adb(["shell", "am", "force-stop", APP_PACKAGE], label="force-stop app")
        await self.adb(["shell", "am", "force-stop", APP_PACKAGE], label="force-stop app")

    async def clear_app_data(self) -> None:
        await self.adb(["shell", "pm", "clear", APP_PACKAGE], label="clear app data")

    async def grant_permissions(self) -> None:
        for permission in ANDROID_PERMISSIONS:
            await self.adb(["shell", "pm", "grant", APP_PACKAGE, permission], label=f"grant {permission}")

    async def current_activity(self) -> None:
        rc, out = await self.capture(
            ["adb", "-s", self.selected_device or "", "shell", "dumpsys", "activity", "activities"],
            timeout=10,
        )
        if rc != 0:
            self.log(out)
            return
        for line in out.splitlines():
            if "mResumedActivity" in line or "topResumedActivity" in line:
                self.log(line.strip())
                return
        self.log("No resumed activity found")

    # ------------------------------------------------------------------
    # Smoke tests and logs
    # ------------------------------------------------------------------
    async def run_smoke(self, kind: str) -> None:
        python = ROOT / ".venv" / "bin" / "python"
        commands = {
            "health": ["bash", "scripts/health-check.sh"],
            "api": [str(python), "api_tests.py"],
            "all": [str(python), "api_tests.py", "--all"],
            "safety": [str(python), "api_tests.py", "--safety"],
            "wizard": [str(python), "api_tests.py", "--wizard"],
            "reset_seed": [str(python), "scripts/reset-and-seed.py"],
        }
        command = commands[kind]
        if self.smoke_log is not None:
            self.smoke_log.push(f"[{now_label()}] Running {kind}: {shell_join(command)}")
        rc = await self.run_command(command, label=f"smoke {kind}")
        if self.smoke_log is not None:
            self.smoke_log.push(f"[{now_label()}] {kind} finished with exit code {rc}")

    async def tail_selected_log(self) -> None:
        if self.log_select is None or self.log_tail is None:
            return
        selected = self.log_select.value
        path = ROOT / selected
        if not path.exists():
            self.log_tail.value = f"No log file at {selected}"
            return
        lines = path.read_text(errors="replace").splitlines()[-120:]
        self.log_tail.value = "\n".join(lines)

    # ------------------------------------------------------------------
    # UI layout
    # ------------------------------------------------------------------
    def build(self) -> None:
        ui.add_head_html(
            """
            <style>
              body { background: #f7f8fb; }
              .q-drawer { background: #111827; color: white; }
              .section-title { font-size: 18px; font-weight: 700; margin: 8px 0; }
              .toolbar { gap: 8px; align-items: center; flex-wrap: wrap; }
              .metric { min-width: 150px; padding: 10px 12px; border: 1px solid #e5e7eb; background: white; }
              .metric .label { font-size: 12px; color: #6b7280; }
              .metric .value { font-size: 18px; font-weight: 700; }
            </style>
            """
        )

        with ui.header().classes("bg-white text-gray-900 border-b border-gray-200"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("DatingApp Dev Control").classes("text-xl font-bold")
                with ui.row().classes("gap-6 text-sm"):
                    self.status_label = ui.label("Stack: unknown")
                    self.device_label = ui.label("Device: none")
                    self.job_label = ui.label("Job: Idle")
                    self.unstick_btn = ui.button("Unstick", on_click=self.force_unbusy, icon="lock_open", color="warning").props("dense size=sm")
                    self.unstick_btn.tooltip("Force-release stuck guard if a command hung")
                    self.unstick_btn.visible = False
                    self.refresh_label = ui.label("Last refresh: never")

        with ui.left_drawer(value=True).props("width=220 behavior=desktop"):
            ui.label("Control").classes("px-4 pt-4 text-xs uppercase tracking-wide text-gray-400")
            with ui.tabs().props("vertical").classes("w-full") as tabs:
                tab_stack = ui.tab("Stack", icon="dns")
                tab_fresh = ui.tab("Fresh Start", icon="restart_alt")
                tab_vikunja = ui.tab("Vikunja", icon="post_add")
                tab_conn = ui.tab("Connection", icon="link")
                tab_android = ui.tab("Android", icon="smartphone")
                tab_health = ui.tab("Health", icon="monitor_heart")
                tab_bots = ui.tab("Bots & AI", icon="smart_toy")
                tab_smoke = ui.tab("Smoke Tests", icon="fact_check")
                tab_logs = ui.tab("Logs", icon="article")
                tab_billing = ui.tab("Billing", icon="paid")
                tab_ai_cache = ui.tab("AI & Costs", icon="auto_awesome")

        with ui.column().classes("w-full p-4 gap-4"):
            with ui.tab_panels(tabs, value=tab_stack).classes("w-full"):
                self._build_stack_panel(tab_stack)
                self._build_fresh_panel(tab_fresh)
                self._build_vikunja_panel(tab_vikunja)
                self._build_connection_panel(tab_conn)
                self._build_android_panel(tab_android)
                self._build_health_panel(tab_health)
                self._build_bots_panel(tab_bots)
                self._build_smoke_panel(tab_smoke)
                self._build_logs_panel(tab_logs)
                self._build_billing_panel(tab_billing)
                self._build_ai_cache_panel(tab_ai_cache)

        ui.timer(5.0, self.refresh_all)
        ui.timer(3.0, self.tail_selected_log)
        ui.timer(0.2, self.refresh_all, once=True)

    def _build_stack_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Stack").classes("section-title")

            # ── Bulk action rows (grouped by category) ──
            with ui.row().classes("toolbar"):
                self.add_button("Refresh", self.refresh_all, icon="refresh", tooltip="Reload all dashboard panels")
            with ui.row().classes("toolbar"):
                self.add_button("Start Full Stack", lambda: self.guarded("Start full stack", self.full_stack_start), icon="play_arrow", color="positive", tooltip="Start Docker infra + all .NET services")
                self.add_button("Stop Full Stack", lambda: self.confirm("Stop full stack", "Stops local services and infrastructure containers.", lambda: self.guarded("Stop full stack", self.full_stack_stop)), icon="stop", color="negative", tooltip="Stop all services + Docker infra")
            with ui.row().classes("toolbar"):
                self.add_button("⚡ Start Lightweight", lambda: self.guarded("Start lightweight", self.lightweight_stack_start), icon="bolt", color="positive", tooltip="Only Keycloak + DBs + YARP + UserService (~60% less RAM)")
                self.add_button("⚡ Stop Lightweight", lambda: self.confirm("Stop lightweight", "Stops UserService, YARP, and Docker infra.", lambda: self.guarded("Stop lightweight", self.lightweight_stack_stop)), icon="stop", color="warning", tooltip="Stop lightweight stack")
            with ui.row().classes("toolbar"):
                self.add_button("Start Infra", lambda: self.guarded("Start infrastructure", self.start_infra), icon="hub", tooltip="Start Docker: Keycloak, DBs, MailHog")
                self.add_button("Stop Infra", lambda: self.confirm("Stop infrastructure", "Stops Keycloak, database, and mail containers.", lambda: self.guarded("Stop infrastructure", self.stop_infra)), icon="power_settings_new", color="warning", tooltip="Stop Docker containers (data persists in volumes)")
            with ui.row().classes("toolbar"):
                self.add_button("Start Services", lambda: self.guarded("Start services", self.start_all_services), icon="play_circle", tooltip="Start all 8 .NET backend services")
                self.add_button("Stop Services", lambda: self.confirm("Stop local services", "Stops all locally running .NET services.", lambda: self.guarded("Stop services", self.stop_all_services)), icon="stop_circle", color="warning", tooltip="Stop all .NET backend processes (Docker stays up)")
                self.add_button("Rebuild All Services", lambda: self.confirm("Rebuild all services", "Runs dotnet restore && dotnet build for all 8 backend services. Services will be rebuilt but not restarted — use Start Services afterward.", lambda: self.guarded("Rebuild all services", self.rebuild_all_services)), icon="build", color="secondary", tooltip="dotnet restore && dotnet build for all .NET services")

            columns = [
                {"name": "service", "label": "Service", "field": "service", "sortable": True},
                {"name": "port", "label": "Port", "field": "port"},
                {"name": "port_state", "label": "Port", "field": "port_state"},
                {"name": "health", "label": "Health", "field": "health"},
                {"name": "code", "label": "Code", "field": "code"},
                {"name": "pid", "label": "PID", "field": "pid"},
                {"name": "log", "label": "Log", "field": "log"},
            ]
            self.service_table = ui.table(columns=columns, rows=[], row_key="key").classes("w-full")

            # ── Per-service Start / Stop in a 4-column grid ──
            ui.label("Individual Services").classes("section-title")
            with ui.element("div").classes("grid grid-cols-4 gap-2"):
                for service in SERVICES:
                    with ui.element("div").classes("flex items-center gap-1 p-2 border rounded bg-white"):
                        ui.label(service.name).classes("text-sm font-semibold min-w-[6rem]")
                        self.add_button(
                            "",
                            lambda key=service.key: self.guarded(f"Start {SERVICE_BY_KEY[key].name}", lambda key=key: self.start_service(key)),
                            icon="play_arrow",
                            tooltip=f"Start {service.name}",
                        )
                        self.add_button(
                            "",
                            lambda key=service.key: self.guarded(f"Stop {SERVICE_BY_KEY[key].name}", lambda key=key: self.stop_service(key)),
                            icon="stop",
                            color="warning",
                            tooltip=f"Stop {service.name}",
                        )

            # ── Live status output (same event log) ──
            ui.label("Status Output").classes("section-title")
            self.stack_event_log = ui.log(max_lines=200).classes("w-full h-48")

            ui.label("Infrastructure containers").classes("section-title")
            infra_columns = [
                {"name": "service", "label": "Service", "field": "service"},
                {"name": "state", "label": "State", "field": "state"},
                {"name": "status", "label": "Status", "field": "status"},
                {"name": "publishers", "label": "Ports", "field": "publishers"},
            ]
            self.infra_table = ui.table(columns=infra_columns, rows=[], row_key="service").classes("w-full")

    def _build_fresh_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Fresh Start").classes("section-title")
            ui.label(
                "Reset interactions, keep demo-user bot paused, seed active bot matches, and optionally relaunch the app."
            ).classes("text-sm text-gray-600")
            clear_data = ui.checkbox("Clear selected Android app data before launch", value=False)
            launch_app = ui.checkbox("Launch selected Android app after reset", value=True)
            with ui.row().classes("toolbar"):
                self.add_button(
                    "Run Fresh Start",
                    lambda: self.confirm(
                        "Run fresh start",
                        "This resets matches, messages, and swipes in the dev stack, then seeds demo matches.",
                        lambda: self.guarded(
                            "Fresh start",
                            lambda: self.fresh_start(
                                clear_app_data=bool(clear_data.value),
                                launch_app=bool(launch_app.value),
                            ),
                        ),
                    ),
                    icon="restart_alt",
                    color="positive",
                    tooltip="Composite reset: pause demo-user bot → YARP admin reset → reset bot counters → seed mutual likes → optionally clear Android app data → optionally launch app",
                )
                self.add_button("Pause demo-user bot", lambda: self.guarded("Pause demo-user bot", lambda: self.bot_json("/api/Bot/pause/demo-user", method="POST")), icon="pause", tooltip="Pause the bot-service agent for demo-user so it doesn't auto-swipe or auto-message while you test")
                self.add_button("Reset bot counters", lambda: self.guarded("Reset bot counters", lambda: self.bot_json("/api/Bot/reset-counters", method="POST")), icon="restart_alt", tooltip="Zero out daily swipe/message counters for all bot personas so they resume activity")

            with ui.row().classes("gap-3"):
                with ui.element("div").classes("metric"):
                    ui.label("Login user").classes("label")
                    ui.label(DEMO_USERNAME).classes("value")
                with ui.element("div").classes("metric"):
                    ui.label("Gateway reset").classes("label")
                    ui.label("/api/admin/reset-interactions").classes("value")
                with ui.element("div").classes("metric"):
                    ui.label("App package").classes("label")
                    ui.label(APP_PACKAGE).classes("value")

    def _build_vikunja_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Vikunja Board").classes("section-title")
            ui.label("Local Kanban board for the DatingApp MVP").classes("text-sm text-gray-600 mb-2")

            with ui.row().classes("toolbar"):
                self.add_button(
                    "Start Vikunja",
                    lambda: self.guarded("Start Vikunja", self.start_vikunja),
                    icon="play_arrow",
                    color="positive",
                    tooltip="Start a local Vikunja container on port 3456",
                )
                self.add_button(
                    "Stop Vikunja",
                    lambda: self.confirm(
                        "Stop Vikunja",
                        "Stop and remove the local Vikunja container?",
                        lambda: self.guarded("Stop Vikunja", self.stop_vikunja),
                    ),
                    icon="stop",
                    color="negative",
                    tooltip="Stop the local Vikunja container",
                )
                self.add_button(
                    "Check Status",
                    lambda: self.guarded("Refresh Vikunja status", self.refresh_vikunja),
                    icon="refresh",
                    tooltip="Refresh Vikunja container and port status",
                )
                ui.link("Open Vikunja", "http://localhost:3456", new_tab=True).classes("ml-2")

            ui.label("Status").classes("subsection-title mt-4")
            self.vikunja_status_label = ui.label("Vikunja: unknown").classes("text-sm font-mono p-2 bg-gray-50 rounded")

    # ── Connection Diagnostics helpers ───────────────────────────────────────

    # Network interfaces that matter for device connectivity (skip virtual/Docker)
    _DEVICE_IFACE_PREFIXES = ("wl", "wlan", "eth", "enp", "enx", "wlp", "usb")

    async def _get_laptop_ips(self) -> dict[str, str]:
        """Return laptop network interface IPs useful for device connectivity."""
        ips: dict[str, str] = {}
        rc, out = await self.capture(["ip", "-4", "-br", "addr", "show"], timeout=3)
        if rc != 0:
            return ips
        for line in out.strip().splitlines():
            parts = line.split()
            if len(parts) < 3:
                continue
            iface, ip_cidr = parts[0], parts[2]
            ip = ip_cidr.split("/")[0]
            if iface == "lo" or ip.startswith("127."):
                continue
            if any(iface.startswith(pfx) for pfx in self._DEVICE_IFACE_PREFIXES):
                label = {
                    "enx": "USB Tether",
                    "enp": "Ethernet",
                    "wlp": "WiFi",
                    "wl": "WiFi",
                    "wlan": "WiFi",
                    "eth": "Ethernet",
                }
                name = label.get(
                    next((pfx for pfx in self._DEVICE_IFACE_PREFIXES if iface.startswith(pfx)), ""),
                    iface,
                )
                ips[name] = ip
        # Also check hostname -I for any additional useful IPs
        rc2, out2 = await self.capture(["hostname", "-I"], timeout=3)
        if rc2 == 0:
            for ip in out2.strip().split():
                if ip.count(".") == 3 and not ip.startswith(("172.", "100.")):
                    # Only add if it's not a docker/vm IP and not already present
                    if ip not in ips.values():
                        ips.setdefault("LAN", ip)
        return ips

    async def _resolve_host(self, host: str) -> str:
        """Resolve a hostname to an IP address. Returns empty string on failure."""
        rc, out = await self.capture(["getent", "hosts", host], timeout=3)
        if rc == 0 and out.strip():
            return out.strip().split()[0]
        # Fallback: try 'host' command
        rc2, out2 = await self.capture(["host", host], timeout=5)
        if rc2 == 0:
            for token in out2.split():
                if token.count(".") == 3:
                    return token
        return ""

    async def _ping_from_device(self, serial: str, host: str, timeout: int = 3) -> tuple[bool, str]:
        """Ping a host from the device. Returns (reachable, detail)."""
        # If host is a hostname, resolve it first
        target = host
        if not host[0].isdigit() and not host.startswith("10.") and not host.startswith("192."):
            target = await self._resolve_host(host)
            if not target:
                return False, f"DNS failure: cannot resolve {host}"
        cmd = ["adb", "-s", serial, "shell", "ping", "-c1", f"-W{timeout}", target]
        rc, out = await self.capture(cmd, timeout=timeout + 5)
        if rc == 0 and "1 received" in out:
            import re
            m = re.search(r"time=([0-9.]+)\s*ms", out)
            latency = f"{float(m.group(1)):.1f}ms" if m else "OK"
            return True, latency
        if "unknown host" in out.lower() or "bad address" in out.lower():
            return False, f"DNS failure: {host} not resolvable from device"
        return False, "unreachable" if "100% packet loss" in out else (out.strip().splitlines()[-1] if out.strip() else "timeout")

    def _build_connection_rows(self, device_serial: str, laptop_ips: dict[str, str]) -> list[dict]:
        """Build diagnostic rows — only useful paths."""
        rows = []
        # Emulator path
        rows.append({
            "path": "Emulator → Local",
            "url": "http://10.0.2.2:8080",
            "host": "10.0.2.2",
            "verdict": "⏳",
            "detail": "Run diagnostics",
            "suggestion": "",
        })

        # Each laptop interface that a phone could reach
        for iface, ip in laptop_ips.items():
            rows.append({
                "path": f"Device → {iface} ({ip})",
                "url": f"http://{ip}:8080",
                "host": ip,
                "verdict": "⏳",
                "detail": "Run diagnostics",
                "suggestion": "",
            })

        # Funnel
        rows.append({
            "path": "Device → Funnel (internet)",
            "url": "https://a.tail45c6a7.ts.net/health",
            "host": "a.tail45c6a7.ts.net",
            "verdict": "⏳",
            "detail": "Run diagnostics",
            "suggestion": "",
        })
        return rows

    def _build_action_plan(self, rows: list[dict]) -> str:
        """Generate a clear action plan from diagnostic results."""
        success_paths = [r for r in rows if r["verdict"] == "✅"]
        failed_paths = [r for r in rows if r["verdict"] != "✅" and r["verdict"] != "⏳"]
        device_serial = rows[1].get("host", "") if len(rows) > 1 else ""

        lines = ["## Action Plan"]

        if not success_paths:
            lines.append("")
            lines.append("**No working paths found.** Follow these in order:")
            is_phone = not device_serial.startswith("emulator-")
            emu_row = next((r for r in rows if "Emulator" in r["path"]), None)
            funnel_row = next((r for r in rows if "Funnel" in r["path"]), None)

            if emu_row and emu_row["verdict"] == "❌":
                lines.append("")
                lines.append("### Emulator (always the easiest)")
                lines.append("1. Start the emulator from the Android tab")
                lines.append("2. The emulator uses `10.0.2.2` — no WiFi needed")
                lines.append("3. Works even when the laptop is offline")

            if is_phone:
                lines.append("")
                lines.append("### Phone — try these in reliability order:")
                lines.append("")
                lines.append("**🥇 WiFi Hotspot (MOST RELIABLE):**")
                lines.append("1. On laptop: Settings → WiFi → 'Create Hotspot' (or use `nmcli dev wifi hotspot`)")
                lines.append("2. Connect your phone to the laptop's hotspot")
                lines.append("3. The laptop becomes the router — both devices are on the same network")
                lines.append("4. IP is stable (usually 10.42.0.1) — won't change on reconnect")
                lines.append("5. In the app, use dev server **Custom** with the hotspot IP")
                lines.append("")
                lines.append("**🥈 Same WiFi Network:**")
                lines.append("1. Connect phone and laptop to the SAME WiFi router")
                lines.append("2. Both get IPs on the same subnet (e.g. 192.168.1.x)")
                lines.append("3. In the app, use dev server **Server (LAN)**")
                lines.append("4. ⚠️ Doesn't work if WiFi isolates clients (hotel/office WiFi)")
                lines.append("")
                lines.append("**🥉 USB Tether (WORKS BUT FRAGILE):**")
                lines.append("1. Connect phone via USB, enable USB tethering on phone")
                lines.append("2. ⚠️ The IP changes EVERY time you reconnect the cable")
                lines.append("3. Some carriers block tethering entirely")
                lines.append("4. Only use this if options 1-2 don't work")
                lines.append("5. Re-run diagnostics after reconnecting to find the new IP")
                lines.append("")
                lines.append("**4️⃣ Funnel (works over internet):**")
                lines.append("1. Requires the server (192.168.1.103) to be running")
                lines.append("2. Works from any internet connection (4G, public WiFi)")
                lines.append("3. In the app, use dev server **Funnel**")
                lines.append("4. URL: `https://a.tail45c6a7.ts.net`")
                lines.append("5. ⚠️ Free Tailscale Funnel is rate-limited, not for heavy use")

            if funnel_row and funnel_row["verdict"] == "❌" and "DNS" in funnel_row.get("detail", ""):
                lines.append("")
                lines.append("### Funnel DNS not resolving")
                lines.append("1. Your device may not have internet access (no 4G/WiFi)")
                lines.append("2. Funnel requires an internet connection — it does NOT work offline")
                lines.append("3. If you're on a plane/train without internet, use WiFi Hotspot instead")
            elif funnel_row and funnel_row["verdict"] == "❌":
                lines.append("")
                lines.append("### Funnel host is down")
                lines.append("1. Check the server: `ssh a@192.168.1.103` then `tailscale funnel status`")
                lines.append("2. The free-tier Funnel only exposes one port (YARP :8080)")

        else:
            lines.append("")
            lines.append("**Working paths found!** ✅")
            for r in success_paths:
                if "Emulator" in r["path"]:
                    lines.append(f"- {r['path']}: Set app to **Local (Emulator)** mode")
                elif "Funnel" in r["path"]:
                    lines.append(f"- {r['path']}: Set app to **Funnel** mode — works over any internet")
                elif "Tether" in r["path"]:
                    ip = r.get("host", "")
                    lines.append(f"- {r['path']}: Set app to **Custom** with host `{ip}`")
                    lines.append(f"  ⚠️ This IP CHANGES when you reconnect USB. Bookmark this page to re-run diagnostics.")
                else:
                    ip = r.get("host", "")
                    lines.append(f"- {r['path']}: Set app to **Custom** with host `{ip}`")

            lines.append("")
            lines.append("To switch dev server in the Flutter app:")
            lines.append("1. Open the app's debug panel (gear icon or settings overlay)")
            lines.append("2. Under 'Dev Server', select the matching option")
            lines.append("3. The server status dot in the top bar turns green when connected")

            # Note what the phone only needs YARP
            lines.append("")
            lines.append("**Important:** The app only needs to reach YARP at port `:8080`.")
            lines.append("YARP proxies all requests to the other services internally.")

            emu_ok = any("Emulator" in r["path"] and r["verdict"] == "✅" for r in rows)
            phone_ok = any("Device" in r["path"] and r["verdict"] == "✅" for r in rows)
            if emu_ok and not phone_ok:
                lines.append("")
                lines.append("**Emulator works but phone doesn't — normal.** The phone is on a different network. Use WiFi Hotspot or Funnel.")

        return "\n".join(lines)

    # ── Connection panel UI ───────────────────────────────────────────────────

    def _build_connection_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Connection Diagnostics").classes("section-title")
            ui.label(
                "Check whether your Android device (emulator or phone) can reach the backend server. "
                "Different network setups require different backend URLs."
            ).classes("text-sm text-gray-600 mb-2")

            # ── Laptop network info ──
            ui.label("Laptop Network Interfaces (device-relevant)").classes("subsection-title")
            self.conn_netinfo = ui.label("Click 'Refresh Network Info' to detect").classes("text-sm font-mono p-2 bg-gray-50 rounded")
            self.conn_ips: dict[str, str] = {}

            # ── Toolbar ──
            with ui.row().classes("toolbar"):
                self.add_button(
                    "Refresh Network Info",
                    lambda: self.guarded("Detect network info", self._refresh_network_info),
                    icon="wifi_find",
                    tooltip="Detect laptop IPs that a phone can actually connect to (WiFi, Ethernet, USB tether)",
                )
                self.add_button(
                    "Run Full Diagnostics",
                    lambda: self.guarded("Run connection diagnostics", self._run_connection_diagnostics),
                    icon="troubleshoot",
                    color="positive",
                    tooltip="Test ALL paths from the selected device (ping each IP + Funnel DNS check) and generate an action plan",
                )
                self.add_button(
                    "Test Emulator → Local",
                    lambda: self.guarded("Test emulator loopback", self._test_emu_to_local),
                    icon="phone_android",
                    tooltip="Test if the emulator can reach the local backend via 10.0.2.2:8080",
                )
                self.add_button(
                    "Test Device → LAN",
                    lambda: self.guarded("Test device LAN", self._test_device_to_lan),
                    icon="wifi",
                    tooltip="Test if the selected device can reach the backend via each laptop IP on port 8080",
                )
                self.add_button(
                    "Test Device → Funnel",
                    lambda: self.guarded("Test device Funnel", self._test_device_to_funnel),
                    icon="public",
                    tooltip="Test if the selected device can resolve and reach the Tailscale Funnel hostname via the internet",
                )

            # ── Match/seeding quick fixes ──
            with ui.row().classes("toolbar mt-2"):
                self.add_button(
                    "Check Matches",
                    lambda: self.guarded("Check matches", self._check_matches),
                    icon="favorite",
                    tooltip="Quick-check: how many matches does demo-user have right now?",
                )
                self.add_button(
                    "Seed Matches Now",
                    lambda: self.guarded("Seed matches", self._seed_matches),
                    icon="volunteer_activism",
                    color="positive",
                    tooltip="Directly create 3 matches (demo-user ↔ Maja, Elsa, Linnea) on the matchmaking service, bypassing the swipe flow",
                )

            # ── Results table ──
            ui.label("Connectivity Results").classes("subsection-title")
            conn_columns = [
                {"name": "path", "label": "Path", "field": "path", "sortable": True},
                {"name": "url", "label": "Target URL", "field": "url"},
                {"name": "verdict", "label": "✅/❌", "field": "verdict"},
                {"name": "detail", "label": "Detail", "field": "detail"},
                {"name": "suggestion", "label": "Suggestion", "field": "suggestion"},
            ]
            self.conn_table = ui.table(columns=conn_columns, rows=[], row_key="path").classes("w-full")

            # ── Action Plan ──
            ui.label("Action Plan").classes("subsection-title mt-4")
            self.conn_action_plan = ui.markdown("Run diagnostics to see an action plan.").classes(
                "text-sm p-3 bg-blue-50 rounded border border-blue-200"
            )

    # ── Connection panel async actions ────────────────────────────────────────

    async def _refresh_network_info(self) -> None:
        self.conn_ips = await self._get_laptop_ips()
        if not self.conn_ips:
            self.conn_netinfo.text = "No device-relevant IPs detected (check WiFi/tether cable)"
            return
        lines = ["IPs your phone/emulator can reach:"]
        for iface, ip in self.conn_ips.items():
            lines.append(f"  {iface}: {ip}")
        self.conn_netinfo.text = "\n".join(lines)
        self.log(f"Network info: {self.conn_ips}")

    async def _test_emu_to_local(self) -> None:
        """Test emulator → 10.0.2.2:8080."""
        devices = await self._adb_devices()
        emu = next((d for d in devices if "emulator" in d.get("serial", "")), None)
        if not emu:
            ui.notify("Emulator not connected — start it in the Android tab first", type="warning")
            return
        rows = [{
            "path": "Emulator → Local", "url": "http://10.0.2.2:8080",
            "host": "10.0.2.2", "verdict": "⏳", "detail": "Testing...", "suggestion": "",
        }]
        await self._run_pings(emu["serial"], rows)
        self._update_action_plan(rows)

    async def _test_device_to_lan(self) -> None:
        """Test selected device → laptop WiFi IP:8080."""
        serial = self.selected_device
        if not serial:
            ui.notify("No device selected — pick one in the Android tab first", type="warning")
            return
        self.conn_ips = await self._get_laptop_ips()
        if not self.conn_ips:
            ui.notify("No LAN IPs detected — is the laptop on a network?", type="warning")
            return
        rows = self._build_connection_rows(serial, self.conn_ips)
        # Remove emulator row since this is a device test
        rows = [r for r in rows if "Emulator" not in r["path"]]
        await self._run_pings(serial, rows)
        self._update_action_plan(rows)

    async def _test_device_to_funnel(self) -> None:
        """Test selected device → Funnel URL."""
        serial = self.selected_device
        if not serial:
            ui.notify("No device selected — pick one in the Android tab first", type="warning")
            return
        rows = [{
            "path": "Device → Funnel (internet)", "url": "https://a.tail45c6a7.ts.net/health",
            "host": "a.tail45c6a7.ts.net", "verdict": "⏳", "detail": "Testing...", "suggestion": "",
        }]
        await self._run_pings(serial, rows)
        self._update_action_plan(rows)

    async def _run_connection_diagnostics(self) -> None:
        """Full diagnostics: detect IPs, test all paths for selected device."""
        serial = self.selected_device
        if not serial:
            ui.notify("No device selected — pick one in the Android tab, or test emulator separately", type="warning")
            return
        self.conn_ips = await self._get_laptop_ips()
        self._refresh_network_info()
        rows = self._build_connection_rows(serial, self.conn_ips)
        # If device is emulator, note it; if phone, include emulator row too
        await self._run_pings(serial, rows)
        self._update_action_plan(rows)

    async def _run_pings(self, serial: str, rows: list[dict]) -> None:
        """Ping each host in rows from the device and update table + suggestions."""
        if self.conn_table is None:
            return
        batch_size = 2
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            tasks = [self._ping_from_device(serial, r["host"]) for r in batch]
            results = await asyncio.gather(*tasks)
            for j, (reachable, detail) in enumerate(results):
                r = batch[j]
                r["verdict"] = "✅" if reachable else "❌"
                r["detail"] = detail
                host = r["host"]
                if reachable:
                    if "10.0.2.2" in host:
                        r["suggestion"] = "✅ Use 'Local (Emulator)' dev server mode"
                    elif "ts.net" in host:
                        r["suggestion"] = "✅ Use 'Funnel' dev server mode — works from anywhere"
                    else:
                        r["suggestion"] = f"✅ Use 'Custom' dev server with host: {host}"
                else:
                    if "10.0.2.2" in host:
                        r["suggestion"] = "❌ Emulator not running or backend not started — check Android tab"
                    elif "ts.net" in host:
                        if "DNS" in detail or "unknown host" in detail:
                            r["suggestion"] = "❌ Device can't resolve Funnel hostname — check device internet connection (4G/WiFi)"
                        else:
                            r["suggestion"] = "❌ Funnel not reachable — the server may be offline or Tailscale Funnel is down"
                    else:
                        r["suggestion"] = "❌ Phone not on same network as this IP — try USB tether or WiFi hotspot"
            self.conn_table.rows = rows
            self.conn_table.update()

    def _update_action_plan(self, rows: list[dict]) -> None:
        """Update the action plan markdown after diagnostics complete."""
        plan = self._build_action_plan(rows)
        if hasattr(self, "conn_action_plan") and self.conn_action_plan is not None:
            self.conn_action_plan.content = plan

    async def _adb_devices(self) -> list[dict]:
        """Get list of connected ADB devices."""
        rc, out = await self.capture(["adb", "devices", "-l"], timeout=5)
        devices = []
        for line in out.strip().splitlines():
            if "\tdevice" in line:
                parts = line.split()
                serial = parts[0]
                detail = " ".join(parts[1:])
                devices.append({"serial": serial, "detail": detail})
        return devices

    async def _check_matches(self) -> None:
        """Quick-check matches and candidates for demo-user."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                token_resp = await client.post(
                    "http://localhost:8090/realms/DatingApp/protocol/openid-connect/token",
                    data={
                        "client_id": "dejtingapp-flutter",
                        "username": "bot_demo-user@bot.local",
                        "password": "bot_pass_demo-user",
                        "grant_type": "password",
                        "scope": "openid",
                    },
                )
                token = token_resp.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}

                match_resp = await client.get("http://localhost:8083/api/matchmaking/matches?userId=1", headers=headers)
                matches = match_resp.json()
                match_count = matches.get("totalCount", 0)

                cand_resp = await client.get("http://localhost:8083/api/matchmaking/profiles/1", headers=headers)
                candidates = cand_resp.json()
                cand_count = len(candidates) if isinstance(candidates, list) else 0

                self.log(f"Match check: {match_count} matches, {cand_count} candidates")
                ui.notify(f"{match_count} matches • {cand_count} candidates", type="positive" if match_count > 0 else "warning")
        except Exception as exc:
            self.log(f"Match check failed: {exc}")
            ui.notify("Match check failed — is the backend running?", type="negative")

    async def _seed_matches(self) -> None:
        """Directly create 3 matches for demo-user on the matchmaking service."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                created = []
                for bot_id in [2, 3, 4]:
                    resp = await client.post(
                        "http://localhost:8083/api/matchmaking/matches",
                        json={"user1Id": 1, "user2Id": bot_id},
                    )
                    data = resp.json()
                    created.append(data.get("matchId", "?"))
                self.log(f"Seeded matches: IDs {created}")
                ui.notify(f"✅ 3 matches created! (IDs: {created})", type="positive")
        except Exception as exc:
            self.log(f"Seed matches failed: {exc}")
            ui.notify("Seed matches failed — is the matchmaking service running?", type="negative")

    def _build_android_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Android").classes("section-title")
            avd_input = ui.input("AVD name", value="DatingApp_Pixel6_API33").classes("w-80")
            memory_input = ui.number("Memory MB", value=8192, min=1024, max=8192, step=512).classes("w-36")
            build_mode = ui.select(["debug", "release"], value="debug", label="APK mode").classes("w-40")

            with ui.row().classes("toolbar"):
                self.add_button("Refresh Devices", self.refresh_android, icon="refresh", tooltip="Re-scan connected Android devices via 'adb devices' and update the device list")
                self.add_button(
                    "Start Emulator",
                    lambda: self.guarded("Start emulator", lambda: self.start_emulator(str(avd_input.value), int(memory_input.value or 8192))),
                    icon="play_arrow",
                    tooltip="Launch an Android emulator from a local AVD image. Default: DatingApp_Pixel6_API33 with 2048MB RAM",
                )
                self.add_button("Stop Emulator", lambda: self.guarded("Stop emulator", self.stop_emulator), icon="stop", color="warning", tooltip="Kill the currently running Android emulator process")
                # Build APK runs in background — dashboard stays responsive, output in log below
                self.add_button("Build APK", lambda: self.build_apk(str(build_mode.value)), icon="build", tooltip="Run 'flutter build apk' in background. Watch the build log below for live progress. Dashboard stays responsive.")
                self.add_button("Install APK", lambda: self.install_apk(str(build_mode.value)), icon="download", tooltip="Install the last-built APK onto the selected device via 'adb install -r'. Output in build log below.")
                self.add_button("Launch App", lambda: self.guarded("Launch app", self.launch_android_app), icon="rocket_launch", color="positive", tooltip="Launch com.dejting.app/.MainActivity on the selected device via 'adb shell am start'")
                self.add_button("Flutter Desktop", lambda: self.guarded("Flutter desktop", self.flutter_run), icon="desktop_windows", color="accent", tooltip="Launch app as native Linux desktop window. Resize to ∼412x915 for phone-size preview. Zero emulator RAM overhead — hot reload in <1 second. No Android emulator or device needed.")
                self.add_button("Force Stop", lambda: self.guarded("Force stop app", self.force_stop_app), icon="pause_circle", color="warning", tooltip="Force-stop the app on the device via 'adb shell am force-stop' (like swiping it away)")
                self.add_button(
                    "Clear App Data",
                    lambda: self.confirm(
                        "Clear app data",
                        "This clears local app storage on the selected device.",
                        lambda: self.guarded("Clear app data", self.clear_app_data),
                    ),
                    icon="delete",
                    color="negative",
                    tooltip="Wipe app's SharedPreferences and local storage via 'adb shell pm clear'. Session, server choice, and onboarding state will be reset.",
                )
                self.add_button("Grant Permissions", lambda: self.guarded("Grant permissions", self.grant_permissions), icon="verified", tooltip="Pre-grant all required Android runtime permissions (location, camera, audio, storage, notifications) via 'adb shell pm grant'")
                self.add_button("Current Activity", lambda: self.guarded("Current activity", self.current_activity), icon="visibility", tooltip="Show the top-most Activity on the selected device via 'adb shell dumpsys activity activities' to debug navigation")

            android_columns = [
                {"name": "serial", "label": "Serial", "field": "serial"},
                {"name": "state", "label": "State", "field": "state"},
                {"name": "detail", "label": "Detail", "field": "detail"},
            ]
            self.android_table = ui.table(columns=android_columns, rows=[], row_key="serial").classes("w-full")

            def on_device_selected(event: Any) -> None:
                row = event.args[1] if isinstance(event.args, list) and len(event.args) > 1 else None
                if isinstance(row, dict) and row.get("serial"):
                    self.selected_device = row["serial"]
                    if self.device_label is not None:
                        self.device_label.text = f"Device: {self.selected_device}"
                    self.log(f"Selected Android device {self.selected_device}")

            self.android_table.on("rowClick", on_device_selected)

            # ── Build / Install live output ──
            ui.label("Build Output").classes("section-title mt-4")
            self.android_status = ui.label("Idle").classes("text-sm text-gray-500")
            self.android_log = ui.log(max_lines=300).classes("w-full h-48 font-mono text-xs")

    def _build_health_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Health").classes("section-title")
            with ui.row().classes("toolbar"):
                self.add_button("Refresh Health", self.refresh_health, icon="refresh", tooltip="Ping all service health endpoints and update the health table with status codes and latency")
                self.add_button("Run Health Script", lambda: self.guarded("Health script", lambda: self.run_smoke("health")), icon="monitor_heart", tooltip="Run the full API smoke test suite (api_tests.py) which verifies auth, profile, match, and messaging flows end-to-end")

            health_columns = [
                {"name": "probe", "label": "Probe", "field": "probe"},
                {"name": "status", "label": "Status", "field": "status"},
                {"name": "code", "label": "Code", "field": "code"},
                {"name": "latency", "label": "Latency", "field": "latency"},
                {"name": "url", "label": "URL", "field": "url"},
            ]
            self.health_table = ui.table(columns=health_columns, rows=[], row_key="probe").classes("w-full")

            ui.label("Database and container checks").classes("section-title")
            db_columns = [
                {"name": "name", "label": "Name", "field": "name"},
                {"name": "container", "label": "Container", "field": "container"},
                {"name": "table", "label": "Table", "field": "table"},
                {"name": "status", "label": "Status", "field": "status"},
                {"name": "count", "label": "Count", "field": "count"},
            ]
            self.db_table = ui.table(columns=db_columns, rows=[], row_key="name").classes("w-full")

    def _build_bots_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Bots & AI").classes("section-title")
            with ui.row().classes("toolbar"):
                self.add_button("Refresh Bots", self.refresh_bots, icon="refresh", tooltip="Fetch bot states, experiment findings, and LLM provider status from bot-service")
                self.add_button("Pause All Bots", lambda: self.guarded("Pause all bots", lambda: self.bot_json("/api/Bot/pause-all", method="POST")), icon="pause", tooltip="Pause all bot-service agents. Bots will stop swiping, messaging, and generating activity.")
                self.add_button("Resume All Bots", lambda: self.guarded("Resume all bots", lambda: self.bot_json("/api/Bot/resume-all", method="POST")), icon="play_arrow", tooltip="Resume all paused bot agents so they continue their demo/training loop")
                self.add_button("Stop Swarm", lambda: self.guarded("Stop swarm", lambda: self.bot_json("/api/Swarm/stop", method="POST")), icon="stop", color="warning", tooltip="Halt the bot swarm experiment — stops all active experiment runs on bot-service")
                self.add_button(
                    "Start Onboarding Swarm",
                    lambda: self.guarded(
                        "Start onboarding swarm",
                        lambda: self.bot_json("/api/Swarm/start", method="POST", json_body={"mode": "onboarding", "botCount": 3}),
                    ),
                    icon="groups",
                    tooltip="Launch a bot swarm experiment with 3 bots in onboarding mode. Bots will register, create profiles, and start swiping.",
                )

            bot_columns = [
                {"name": "persona", "label": "Persona", "field": "persona"},
                {"name": "status", "label": "Status", "field": "status"},
                {"name": "profile", "label": "Profile", "field": "profile"},
                {"name": "swipes", "label": "Swipes", "field": "swipes"},
                {"name": "messages", "label": "Messages", "field": "messages"},
                {"name": "matches", "label": "Matches", "field": "matches"},
                {"name": "last", "label": "Last Action", "field": "last"},
            ]
            self.bot_table = ui.table(columns=bot_columns, rows=[], row_key="persona").classes("w-full")

            ui.label("Findings and LLM").classes("section-title")
            finding_columns = [
                {"name": "group", "label": "Group", "field": "group"},
                {"name": "name", "label": "Name", "field": "name"},
                {"name": "count", "label": "Count", "field": "count"},
            ]
            self.findings_table = ui.table(columns=finding_columns, rows=[], row_key="name").classes("w-full")

    def _build_smoke_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Smoke Tests").classes("section-title")
            with ui.row().classes("toolbar"):
                self.add_button("Health", lambda: self.guarded("Smoke health", lambda: self.run_smoke("health")), icon="monitor_heart", tooltip="Run health-check smoke tests: ping all service endpoints and report pass/fail status")
                self.add_button("API Match Loop", lambda: self.guarded("Smoke API", lambda: self.run_smoke("api")), icon="route", tooltip="Run the match loop smoke test: create users, like profiles, verify matches are detected")
                self.add_button("All API Scenarios", lambda: self.guarded("Smoke all", lambda: self.run_smoke("all")), icon="fact_check", tooltip="Run all smoke test scenarios: auth, profile, match, messaging, safety, and verification")
                self.add_button("Safety", lambda: self.guarded("Smoke safety", lambda: self.run_smoke("safety")), icon="shield", tooltip="Run safety service smoke tests: content moderation, blocking, and reporting workflows")
                self.add_button("Wizard", lambda: self.guarded("Smoke wizard", lambda: self.run_smoke("wizard")), icon="checklist", tooltip="Run the onboarding wizard smoke test: simulate the full profile creation flow end-to-end")
                self.add_button("Reset and Seed", lambda: self.guarded("Reset and seed", lambda: self.run_smoke("reset_seed")), icon="restart_alt", tooltip="Run the reset-and-seed smoke test: clear interactions, seed mutual likes, verify matches are created")
            self.smoke_log = ui.log(max_lines=200).classes("w-full h-64")

    def _build_logs_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Logs").classes("section-title")
            choices = [str(service.log_file.relative_to(ROOT)) for service in SERVICES]
            self.log_select = ui.select(choices, value=choices[0], label="Service log").classes("w-80")
            with ui.row().classes("toolbar"):
                self.add_button("Refresh Log", self.tail_selected_log, icon="refresh", tooltip="Re-read the currently selected service log file and display its latest lines")
                self.add_button("Clear Event Log", lambda: self.event_log.clear() if self.event_log else None, icon="clear", tooltip="Clear the command event log panel (does not affect service logs on disk)")
            self.log_tail = ui.textarea("Tail").props("readonly outlined").classes("w-full h-80 font-mono text-xs")
            ui.label("Command event log").classes("section-title")
            self.event_log = ui.log(max_lines=400).classes("w-full h-80")

    # ─── AI & Caching Panel ────────────────────────────────────────────

    def _build_ai_cache_panel(self, tab: Any) -> None:
        """Batch API control, prompt caching, and token cost tracking."""
        with ui.tab_panel(tab):
            ui.label("AI Batch Processing & Prompt Caching").classes("section-title")

            # ── API key status ──
            with ui.card().classes("w-full"):
                ui.label("Configuration").classes("text-sm font-semibold text-gray-600")
                api_key = self._ai_api_key()
                key_ok = bool(api_key and api_key.startswith("sk-ant-"))
                self._ai_api_key_label = ui.label(
                    f"✅ ANTHROPIC_API_KEY set ({api_key[:12]}…)" if key_ok
                    else "⚠️ ANTHROPIC_API_KEY not set — export it in your shell or .env"
                ).classes(f"text-sm {'text-green-700' if key_ok else 'text-orange-600'} p-2 bg-gray-50 rounded")
                with ui.row().classes("gap-2"):
                    self._ai_model_select = ui.select(
                        label="Model",
                        value="claude-sonnet-4-20250514",
                        options=[
                            "claude-sonnet-4-20250514",
                            "claude-4-opus-20250514",
                            "claude-3-5-sonnet-20241022",
                            "claude-3-5-haiku-20241022",
                        ],
                    ).classes("min-w-[250px]")
                    self._ai_cache_ttl = ui.select(
                        label="Cache TTL",
                        value="ephemeral",
                        options={"ephemeral": "Ephemeral (5 min)", "none": "No cache"},
                    ).classes("min-w-[180px]")

            # ── Cache Test ──
            with ui.card().classes("w-full"):
                ui.label("Prompt Cache").classes("text-sm font-semibold text-gray-600")
                ui.label(
                    "Cache your DatingApp system context so repeated queries pay 90% less for cached tokens."
                ).classes("text-xs text-gray-500")
                with ui.row().classes("toolbar"):
                    self.add_button("Test Cache", lambda: self.guarded("Test cache", self._ai_test_cache),
                                    icon="memory", color="info", tooltip="Send a tiny request and check cache hit/miss")
                    self.add_button("Warm Cache", lambda: self.guarded("Warm cache", self._ai_warm_cache),
                                    icon="whatshot", color="positive",
                                    tooltip="Pre-load DatingApp system context into the cache")
                self._ai_cache_log = ui.log(max_lines=80).classes("w-full h-32")

            # ── Batch Job Submission ──
            with ui.card().classes("w-full"):
                ui.label("Batch Jobs (50% cheaper — async, ~24 h)").classes("text-sm font-semibold text-gray-600")
                self._ai_batch_type = ui.select(
                    label="Analysis Type",
                    value="test-coverage",
                    options={
                        "test-coverage": "📊 Test Coverage Analysis",
                        "api-contract": "🔗 API Contract Validation",
                        "service-arch": "🏗️ Service Architecture Review",
                        "log-analysis": "📝 Dev Log Analysis",
                        "custom": "✨ Custom Query",
                    },
                ).classes("w-full")
                self._ai_custom_query = ui.textarea(
                    label="Custom query (only used when Custom is selected)",
                    value="",
                ).classes("w-full")
                self._ai_custom_query.visible = False
                self._ai_batch_type.on_value_change(
                    lambda e: setattr(self._ai_custom_query, "visible", e.value == "custom")
                )
                with ui.row().classes("toolbar"):
                    self.add_button("Submit Batch", lambda: self.guarded("Submit batch", self._ai_submit_batch),
                                    icon="send", color="positive", tooltip="Submit analysis as a batch job (50% savings)")
                    self.add_button("Check Batch", lambda: self.guarded("Check batch", self._ai_check_batch),
                                    icon="hourglass_top", color="info", tooltip="Check status of last submitted batch")
                    self.add_button("Fetch Results", lambda: self.guarded("Fetch results", self._ai_fetch_results),
                                    icon="download", color="secondary", tooltip="Download results for completed batch")
                self._ai_batch_id_label = ui.label("Last batch: (none)").classes("text-xs text-gray-500")
                self._ai_batch_log = ui.log(max_lines=150).classes("w-full h-40")

            # ── Cost Calculator ──
            with ui.card().classes("w-full"):
                ui.label("Token Cost Calculator").classes("text-sm font-semibold text-gray-600")
                with ui.row().classes("gap-4 items-end"):
                    self._ai_token_input = ui.number(label="Input tokens", value=50000, min=100, step=5000).classes("w-40")
                    self._ai_token_output = ui.number(label="Output tokens", value=4000, min=100, step=1000).classes("w-40")
                    self.add_button("Calculate", self._ai_calculate_cost, icon="calculate", color="info")
                self._ai_cost_label = ui.label("").classes(
                    "text-sm font-mono text-gray-700 p-3 bg-gray-50 rounded whitespace-pre"
                )
                self._ai_calculate_cost()  # show defaults on load

    # ── AI helper methods ──

    def _ai_calculate_cost(self) -> None:
        inp = int(self._ai_token_input.value or 50000)
        out = int(self._ai_token_output.value or 4000)
        # Sonnet pricing (per 1M tokens): input $3, output $15
        reg_in = (inp / 1_000_000) * 3.0
        reg_out = (out / 1_000_000) * 15.0
        reg = reg_in + reg_out
        batch_in = reg_in * 0.5
        batch_out = reg_out * 0.5
        batch = batch_in + batch_out
        cache_in = reg_in * 0.1
        combo = batch_in * 0.1 + batch_out
        self._ai_cost_label.set_text(
            f"{'Mode':<22} {'Input':>8} {'Output':>8} {'Total':>8}\n"
            f"{'─' * 50}\n"
            f"{'Regular':<22} ${reg_in:>7.4f} ${reg_out:>7.4f} ${reg:>7.4f}\n"
            f"{'Batch (−50%)':<22} ${batch_in:>7.4f} ${batch_out:>7.4f} ${batch:>7.4f}\n"
            f"{'Cache hit (−90% in)':<22} ${cache_in:>7.4f} ${reg_out:>7.4f} ${cache_in + reg_out:>7.4f}\n"
            f"{'Batch + Cache':<22} ${combo - batch_out:>7.4f} ${batch_out:>7.4f} ${combo:>7.4f}\n"
            f"{'─' * 50}\n"
            f"Max savings vs regular: ${reg - combo:.4f} ({(1 - combo / reg) * 100:.0f}%)"
        )

    def _ai_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update(load_env_files())
        return env

    def _ai_api_key(self) -> str:
        env = self._ai_env()
        return env.get("ANTHROPIC_API_KEY", "")

    async def _ai_test_cache(self) -> None:
        log = self._ai_cache_log
        log.push(f"[{now_label()}] Testing prompt cache …")
        key = self._ai_api_key()
        if not key:
            log.push("❌ ANTHROPIC_API_KEY not set")
            return
        model = self._ai_model_select.value
        use_cache = self._ai_cache_ttl.value == "ephemeral"
        sys_block = '{"type":"text","text":"You are a DatingApp backend expert.","cache_control":{"type":"ephemeral"}}' if use_cache else '{"type":"text","text":"You are a DatingApp backend expert."}'
        script = (
            f'curl -s https://api.anthropic.com/v1/messages '
            f'-H "x-api-key: {key}" '
            f'-H "anthropic-version: 2023-06-01" '
            f'-H "content-type: application/json" '
            f'-d \'{{"model":"{model}","max_tokens":30,"system":[{sys_block}],'
            f'"messages":[{{"role":"user","content":"Say OK"}}]}}\''
        )
        try:
            proc = await asyncio.create_subprocess_shell(
                script, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=20)
            body = stdout.decode()
            try:
                data = json.loads(body)
                usage = data.get("usage", {})
                log.push(f"  Input tokens      : {usage.get('input_tokens', '?')}")
                log.push(f"  Cache creation     : {usage.get('cache_creation_input_tokens', 0)}")
                log.push(f"  Cache read (hit)   : {usage.get('cache_read_input_tokens', 0)}")
                cache_read = usage.get("cache_read_input_tokens", 0)
                if cache_read > 0:
                    log.push("✅ Cache HIT — subsequent calls use cached system prompt")
                else:
                    log.push("ℹ️ Cache MISS (first call writes to cache; next call within 5 min will hit)")
                if data.get("error"):
                    log.push(f"⚠️ API error: {data['error'].get('message', body[:200])}")
            except json.JSONDecodeError:
                log.push(f"⚠️ Raw response: {body[:300]}")
        except asyncio.TimeoutError:
            log.push("❌ Request timed out (20 s)")
        except Exception as exc:
            log.push(f"❌ {exc}")

    async def _ai_warm_cache(self) -> None:
        """Pre-load the full DatingApp system context into the cache."""
        log = self._ai_cache_log
        log.push(f"[{now_label()}] Warming cache with DatingApp system context …")
        key = self._ai_api_key()
        if not key:
            log.push("❌ ANTHROPIC_API_KEY not set")
            return
        # Prefer the optimized cache prompt; fall back to copilot-instructions.md
        ctx_file = ROOT / ".ai-system-prompt.md"
        if not ctx_file.exists():
            ctx_file = ROOT / ".github" / "copilot-instructions.md"
        if not ctx_file.exists():
            log.push("⚠️ No system prompt file found — using short fallback")
            system_text = "You are an expert .NET 8 architect for the DatingApp dating platform."
        else:
            system_text = ctx_file.read_text(errors="replace")
            log.push(f"  Loaded {len(system_text)} chars from {ctx_file.name}")

        model = self._ai_model_select.value
        payload = json.dumps({
            "model": model,
            "max_tokens": 20,
            "system": [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}],
            "messages": [{"role": "user", "content": "Confirm cache warm."}],
        })
        try:
            proc = await asyncio.create_subprocess_exec(
                "curl", "-s", "https://api.anthropic.com/v1/messages",
                "-H", f"x-api-key: {key}",
                "-H", "anthropic-version: 2023-06-01",
                "-H", "content-type: application/json",
                "-d", payload,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
            data = json.loads(stdout.decode())
            usage = data.get("usage", {})
            created = usage.get("cache_creation_input_tokens", 0)
            read = usage.get("cache_read_input_tokens", 0)
            log.push(f"  Cache creation tokens: {created}")
            log.push(f"  Cache read tokens    : {read}")
            if created > 0:
                log.push(f"✅ Cached {created} tokens — subsequent calls save 90% on system context for 5 min")
            elif read > 0:
                log.push("✅ Cache already warm — hit!")
            elif data.get("error"):
                log.push(f"⚠️ API error: {data['error'].get('message', '')[:200]}")
            else:
                log.push("ℹ️ Cache write may not have occurred (system text below minimum 1024 tokens?)")
        except Exception as exc:
            log.push(f"❌ {exc}")

    def _ai_batch_query(self) -> str:
        bt = self._ai_batch_type.value
        if bt == "custom":
            return self._ai_custom_query.value or "Summarise DatingApp architecture."
        queries = {
            "test-coverage": (
                "Analyze the DatingApp test coverage across all 8 .NET services. "
                "For each service (UserService :8082, MatchmakingService :8083, photo-service :8085, "
                "messaging-service :8086, swipe-service :8087, safety-service :8088, bot-service :8089, "
                "dejting-yarp :8080): 1) Identify likely untested code paths 2) Suggest 3-5 new unit tests "
                "3) Flag risky integration points. Focus on auth, match creation, and swipe contract."
            ),
            "api-contract": (
                "Validate the DatingApp API contracts: swipe-service (TargetUserId as string after contract fix), "
                "messaging-service (REST vs SignalR conversationId differences: alphabetic keycloak IDs joined by _ "
                "vs matchId), photo-service (auth header required). For each: suggest fixes, backward compat concerns."
            ),
            "service-arch": (
                "Review the DatingApp microservice architecture (8 .NET 8 services behind a YARP gateway, "
                "Keycloak OIDC, MySQL per-service, SignalR messaging). Assess resilience, suggest circuit breaker "
                "patterns, caching layers, and single-points-of-failure. Consider the Tailscale Funnel tunnel setup."
            ),
            "log-analysis": (
                "Analyze these DatingApp development patterns and suggest improvements: "
                "multi-repo git workflow (8+ repos), NiceGUI dashboard at :9100, bot-service demo personas, "
                "Whisper feedback transcription pipeline. Focus on developer productivity bottlenecks."
            ),
        }
        return queries.get(bt, queries["test-coverage"])

    async def _ai_submit_batch(self) -> None:
        log = self._ai_batch_log
        key = self._ai_api_key()
        if not key:
            log.push("❌ ANTHROPIC_API_KEY not set"); return

        query = self._ai_batch_query()
        model = self._ai_model_select.value
        job_id = f"da-{hashlib.md5(query.encode()).hexdigest()[:8]}"
        log.push(f"[{now_label()}] Submitting batch job '{job_id}' to {model} …")

        # Load cached system prompt for richer context in batch jobs
        sys_file = ROOT / ".ai-system-prompt.md"
        if sys_file.exists():
            sys_text = sys_file.read_text(errors="replace")
        else:
            sys_text = "You are an expert .NET 8 / Flutter architect for the DatingApp dating platform."
        sys_text += "\n\nProvide specific, actionable recommendations with code examples where appropriate."

        payload = json.dumps({
            "requests": [{
                "custom_id": job_id,
                "params": {
                    "model": model,
                    "max_tokens": 4096,
                    "messages": [{"role": "user", "content": query}],
                    "system": sys_text,
                },
            }],
        })
        try:
            proc = await asyncio.create_subprocess_exec(
                "curl", "-s", "-X", "POST", "https://api.anthropic.com/v1/messages/batches",
                "-H", f"x-api-key: {key}",
                "-H", "anthropic-version: 2023-06-01",
                "-H", "content-type: application/json",
                "-d", payload,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
            data = json.loads(stdout.decode())
            if data.get("id"):
                batch_id = data["id"]
                self._ai_last_batch_id = batch_id
                self._ai_batch_id_label.set_text(f"Last batch: {batch_id}")
                log.push(f"✅ Batch submitted: {batch_id}")
                log.push(f"   Status: {data.get('processing_status', '?')}")
                # Persist for later retrieval
                (ROOT / ".ai-last-batch-id").write_text(batch_id)
            elif data.get("error"):
                log.push(f"❌ API error: {data['error'].get('message', '')[:300]}")
            else:
                log.push(f"⚠️ Unexpected: {json.dumps(data)[:300]}")
        except Exception as exc:
            log.push(f"❌ {exc}")

    async def _ai_check_batch(self) -> None:
        log = self._ai_batch_log
        key = self._ai_api_key()
        if not key:
            log.push("❌ ANTHROPIC_API_KEY not set"); return

        batch_id = getattr(self, "_ai_last_batch_id", None)
        if not batch_id:
            id_file = ROOT / ".ai-last-batch-id"
            batch_id = id_file.read_text().strip() if id_file.exists() else None
        if not batch_id:
            log.push("⚠️ No batch job ID found — submit a job first"); return

        log.push(f"[{now_label()}] Checking batch {batch_id} …")
        try:
            proc = await asyncio.create_subprocess_exec(
                "curl", "-s", f"https://api.anthropic.com/v1/messages/batches/{batch_id}",
                "-H", f"x-api-key: {key}",
                "-H", "anthropic-version: 2023-06-01",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=20)
            data = json.loads(stdout.decode())
            status = data.get("processing_status", "unknown")
            counts = data.get("request_counts", {})
            log.push(f"  Status     : {status}")
            log.push(f"  Succeeded  : {counts.get('succeeded', '?')}")
            log.push(f"  Errored    : {counts.get('errored', '?')}")
            log.push(f"  In progress: {counts.get('processing', '?')}")
            if status == "ended":
                log.push("✅ Batch complete — click 'Fetch Results' to download")
            elif data.get("error"):
                log.push(f"⚠️ {data['error'].get('message', '')[:200]}")
        except Exception as exc:
            log.push(f"❌ {exc}")

    async def _ai_fetch_results(self) -> None:
        log = self._ai_batch_log
        key = self._ai_api_key()
        if not key:
            log.push("❌ ANTHROPIC_API_KEY not set"); return

        batch_id = getattr(self, "_ai_last_batch_id", None)
        if not batch_id:
            id_file = ROOT / ".ai-last-batch-id"
            batch_id = id_file.read_text().strip() if id_file.exists() else None
        if not batch_id:
            log.push("⚠️ No batch job ID found"); return

        log.push(f"[{now_label()}] Fetching results for {batch_id} …")
        try:
            proc = await asyncio.create_subprocess_exec(
                "curl", "-s", f"https://api.anthropic.com/v1/messages/batches/{batch_id}/results",
                "-H", f"x-api-key: {key}",
                "-H", "anthropic-version: 2023-06-01",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
            raw = stdout.decode()
            out_file = ROOT / "logs" / f"batch-result-{batch_id[:16]}.jsonl"
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(raw)
            log.push(f"✅ Results saved to {out_file}")
            # Parse JSONL and show content
            for line in raw.strip().splitlines()[:5]:
                try:
                    entry = json.loads(line)
                    cid = entry.get("custom_id", "?")
                    result = entry.get("result", {})
                    msg_type = result.get("type", "?")
                    if msg_type == "succeeded":
                        content = result.get("message", {}).get("content", [])
                        text = content[0].get("text", "")[:500] if content else "(empty)"
                        log.push(f"  [{cid}] ✅ {text}")
                    else:
                        log.push(f"  [{cid}] {msg_type}: {json.dumps(result)[:200]}")
                except json.JSONDecodeError:
                    log.push(f"  (raw) {line[:200]}")
            if raw.count("\n") > 5:
                log.push(f"  … {raw.count(chr(10)) - 5} more entries — see {out_file}")
        except Exception as exc:
            log.push(f"❌ {exc}")

    def _build_billing_panel(self, tab: Any) -> None:
        with ui.tab_panel(tab):
            ui.label("Billing & Monetization").classes("section-title")

            with ui.row().classes("toolbar"):
                self.add_button("Refresh Stats", self.refresh_billing, icon="refresh",
                                tooltip="Refresh billing statistics from the UserService admin billing endpoint")
                self.add_button("Grant Free Sparks (100)",
                                lambda: self.guarded("Grant sparks", lambda: self._grant_test_sparks(100)),
                                icon="bolt", color="positive",
                                tooltip="Sandbox: credit 100 Sparks to demo-user for testing")

            # ── Metrics row ──
            with ui.row().classes("gap-4 flex-wrap"):
                with ui.element("div").classes("metric"):
                    ui.label("Total Premium Users").classes("label")
                    self.billing_premium_label = ui.label("...").classes("value text-xl font-bold")
                with ui.element("div").classes("metric"):
                    ui.label("Total Purchases").classes("label")
                    self.billing_purchases_label = ui.label("...").classes("value text-xl")
                with ui.element("div").classes("metric"):
                    ui.label("Sparks Credited").classes("label")
                    self.billing_credited_label = ui.label("...").classes("value text-xl")
                with ui.element("div").classes("metric"):
                    ui.label("Sparks Spent").classes("label")
                    self.billing_spent_label = ui.label("...").classes("value text-xl")
                with ui.element("div").classes("metric"):
                    ui.label("Last Updated").classes("label")
                    self.billing_updated_label = ui.label("...").classes("value text-sm text-gray-500")

            # ── Pricing catalog ──
            ui.label("Pricing Catalog").classes("section-title")
            with ui.row().classes("toolbar"):
                ui.label("Prices are shown as configured in appsettings / hardcoded catalog.").classes("text-sm text-gray-500")
            pricing_cols = [
                {"name": "sku", "label": "SKU", "field": "sku"},
                {"name": "name", "label": "Name", "field": "name"},
                {"name": "desc", "label": "Description", "field": "desc"},
                {"name": "price", "label": "Price (US cents)", "field": "price"},
                {"name": "details", "label": "Details", "field": "details"},
            ]
            pricing_rows = [
                {"sku": "premium_month", "name": "Premium Month", "desc": "30 days full access", "price": "—", "details": "Unlimited swipes, 2 Sparks/day"},
                {"sku": "premium_3months", "name": "Premium Quarter", "desc": "90 days full access", "price": "—", "details": "Save vs. monthly"},
                {"sku": "premium_year", "name": "Premium Year", "desc": "365 days full access", "price": "—", "details": "Best value"},
                {"sku": "sparks_100", "name": "Starter Pack", "desc": "100 Sparks", "price": "99", "details": "~$0.99 ❌ sandbox only"},
                {"sku": "sparks_500", "name": "Boost Pack", "desc": "500 Sparks", "price": "399", "details": "~$3.99 ❌ sandbox only"},
                {"sku": "sparks_1500", "name": "Super Pack", "desc": "1500 Sparks", "price": "999", "details": "~$9.99 ❌ sandbox only"},
            ]
            self.billing_pricing_table = ui.table(columns=pricing_cols, rows=pricing_rows, row_key="sku").classes("w-full")
            ui.label("Note: Prices shown above are sandbox stubs. Production prices configured via appsettings or admin API.").classes("text-xs text-gray-400 mt-1")

            # ── Recent Purchases ──
            ui.label("Recent Purchases (30 days)").classes("section-title")
            purchase_cols = [
                {"name": "user", "label": "User", "field": "user"},
                {"name": "sku", "label": "SKU", "field": "sku"},
                {"name": "date", "label": "Date", "field": "date"},
            ]
            self.billing_purchases_table = ui.table(columns=purchase_cols, rows=[], row_key="id").classes("w-full")

            # ── Active Subscriptions ──
            ui.label("Active Subscriptions").classes("section-title")
            subs_cols = [
                {"name": "user", "label": "User", "field": "user"},
                {"name": "tier", "label": "Tier", "field": "tier"},
                {"name": "expires", "label": "Expires", "field": "expires"},
                {"name": "remaining", "label": "Days Left", "field": "remaining"},
            ]
            self.billing_subs_table = ui.table(columns=subs_cols, rows=[], row_key="user").classes("w-full")

            # ── Top Sparks Users ──
            ui.label("Top Sparks Users").classes("section-title")
            sparks_cols = [
                {"name": "user", "label": "User", "field": "user"},
                {"name": "balance", "label": "Balance", "field": "balance"},
                {"name": "daily_used", "label": "Used Today", "field": "daily_used"},
            ]
            self.billing_sparks_table = ui.table(columns=sparks_cols, rows=[], row_key="user").classes("w-full")

            # Initial load
            ui.timer(0.1, self.refresh_billing, once=True)

    async def _grant_test_sparks(self, amount: int) -> None:
        """Credit Sparks to demo-user for testing via the purchase endpoint."""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                token = await self._get_demo_token(client)
                if not token:
                    ui.notify("Cannot grant Sparks: no demo token", type="negative")
                    return
                resp = await client.post(
                    "http://localhost:8080/api/billing/purchase",
                    json={"sku": f"sparks_{amount}"},
                    headers={"Authorization": f"Bearer {token}"},
                )
                if resp.status_code == 200:
                    ui.notify(f"Granted {amount} Sparks to demo-user", type="positive")
                else:
                    ui.notify(f"Grant failed: {resp.status_code}", type="negative")
        except Exception as e:
            ui.notify(f"Grant error: {e}", type="negative")

    async def refresh_billing(self) -> None:
        """Fetch billing stats from the admin endpoint and update tables."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "http://localhost:8082/api/billing/admin/stats",
                    headers={"X-Internal-API-Key": self._get_internal_api_key()},
                )
                if resp.status_code != 200:
                    ui.notify(f"Billing stats failed: {resp.status_code}", type="warning")
                    return
                data = resp.json()

            # Update metric labels
            if hasattr(self, 'billing_premium_label') and self.billing_premium_label:
                self.billing_premium_label.set_text(str(data.get("totalPremiumUsers", 0)))
            if hasattr(self, 'billing_purchases_label') and self.billing_purchases_label:
                self.billing_purchases_label.set_text(str(data.get("totalPurchases", 0)))
            if hasattr(self, 'billing_credited_label') and self.billing_credited_label:
                self.billing_credited_label.set_text(str(data.get("totalSparksCredited", 0)))
            if hasattr(self, 'billing_spent_label') and self.billing_spent_label:
                self.billing_spent_label.set_text(str(data.get("totalSparksSpent", 0)))
            if hasattr(self, 'billing_updated_label') and self.billing_updated_label:
                ts = data.get("generatedAt", "")
                self.billing_updated_label.set_text(ts[:19] if ts else "N/A")

            # Update purchase table
            purchases = data.get("recentPurchases", [])
            pur_rows = []
            for i, p in enumerate(purchases):
                pur_rows.append({
                    "id": str(i),
                    "user": p.get("userId", "")[:20],
                    "sku": p.get("sku", ""),
                    "date": (p.get("purchasedAt", "")[:19]),
                })
            if self.billing_purchases_table:
                self.billing_purchases_table.rows = pur_rows

            # Update subscription table
            subs = data.get("activeSubscriptions", [])
            sub_rows = []
            for s in subs:
                remaining = s.get("daysRemaining", 0)
                status = "✅ Active" if remaining > 0 else "⚠ Expired"
                expires = (s.get("expiresAt") or "")[:10]
                sub_rows.append({
                    "user": s.get("userId", "")[:20],
                    "tier": s.get("tier", ""),
                    "expires": expires,
                    "remaining": f"{remaining}d {status}",
                })
            if self.billing_subs_table:
                self.billing_subs_table.rows = sub_rows

            # Update Sparks table
            sparks = data.get("topSparksUsers", [])
            sp_rows = []
            for u in sparks:
                sp_rows.append({
                    "user": u.get("userId", "")[:20],
                    "balance": str(u.get("balance", 0)),
                    "daily_used": str(u.get("dailyUsed", 0)),
                })
            if self.billing_sparks_table:
                self.billing_sparks_table.rows = sp_rows

        except httpx.ConnectError:
            self.log("Billing refresh skipped (services not running)")
        except Exception as e:
            ui.notify(f"Billing refresh error: {e}", type="warning")

    @staticmethod
    def _get_internal_api_key() -> str:
        return "user-service-internal-key-dev-only"

    @staticmethod
    async def _get_demo_token(client: httpx.AsyncClient) -> str | None:
        """Get an access token for the dev login user (bot_demo-user) via Keycloak direct grant."""
        try:
            resp = await client.post(
                "http://localhost:8090/realms/DatingApp/protocol/openid-connect/token",
                data={
                    "grant_type": "password",
                    "client_id": "dejtingapp-flutter",
                    "username": "bot_demo-user@bot.local",
                    "password": "bot_pass_demo-user",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if resp.status_code == 200:
                body = resp.json()
                return body.get("access_token")
            else:
                print(f"Token error: {resp.status_code} {resp.text[:200]}")
        except Exception as e:
            print(f"Token exception: {e}")
        return None


def print_dry_run_summary() -> None:
    print("DatingApp Dev Control Dashboard dry run")
    print(f"Root: {ROOT}")
    print(f"Flutter root: {FLUTTER_ROOT}")
    print(f"Dashboard URL: http://localhost:{DEFAULT_PORT}")
    print("")
    print("Services:")
    for service in SERVICES:
        exists = "ok" if service.cwd.exists() else "missing"
        print(f"  {service.name:20} :{service.port} {exists} {shell_join(service.command)}")
    print("")
    print("Bot routes:")
    for route in [
        "/api/Bot/status",
        "/api/Bot/personas",
        "/api/Bot/pause-all",
        "/api/Bot/resume-all",
        "/api/Bot/reset-counters",
        "/api/Findings/summary",
        "/api/Findings/recent",
        "/api/Findings/llm-stats",
        "/api/Swarm/status",
        "/api/Swarm/start",
        "/api/Swarm/stop",
        "/api/Swarm/modes",
        "/api/bot/Experiments",
    ]:
        print(f"  http://localhost:8089{route}")
    print("")
    print(f"Android package: {APP_PACKAGE}/{APP_ACTIVITY}")
    print(f"Demo login: {DEMO_USERNAME} / <masked>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DatingApp local NiceGUI control dashboard")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Dashboard port")
    parser.add_argument("--host", default="127.0.0.1", help="Dashboard bind host")
    parser.add_argument("--dry-run", action="store_true", help="Print configuration and exit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.dry_run:
        print_dry_run_summary()
        return

    _load_runtime_dependencies(require_ui=True)
    dashboard = DevDashboard(dry_run=False)

    @ui.page("/")
    def index() -> None:
        dashboard.build()

    app.on_shutdown(lambda: print("Dashboard shutdown", flush=True))
    ui.run(
        host=args.host,
        port=args.port,
        title="DatingApp Dev Control",
        reload=False,
        show=False,
    )


if __name__ == "__main__":
    main()
