"""Semantic Navigation Engine — state machine that drives the app.

Detects the current screen via uiautomator XML signatures, looks up the
appropriate action, executes it via ADB, captures a screenshot, and repeats.

Text-based navigation: taps elements by content-desc text, never pixel coords.
State-machine driven: survives screen reordering, additions, and removals.

Retry logic: screen detection is retried up to ``retry_count`` times with
exponential backoff (default: 3 retries at 1 s, 2 s, 4 s).  Screens that
required at least one retry are marked as *flaky* in the report.

System-dialog handling: common Android overlays (ANR, battery optimization,
permission re-prompts) are dismissed automatically before each detection
attempt so they never count as an unknown screen.
"""

import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path

from adb_client import AdbClient
from element_finder import find_by_text, find_input_field, get_all_elements
from signatures import ScreenId, detect_screen

# ---------------------------------------------------------------------------
# Android system-dialog patterns
# ---------------------------------------------------------------------------

# Button texts that dismiss "App isn't responding" dialogs
_ANR_DISMISS_TEXTS = ["Wait", "Close app", "OK"]

# Button texts that dismiss battery / background-restriction dialogs
_BATTERY_DISMISS_TEXTS = ["Not now", "Remind me later", "DISMISS", "Cancel", "No thanks"]

# Button texts that accept or dismiss permission re-prompts
_PERMISSION_ACCEPT_TEXTS = ["Allow", "While using the app", "Only this time"]
_PERMISSION_DENY_TEXTS = ["Don't ask again", "Deny and don't ask again"]

# Package names of known system-dialog processes (used as a quick filter)
_SYSTEM_DIALOG_PACKAGES = frozenset([
    "android",
    "com.android.systemui",
    "com.android.packageinstaller",
    "com.android.permissioncontroller",
    "com.google.android.permissioncontroller",
    "com.miui.securitycenter",
    "com.samsung.android.lool",
])

# Content-desc / text fragments that indicate a system dialog is present
_SYSTEM_DIALOG_INDICATORS = [
    "isn't responding",
    "has stopped",
    "keeps stopping",
    "isn't responding",
    "Battery optimization",
    "background battery",
    "restrict battery",
    "This app may not work",
]


class ActionType(Enum):
    TAP_TEXT = auto()      # Tap element matching text
    INPUT_TEXT = auto()    # Type text into focused field
    SWIPE_LEFT = auto()    # Swipe left (pass)
    SWIPE_RIGHT = auto()   # Swipe right (like)
    PRESS_BACK = auto()    # Press back button
    WAIT = auto()          # Wait N seconds
    TAP_COORD = auto()     # Tap specific coordinates (fallback)
    SKIP = auto()          # Skip this screen (no action needed)
    TAP_TAB = auto()       # Tap a bottom nav tab by text


@dataclass
class Action:
    action_type: ActionType
    value: str = ""       # Text to find/type, or seconds to wait
    description: str = "" # Human-readable description of what this does


@dataclass
class StepResult:
    screen: ScreenId
    action: Action | None
    screenshot_path: str = ""
    xml_path: str = ""
    success: bool = True
    error: str = ""
    duration_ms: int = 0
    retry_count: int = 0  # Number of retries needed to detect this screen


@dataclass
class UseCaseResult:
    name: str
    steps: list[StepResult] = field(default_factory=list)
    success: bool = True
    error: str = ""
    duration_ms: int = 0
    flaky_screens: list[str] = field(default_factory=list)  # Screen names that needed retries

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "flaky_screens": self.flaky_screens,
            "steps": [
                {
                    "screen": s.screen.name,
                    "action": s.action.description if s.action else "none",
                    "success": s.success,
                    "error": s.error,
                    "screenshot": s.screenshot_path,
                    "duration_ms": s.duration_ms,
                    "retry_count": s.retry_count,
                }
                for s in self.steps
            ],
        }


def _ts() -> str:
    """Return a compact UTC timestamp string for log lines."""
    return datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]


class Navigator:
    """State machine that navigates through app screens via ADB."""

    def __init__(
        self,
        adb: AdbClient,
        output_dir: str | Path = "/app/test-results",
        settle_time: float = 2.0,
        max_retries: int = 3,
        retry_count: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialise the navigator.

        Args:
            adb: ADB client instance.
            output_dir: Directory for screenshots and XML dumps.
            settle_time: Seconds to wait between actions.
            max_retries: Max consecutive same-screen iterations before pressing
                back to escape a stuck state.
            retry_count: How many times to retry screen detection on failure or
                UNKNOWN result before giving up (default 3, backoff 1 s/2 s/4 s).
            retry_delay: Base delay in seconds for the first retry; subsequent
                retries double this value (exponential backoff).
        """
        self.adb = adb
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.settle_time = settle_time
        self.max_retries = max_retries
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self._step_counter = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _capture(self, use_case: str, label: str) -> tuple[str, str]:
        """Capture screenshot + UI dump. Returns (screenshot_path, xml_path)."""
        self._step_counter += 1
        prefix = f"{self._step_counter:03d}-{use_case}-{label}"
        ss_path = str(self.output_dir / f"{prefix}.png")
        xml_path = str(self.output_dir / f"{prefix}.xml")

        try:
            self.adb.save_screenshot(ss_path)
        except Exception as e:
            ss_path = f"ERROR: {e}"

        try:
            xml = self.adb.ui_dump()
            Path(xml_path).write_text(xml, encoding="utf-8")
        except Exception as e:
            xml_path = f"ERROR: {e}"

        return ss_path, xml_path

    # ------------------------------------------------------------------
    # System-dialog handling
    # ------------------------------------------------------------------

    def _is_system_dialog(self, xml: str) -> bool:
        """Return True if the XML looks like an Android system dialog overlay."""
        xml_lower = xml.lower()
        return any(indicator.lower() in xml_lower for indicator in _SYSTEM_DIALOG_INDICATORS)

    def _dismiss_system_dialog(self, xml: str) -> bool:
        """Attempt to dismiss a known Android system dialog.

        Tries dismiss-button texts in priority order.  Returns True if a
        button was found and tapped, False otherwise.
        """
        # ANR "App isn't responding" — prefer "Wait" so the app stays alive
        for text in _ANR_DISMISS_TEXTS:
            pos = find_by_text(xml, text)
            if pos:
                print(f"[{_ts()}] 🛡  Dismissing ANR/system dialog via '{text}'")
                self.adb.tap(pos[0], pos[1])
                return True

        # Permission re-prompts — accept them to keep the flow moving
        for text in _PERMISSION_ACCEPT_TEXTS:
            pos = find_by_text(xml, text)
            if pos:
                print(f"[{_ts()}] 🛡  Dismissing permission dialog via '{text}'")
                self.adb.tap(pos[0], pos[1])
                return True

        # Battery / background-restriction dialogs
        for text in _BATTERY_DISMISS_TEXTS:
            pos = find_by_text(xml, text)
            if pos:
                print(f"[{_ts()}] 🛡  Dismissing battery dialog via '{text}'")
                self.adb.tap(pos[0], pos[1])
                return True

        # Last resort: press back
        print(f"[{_ts()}] 🛡  Dismissing unknown system dialog via BACK key")
        self.adb.press_back()
        return True

    # ------------------------------------------------------------------
    # Screen detection with retry + backoff
    # ------------------------------------------------------------------

    def detect_current_screen(self) -> tuple[ScreenId, str]:
        """Get current screen ID and raw XML (no retry).

        Use :meth:`detect_current_screen_with_retry` from ``run_flow`` to get
        automatic retry/backoff and system-dialog dismissal.
        """
        xml = self.adb.ui_dump()
        screen_id, score = detect_screen(xml)
        return screen_id, xml

    def detect_current_screen_with_retry(self) -> tuple[ScreenId, str, int]:
        """Detect the current screen, retrying up to ``retry_count`` times.

        Between attempts the navigator:
        1. Checks for and dismisses any Android system dialogs.
        2. Waits with exponential backoff (base ``retry_delay`` seconds).

        Returns:
            (screen_id, xml, retries_used) where *retries_used* is the number
            of extra attempts needed beyond the first (0 = succeeded first try).

        Raises:
            RuntimeError: if the UI dump itself fails on every attempt.
        """
        last_exc: Exception | None = None
        delay = self.retry_delay

        for attempt in range(self.retry_count + 1):  # attempt 0 = first try
            try:
                xml = self.adb.ui_dump()
            except Exception as exc:
                last_exc = exc
                retries_left = self.retry_count - attempt
                if retries_left > 0:
                    print(
                        f"[{_ts()}] ⚠  UI dump failed (attempt {attempt + 1}/"
                        f"{self.retry_count + 1}): {exc} — retrying in {delay:.1f}s"
                    )
                    time.sleep(delay)
                    delay *= 2
                continue

            # Dismiss any system dialog before trying to identify the screen
            if self._is_system_dialog(xml):
                self._dismiss_system_dialog(xml)
                time.sleep(1.0)
                try:
                    xml = self.adb.ui_dump()
                except Exception:
                    pass  # use the xml we already have

            screen_id, score = detect_screen(xml)

            if screen_id != ScreenId.UNKNOWN or attempt == self.retry_count:
                if attempt > 0:
                    print(
                        f"[{_ts()}] ✅ Screen detected as {screen_id.name} "
                        f"after {attempt} retry/retries (score={score:.1f})"
                    )
                return screen_id, xml, attempt

            # Still UNKNOWN — retry with backoff
            print(
                f"[{_ts()}] 🔁 Screen UNKNOWN on attempt {attempt + 1}/"
                f"{self.retry_count + 1} — waiting {delay:.1f}s before retry"
            )
            time.sleep(delay)
            delay *= 2

        # All attempts exhausted without a successful UI dump
        if last_exc is not None:
            raise RuntimeError(f"UI dump failed after {self.retry_count + 1} attempts: {last_exc}")

        # Should be unreachable, but satisfy type checker
        raise RuntimeError("detect_current_screen_with_retry: unexpected exit")  # pragma: no cover

    def execute_action(self, action: Action, xml: str) -> bool:
        """Execute a single action. Returns True if action was performed."""
        if action.action_type == ActionType.TAP_TEXT:
            pos = find_by_text(xml, action.value)
            if pos:
                self.adb.tap(pos[0], pos[1])
                return True
            return False

        elif action.action_type == ActionType.INPUT_TEXT:
            pos = find_input_field(xml)
            if pos:
                self.adb.tap(pos[0], pos[1])
                time.sleep(0.3)
            self.adb.input_text(action.value)
            self.adb.hide_keyboard()
            return True

        elif action.action_type == ActionType.SWIPE_LEFT:
            self.adb.swipe_left()
            return True

        elif action.action_type == ActionType.SWIPE_RIGHT:
            self.adb.swipe_right()
            return True

        elif action.action_type == ActionType.PRESS_BACK:
            self.adb.press_back()
            return True

        elif action.action_type == ActionType.WAIT:
            time.sleep(float(action.value))
            return True

        elif action.action_type == ActionType.TAP_COORD:
            parts = action.value.split(",")
            self.adb.tap(int(parts[0]), int(parts[1]))
            return True

        elif action.action_type == ActionType.TAP_TAB:
            pos = find_by_text(xml, action.value)
            if pos:
                self.adb.tap(pos[0], pos[1])
                return True
            return False

        elif action.action_type == ActionType.SKIP:
            return True

        return False

    def run_flow(
        self,
        name: str,
        flow: dict[ScreenId, list[Action]],
        terminal_screens: set[ScreenId] | None = None,
        max_steps: int = 50,
    ) -> UseCaseResult:
        """Run a use case flow — state machine loop.

        Args:
            name: Use case name for reporting
            flow: Mapping of ScreenId → list of Actions to perform on that screen
            terminal_screens: Set of ScreenIds that indicate the flow is complete
            max_steps: Safety limit to prevent infinite loops
        """
        result = UseCaseResult(name=name)
        start_time = time.time()
        last_screen = None
        stuck_count = 0
        # Track which screen names have been seen with retries
        _flaky_seen: set[str] = set()

        for step_num in range(max_steps):
            step_start = time.time()

            # Detect current screen (with retry + backoff + dialog dismissal)
            try:
                screen_id, xml, retries_used = self.detect_current_screen_with_retry()
            except Exception as e:
                result.steps.append(StepResult(
                    screen=ScreenId.UNKNOWN, action=None,
                    success=False, error=f"UI dump failed: {e}"
                ))
                result.success = False
                result.error = f"UI dump failed at step {step_num}"
                break

            # Record flaky screens (needed at least one retry to detect)
            if retries_used > 0:
                screen_name = screen_id.name
                if screen_name not in _flaky_seen:
                    _flaky_seen.add(screen_name)
                    result.flaky_screens.append(screen_name)
                    print(
                        f"[{_ts()}] ⚠  Flaky screen detected: {screen_name} "
                        f"(needed {retries_used} retry/retries)"
                    )

            # Check if we're at a terminal screen
            if terminal_screens and screen_id in terminal_screens:
                ss_path, xml_path = self._capture(name, f"terminal-{screen_id.name}")
                result.steps.append(StepResult(
                    screen=screen_id,
                    action=Action(ActionType.SKIP, description="Terminal screen reached"),
                    screenshot_path=ss_path, xml_path=xml_path,
                    duration_ms=int((time.time() - step_start) * 1000),
                    retry_count=retries_used,
                ))
                break

            # Check if stuck
            if screen_id == last_screen:
                stuck_count += 1
                if stuck_count >= self.max_retries:
                    ss_path, xml_path = self._capture(name, f"stuck-{screen_id.name}")
                    result.steps.append(StepResult(
                        screen=screen_id, action=None,
                        screenshot_path=ss_path, xml_path=xml_path,
                        success=False, error=f"Stuck on {screen_id.name} for {stuck_count} iterations",
                        duration_ms=int((time.time() - step_start) * 1000),
                        retry_count=retries_used,
                    ))
                    # Try pressing back as escape
                    self.adb.press_back()
                    time.sleep(self.settle_time)
                    stuck_count = 0
                    continue
            else:
                stuck_count = 0
            last_screen = screen_id

            # Look up actions for this screen
            actions = flow.get(screen_id)
            if not actions:
                # Unknown screen in this flow — capture and skip
                if screen_id == ScreenId.UNKNOWN:
                    ss_path, xml_path = self._capture(name, f"unknown-{step_num}")
                    result.steps.append(StepResult(
                        screen=screen_id, action=None,
                        screenshot_path=ss_path, xml_path=xml_path,
                        success=False, error="Unknown screen encountered",
                        duration_ms=int((time.time() - step_start) * 1000),
                        retry_count=retries_used,
                    ))
                    time.sleep(self.settle_time)
                    continue
                # Known screen but not in this flow — skip it
                ss_path, xml_path = self._capture(name, f"skip-{screen_id.name}")
                result.steps.append(StepResult(
                    screen=screen_id,
                    action=Action(ActionType.SKIP, description=f"Screen {screen_id.name} not in flow"),
                    screenshot_path=ss_path, xml_path=xml_path,
                    duration_ms=int((time.time() - step_start) * 1000),
                    retry_count=retries_used,
                ))
                time.sleep(self.settle_time)
                continue

            # Execute all actions for this screen
            for action in actions:
                ss_path, xml_path = self._capture(name, f"{screen_id.name}-{action.description}")
                ok = self.execute_action(action, xml)
                step_result = StepResult(
                    screen=screen_id, action=action,
                    screenshot_path=ss_path, xml_path=xml_path,
                    success=ok,
                    error="" if ok else f"Action failed: {action.description}",
                    duration_ms=int((time.time() - step_start) * 1000),
                    retry_count=retries_used,
                )
                result.steps.append(step_result)
                if not ok:
                    result.success = False

                time.sleep(self.settle_time)
                # Re-dump XML after action for next action in same screen
                try:
                    xml = self.adb.ui_dump()
                except Exception:
                    pass

        result.duration_ms = int((time.time() - start_time) * 1000)
        # If we exited the loop without terminal, it's a timeout
        if not terminal_screens or (result.steps and result.steps[-1].screen not in (terminal_screens or set())):
            if not result.error:
                result.error = f"Flow did not reach terminal screen within {max_steps} steps"
                result.success = False

        return result
