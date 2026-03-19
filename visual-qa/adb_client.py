"""ADB client wrapper for visual QA automation.

Connects to Android emulator via ADB and provides methods for:
- Screenshots, UI hierarchy dumps
- Tap, swipe, text input
- APK installation and app lifecycle
"""

import os
import re
import subprocess
import time
from pathlib import Path


class AdbClient:
    def __init__(self, host: str | None = None, port: str | None = None):
        self.host = host or os.environ.get("ADB_HOST", "localhost")
        self.port = port or os.environ.get("ADB_PORT", "5555")
        self.serial = f"{self.host}:{self.port}"
        self._connected = False

    def _run(self, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
        cmd = ["adb", "-s", self.serial] + args
        return subprocess.run(cmd, capture_output=True, timeout=timeout)

    def connect(self, retries: int = 10, delay: float = 5.0) -> bool:
        for i in range(retries):
            result = subprocess.run(
                ["adb", "connect", self.serial],
                capture_output=True, timeout=10
            )
            output = result.stdout.decode(errors="replace")
            if "connected" in output.lower():
                self._connected = True
                return True
            time.sleep(delay)
        return False

    def wait_for_boot(self, timeout: int = 300) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            result = self._run(["shell", "getprop", "sys.boot_completed"])
            if result.stdout.strip() == b"1":
                return True
            time.sleep(5)
        return False

    def screenshot(self) -> bytes:
        result = self._run(["exec-out", "screencap", "-p"], timeout=15)
        if result.returncode != 0:
            raise RuntimeError(f"Screenshot failed: {result.stderr.decode(errors='replace')}")
        return result.stdout

    def save_screenshot(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.screenshot()
        path.write_bytes(data)
        return path

    def ui_dump(self) -> str:
        self._run(["shell", "uiautomator", "dump", "/sdcard/window_dump.xml"], timeout=15)
        result = self._run(["shell", "cat", "/sdcard/window_dump.xml"], timeout=10)
        if result.returncode != 0:
            raise RuntimeError(f"UI dump failed: {result.stderr.decode(errors='replace')}")
        return result.stdout.decode("utf-8", errors="replace")

    def tap(self, x: int, y: int) -> None:
        self._run(["shell", "input", "tap", str(x), str(y)])

    def long_press(self, x: int, y: int, duration_ms: int = 1000) -> None:
        self._run(["shell", "input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        self._run(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])

    def swipe_left(self, y: int = 1170) -> None:
        self.swipe(800, y, 200, y, 200)

    def swipe_right(self, y: int = 1170) -> None:
        self.swipe(200, y, 800, y, 200)

    def input_text(self, text: str) -> None:
        escaped = text.replace(" ", "%s").replace("&", "\\&").replace("<", "\\<").replace(">", "\\>")
        self._run(["shell", "input", "text", escaped])

    def press_back(self) -> None:
        self._run(["shell", "input", "keyevent", "KEYCODE_BACK"])

    def press_enter(self) -> None:
        self._run(["shell", "input", "keyevent", "KEYCODE_ENTER"])

    def press_home(self) -> None:
        self._run(["shell", "input", "keyevent", "KEYCODE_HOME"])

    def hide_keyboard(self) -> None:
        self._run(["shell", "input", "keyevent", "KEYCODE_ESCAPE"])

    def install_apk(self, apk_path: str | Path) -> bool:
        result = self._run(["install", "-r", "-g", str(apk_path)], timeout=120)
        return result.returncode == 0

    def launch_app(self, package: str = "com.dejting.app", activity: str = ".MainActivity") -> None:
        self._run(["shell", "am", "start", "-n", f"{package}/{activity}"])

    def clear_app(self, package: str = "com.dejting.app") -> None:
        self._run(["shell", "pm", "clear", package])

    def force_stop(self, package: str = "com.dejting.app") -> None:
        self._run(["shell", "am", "force-stop", package])

    def grant_permissions(self, package: str = "com.dejting.app") -> None:
        permissions = [
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.CAMERA",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.POST_NOTIFICATIONS",
        ]
        for perm in permissions:
            self._run(["shell", "pm", "grant", package, perm])

    def get_current_activity(self) -> str:
        result = self._run(["shell", "dumpsys", "activity", "activities"])
        output = result.stdout.decode(errors="replace")
        for line in output.splitlines():
            if "mResumedActivity" in line or "topResumedActivity" in line:
                return line.strip()
        return ""

    def is_screen_on(self) -> bool:
        result = self._run(["shell", "dumpsys", "power"])
        return b"mWakefulness=Awake" in result.stdout

    def wake_screen(self) -> None:
        if not self.is_screen_on():
            self._run(["shell", "input", "keyevent", "KEYCODE_WAKEUP"])
            time.sleep(0.5)
            self.swipe(540, 2000, 540, 1000, 300)  # swipe up to unlock
